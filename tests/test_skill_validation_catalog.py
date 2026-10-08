from __future__ import annotations

from pathlib import Path
import stat
import unittest

from scripts.skill_validation.bundles import validate_bundle
from scripts.skill_validation.catalog import discover
from scripts.skill_validation.models import Skill, SourceFile
from scripts.skill_validation.structure import validate_structure


ROOT = Path(__file__).resolve().parents[1]


def root_skills() -> tuple[str, ...]:
    return tuple(sorted(path.parent.name for path in ROOT.glob("*/SKILL.md")))


def source_files(skill_name: str) -> tuple[SourceFile, ...]:
    directory = ROOT / skill_name
    files = []
    for path in sorted(directory.rglob("*")):
        if path.is_symlink():
            raise AssertionError(f"symlink in skill source: {path.relative_to(ROOT)}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise AssertionError(f"non-regular skill source: {path.relative_to(ROOT)}")
        relative = path.relative_to(ROOT).as_posix()
        mode = "100755" if path.stat().st_mode & stat.S_IXUSR else "100644"
        files.append(SourceFile(relative, path.read_bytes(), mode))
    return tuple(files)


def skill_from_source(name: str) -> Skill:
    return Skill(name, source_files(name))


def repository_source_files() -> tuple[SourceFile, ...]:
    files = []
    for path in sorted(ROOT.rglob("*")):
        relative = path.relative_to(ROOT)
        if relative.parts[0].startswith("."):
            continue
        if path.is_symlink():
            raise AssertionError(f"symlink in repository source: {relative.as_posix()}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise AssertionError(f"non-regular repository source: {relative.as_posix()}")
        mode = "100755" if path.stat().st_mode & stat.S_IXUSR else "100644"
        files.append(SourceFile(relative.as_posix(), path.read_bytes(), mode))
    return tuple(files)


class SkillCatalogContractTests(unittest.TestCase):
    def test_every_root_skill_has_a_valid_review_manifest(self):
        names = root_skills()
        self.assertTrue(names, "expected at least one root skill")
        for name in names:
            with self.subTest(skill=name):
                findings = validate_structure(skill_from_source(name))
                self.assertEqual(
                    [(item.rule_id, item.path, item.message) for item in findings],
                    [],
                )

    def test_every_existing_optional_bundle_matches_source_exactly(self):
        bundles = sorted(ROOT.glob("*.skill"))
        skill_names = set(root_skills())
        bundle_names = {path.stem for path in bundles}
        self.assertLessEqual(bundle_names, skill_names, "orphan optional bundle found")
        for bundle_path in bundles:
            name = bundle_path.stem
            with self.subTest(bundle=bundle_path.name):
                self.assertFalse(bundle_path.is_symlink(), "bundle symlink is unsupported")
                self.assertTrue(bundle_path.is_file(), "bundle must be a regular file")
                bundle_mode = "100755" if bundle_path.stat().st_mode & stat.S_IXUSR else "100644"
                bundle = SourceFile(bundle_path.name, bundle_path.read_bytes(), bundle_mode)
                findings = validate_bundle(bundle, skill_from_source(name))
                self.assertEqual(
                    [(item.rule_id, item.path, item.message) for item in findings],
                    [],
                )

    def test_index_workflow_is_read_only_and_never_pushes(self):
        workflow = (ROOT / ".github/workflows/update-skills-index.yml").read_text(encoding="utf-8")
        self.assertNotRegex(workflow, r"(?im)^\s*contents:\s*write\s*$")
        self.assertNotRegex(workflow, r"(?im)^\s*(?:run:\s*)?git\s+push\b")


class RepositoryRootContractTests(unittest.TestCase):
    def test_no_root_directory_is_missing_a_skill_manifest(self):
        _, findings = discover(repository_source_files())
        orphans = sorted((item.rule_id, item.path) for item in findings if item.rule_id == "INV002")
        self.assertEqual(
            orphans,
            [],
            "Every top-level directory must contain a SKILL.md manifest or be an infrastructure root",
        )


if __name__ == "__main__":
    unittest.main()
