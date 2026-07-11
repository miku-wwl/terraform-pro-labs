#!/usr/bin/env python3
"""Prove replacement ordering from a stateful plan."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

STARTER = Path(__file__).resolve().parents[1] / "starter"
MARKER = "EXPECTED_CREATE_BEFORE_DESTROY_INCOMPLETE"


def run(terraform: str, cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [terraform, *args], cwd=cwd, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, check=False
    )


def main() -> int:
    terraform = shutil.which("terraform")
    if terraform is None:
        print("Terraform executable was not found.")
        return 2
    with tempfile.TemporaryDirectory(prefix="tfpro-lab22-") as temporary:
        workdir = Path(temporary)
        for source in STARTER.glob("*.tf"):
            shutil.copy2(source, workdir / source.name)
        for args in (
            ("init", "-backend=false", "-input=false", "-no-color"),
            ("apply", "-auto-approve", "-input=false", "-no-color", "-var", "release=v1"),
            ("plan", "-input=false", "-no-color", "-out=release.tfplan", "-var", "release=v2"),
        ):
            completed = run(terraform, workdir, *args)
            if completed.returncode != 0:
                print(completed.stdout.rstrip())
                return completed.returncode
        shown = run(terraform, workdir, "show", "-json", "release.tfplan")
        if shown.returncode != 0:
            print(shown.stdout.rstrip())
            return shown.returncode
        plan = json.loads(shown.stdout)
        change = next(
            item for item in plan["resource_changes"]
            if item["address"] == "terraform_data.service"
        )
        actions = change["change"]["actions"]
        if actions == ["create", "delete"]:
            print("Replacement verification passed: release change plans create then delete.")
            return 0
        if actions == ["delete", "create"]:
            print(f"{MARKER}: release replacement is still ordered delete then create.")
            return 1
        print(f"Unexpected service actions: {actions!r}; a real replacement was required.")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
