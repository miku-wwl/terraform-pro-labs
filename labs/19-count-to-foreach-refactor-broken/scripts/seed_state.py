#!/usr/bin/env python3
"""Seed Lab 19 count-indexed state in an isolated learner runtime."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


LAB_DIR = Path(__file__).resolve().parents[1]
RUNTIME = LAB_DIR / ".lab-state"
WORK = RUNTIME / "learner"
FIXTURE = RUNTIME / "fixture.json"
OLD = [f"terraform_data.bucket[{index}]" for index in range(3)]
TARGET = [
    'terraform_data.bucket["logs"]',
    'terraform_data.bucket["assets"]',
    'terraform_data.bucket["archive"]',
]


def run(terraform: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([terraform, *args], cwd=WORK, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


def require(result: subprocess.CompletedProcess[str], operation: str) -> None:
    if result.returncode:
        if result.stdout:
            print(result.stdout.rstrip())
        raise RuntimeError(f"{operation} failed with exit code {result.returncode}")


def main() -> int:
    terraform = shutil.which("terraform")
    if terraform is None:
        print("Terraform executable was not found.")
        return 2
    if RUNTIME.exists():
        print("Lab 19 already has generated state; run 'python tools/labctl.py reset 19' first.")
        return 1
    try:
        shutil.copytree(LAB_DIR / "bootstrap" / "old-config", WORK)
        require(run(terraform, "init", "-backend=false", "-input=false", "-no-color"), "bootstrap init")
        require(run(terraform, "apply", "-auto-approve", "-input=false", "-no-color"), "bootstrap apply")
        listed = run(terraform, "state", "list", "-no-color")
        require(listed, "bootstrap state list")
        addresses = sorted(line.strip() for line in listed.stdout.splitlines() if line.strip())
        if addresses != sorted(OLD):
            raise RuntimeError(f"unexpected old addresses: {addresses!r}")
        output = run(terraform, "output", "-json", "records")
        require(output, "bootstrap output")
        values = json.loads(output.stdout)
        FIXTURE.write_text(json.dumps({
            "old_addresses": OLD,
            "target_addresses": TARGET,
            "records_by_index": values,
        }, indent=2) + "\n", encoding="utf-8")
        print("Seeded exact old count addresses:")
        for address in OLD:
            print(f"  - {address}")
        return 0
    except (OSError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"Seed failed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
