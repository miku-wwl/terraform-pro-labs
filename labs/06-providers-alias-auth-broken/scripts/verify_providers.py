#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parents[1]
STARTER = LAB_DIR / "starter"
MARKER = "EXPECTED_PROVIDER_ALIAS_AUTH_INCOMPLETE"


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
        print(f"{MARKER}: provider alias selection is incomplete.")
        return test.returncode

    versions = (STARTER / "versions.tf").read_text(encoding="utf-8")
    main = (STARTER / "main.tf").read_text(encoding="utf-8")
    required_provider_ok = (
        re.search(r'source\s*=\s*"hashicorp/aws"', versions) is not None
        and re.search(r'version\s*=\s*"~> 6\.0"', versions) is not None
    )
    pinned_auth = re.search(r'(?m)^\s*(profile|access_key|secret_key|token)\s*=', main) is not None
    if not required_provider_ok or pinned_auth:
        print(
            f"{MARKER}: keep the declared provider source/version and allow the standard AWS "
            "credential chain instead of pinning authentication in configuration."
        )
        return 1
    print("Provider verification passed: requirements, alias selection, and auth boundary are correct.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
