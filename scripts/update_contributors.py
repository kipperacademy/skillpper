#!/usr/bin/env python3
"""Build the public contributor snapshot used by GitHub Pages."""

import argparse
import json
import os
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
MAX_CONTRIBUTORS = 12


def fetch_contributors(repository: str, token: str) -> list[dict]:
    owner, name = repository.split("/", 1)
    url = (
        f"https://api.github.com/repos/{quote(owner, safe='')}/"
        f"{quote(name, safe='')}/contributors?per_page=100"
    )
    request = Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "skillpper-pages",
        },
    )
    with urlopen(request, timeout=20) as response:
        if response.status == 204:
            return []
        data = json.load(response)
    if not isinstance(data, list):
        raise ValueError("GitHub contributors response must be a list")
    return data


def contributor_snapshot(repository: str, contributors: list[dict]) -> dict:
    people = []
    for contributor in contributors:
        if not isinstance(contributor, dict):
            continue
        login = contributor.get("login")
        avatar_url = contributor.get("avatar_url")
        profile_url = contributor.get("html_url")
        if (
            contributor.get("type") != "User"
            or not isinstance(login, str)
            or login.lower().endswith("[bot]")
            or not isinstance(avatar_url, str)
            or not avatar_url.startswith("https://avatars.githubusercontent.com/")
            or not isinstance(profile_url, str)
            or not profile_url.startswith("https://github.com/")
        ):
            continue
        people.append({"login": login, "avatar_url": avatar_url, "html_url": profile_url})
        if len(people) == MAX_CONTRIBUTORS:
            break
    return {"repository": repository, "contributors": people}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY"))
    parser.add_argument("--output", type=Path, default=ROOT / "docs" / "contributors.json")
    args = parser.parse_args()
    token = os.environ.get("GH_TOKEN")
    if not args.repository or args.repository.count("/") != 1 or not token:
        parser.error("GITHUB_REPOSITORY (owner/repo) and GH_TOKEN are required")
    snapshot = contributor_snapshot(
        args.repository, fetch_contributors(args.repository, token)
    )
    args.output.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
