import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts.update_contributors import (
    MAX_CONTRIBUTORS,
    contributor_snapshot,
    fetch_contributors,
    main,
)


def contributor(login, account_type="User"):
    return {
        "login": login,
        "type": account_type,
        "avatar_url": f"https://avatars.githubusercontent.com/u/{login}",
        "html_url": f"https://github.com/{login}",
    }


class ContributorsTests(unittest.TestCase):
    def test_keeps_human_contributors_in_api_order_and_limits_display(self):
        source = [
            contributor("github-actions[bot]", "Bot"),
            contributor("copy[bot]"),
            contributor("missing-avatar") | {"avatar_url": None},
            contributor("external-link") | {"html_url": "https://example.com/profile"},
        ]
        source += [contributor(f"person-{index}") for index in range(MAX_CONTRIBUTORS + 2)]

        result = contributor_snapshot("owner/repo", source)

        self.assertEqual(result["repository"], "owner/repo")
        self.assertEqual(len(result["contributors"]), MAX_CONTRIBUTORS)
        self.assertEqual(result["contributors"][0]["login"], "person-0")
        self.assertEqual(result["contributors"][-1]["login"], "person-11")
        self.assertEqual(
            set(result["contributors"][0]), {"login", "avatar_url", "html_url"}
        )

    @patch("scripts.update_contributors.urlopen")
    def test_fetch_uses_repository_and_token_without_exposing_it_in_url(self, urlopen):
        response = io.BytesIO(
            json.dumps([contributor("person")]).encode("utf-8")
        )
        response.status = 200
        urlopen.return_value.__enter__.return_value = response

        result = fetch_contributors("owner/repo", "secret-token")

        self.assertEqual(result[0]["login"], "person")
        request = urlopen.call_args.args[0]
        self.assertEqual(
            request.full_url,
            "https://api.github.com/repos/owner/repo/contributors?per_page=100",
        )
        self.assertEqual(request.get_header("Authorization"), "Bearer secret-token")
        self.assertNotIn("secret-token", request.full_url)

    @patch("scripts.update_contributors.urlopen")
    def test_empty_repository_returns_no_contributors(self, urlopen):
        response = io.BytesIO()
        response.status = 204
        urlopen.return_value.__enter__.return_value = response
        self.assertEqual(fetch_contributors("owner/repo", "secret-token"), [])

    @patch("scripts.update_contributors.urlopen")
    def test_main_writes_a_public_snapshot_without_credentials(self, urlopen):
        response = io.BytesIO(json.dumps([contributor("person")]).encode("utf-8"))
        response.status = 200
        urlopen.return_value.__enter__.return_value = response
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "contributors.json"
            with patch.dict(os.environ, {"GITHUB_REPOSITORY": "owner/repo", "GH_TOKEN": "secret-token"}), patch.object(
                sys, "argv", ["update_contributors.py", "--output", str(output)]
            ):
                main()
            snapshot = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(snapshot["contributors"][0]["login"], "person")
            self.assertNotIn("secret-token", output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
