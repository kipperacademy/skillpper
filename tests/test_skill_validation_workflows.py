from pathlib import Path
import os
import json
import re
import subprocess
import tempfile
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = ROOT / ".github" / "workflows"
EXPECTED_ACTION = re.compile(r"^actions/(?:checkout|setup-python|upload-artifact)@v7$")
ALLOWED_EVENTS = {"push", "pull_request", "workflow_dispatch"}
PULL_REQUEST_TYPES = {"opened", "synchronize", "reopened", "ready_for_review", "edited"}


def load_workflow(name):
    # BaseLoader keeps the YAML 1.2-style `on` key a string (PyYAML's default
    # SafeLoader treats it as boolean True under YAML 1.1 rules).
    return yaml.load((WORKFLOW_DIR / name).read_text(encoding="utf-8"), Loader=yaml.BaseLoader)


def walk(value):
    if isinstance(value, dict):
        yield value
        for nested in value.values():
            yield from walk(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from walk(nested)


class WorkflowContractTests(unittest.TestCase):
    def test_validation_runs_for_every_pull_request_and_only_on_unprivileged_events(self):
        workflow = load_workflow("validate-skills.yml")
        self.assertIn("on", workflow)
        self.assertEqual(set(workflow["on"]), {"pull_request"})
        self.assertEqual(set(workflow["on"]["pull_request"]["types"]), PULL_REQUEST_TYPES)
        self.assertNotIn("paths", workflow["on"]["pull_request"])
        self.assertNotIn("paths-ignore", workflow["on"]["pull_request"])
        self.assertTrue(set(workflow["on"]).issubset(ALLOWED_EVENTS))
        self.assertEqual(workflow["permissions"], {"contents": "read"})
        for item in walk(workflow):
            if "permissions" in item:
                self.assertEqual(item["permissions"], {"contents": "read"})
        raw = (WORKFLOW_DIR / "validate-skills.yml").read_text(encoding="utf-8")
        self.assertNotRegex(raw, r"(?i)pull_request_target|workflow_run|secrets\s*:\s*inherit|\bsecrets\.")

    def test_scan_job_is_required_fail_closed_and_runs_only_base_validator(self):
        workflow = load_workflow("validate-skills.yml")
        jobs = workflow["jobs"]
        scan = jobs["skill-validation"]
        self.assertEqual(scan["name"], "skill-validation")
        self.assertEqual(scan["runs-on"], "ubuntu-latest")
        self.assertEqual(scan["timeout-minutes"], "10")
        self.assertNotIn("if", scan)
        self.assertNotIn("continue-on-error", str(scan))
        steps = scan["steps"]
        checkout = next(step for step in steps if step.get("uses", "").startswith("actions/checkout@"))
        self.assertEqual(checkout["with"]["repository"], "kipperacademy/skillpper")
        self.assertEqual(checkout["with"]["path"], "trusted")
        self.assertEqual(checkout["with"]["ref"], "${{ github.event.pull_request.base.sha }}")
        self.assertEqual(checkout["with"]["persist-credentials"], "false")
        self.assertEqual(checkout["with"]["submodules"], "false")
        self.assertEqual(checkout["with"]["lfs"], "false")
        script = "\n".join(step.get("run", "") for step in steps)
        self.assertIn("refs/pull/$PR_NUMBER/merge", script)
        self.assertIn("https://github.com/kipperacademy/skillpper.git", script)
        self.assertIn('rev-parse FETCH_HEAD', script)
        self.assertIn('"$CANDIDATE_SHA"', script)
        self.assertIn("python -I trusted/scripts/validate_skills.py", script)
        self.assertIn("--base-sha \"$BASE_SHA\"", script)
        self.assertIn("--candidate-sha \"$CANDIDATE_SHA\"", script)
        self.assertIn("requirements-validation.txt", script)
        self.assertIn("--require-hashes", script)
        self.assertIn("--only-binary=:all:", script)
        self.assertNotRegex(script, r"\$\{\{\s*github\.event\.pull_request\.(?:title|head\.ref)")

    @unittest.skipIf(os.name == "nt", "bootstrap shell runs on the Ubuntu scanner")
    def test_missing_base_validator_fails_with_explicit_bootstrap_report(self):
        workflow = load_workflow("validate-skills.yml")
        step = next(step for step in workflow["jobs"]["skill-validation"]["steps"]
                    if step.get("name") == "Verify trusted validator is available")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            env = dict(os.environ, RUNNER_TEMP=directory)
            result = subprocess.run(["bash", "-e", "-c", step["run"]], cwd=root,
                                    env=env, capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 2)
            report = json.loads((root / "skill-report.json").read_text())
            self.assertFalse(report["complete"])
            self.assertEqual(report["reason"], "trusted_base_validator_missing")
            trusted = root / "trusted/scripts"
            trusted.mkdir(parents=True)
            for name in ("validate_skills.py", "requirements-validation.txt"):
                (trusted / name).write_text("")
            result = subprocess.run(["bash", "-e", "-c", step["run"]], cwd=root,
                                    env=env, capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 0)

    def test_reports_are_summarized_and_only_explicit_files_are_uploaded(self):
        workflow = load_workflow("validate-skills.yml")
        steps = workflow["jobs"]["skill-validation"]["steps"]
        summary = next(step for step in steps if step.get("name") == "Add redacted report to step summary")
        artifact = next(step for step in steps if step.get("name") == "Upload validation reports")
        self.assertEqual(summary["if"], "always()")
        self.assertIn("GITHUB_STEP_SUMMARY", summary["run"])
        self.assertIn("-f", summary["run"])
        self.assertEqual(artifact["if"], "always()")
        self.assertEqual(artifact["with"]["retention-days"], "7")
        self.assertEqual(artifact["with"]["if-no-files-found"], "error")
        self.assertEqual(set(artifact["with"]["path"].splitlines()), {
            "${{ runner.temp }}/skill-report.json",
            "${{ runner.temp }}/skill-report.md",
        })

    def test_validator_tests_are_separate_unprivileged_candidate_execution(self):
        workflow = load_workflow("validate-skills.yml")
        job = workflow["jobs"]["validator-tests"]
        self.assertEqual(job["name"], "validator-tests")
        self.assertEqual(job["runs-on"], "ubuntu-latest")
        steps = job["steps"]
        checkout = next(step for step in steps if step.get("uses", "").startswith("actions/checkout@"))
        self.assertEqual(checkout["with"]["ref"], "${{ github.sha }}")
        self.assertEqual(checkout["with"]["persist-credentials"], "false")
        runs = "\n".join(step.get("run", "") for step in steps)
        self.assertIn("pip install --disable-pip-version-check -r scripts/requirements.txt", runs)
        self.assertIn("python -m unittest discover -s tests -v", runs)

    def test_all_workflow_actions_use_stable_major_versions(self):
        for name in ("validate-skills.yml", "cross-platform-tests.yml", "update-skills-index.yml"):
            workflow = load_workflow(name)
            raw = (WORKFLOW_DIR / name).read_text(encoding="utf-8")
            uses = [item["uses"] for item in walk(workflow) if "uses" in item]
            self.assertTrue(uses, f"{name}: expected at least one versioned action")
            for reference in uses:
                with self.subTest(workflow=name, action=reference):
                    self.assertRegex(reference, EXPECTED_ACTION)
            for item in walk(workflow):
                if item.get("uses", "").startswith("actions/checkout@"):
                    self.assertEqual(item["with"]["persist-credentials"], "false")
                    self.assertEqual(item["with"]["submodules"], "false")
                    self.assertEqual(item["with"]["lfs"], "false")
                if item.get("uses", "").startswith("actions/setup-python@"):
                    self.assertNotIn("cache", item.get("with", {}))
                self.assertNotIn("actions/cache@", item.get("uses", ""))

    def test_every_workflow_pins_stable_action_versions(self):
        for path in sorted(WORKFLOW_DIR.glob("*.yml")):
            workflow = load_workflow(path.name)
            uses = [item["uses"] for item in walk(workflow) if "uses" in item]
            self.assertTrue(uses, f"{path.name}: expected at least one versioned action")
            for reference in uses:
                with self.subTest(workflow=path.name, action=reference):
                    self.assertRegex(reference, EXPECTED_ACTION)

    def test_cross_platform_tests_run_on_every_pull_request_without_path_filters(self):
        workflow = load_workflow("cross-platform-tests.yml")
        self.assertIn("pull_request", workflow["on"])
        self.assertNotIn("paths", workflow["on"]["pull_request"])
        self.assertNotIn("paths-ignore", workflow["on"]["pull_request"])
        matrix = workflow["jobs"]["test"]["strategy"]["matrix"]["os"]
        self.assertEqual(set(matrix), {"ubuntu-latest", "macos-latest", "windows-latest"})

    def test_index_workflow_is_read_only_and_checks_freshness(self):
        workflow = load_workflow("update-skills-index.yml")
        self.assertEqual(workflow["permissions"], {"contents": "read"})
        raw = (WORKFLOW_DIR / "update-skills-index.yml").read_text(encoding="utf-8")
        self.assertNotRegex(raw, r"(?im)^\s*contents:\s*write\s*$")
        self.assertNotRegex(raw, r"(?im)\bgit\s+push\b")
        self.assertIn("python scripts/update_skills_index.py --check", raw)
        self.assertIn("python -m unittest discover -s tests -v", raw)

    def test_docs_only_and_bundle_only_changes_cannot_be_skipped(self):
        workflow = load_workflow("validate-skills.yml")
        self.assertNotIn("paths", workflow["on"]["pull_request"])
        self.assertNotIn("paths-ignore", workflow["on"]["pull_request"])
        self.assertNotIn("if", workflow["jobs"]["skill-validation"])
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            (repo / "docs").mkdir()
            (repo / "docs" / "change.md").write_text("docs only", encoding="utf-8")
            (repo / "demo.skill").write_bytes(b"bundle only")
            changed = subprocess.run(
                ["git", "-C", str(repo), "status", "--short"],
                check=True, capture_output=True, text=True,
            ).stdout
            self.assertIn("docs/", changed)
            self.assertIn("demo.skill", changed)

    def test_merge_ref_change_has_an_explicit_sha_equality_gate(self):
        workflow = load_workflow("validate-skills.yml")
        fetch = next(step for step in workflow["jobs"]["skill-validation"]["steps"]
                     if step.get("name") == "Fetch and verify pull request merge ref")
        self.assertRegex(fetch["run"], r"case \"\$PR_NUMBER\" in[\s\S]*\*\[!0-9\]\*[\s\S]*exit 2")
        self.assertRegex(fetch["run"], r"test \"\$\(git -C trusted rev-parse FETCH_HEAD\)\" = \"\$CANDIDATE_SHA\"")

    @unittest.skipIf(os.name == "nt", "bash-based merge-ref fixture is covered by the Ubuntu validator job")
    def test_merge_ref_moved_after_event_fails_the_workflow_fetch_script(self):
        workflow = load_workflow("validate-skills.yml")
        fetch = next(step for step in workflow["jobs"]["skill-validation"]["steps"]
                     if step.get("name") == "Fetch and verify pull request merge ref")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            remote = root / "candidate.git"
            source = root / "source"
            trusted = root / "trusted"
            subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
            subprocess.run(["git", "init", "-q", str(source)], check=True)
            subprocess.run(["git", "-C", str(source), "config", "user.name", "Workflow test"], check=True)
            subprocess.run(["git", "-C", str(source), "config", "user.email", "workflow@example.invalid"], check=True)
            (source / "README.md").write_text("candidate one", encoding="utf-8")
            subprocess.run(["git", "-C", str(source), "add", "README.md"], check=True)
            subprocess.run(["git", "-C", str(source), "-c", "commit.gpgsign=false", "commit", "-qm", "one"], check=True)
            first_sha = subprocess.run(["git", "-C", str(source), "rev-parse", "HEAD"], check=True,
                                       capture_output=True, text=True).stdout.strip()
            subprocess.run(["git", "-C", str(source), "push", str(remote), "HEAD:refs/pull/17/merge"],
                           check=True, capture_output=True)
            subprocess.run(["git", "init", "-q", str(trusted)], check=True)

            script = fetch["run"].replace("https://github.com/kipperacademy/skillpper.git", str(remote))
            env = os.environ.copy()
            env.update({"PR_NUMBER": "17", "CANDIDATE_SHA": first_sha})
            first = subprocess.run(["bash", "-e", "-c", script], cwd=root, env=env,
                                   capture_output=True, text=True, timeout=10)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)

            (source / "README.md").write_text("candidate two", encoding="utf-8")
            subprocess.run(["git", "-C", str(source), "add", "README.md"], check=True)
            subprocess.run(["git", "-C", str(source), "-c", "commit.gpgsign=false", "commit", "-qm", "two"], check=True)
            second_sha = subprocess.run(["git", "-C", str(source), "rev-parse", "HEAD"], check=True,
                                        capture_output=True, text=True).stdout.strip()
            subprocess.run(["git", "-C", str(source), "push", "--force", str(remote), "HEAD:refs/pull/17/merge"],
                           check=True, capture_output=True)
            self.assertNotEqual(first_sha, second_sha)
            moved = subprocess.run(["bash", "-e", "-c", script], cwd=root, env=env,
                                   capture_output=True, text=True, timeout=10)
            self.assertNotEqual(moved.returncode, 0)


if __name__ == "__main__":
    unittest.main()
