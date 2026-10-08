from pathlib import Path
import contextlib
import io
import os
import sys
import tempfile
import unittest
from unittest import mock

from scripts import update_skill_votes
from scripts.update_skill_votes import (
    MissingVoteCategoryError,
    canonical_discussions,
    dashboard_data,
    parse_skill_marker,
    read_skill_metadata,
    render_ranking,
    resolve_category_id,
    thumbs_up_count,
    vote_body,
)


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

    def test_resolve_category_id_matches_case_insensitively(self):
        categories = [
            {"id": "C_general", "name": "General"},
            {"id": "C_votes", "name": "Skill Votes"},
        ]
        self.assertEqual(resolve_category_id(categories, "skill votes"), "C_votes")

    def test_resolve_category_id_raises_when_category_is_missing(self):
        categories = [{"id": "C_general", "name": "General"}]
        with self.assertRaises(MissingVoteCategoryError):
            resolve_category_id(categories, "Skill Votes")

    def _run_main(self, argv, environ):
        missing = MissingVoteCategoryError("Skill Votes")
        with mock.patch.object(update_skill_votes, "repository_context", side_effect=missing), \
             mock.patch.dict(os.environ, environ, clear=True), \
             mock.patch.object(sys, "argv", ["update_skill_votes.py", *argv]), \
             contextlib.redirect_stderr(io.StringIO()):
            return update_skill_votes.main()

    def test_main_skips_failure_for_scheduled_runs_when_category_is_missing(self):
        environ = {"GH_TOKEN": "token", "GITHUB_REPOSITORY": "owner/name", "GITHUB_EVENT_NAME": "schedule"}
        self.assertEqual(self._run_main([], environ), 0)

    def test_main_fails_for_manual_runs_when_category_is_missing(self):
        environ = {"GH_TOKEN": "token", "GITHUB_REPOSITORY": "owner/name"}
        self.assertEqual(self._run_main([], environ), 1)

    def test_main_allows_missing_category_with_explicit_flag(self):
        environ = {"GH_TOKEN": "token", "GITHUB_REPOSITORY": "owner/name"}
        self.assertEqual(self._run_main(["--allow-missing-category"], environ), 0)

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
