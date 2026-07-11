#!/usr/bin/env python3
"""Run the learner-authored suite and require meaningful sequential state coverage."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parents[1]
STARTER = LAB_DIR / "starter"
TEST_FILE = STARTER / "tests" / "release_flow.tftest.hcl"
MARKER = "EXPECTED_SEQUENTIAL_TEST_FLOW_INCOMPLETE"


def main() -> int:
    terraform = shutil.which("terraform")
    if terraform is None:
        print("Terraform executable was not found.")
        return 2
    initialized = subprocess.run(
        [terraform, "init", "-backend=false", "-input=false", "-no-color"],
        cwd=STARTER, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False
    )
    print(initialized.stdout.rstrip())
    if initialized.returncode:
        return initialized.returncode
    tested = subprocess.run(
        [terraform, "test", "-no-color"], cwd=STARTER, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False
    )
    print(tested.stdout.rstrip())
    if tested.returncode:
        print(f"{MARKER}: the authored sequential Terraform Test suite does not pass.")
        return tested.returncode

    source = TEST_FILE.read_text(encoding="utf-8")
    run_count = len(re.findall(r'\brun\s+"', source))
    apply_count = len(re.findall(r"\bcommand\s*=\s*apply\b", source))
    plan_count = len(re.findall(r"\bcommand\s*=\s*plan\b", source))
    assertion_count = len(re.findall(r"\bassert\s*\{", source))
    has_expected_failure = re.search(r"\bexpect_failures\s*=", source) is not None
    has_cross_run_id = re.search(r"\brun\.[A-Za-z0-9_-]+\.deployment_id\b", source) is not None
    has_v1 = '"v1"' in source
    has_v2 = '"v2"' in source
    complete = (
        run_count >= 4
        and apply_count >= 2
        and plan_count >= 1
        and assertion_count >= 5
        and has_expected_failure
        and has_cross_run_id
        and has_v1
        and has_v2
    )
    if not complete:
        print(
            f"{MARKER}: runs={run_count}, applies={apply_count}, plans={plan_count}, "
            f"assertions={assertion_count}, expected_failure={has_expected_failure}, "
            f"cross_run_id={has_cross_run_id}, v1={has_v1}, v2={has_v2}."
        )
        return 1
    if "4 passed, 0 failed" not in tested.stdout:
        print(f"{MARKER}: the suite must contain exactly four passing run scenarios.")
        return 1
    print("Sequential Terraform Test verification passed: setup, replacement, steady state, and failure coverage are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
