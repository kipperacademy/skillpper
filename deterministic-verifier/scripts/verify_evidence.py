#!/usr/bin/env python3
"""Validate an Empirical Verification Sign-Off block in Markdown documentation."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SIGN_OFF_HEADING = re.compile(r"^#+\s+.*Empirical Verification Sign-Off", re.IGNORECASE | re.MULTILINE)
RED_SECTION = re.compile(r"^#+\s+.*(?:Baseline|Reproduction|Red Phase)", re.IGNORECASE | re.MULTILINE)
GREEN_SECTION = re.compile(r"^#+\s+.*(?:Terminal Execution Log|Green Phase)", re.IGNORECASE | re.MULTILINE)
REGRESSION_SECTION = re.compile(r"^#+\s+.*(?:Regression Status|Full Regression)", re.IGNORECASE | re.MULTILINE)
EXIT_CODE_ZERO = re.compile(r"(?:\*\*Exit Code\*\*|Exit Code|exit status|código de saída)\s*[:=]?\s*[`*]?0[`*]?", re.IGNORECASE)
COMMAND_BLOCK = re.compile(r"(?:\*\*Command\*\*|\*\*Comando\*\*|Command|Comando)\s*[:=]?\s*[`*]?([^\n`*]+)[`*]?", re.IGNORECASE)


def validate(content: str) -> list[str]:
    errors: list[str] = []

    if not SIGN_OFF_HEADING.search(content):
        errors.append("Missing required 'Empirical Verification Sign-Off' heading.")
        return errors

    if not GREEN_SECTION.search(content):
        errors.append("Missing 'Terminal Execution Log (Green Phase)' section.")

    if not EXIT_CODE_ZERO.search(content):
        errors.append("Missing confirmation of passing exit code 0 in terminal execution log.")

    if not COMMAND_BLOCK.search(content):
        errors.append("Missing exact terminal execution command in log.")

    if not REGRESSION_SECTION.search(content):
        errors.append("Missing 'Full Regression Status' section.")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that a Markdown report contains deterministic terminal evidence."
    )
    parser.add_argument("report", type=Path, help="Path to Markdown report file")
    args = parser.parse_args()

    if not args.report.is_file():
        print(f"File not found: {args.report}", file=sys.stderr)
        return 2

    text = args.report.read_text(encoding="utf-8")
    errors = validate(text)

    if errors:
        print(f"Empirical verification validation failed for {args.report}:", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1

    print(f"Empirical verification sign-off validated successfully: {args.report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
