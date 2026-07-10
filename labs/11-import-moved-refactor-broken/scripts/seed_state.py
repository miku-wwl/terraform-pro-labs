#!/usr/bin/env python3
"""Create an isolated import identity from the Lab 11 old configuration."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


LAB_DIR = Path(__file__).resolve().parents[1]
OLD_CONFIG = LAB_DIR / "bootstrap" / "old-config"
RUNTIME = LAB_DIR / ".lab-state"
BOOTSTRAP_WORK = RUNTIME / "bootstrap"
FIXTURE = RUNTIME / "fixture.json"
OLD_ADDRESS = "random_id.legacy_record"


def run(terraform: str, cwd: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [terraform, *arguments],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def require_success(completed: subprocess.CompletedProcess[str], operation: str) -> None:
    if completed.returncode != 0:
        if completed.stdout:
            print(completed.stdout.rstrip())
        raise RuntimeError(f"{operation} failed with exit code {completed.returncode}")


def main() -> int:
    terraform = shutil.which("terraform")
    if terraform is None:
        print("Terraform executable was not found.")
        return 2
    if RUNTIME.exists():
        print("Lab 11 already has generated state; run 'python tools/labctl.py reset 11' first.")
        return 1

    try:
        shutil.copytree(OLD_CONFIG, BOOTSTRAP_WORK)
        require_success(
            run(terraform, BOOTSTRAP_WORK, "init", "-backend=false", "-input=false", "-no-color"),
            "bootstrap init",
        )
        require_success(
            run(terraform, BOOTSTRAP_WORK, "apply", "-auto-approve", "-input=false", "-no-color"),
            "bootstrap apply",
        )

        addresses = run(terraform, BOOTSTRAP_WORK, "state", "list", "-no-color")
        require_success(addresses, "bootstrap state inspection")
        observed_addresses = [line.strip() for line in addresses.stdout.splitlines() if line.strip()]
        if observed_addresses != [OLD_ADDRESS]:
            raise RuntimeError(
                f"bootstrap state addresses were {observed_addresses!r}; expected [{OLD_ADDRESS!r}]"
            )

        output = run(terraform, BOOTSTRAP_WORK, "output", "-raw", "import_id")
        require_success(output, "bootstrap output inspection")
        import_id = output.stdout.strip()
        if not import_id:
            raise RuntimeError("bootstrap import identifier was empty")

        FIXTURE.write_text(
            json.dumps(
                {
                    "import_id": import_id,
                    "old_address": OLD_ADDRESS,
                    "target_address": "module.record.random_id.this",
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        relinquish = run(terraform, BOOTSTRAP_WORK, "state", "rm", OLD_ADDRESS, "-no-color")
        require_success(relinquish, "bootstrap state handoff")
        remaining = run(terraform, BOOTSTRAP_WORK, "state", "list", "-no-color")
        require_success(remaining, "post-handoff state inspection")
        if remaining.stdout.strip():
            raise RuntimeError("bootstrap state was not empty after handing off the import identity")

        print(f"Seeded old state address: {OLD_ADDRESS}")
        print(f"Captured local import identity: {import_id}")
        print("Released the identity from bootstrap state for the learner import stage.")
        return 0
    except (OSError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"Seed failed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
