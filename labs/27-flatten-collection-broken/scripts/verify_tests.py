#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parents[1]
SOURCE = LAB_DIR / "starter" / "main.tf"
MARKER = "EXPECTED_NESTED_COLLECTION_TRANSFORM_INCOMPLETE"


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
        print(f"{MARKER}: nested rows, stable keys, or merged tag precedence is incomplete.")
        return test.returncode
    source = SOURCE.read_text(encoding="utf-8")
    if "flatten(" not in source or len(re.findall(r"\bmerge\s*\(", source)) != 1:
        print(f"{MARKER}: use the target flatten and layered merge constructs exactly once.")
        return 1
    print("Nested collection verification passed: behavior and target constructs are correct.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
