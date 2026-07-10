#!/usr/bin/env python3
from __future__ import annotations
import shutil, subprocess, sys
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parents[1]
MARKER = "EXPECTED_FILTERED_FOREACH_INCOMPLETE"

def main() -> int:
    terraform = shutil.which("terraform")
    if terraform is None: print("Terraform executable was not found."); return 2
    init = subprocess.run([terraform, "init", "-backend=false", "-input=false", "-test-directory=tests", "-no-color"], cwd=LAB_DIR, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    if init.returncode: print(init.stdout.rstrip()); return init.returncode
    test = subprocess.run([terraform, "test", "-test-directory=tests", "-no-color"], cwd=LAB_DIR, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    print(test.stdout.rstrip())
    if test.returncode: print(f"{MARKER}: filtering or stable map output behavior is incomplete.")
    return test.returncode

if __name__ == "__main__": raise SystemExit(main())
