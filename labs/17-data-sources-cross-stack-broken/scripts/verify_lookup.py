#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parents[1]
SOURCE = LAB_DIR / "starter" / "main.tf"
MARKER = "EXPECTED_CROSS_STACK_LOOKUP_INCOMPLETE"


def main() -> int:
    terraform = shutil.which("terraform")
    if terraform is None:
        print("Terraform executable was not found.")
        return 2
    for args in (
        ("init", "-backend=false", "-input=false", "-test-directory=tests", "-no-color"),
        ("test", "-test-directory=tests", "-no-color"),
    ):
        completed = subprocess.run(
            [terraform, *args], cwd=LAB_DIR, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False
        )
        print(completed.stdout.rstrip())
        if completed.returncode:
            if args[0] == "test":
                print(f"{MARKER}: lookup input or normalized output boundary is incomplete.")
            return completed.returncode
    source = SOURCE.read_text(encoding="utf-8")
    if re.search(r'\bdata\s+"terraform_remote_state"\s+"network"\s*\{', source) is None:
        print(f"{MARKER}: the consumer must use the protected producer state through a data source.")
        return 1
    print("Cross-stack lookup verification passed for both producer snapshots and the input boundary.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
