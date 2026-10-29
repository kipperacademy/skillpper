from pathlib import Path
import tempfile
import unittest

from scripts.skill_validation.catalog import discover
from scripts.skill_validation.models import SourceFile
from scripts.update_skill_votes import read_skill_metadata, render_ranking


class LearningCategoryTests(unittest.TestCase):
    def test_catalog_groups_complete_skills_and_rejects_deeper_manifests(self):
        paths = (
            "Aprendizagem/aprender/SKILL.md",
            "Aprendizagem/aprender/shared/PROFILE.md",
            "Aprendizagem/construir/SKILL.md",
            "Aprendizagem/construir/nested/SKILL.md",
        )
        skills, findings = discover(tuple(SourceFile(p, b"", "100644") for p in paths))
        self.assertEqual([s.name for s in skills], ["Aprendizagem/aprender", "Aprendizagem/construir"])
        self.assertEqual([f.path for f in skills[0].files], list(paths[:2]))
        self.assertEqual([(f.rule_id, f.path) for f in findings], [("INV005", paths[-1])])

    def test_votes_keep_identity_and_link_to_category(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / "Aprendizagem/aprender"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("---\nname: aprender\ndescription: Estudo\n---\n")
            metadata = read_skill_metadata(root)
            self.assertEqual(metadata, {"aprender": "Estudo"})
            ranking = render_ranking(metadata, {}, "Skill Votes", root=root)
            self.assertIn("[aprender](./Aprendizagem/aprender/SKILL.md)", ranking)
