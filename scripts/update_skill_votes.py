#!/usr/bin/env python3
"""Generate RANKING.md from GitHub Discussion vote reactions."""

import argparse
from datetime import datetime, timezone
import html
import json
import os
from pathlib import Path
import re
import sys
from urllib import error, request

import yaml

ROOT = Path(__file__).resolve().parents[1]
RANKING = ROOT / "RANKING.md"
DOCS_DATA = ROOT / "docs" / "votes.json"
DISCUSSION_REGISTRY = ROOT / "docs" / "vote-discussions.json"
DEFAULT_CATEGORY = "Skill Votes"
MARKER_RE = re.compile(r"<!--\s*skillpper-vote-skill:\s*([a-z0-9]+(?:-[a-z0-9]+)*)\s*-->")


class MissingVoteCategoryError(RuntimeError):
    """Raised when the configured Discussion category does not exist yet."""

    def __init__(self, category_name: str) -> None:
        super().__init__(
            f"Discussion category {category_name!r} was not found. "
            "Enable GitHub Discussions and create that category first."
        )


def read_skill_metadata(root: Path) -> dict[str, str]:
    """Return root-level skill names mapped to descriptions."""
    skills = {}
    for path in sorted(root.glob("*/SKILL.md")):
        if path.parent.name.startswith("."):
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        if not lines or lines[0] != "---":
            raise ValueError(f"{path}: expected YAML frontmatter starting with ---")
        try:
            end = lines.index("---", 1)
        except ValueError as exc:
            raise ValueError(f"{path}: missing closing --- in frontmatter") from exc
        metadata = yaml.safe_load("\n".join(lines[1:end]))
        if not isinstance(metadata, dict):
            raise ValueError(f"{path}: frontmatter must be a mapping")
        name = metadata.get("name")
        description = metadata.get("description")
        if not isinstance(name, str) or not isinstance(description, str):
            raise ValueError(f"{path}: name and description must be strings")
        if name != path.parent.name:
            raise ValueError(f"{path}: name must match folder name {path.parent.name!r}")
        skills[name] = description
    return skills


def vote_body(skill: str) -> str:
    return "\n".join(
        [
            f"<!-- skillpper-vote-skill: {skill} -->",
            "",
            f"# Vote for `{skill}`",
            "",
            "React to this discussion with `:+1:` to vote for this skill.",
            "Add a comment if you want to share what worked, what was confusing, or what would make it better.",
        ]
    )


def parse_skill_marker(body: str) -> str | None:
    match = MARKER_RE.search(body or "")
    return match.group(1) if match else None


def github_graphql(token: str, query: str, variables: dict) -> dict:
    payload = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    req = request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub GraphQL request failed: {exc.code} {detail}") from exc
    if result.get("errors"):
        raise RuntimeError(f"GitHub GraphQL returned errors: {result['errors']}")
    return result["data"]


def resolve_category_id(categories: list[dict], category_name: str) -> str:
    for category in categories:
        if category["name"].lower() == category_name.lower():
            return category["id"]
    raise MissingVoteCategoryError(category_name)


def repository_context(token: str, owner: str, name: str, category_name: str) -> tuple[str, str]:
    query = """
    query($owner: String!, $name: String!) {
      repository(owner: $owner, name: $name) {
        id
        discussionCategories(first: 25) {
          nodes {
            id
            name
          }
        }
      }
    }
    """
    repo = github_graphql(token, query, {"owner": owner, "name": name})["repository"]
    if repo is None:
        raise RuntimeError(f"Repository {owner}/{name} was not found")
    category_id = resolve_category_id(repo["discussionCategories"]["nodes"], category_name)
    return repo["id"], category_id


def fetch_category_discussions(token: str, owner: str, name: str, category_id: str) -> dict[str, dict]:
    query = """
    query($owner: String!, $name: String!, $categoryId: ID!, $after: String) {
      repository(owner: $owner, name: $name) {
        discussions(first: 100, after: $after, categoryId: $categoryId, orderBy: {field: CREATED_AT, direction: ASC}) {
          pageInfo {
            hasNextPage
            endCursor
          }
          nodes {
            id
            title
            body
            url
            reactionGroups {
              content
              users {
                totalCount
              }
            }
          }
        }
      }
    }
    """
    discussions: dict[str, dict] = {}
    after = None
    while True:
        data = github_graphql(
            token,
            query,
            {"owner": owner, "name": name, "categoryId": category_id, "after": after},
        )
        page = data["repository"]["discussions"]
        for node in page["nodes"]:
            discussions[node["id"]] = node
        if not page["pageInfo"]["hasNextPage"]:
            return discussions
        after = page["pageInfo"]["endCursor"]


def create_discussion(token: str, repository_id: str, category_id: str, skill: str) -> dict:
    mutation = """
    mutation($repositoryId: ID!, $categoryId: ID!, $title: String!, $body: String!) {
      createDiscussion(input: {repositoryId: $repositoryId, categoryId: $categoryId, title: $title, body: $body}) {
        discussion {
          id
          title
          body
          url
          reactionGroups {
            content
            users {
              totalCount
            }
          }
        }
      }
    }
    """
    data = github_graphql(
        token,
        mutation,
        {
            "repositoryId": repository_id,
            "categoryId": category_id,
            "title": f"Vote: {skill}",
            "body": vote_body(skill),
        },
    )
    return data["createDiscussion"]["discussion"]


def thumbs_up_count(discussion: dict | None) -> int:
    if not discussion:
        return 0
    for group in discussion.get("reactionGroups", []):
        if group["content"] == "THUMBS_UP":
            return int(group["users"]["totalCount"])
    return 0


def read_discussion_registry() -> dict[str, dict]:
    if not DISCUSSION_REGISTRY.exists():
        return {}
    data = json.loads(DISCUSSION_REGISTRY.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{DISCUSSION_REGISTRY}: expected a JSON object")
    discussions = data.get("discussions", {})
    if not isinstance(discussions, dict):
        raise ValueError(f"{DISCUSSION_REGISTRY}: discussions must be an object")
    return discussions


def write_discussion_registry(registry: dict[str, dict], check: bool) -> int:
    content = json.dumps({"discussions": dict(sorted(registry.items()))}, ensure_ascii=False, indent=2) + "\n"
    current = DISCUSSION_REGISTRY.read_text(encoding="utf-8") if DISCUSSION_REGISTRY.exists() else ""
    if current == content:
        print("Vote discussion registry is up to date.")
        return 0
    if check:
        print("Vote discussion registry is outdated. Run: python scripts/update_skill_votes.py", file=sys.stderr)
        return 1
    DISCUSSION_REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    DISCUSSION_REGISTRY.write_text(content, encoding="utf-8")
    print("Updated the vote discussion registry.")
    return 0


def canonical_discussions(skills: dict[str, str], registry: dict[str, dict], discussions_by_id: dict[str, dict]) -> dict[str, dict]:
    discussions = {}
    marker_claims: dict[str, list[str]] = {skill: [] for skill in skills}
    for discussion_id, discussion in discussions_by_id.items():
        skill = parse_skill_marker(discussion.get("body", ""))
        if skill in marker_claims:
            marker_claims[skill].append(discussion_id)

    for skill in sorted(skills):
        entry = registry.get(skill)
        if not isinstance(entry, dict):
            continue
        discussion_id = entry.get("id")
        if not isinstance(discussion_id, str):
            continue
        discussion = discussions_by_id.get(discussion_id)
        if not discussion:
            print(f"Registered vote discussion for {skill} was not found.")
            continue
        marker = parse_skill_marker(discussion.get("body", ""))
        # An explicit registry marker preserves a renamed skill's existing discussion.
        if marker != entry.get("marker", skill):
            print(f"Registered vote discussion for {skill} has an invalid marker; ignoring it.")
            continue
        discussions[skill] = discussion

    for skill, ids in marker_claims.items():
        registered_id = registry.get(skill, {}).get("id") if isinstance(registry.get(skill), dict) else None
        duplicates = [discussion_id for discussion_id in ids if discussion_id != registered_id]
        if duplicates:
            print(f"Ignoring unregistered duplicate vote discussions for {skill}: {', '.join(duplicates)}")
    return discussions


def render_ranking(skills: dict[str, str], discussions: dict[str, dict], category_name: str) -> str:
    rows = ranked_rows(skills, discussions)

    lines = [
        "# Community Skill Ranking",
        "",
        "This ranking is generated from GitHub Discussion `:+1:` reactions.",
        f"Vote discussions live in the `{category_name}` discussion category.",
        "",
        "| Rank | Skill | Votes | Discussion |",
        "| ---: | --- | ---: | --- |",
    ]
    for index, row in enumerate(rows, start=1):
        skill = html.escape(row["skill"], quote=False)
        discussion = f"[Vote]({row['discussion_url']})" if row["discussion_url"] else "Not created yet"
        lines.append(f"| {index} | [{skill}](./{skill}/SKILL.md) | {row['votes']} | {discussion} |")
    if not rows:
        lines.append("| - | No skills available yet. | 0 | - |")
    lines.extend(
        [
            "",
            "Do not edit this file by hand. Run `python scripts/update_skill_votes.py` instead.",
            "",
        ]
    )
    return "\n".join(lines)


def write_ranking(content: str, check: bool) -> int:
    current = RANKING.read_text(encoding="utf-8") if RANKING.exists() else ""
    if current == content:
        print("Community ranking is up to date.")
        return 0
    if check:
        print("Community ranking is outdated. Run: python scripts/update_skill_votes.py", file=sys.stderr)
        return 1
    RANKING.write_text(content, encoding="utf-8")
    print("Updated the community ranking.")
    return 0


def ranked_rows(skills: dict[str, str], discussions: dict[str, dict]) -> list[dict]:
    rows = []
    for skill in sorted(skills):
        discussion = discussions.get(skill)
        rows.append(
            {
                "skill": skill,
                "description": " ".join(skills[skill].split()),
                "votes": thumbs_up_count(discussion),
                "discussion_url": discussion["url"] if discussion else "",
            }
        )
    rows.sort(key=lambda row: (-row["votes"], row["skill"]))
    for index, row in enumerate(rows, start=1):
        row["rank"] = index
    return rows


def dashboard_data(skills: dict[str, str], discussions: dict[str, dict], category_name: str, repository: str | None) -> dict:
    rows = ranked_rows(skills, discussions)
    return {
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "repository": repository,
        "category": category_name,
        "total_skills": len(rows),
        "total_votes": sum(row["votes"] for row in rows),
        "skills": rows,
    }


def write_dashboard_data(data: dict, check: bool) -> int:
    current_data = None
    if DOCS_DATA.exists():
        try:
            current_data = json.loads(DOCS_DATA.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            current_data = None
    if isinstance(current_data, dict):
        comparable_current = dict(current_data)
        comparable_next = dict(data)
        comparable_current.pop("updated_at", None)
        comparable_next.pop("updated_at", None)
        if comparable_current == comparable_next:
            print("Dashboard vote data is up to date.")
            return 0

    content = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    current = DOCS_DATA.read_text(encoding="utf-8") if DOCS_DATA.exists() else ""
    if current == content:
        print("Dashboard vote data is up to date.")
        return 0
    if check:
        print("Dashboard vote data is outdated. Run: python scripts/update_skill_votes.py", file=sys.stderr)
        return 1
    DOCS_DATA.parent.mkdir(parents=True, exist_ok=True)
    DOCS_DATA.write_text(content, encoding="utf-8")
    print("Updated the dashboard vote data.")
    return 0


def split_repository(value: str) -> tuple[str, str]:
    parts = value.split("/", 1)
    if len(parts) != 2 or not all(parts):
        raise ValueError("GITHUB_REPOSITORY must look like owner/name")
    return parts[0], parts[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--category", default=DEFAULT_CATEGORY, help="GitHub Discussions category used for voting")
    parser.add_argument("--check", action="store_true", help="fail if RANKING.md is outdated")
    parser.add_argument(
        "--sync-discussions",
        action="store_true",
        help="create missing vote discussions before generating RANKING.md",
    )
    parser.add_argument(
        "--allow-missing-category",
        action="store_true",
        help="exit successfully when the vote category is not configured yet",
    )
    args = parser.parse_args()

    try:
        skills = read_skill_metadata(ROOT)
        token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        repository = os.environ.get("GITHUB_REPOSITORY")
        if not token or not repository:
            content = render_ranking(skills, {}, args.category)
            data = dashboard_data(skills, {}, args.category, repository)
            registry = read_discussion_registry()
            registry = {skill: registry[skill] for skill in sorted(skills) if skill in registry}
            return (
                write_ranking(content, args.check)
                or write_dashboard_data(data, args.check)
                or write_discussion_registry(registry, args.check)
            )

        owner, name = split_repository(repository)
        repository_id, category_id = repository_context(token, owner, name, args.category)
        registry = read_discussion_registry()
        registry = {skill: registry[skill] for skill in sorted(skills) if skill in registry}
        discussions_by_id = fetch_category_discussions(token, owner, name, category_id)
        discussions = canonical_discussions(skills, registry, discussions_by_id)
        missing = [skill for skill in sorted(skills) if skill not in discussions]
        if args.sync_discussions:
            for skill in missing:
                discussions[skill] = create_discussion(token, repository_id, category_id, skill)
                registry[skill] = {"id": discussions[skill]["id"], "url": discussions[skill]["url"]}
                print(f"Created vote discussion for {skill}.")
        elif missing:
            print("Missing vote discussions: " + ", ".join(missing))

        content = render_ranking(skills, discussions, args.category)
        data = dashboard_data(skills, discussions, args.category, repository)
        return (
            write_ranking(content, args.check)
            or write_dashboard_data(data, args.check)
            or write_discussion_registry(registry, args.check)
        )
    except MissingVoteCategoryError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        if args.allow_missing_category or os.environ.get("GITHUB_EVENT_NAME") == "schedule":
            print(f"::warning::{exc}")
            print("Skipping this run until the vote category is configured.", file=sys.stderr)
            return 0
        return 1
    except (OSError, RuntimeError, ValueError, yaml.YAMLError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
