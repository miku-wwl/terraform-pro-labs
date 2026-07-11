#!/usr/bin/env python3
"""Prove replacement is caused specifically by an upstream dependency change."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

STARTER = Path(__file__).resolve().parents[1] / "starter"
MARKER = "EXPECTED_REPLACE_TRIGGER_INCOMPLETE"


def run(terraform: str, cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [terraform, *args], cwd=cwd, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, check=False
    )


def plan_json(terraform: str, workdir: Path, name: str, *variables: str) -> dict:
    arguments = ["plan", "-input=false", "-no-color", f"-out={name}.tfplan"]
    for variable in variables:
        arguments.extend(["-var", variable])
    planned = run(terraform, workdir, *arguments)
    if planned.returncode != 0:
        raise RuntimeError(planned.stdout)
    shown = run(terraform, workdir, "show", "-json", f"{name}.tfplan")
    if shown.returncode != 0:
        raise RuntimeError(shown.stdout)
    return json.loads(shown.stdout)


def change(plan: dict, address: str) -> dict:
    return next(item for item in plan["resource_changes"] if item["address"] == address)


def main() -> int:
    terraform = shutil.which("terraform")
    if terraform is None:
        print("Terraform executable was not found.")
        return 2
    try:
        with tempfile.TemporaryDirectory(prefix="tfpro-lab32-") as temporary:
            workdir = Path(temporary)
            for source in STARTER.glob("*.tf"):
                shutil.copy2(source, workdir / source.name)
            for args in (
                ("init", "-backend=false", "-input=false", "-no-color"),
                ("apply", "-auto-approve", "-input=false", "-no-color"),
            ):
                completed = run(terraform, workdir, *args)
                if completed.returncode != 0:
                    print(completed.stdout.rstrip())
                    return completed.returncode
            release_plan = plan_json(terraform, workdir, "release", "release_version=v2")
            name_plan = plan_json(terraform, workdir, "name", "service_name=orders")
    except (KeyError, StopIteration, ValueError, RuntimeError) as exc:
        print(f"Unexpected dependency replacement verification error: {exc}")
        return 2

    marker_change = change(release_plan, "terraform_data.release_marker")
    release_service = change(release_plan, "terraform_data.service")
    name_service = change(name_plan, "terraform_data.service")
    marker_actions = marker_change["change"]["actions"]
    release_actions = release_service["change"]["actions"]
    release_reason = release_service.get("action_reason")
    name_actions = name_service["change"]["actions"]

    correct = (
        marker_actions == ["update"]
        and release_actions in (["delete", "create"], ["create", "delete"])
        and release_reason == "replace_by_triggers"
        and name_actions == ["update"]
    )
    if correct:
        print(
            "Dependency replacement verification passed: upstream release change replaces the "
            "service, while a direct name change remains an update."
        )
        return 0
    print(
        f"{MARKER}: marker={marker_actions!r}, release-service={release_actions!r}, "
        f"reason={release_reason!r}, name-service={name_actions!r}."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
