#!/usr/bin/env python3
from __future__ import annotations
import re, shutil, subprocess, sys
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parents[1]
SOURCE = LAB_DIR / "starter" / "main.tf"
MARKER = "EXPECTED_CONDITIONAL_READ_INCOMPLETE"

def main() -> int:
    terraform = shutil.which("terraform")
    if terraform is None: print("Terraform executable was not found."); return 2
    init = subprocess.run([terraform, "init", "-backend=false", "-input=false", "-test-directory=tests", "-no-color"], cwd=LAB_DIR, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    if init.returncode: print(init.stdout.rstrip()); return init.returncode
    test = subprocess.run([terraform, "test", "-test-directory=tests", "-no-color"], cwd=LAB_DIR, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    print(test.stdout.rstrip())
    source = SOURCE.read_text(encoding="utf-8")
    functions_present = re.search(r"\bone\s*\(", source) and re.search(r"\btry\s*\(", source)
    if test.returncode or not functions_present:
        if not functions_present: print("Required source contract is incomplete: both one() and try() must be used.")
        print(f"{MARKER}: the zero-or-one reads are not both safe and explicit.")
        return 1
    return 0

if __name__ == "__main__": raise SystemExit(main())
