#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parents[1]
SOURCE = LAB_DIR / "starter" / "main.tf"
MARKER = "EXPECTED_DYNAMIC_BLOCK_INCOMPLETE"


def main() -> int:
    terraform = shutil.which("terraform")
    if terraform is None:
        print("Terraform executable was not found.")
        return 2
    init = subprocess.run(
        [terraform, "init", "-backend=false", "-input=false", "-test-directory=tests", "-no-color"],
        cwd=LAB_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if init.returncode:
        print(init.stdout.rstrip())
        return init.returncode
    test = subprocess.run(
        [terraform, "test", "-test-directory=tests", "-no-color"],
        cwd=LAB_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    print(test.stdout.rstrip())
    if test.returncode:
        print(f"{MARKER}: nested ingress count or content does not follow the input collection.")
        return test.returncode

    source = SOURCE.read_text(encoding="utf-8")
    has_dynamic = re.search(r'\bdynamic\s+"ingress"\s*\{', source) is not None
    has_static = re.search(r'(?m)^\s*ingress\s*\{', source) is not None
    if not has_dynamic or has_static:
        print(f"{MARKER}: use one dynamic ingress construct without static ingress duplication.")
        return 1
    print("Dynamic block verification passed: count, content, and source structure are correct.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
