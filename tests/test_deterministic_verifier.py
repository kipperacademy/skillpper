from __future__ import annotations

import importlib.util
from pathlib import Path
import shutil
import sys
import unittest

sys.dont_write_bytecode = True

from scripts.skill_validation.policy import load_policy
from scripts.skill_validation.security import scan_security
from scripts.skill_validation.structure import validate_structure
from tests.test_skill_validation_catalog import ROOT, skill_from_source

SCRIPT_PATH = ROOT / "deterministic-verifier" / "scripts" / "verify_evidence.py"
_spec = importlib.util.spec_from_file_location("verify_evidence", SCRIPT_PATH)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
validate_evidence = _module.validate


class DeterministicVerifierSkillTests(unittest.TestCase):
    def setUp(self):
        self._cleanup_pycache()
        self.skill = skill_from_source("deterministic-verifier")
        self.policy = load_policy(ROOT / "security" / "skill-validation-policy.yaml")

    def tearDown(self):
        self._cleanup_pycache()

    def _cleanup_pycache(self):
        pycache = ROOT / "deterministic-verifier" / "scripts" / "__pycache__"
        if pycache.exists():
            shutil.rmtree(pycache)

    def test_skill_conforms_to_structure_and_manifest_specifications(self):
        findings = validate_structure(self.skill)
        self.assertEqual(
            [(item.rule_id, item.path, item.message) for item in findings],
            [],
            "deterministic-verifier must have zero structural or manifest findings",
        )

    def test_skill_passes_security_scanners_without_findings(self):
        findings = scan_security(self.skill.files, self.policy)
        self.assertEqual(
            [(item.rule_id, item.path, item.message) for item in findings],
            [],
            "deterministic-verifier must trigger zero security findings",
        )

    def test_verify_evidence_validator_accepts_valid_signoff(self):
        valid_report = """
# Task Summary

### 🔬 Empirical Verification Sign-Off

#### 1. Baseline & Reproduction (Red Phase)
- **Reproduction Test**: `tests/unit/gateway.spec.ts:12`
- **Initial Exit Code**: `1` (Failing as expected)

#### 2. Terminal Execution Log (Green Phase)
- **Command**: `npm test -- tests/unit/gateway.spec.ts`
- **Exit Code**: `0` (Passing: 12 tests passed)

#### 3. Boundary Values Verified
- [x] Zero amount rejected

#### 4. Full Regression Status
- **Typecheck**: `tsc --noEmit` -> OK (Exit Code: 0)
- **Full Suite**: 86 passing tests
"""
        errors = validate_evidence(valid_report)
        self.assertEqual(errors, [])

    def test_verify_evidence_validator_rejects_missing_terminal_evidence(self):
        invalid_report = """
# Task Summary

### 🔬 Empirical Verification Sign-Off

I implemented the change and tested it thoroughly in my head. Everything works!
"""
        errors = validate_evidence(invalid_report)
        self.assertIn("Missing 'Terminal Execution Log (Green Phase)' section.", errors)
        self.assertIn("Missing confirmation of passing exit code 0 in terminal execution log.", errors)


if __name__ == "__main__":
    unittest.main()
