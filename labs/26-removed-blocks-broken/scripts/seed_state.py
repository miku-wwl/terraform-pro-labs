#!/usr/bin/env python3
"""Seed the two-resource pre-refactor state for Lab 26."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


LAB_DIR = Path(__file__).resolve().parents[1]
RUNTIME = LAB_DIR / ".lab-state"
WORK = RUNTIME / "learner"
FIXTURE = RUNTIME / "fixture.json"
OLD_ADDRESSES = ["terraform_data.legacy_attachment", "terraform_data.service_old"]


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
        print("Lab 26 already has generated state; run 'python tools/labctl.py reset 26' first.")
        return 1
    try:
        shutil.copytree(LAB_DIR / "bootstrap" / "old-config", WORK)
        require(run(terraform, "init", "-backend=false", "-input=false", "-no-color"), "bootstrap init")
        require(run(terraform, "apply", "-auto-approve", "-input=false", "-no-color"), "bootstrap apply")
        listed = run(terraform, "state", "list", "-no-color")
        require(listed, "bootstrap state list")
        addresses = sorted(line.strip() for line in listed.stdout.splitlines() if line.strip())
        if addresses != OLD_ADDRESSES:
            raise RuntimeError(f"unexpected old state addresses: {addresses!r}")
        service = run(terraform, "output", "-json", "service")
        attachment = run(terraform, "output", "-json", "attachment")
        require(service, "service output")
        require(attachment, "attachment output")
        FIXTURE.write_text(json.dumps({
            "old_addresses": OLD_ADDRESSES,
            "service": json.loads(service.stdout),
            "attachment": json.loads(attachment.stdout),
        }, indent=2) + "\n", encoding="utf-8")
        print("Seeded old state addresses:")
        for address in OLD_ADDRESSES:
            print(f"  - {address}")
        return 0
    except (OSError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"Seed failed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
