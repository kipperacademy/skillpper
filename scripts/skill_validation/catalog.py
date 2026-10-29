"""Discover complete skill roots from a flat collection of trusted Git blobs."""

from .models import Finding, Skill, SourceFile, finding
from .models import portable_path_prefixes


INFRASTRUCTURE_ROOTS = frozenset({".git", ".github", ".conductor", "docs", "scripts", "tests", "security"})


def discover(files: tuple[SourceFile, ...]) -> tuple[tuple[Skill, ...], tuple[Finding, ...]]:
    """Build skills, report unexpected roots and bundles without matching source."""
    by_path = {source.path: source for source in files}
    roots: dict[str, list[SourceFile]] = {}
    archives: dict[str, SourceFile] = {}
    findings: list[Finding] = []

    portable_prefixes: dict[str, str] = {}
    seen_paths: set[str] = set()
    for source in files:
        collision = source.path in seen_paths
        seen_paths.add(source.path)
        for portable_key, spelling in portable_path_prefixes(source.path):
            previous_spelling = portable_prefixes.get(portable_key)
            if previous_spelling is not None and previous_spelling != spelling:
                collision = True
            portable_prefixes[portable_key] = spelling
        if collision:
            findings.append(finding(
                "INV004", "error", source.path, None,
                "Path or directory prefix collides on a case-insensitive filesystem.",
                source.data,
            ))

        parts = source.path.split("/")
        if parts[-1] == "SKILL.md" and not (
            (len(parts) == 2 and parts[0] not in INFRASTRUCTURE_ROOTS and parts[0] != "Aprendizagem")
            or (len(parts) == 3 and parts[0] == "Aprendizagem")
        ):
            findings.append(finding(
                "INV005", "error", source.path, None,
                "SKILL.md is permitted only in a root skill directory or directly inside Aprendizagem.",
                source.data,
            ))

    for source in files:
        if "/" not in source.path:
            if source.path.endswith(".skill"):
                archives[source.path[:-6]] = source
            continue
        root, _ = source.path.split("/", 1)
        if root in INFRASTRUCTURE_ROOTS:
            continue
        if root == "Aprendizagem" and source.path.count("/") >= 2:
            root = "/".join(source.path.split("/")[:2])
        roots.setdefault(root, []).append(source)

    skills: list[Skill] = []
    skill_roots: set[str] = set()
    for root in sorted(roots):
        root_files = tuple(sorted(roots[root], key=lambda source: source.path))
        if f"{root}/SKILL.md" in by_path:
            skill_roots.add(root)
            skills.append(Skill(root, root_files))
        else:
            # The directory is in the candidate inventory but has no root manifest.
            findings.append(finding("INV002", "error", root, None, "Root directory has no SKILL.md manifest.", b""))

    for bundle_name, bundle in sorted(archives.items()):
        if bundle_name not in skill_roots:
            findings.append(finding("INV003", "error", bundle.path, None, "Skill bundle has no matching source directory.", bundle.data))

    return tuple(skills), tuple(sorted(findings, key=lambda item: (item.path, item.rule_id)))
