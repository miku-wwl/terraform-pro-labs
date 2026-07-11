#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parents[1]
SOURCE = LAB_DIR / "starter" / "main.tf"
MARKER = "EXPECTED_SEPARATE_SG_RULES_INCOMPLETE"


def main() -> int:
    terraform = shutil.which("terraform")
    if terraform is None:
        print("Terraform executable was not found.")
        return 2
    init = subprocess.run(
        [terraform, "init", "-backend=false", "-input=false", "-test-directory=tests", "-no-color"],
        cwd=LAB_DIR, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False
    )
    if init.returncode:
        print(init.stdout.rstrip())
        return init.returncode
    test = subprocess.run(
        [terraform, "test", "-test-directory=tests", "-no-color"],
        cwd=LAB_DIR, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False
    )
    print(test.stdout.rstrip())
    if test.returncode:
        print(f"{MARKER}: independent ingress or egress rule behavior is incomplete.")
        return test.returncode
    source = SOURCE.read_text(encoding="utf-8")
    if re.search(r'(?m)^\s*(ingress|egress)\s*\{', source):
        print(f"{MARKER}: inline security-group rules must not be mixed with independent rule resources.")
        return 1
    print("Security-group rule verification passed: independent rule resources are exact.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
