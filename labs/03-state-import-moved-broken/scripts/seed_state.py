#!/usr/bin/env python3
"""Seed two local random identities for Lab 03 declarative import."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


LAB_DIR = Path(__file__).resolve().parents[1]
SOURCE = LAB_DIR / "bootstrap" / "old-config"
RUNTIME = LAB_DIR / ".lab-state"
WORK = RUNTIME / "bootstrap"
FIXTURE = RUNTIME / "fixture.json"
NAMES = ("api", "worker")
OLD_ADDRESSES = [f'random_id.legacy["{name}"]' for name in NAMES]
TARGET_ADDRESSES = [f'module.record["{name}"].random_id.this' for name in NAMES]


def run(terraform: str, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [terraform, *arguments], cwd=WORK, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False
    )


def require(completed: subprocess.CompletedProcess[str], operation: str) -> None:
    if completed.returncode:
        if completed.stdout:
            print(completed.stdout.rstrip())
        raise RuntimeError(f"{operation} failed with exit code {completed.returncode}")


def main() -> int:
    terraform = shutil.which("terraform")
    if terraform is None:
        print("Terraform executable was not found.")
        return 2
    if RUNTIME.exists():
        print("Lab 03 already has generated state; run 'python tools/labctl.py reset 03' first.")
        return 1
    try:
        shutil.copytree(SOURCE, WORK)
        require(run(terraform, "init", "-backend=false", "-input=false", "-no-color"), "bootstrap init")
        require(run(terraform, "apply", "-auto-approve", "-input=false", "-no-color"), "bootstrap apply")
        listed = run(terraform, "state", "list", "-no-color")
        require(listed, "bootstrap state list")
        addresses = sorted(line.strip() for line in listed.stdout.splitlines() if line.strip())
        if addresses != sorted(OLD_ADDRESSES):
            raise RuntimeError(f"unexpected bootstrap addresses: {addresses!r}")
        output = run(terraform, "output", "-json", "import_ids")
        require(output, "bootstrap output")
        import_ids = json.loads(output.stdout)
        if sorted(import_ids) != list(NAMES) or not all(import_ids.values()):
            raise RuntimeError("bootstrap identifiers are incomplete")
        for address in OLD_ADDRESSES:
            require(run(terraform, "state", "rm", address), f"release {address}")
        FIXTURE.write_text(json.dumps({
            "import_ids": import_ids,
            "old_addresses": OLD_ADDRESSES,
            "target_addresses": TARGET_ADDRESSES,
        }, indent=2) + "\n", encoding="utf-8")
        print("Seeded old state addresses:")
        for address in OLD_ADDRESSES:
            print(f"  - {address}")
        print("Captured and released two local import identities.")
        return 0
    except (OSError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"Seed failed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
