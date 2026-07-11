#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parents[1]
MARKER = "EXPECTED_S3_CONDITIONAL_CONFIGURATION_INCOMPLETE"


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
                print(f"{MARKER}: filtering, lifecycle, tag precedence, or map outputs are incomplete.")
            return completed.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
