import subprocess
import sys
import unittest

from scripts.skill_validation.models import Skill, SourceFile
from scripts.skill_validation.structure import parse_frontmatter, strict_yaml, validate_structure


class SkillStructureTests(unittest.TestCase):
    def skill(self, metadata=None, body="# Instruções\n\nExplique e pratique.\n", extra=None):
        files = [
            SourceFile(
                "demo/SKILL.md",
                ("---\n" + (metadata or "name: demo\ndescription: Uma habilidade de exemplo.\n") + "---\n" + body).encode(),
                "100644",
            ),
            SourceFile(
                "demo/skill-review.yaml",
                b"""schema_version: 1
purpose: Produzir um quiz sobre um tema e nivel.
differentiation: Cria e revisa perguntas; nao pesquisa palestras.
access:
  files_read: []
  files_written: []
  network_hosts: []
  tools: []
  dependencies: []
cases:
  - id: happy-path
    prompt: Crie tres perguntas sobre tabelas hash.
    expected: [Tres perguntas adequadas.]
    forbidden: [Pedir credenciais.]
  - id: boundary
    prompt: Crie um quiz sem tema.
    expected: [Perguntar pelo tema ausente.]
    forbidden: [Inventar o tema.]
""",
                "100644",
            ),
        ]
        if extra:
            files.extend(SourceFile(f"demo/{path}", data, "100644") for path, data in extra.items())
        return Skill("demo", tuple(files))

    def errors(self, skill):
        return [finding for finding in validate_structure(skill) if finding.severity == "error"]

    def test_valid_bilingual_skill_and_manifest_pass(self):
        skill = self.skill(body="# Instruções\n\nAsk the learner to predict first.\n")
        self.assertEqual(self.errors(skill), [])

    def test_metadata_name_and_description_validation(self):
        for metadata in (
            "description: Missing name\n",
            "name: Invalid_Name\ndescription: valid description\n",
            "name: demo\ndescription: '   '\n",
            "name: demo\ndescription: " + "x" * 1025 + "\n",
        ):
            with self.subTest(metadata=metadata[:60]):
                self.assertTrue(self.errors(self.skill(metadata=metadata)))

    def test_description_1024_characters_is_valid(self):
        self.assertEqual(self.errors(self.skill(metadata="name: demo\ndescription: '" + "x" * 1024 + "'\n")), [])

    def test_host_invocation_metadata_preserves_types(self):
        base = "name: demo\ndescription: Estudo guiado.\n"
        for flag in ("true", "false"):
            with self.subTest(flag=flag):
                self.assertEqual(self.errors(self.skill(metadata=base + "argument-hint: O que estudar?\ndisable-model-invocation: " + flag + "\n")), [])
        for field in ("disable-model-invocation: 'false'", "disable-model-invocation: 0", "argument-hint: []", "argument-hint: ''", "unknown-field: true"):
            with self.subTest(field=field):
                self.assertTrue(any(error.rule_id == "STR005" for error in self.errors(self.skill(metadata=base + field + "\n"))))

    def test_duplicate_keys_aliases_and_malformed_yaml_are_rejected(self):
        for raw in (
            b"name: demo\ndescription: one\ndescription: two\n",
            b"name: demo\ndescription: &d shared\nother: *d\n",
            b"name: [broken\n",
        ):
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    strict_yaml(raw)

    def test_frontmatter_limits_and_utf8_are_rejected(self):
        with self.assertRaises(ValueError):
            parse_frontmatter(b"---\nname: demo\ndescription: " + b"x" * 8200 + b"\n---\nbody")
        with self.assertRaises(ValueError):
            parse_frontmatter(b"---\nname: demo\ndescription: ok\n---\n\xff")
        with self.assertRaises(ValueError):
            parse_frontmatter(b"---\nname: demo\ndescription: ok\n---\n")

    def test_empty_body_is_rejected(self):
        self.assertTrue(self.errors(self.skill(body=" \n\t\n")))

    def test_local_links_and_images_must_exist_and_stay_inside_skill(self):
        body = """# Links
[missing](./absent.md)
[escape](../../outside.md)
![image](assets/missing.png)
[fragment](#overview)
[reference][guide]

[guide]: docs/guide.md "title"
"""
        found = self.errors(self.skill(body=body))
        self.assertGreaterEqual(len(found), 3)
        good = self.skill(body="[guide](docs/guide.md#intro) ![image](assets/pic.png)\n", extra={
            "docs/guide.md": b"# Guide\n", "assets/pic.png": b"\x89PNG\r\n\x1a\n" + b"0" * 16,
        })
        self.assertEqual(self.errors(good), [])

    def test_review_manifest_shape_and_required_case_ids(self):
        skill = self.skill()
        bad = Skill(skill.name, tuple(
            SourceFile(file.path, b"schema_version: 1\npurpose: P\ndifferentiation: D\naccess: {}\ncases: []\n", file.mode)
            if file.path.endswith("skill-review.yaml") else file
            for file in skill.files
        ))
        self.assertTrue(self.errors(bad))

    def test_manifest_rejects_aliases_and_duplicate_keys(self):
        for manifest in (
            b"schema_version: 1\nschema_version: 1\npurpose: P\ndifferentiation: D\naccess: {}\ncases: []\n",
            b"schema_version: 1\npurpose: &p P\ndifferentiation: *p\naccess: {}\ncases: []\n",
        ):
            with self.subTest(manifest=manifest):
                base = self.skill()
                changed = Skill(base.name, tuple(
                    SourceFile(file.path, manifest, file.mode)
                    if file.path.endswith("skill-review.yaml") else file
                    for file in base.files
                ))
                self.assertTrue(self.errors(changed))

    def test_fragment_links_resolve_in_virtual_file_map_and_bad_schemes_fail(self):
        good = self.skill(body="[guide](docs/guide.md#intro)\n[shortcut]\n\n[shortcut]: docs/guide.md#intro\n", extra={"docs/guide.md": b"# Intro\n"})
        self.assertEqual(self.errors(good), [])
        bad = self.skill(body="[local file](file:///tmp/guide.md)\n")
        self.assertTrue(self.errors(bad))

    def test_nonregular_entries_and_markdown_code_destinations(self):
        base = self.skill()
        symlink = Skill(base.name, tuple(
            SourceFile(file.path, file.data, "120000") if file.path.endswith("SKILL.md") else file
            for file in base.files
        ))
        self.assertTrue(self.errors(symlink))
        body = "# Header\n```md\n[ignored](in-code.md)\n```\n`[ignored](inline.md)`\n[missing](outside.md)\n"
        found = self.errors(self.skill(body=body))
        missing = [finding for finding in found if finding.rule_id == "STR014"]
        self.assertEqual(len(missing), 1)
        self.assertEqual(missing[0].line, 10)

    def test_env_example_is_supported_text(self):
        self.assertEqual(self.errors(self.skill(extra={'.env.example': b'API_URL=https://example.invalid\n'})), [])

    def test_malformed_link_work_is_bounded(self):
        code = (
            "from scripts.skill_validation.structure import _destinations\n"
            "try:\n list(_destinations('[x](' * 20000))\n"
            "except ValueError:\n pass\n"
        )
        subprocess.run([sys.executable, '-c', code], timeout=5, check=True, capture_output=True)

    def test_unclosed_link_fails_with_safe_finding(self):
        found = self.errors(self.skill(body='[bad](never-closed'))
        self.assertTrue(any(item.rule_id == 'STR015' for item in found))


if __name__ == "__main__":
    unittest.main()
