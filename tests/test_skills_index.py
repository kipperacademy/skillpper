from pathlib import Path
import tempfile
import unittest

from scripts.update_skills_index import END, ROOT, START, render_index, updated_readme


class SkillsIndexTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.readme = self.root / "README.md"
        self.readme.write_text(f"Intro\n{START}\nstale\n{END}\nOutro\n", encoding="utf-8")

    def skill(self, name, metadata):
        folder = self.root / name
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / "SKILL.md"
        path.write_text(f"---\n{metadata}\n---\n# Instructions\n", encoding="utf-8")
        return path

    def test_sorted_multiline_unicode_and_literal_markdown(self):
        self.skill("zeta", "name: zeta\ndescription: >-\n  Pesquisa técnica\n  com fontes.")
        self.skill("alpha", 'name: alpha\ndescription: "A | B <tag> [link](url) `code`"')
        result = updated_readme(self.root)
        self.assertLess(result.index("[alpha]"), result.index("[zeta]"))
        self.assertIn("Pesquisa técnica com fontes.", result)
        self.assertIn(r"A \| B &lt;tag&gt; \[link\](url) \`code\`", result)
        self.assertTrue(result.startswith(f"Intro\n{START}\n"))
        self.assertTrue(result.endswith(f"{END}\nOutro\n"))
        self.readme.write_text(result, encoding="utf-8")
        self.assertEqual(updated_readme(self.root), result)

    def test_discovery_add_remove_and_metadata_change(self):
        self.skill("nested/ignored", "name: ignored\ndescription: Nested")
        self.skill(".hidden", "name: hidden\ndescription: Hidden")
        path = self.skill("example", "name: example\ndescription: Before")
        self.assertIn("Before", render_index(self.root))
        self.skill("example", "name: example\ndescription: After")
        self.assertIn("After", render_index(self.root))
        path.unlink()
        self.assertIn("No skills available yet", render_index(self.root))

    def test_learning_category_keeps_skill_names_and_nested_links(self):
        self.skill("Aprendizagem/aprender", "name: aprender\ndescription: Estudo guiado")
        self.assertIn("[aprender](./Aprendizagem/aprender/SKILL.md)", render_index(self.root))

    def test_invalid_metadata_fails_without_changing_readme(self):
        original = self.readme.read_text(encoding="utf-8")
        for metadata in (
            "name: example", "name: example\ndescription: ''",
            "name: example\ndescription: 123", "name: other\ndescription: Valid",
            "name: example\ndescription: [broken", "- list",
        ):
            with self.subTest(metadata=metadata):
                self.skill("example", metadata)
                with self.assertRaises(ValueError):
                    updated_readme(self.root)
                self.assertEqual(self.readme.read_text(encoding="utf-8"), original)

    def test_missing_frontmatter_delimiters(self):
        path = self.skill("example", "name: example\ndescription: Example")
        for content in ("# No frontmatter", "---\nname: example\n"):
            path.write_text(content, encoding="utf-8")
            with self.assertRaises(ValueError):
                render_index(self.root)

    def test_missing_duplicate_or_reversed_markers(self):
        for content in ("No markers", START + END + END, END + START):
            self.readme.write_text(content, encoding="utf-8")
            with self.assertRaises(ValueError):
                updated_readme(self.root)


class RepositoryIndexTests(unittest.TestCase):
    """Guard the checked-in README, not just the generator in a temp dir."""

    maxDiff = None

    def test_readme_index_is_in_sync(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertEqual(
            updated_readme(ROOT), readme,
            "README skills index is outdated. Run: python scripts/update_skills_index.py",
        )


if __name__ == "__main__":
    unittest.main()
