from pathlib import Path
import json
import re
import tempfile
import unittest

from scripts.update_skill_votes import (
    VOTES_END,
    VOTES_START,
    canonical_discussions,
    dashboard_data,
    parse_skill_marker,
    read_skill_metadata,
    render_embedded_votes,
    render_ranking,
    thumbs_up_count,
    vote_body,
)

ROOT = Path(__file__).resolve().parents[1]


class SkillVotesTests(unittest.TestCase):
    def test_vote_body_contains_parseable_marker(self):
        body = vote_body("design-craft")
        self.assertEqual(parse_skill_marker(body), "design-craft")

    def test_render_ranking_sorts_by_votes_then_name(self):
        skills = {
            "study-quiz": "Quiz helper",
            "design-craft": "Design helper",
            "prepare-technical-slides": "Research helper",
        }
        discussions = {
            "study-quiz": {
                "url": "https://github.com/example/repo/discussions/2",
                "reactionGroups": [{"content": "THUMBS_UP", "users": {"totalCount": 7}}],
            },
            "design-craft": {
                "url": "https://github.com/example/repo/discussions/1",
                "reactionGroups": [{"content": "THUMBS_UP", "users": {"totalCount": 7}}],
            },
        }

        ranking = render_ranking(skills, discussions, "Skill Votes")

        self.assertLess(ranking.index("[design-craft]"), ranking.index("[study-quiz]"))
        self.assertLess(ranking.index("[study-quiz]"), ranking.index("[prepare-technical-slides]"))
        self.assertIn("| 1 | [design-craft](./design-craft/SKILL.md) | 7 | [Vote](", ranking)
        self.assertIn("| 3 | [prepare-technical-slides](./prepare-technical-slides/SKILL.md) | 0 | Not created yet |", ranking)

    def test_thumbs_up_count_ignores_other_reactions(self):
        discussion = {
            "reactionGroups": [
                {"content": "HEART", "users": {"totalCount": 10}},
                {"content": "THUMBS_UP", "users": {"totalCount": 3}},
            ]
        }
        self.assertEqual(thumbs_up_count(discussion), 3)
        self.assertEqual(thumbs_up_count(None), 0)

    def test_dashboard_data_includes_repository_totals_and_ranks(self):
        data = dashboard_data(
            {"alpha": "First skill", "beta": "Second skill"},
            {
                "beta": {
                    "url": "https://github.com/example/repo/discussions/2",
                    "reactionGroups": [{"content": "THUMBS_UP", "users": {"totalCount": 2}}],
                }
            },
            "Skill Votes",
            "example/repo",
        )

        self.assertEqual(data["repository"], "example/repo")
        self.assertEqual(data["total_skills"], 2)
        self.assertEqual(data["total_votes"], 2)
        self.assertEqual(data["skills"][0]["skill"], "beta")
        self.assertEqual(data["skills"][0]["rank"], 1)

    def test_canonical_discussions_ignore_duplicate_markers(self):
        official = {
            "id": "D_official",
            "body": "<!-- skillpper-vote-skill: alpha -->",
            "url": "https://github.com/example/repo/discussions/1",
            "reactionGroups": [{"content": "THUMBS_UP", "users": {"totalCount": 4}}],
        }
        duplicate = {
            "id": "D_duplicate",
            "body": "<!-- skillpper-vote-skill: alpha -->",
            "url": "https://github.com/example/repo/discussions/2",
            "reactionGroups": [{"content": "THUMBS_UP", "users": {"totalCount": 99}}],
        }

        discussions = canonical_discussions(
            {"alpha": "First skill"},
            {"alpha": {"id": "D_official", "url": official["url"]}},
            {"D_official": official, "D_duplicate": duplicate},
        )

        self.assertEqual(thumbs_up_count(discussions["alpha"]), 4)

    def test_canonical_discussions_does_not_accept_preclaimed_marker(self):
        preclaim = {
            "id": "D_preclaim",
            "body": "<!-- skillpper-vote-skill: alpha -->",
            "url": "https://github.com/example/repo/discussions/2",
            "reactionGroups": [{"content": "THUMBS_UP", "users": {"totalCount": 99}}],
        }

        discussions = canonical_discussions(
            {"alpha": "First skill"},
            {},
            {"D_preclaim": preclaim},
        )

        self.assertEqual(discussions, {})

    def test_dashboard_page_embeds_vote_data(self):
        page = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
        self.assertEqual(page.count(VOTES_START), 1, "docs/index.html must contain exactly one VOTES:START marker")
        self.assertEqual(page.count(VOTES_END), 1, "docs/index.html must contain exactly one VOTES:END marker")
        match = re.search(r'<script type="application/json" id="votesData">(.*?)</script>', page, re.DOTALL)
        if match is None:
            self.fail("docs/index.html must embed vote data in #votesData")
        payload = json.loads(match.group(1))
        votes = json.loads((ROOT / "docs" / "votes.json").read_text(encoding="utf-8"))
        comparable_payload = dict(payload)
        comparable_votes = dict(votes)
        comparable_payload.pop("updated_at", None)
        comparable_votes.pop("updated_at", None)
        self.assertEqual(
            comparable_payload, comparable_votes,
            "Embedded vote data is outdated. Run: python scripts/update_skill_votes.py",
        )

    def test_embedded_votes_escape_closing_script_tags(self):
        data = {
            "updated_at": "2026-10-07T00:00:00Z",
            "repository": "example/repo",
            "category": "Skill Votes",
            "total_skills": 1,
            "total_votes": 0,
            "skills": [
                {
                    "skill": "evil",
                    "description": "Tricky </script><script>alert(1)</script> description",
                    "votes": 0,
                    "discussion_url": "",
                    "rank": 1,
                }
            ],
        }
        block = render_embedded_votes(data)
        self.assertNotIn("</script><script>", block)
        self.assertNotIn("</script>", block.split('id="votesData">', 1)[1].rsplit("</script>", 1)[0])
        match = re.search(r'<script type="application/json" id="votesData">(.*?)</script>', block, re.DOTALL)
        if match is None:
            self.fail("rendered block must contain parseable #votesData payload")
        self.assertEqual(json.loads(match.group(1)), data)

    def test_read_skill_metadata_discovers_root_skills(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            skill = root / "alpha"
            skill.mkdir()
            (skill / "SKILL.md").write_text("---\nname: alpha\ndescription: Test\n---\n", encoding="utf-8")
            nested = root / "nested" / "ignored"
            nested.mkdir(parents=True)
            (nested / "SKILL.md").write_text("---\nname: ignored\ndescription: Nope\n---\n", encoding="utf-8")

            self.assertEqual(read_skill_metadata(root), {"alpha": "Test"})


if __name__ == "__main__":
    unittest.main()
