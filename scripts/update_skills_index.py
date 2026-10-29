#!/usr/bin/env python3
"""Generate the README index from root and Aprendizagem skill frontmatter."""

import argparse
import html
from pathlib import Path
import re
import sys

import yaml

START = "<!-- SKILLS:START -->"
END = "<!-- SKILLS:END -->"
ROOT = Path(__file__).resolve().parents[1]


def table_text(value: str) -> str:
    """Keep metadata as literal text inside a single Markdown table cell."""
    value = html.escape(" ".join(value.split()), quote=False)
    return re.sub(r"([\\|`*_\[\]])", r"\\\1", value)


def render_index(root: Path) -> str:
    skills = []
    for path in sorted([*root.glob("*/SKILL.md"), *root.glob("Aprendizagem/*/SKILL.md")]):
        if path.parent.name.startswith("."):
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        if not lines or lines[0] != "---":
            raise ValueError(f"{path}: expected YAML frontmatter starting with ---")
        try:
            end = lines.index("---", 1)
        except ValueError as exc:
            raise ValueError(f"{path}: missing closing --- in frontmatter") from exc
        try:
            metadata = yaml.safe_load("\n".join(lines[1:end]))
        except yaml.YAMLError as exc:
            raise ValueError(f"{path}: invalid YAML frontmatter: {exc}") from exc
        if not isinstance(metadata, dict):
            raise ValueError(f"{path}: frontmatter must be a mapping")
        for field in ("name", "description"):
            value = metadata.get(field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{path}: {field} must be a non-empty string")
        name = metadata["name"]
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
            raise ValueError(f"{path}: name must use lowercase letters, digits, and hyphens")
        if name != path.parent.name:
            raise ValueError(f"{path}: name must match folder name {path.parent.name!r}")
        skills.append((name, metadata["description"], path.relative_to(root).as_posix()))

    rows = ["| Skill | Description |", "| --- | --- |"]
    for name, description, path in sorted(skills):
        rows.append(f"| [{name}](./{path}) | {table_text(description)} |")
    if not skills:
        rows.append("| — | No skills available yet. |")
    return "\n".join(rows)


def updated_readme(root: Path) -> str:
    readme = (root / "README.md").read_text(encoding="utf-8")
    if readme.count(START) != 1 or readme.count(END) != 1:
        raise ValueError("README.md must contain exactly one pair of skills index markers")
    start = readme.index(START) + len(START)
    end = readme.index(END)
    if end < start:
        raise ValueError("README.md skills index markers are in the wrong order")
    return readme[:start] + "\n\n" + render_index(root) + "\n\n" + readme[end:]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the index is outdated")
    args = parser.parse_args()
    try:
        updated = updated_readme(ROOT)
        path = ROOT / "README.md"
        if updated == path.read_text(encoding="utf-8"):
            print("Skills index is up to date.")
            return 0
        if args.check:
            print("Skills index is outdated. Run: python scripts/update_skills_index.py", file=sys.stderr)
            return 1
        path.write_text(updated, encoding="utf-8")
        print("Updated the README skills index.")
        return 0
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
