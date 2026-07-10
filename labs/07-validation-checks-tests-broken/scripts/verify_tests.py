#!/usr/bin/env python3
"""Run the public Terraform tests and classify the intended starter failure."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


LAB_DIR = Path(__file__).resolve().parents[1]


def main() -> int:
    terraform = shutil.which("terraform")
    if terraform is None:
        print("Terraform executable was not found.")
        return 2

    initialized = subprocess.run(
        [terraform, "init", "-backend=false", "-input=false", "-test-directory=tests", "-no-color"],
        cwd=LAB_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if initialized.returncode != 0:
        print(initialized.stdout.rstrip())
        return initialized.returncode

    completed = subprocess.run(
        [terraform, "test", "-test-directory=tests", "-no-color"],
        cwd=LAB_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    print(completed.stdout.rstrip())
    if completed.returncode != 0 and "Missing expected failure" in completed.stdout:
        print("EXPECTED_GUARDS_INCOMPLETE: one or more guard conditions are still permissive.")
        return 1
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
