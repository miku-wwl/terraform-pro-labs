#!/usr/bin/env python3
"""Behaviorally verify that a destroy plan is blocked by prevent_destroy."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


STARTER = Path(__file__).resolve().parents[1] / "starter"


def run(terraform: str, cwd: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [terraform, *arguments],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def main() -> int:
    terraform = shutil.which("terraform")
    if terraform is None:
        print("Terraform executable was not found.")
        return 2

    with tempfile.TemporaryDirectory(prefix="tfpro-lab01-") as temporary:
        workdir = Path(temporary)
        for source in STARTER.glob("*.tf"):
            shutil.copy2(source, workdir / source.name)

        init = run(terraform, workdir, "init", "-backend=false", "-input=false", "-no-color")
        if init.returncode != 0:
            print(init.stdout)
            return init.returncode

        apply = run(terraform, workdir, "apply", "-auto-approve", "-input=false", "-no-color")
        if apply.returncode != 0:
            print(apply.stdout)
            return apply.returncode

        destroy_plan = run(terraform, workdir, "plan", "-destroy", "-input=false", "-no-color")
        diagnostic = destroy_plan.stdout.lower()
        target_address = "terraform_data.deployment_record"
        if (
            destroy_plan.returncode != 0
            and "prevent_destroy" in diagnostic
            and target_address in diagnostic
        ):
            print("Lifecycle verification passed: destroy plan was blocked by prevent_destroy.")
            return 0

        if destroy_plan.returncode in (0, 2):
            print("EXPECTED_GUARD_MISSING: destroy plan was allowed.")
            return 1

        print(destroy_plan.stdout)
        print("Unexpected destroy-plan failure; prevent_destroy diagnostic was absent.")
        return destroy_plan.returncode or 2


if __name__ == "__main__":
    raise SystemExit(main())
