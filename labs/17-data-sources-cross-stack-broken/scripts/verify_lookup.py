#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parents[1]
SOURCE = LAB_DIR / "starter" / "main.tf"
MARKER = "EXPECTED_CROSS_STACK_LOOKUP_INCOMPLETE"


def strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    return re.sub(r"(?m)(?<!:)//.*$|#.*$", "", text)


def fixture_strings(value: object) -> set[str]:
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        return set().union(*(fixture_strings(item) for item in value), set())
    if isinstance(value, dict):
        return set().union(*(fixture_strings(item) for item in value.values()), set())
    return set()


def source_issues(source: str) -> list[str]:
    code = strip_comments(source)
    expressions = re.sub(r'"(?:\\.|[^"\\])*"', '""', code)
    issues: list[str] = []
    if re.search(r'\bdata\s+"terraform_remote_state"\s+"network"\s*\{', code) is None:
        issues.append('declare data "terraform_remote_state" "network"')
    if re.search(r"\bdata\.terraform_remote_state\.network\.outputs\b", expressions) is None:
        issues.append("derive the consumer contract from data.terraform_remote_state.network.outputs")

    protected_values: set[str] = set()
    for fixture in ("network-primary.tfstate", "network-secondary.tfstate"):
        data = json.loads((LAB_DIR / "fixtures" / fixture).read_text(encoding="utf-8"))
        for output in data.get("outputs", {}).values():
            protected_values.update(fixture_strings(output.get("value")))
    quoted_literals = set(re.findall(r'"((?:\\.|[^"\\])*)"', code))
    copied = sorted(value for value in protected_values if value and value in quoted_literals)
    if copied:
        issues.append("remove copied producer output values from the editable configuration")
    return issues


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
    issues = source_issues(SOURCE.read_text(encoding="utf-8"))
    if issues:
        print(f"{MARKER}: the consumer must use producer outputs through the protected data boundary.")
        for issue in issues:
            print(f"  - {issue}")
        return 1
    print("Cross-stack lookup verification passed for both snapshots, output wiring, and no-copy boundary.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
