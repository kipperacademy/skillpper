import stat
import unittest
from pathlib import Path

from scripts.skill_validation.bundles import validate_bundle
from scripts.skill_validation.models import Skill, SourceFile


ROOT = Path(__file__).resolve().parents[1]


class SkillBundleTests(unittest.TestCase):
    def test_optional_archives_match_their_complete_source_tree(self):
        bundles = sorted(ROOT.glob("*.skill"))
        self.assertTrue(bundles, "expected at least one distributable skill bundle")

        for bundle in bundles:
            with self.subTest(bundle=bundle.name):
                with tempfile.TemporaryDirectory() as temp_dir:
                    with zipfile.ZipFile(bundle) as archive:
                        archive.extractall(temp_dir)

                    extracted_root = Path(temp_dir)
                    skill_files = list(extracted_root.glob("*/SKILL.md"))
                    self.assertEqual(len(skill_files), 1)
                    source_root = ROOT / bundle.stem
                    self.assertTrue(source_root.is_dir())

                    for source_file in source_root.rglob("*"):
                        if source_file.is_file():
                            archived_file = extracted_root / source_file.relative_to(ROOT)
                            self.assertTrue(archived_file.is_file())
                            if source_file.suffix.lower() in {".md", ".yaml", ".yml"}:
                                self.assertEqual(
                                    source_file.read_text(encoding="utf-8"),
                                    archived_file.read_text(encoding="utf-8"),
                                )
                            else:
                                self.assertEqual(source_file.read_bytes(), archived_file.read_bytes())

                    for markdown in extracted_root.rglob("*.md"):
                        content = markdown.read_text(encoding="utf-8")
                        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", content):
                            if target.startswith(("http://", "https://", "#", "mailto:")):
                                continue
                            local_target = target.split("#", 1)[0]
                            if local_target:
                                self.assertTrue(
                                    (markdown.parent / local_target).resolve().is_file(),
                                    f"{bundle.name}: broken relative link {target!r} in {markdown}",
                                )


if __name__ == "__main__":
    unittest.main()
