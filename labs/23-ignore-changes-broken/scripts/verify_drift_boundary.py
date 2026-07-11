#!/usr/bin/env python3
"""Verify that only externally-owned owner drift is ignored."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

STARTER = Path(__file__).resolve().parents[1] / "starter"
MARKER = "EXPECTED_IGNORE_CHANGES_BOUNDARY_INCOMPLETE"


def run(terraform: str, cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [terraform, *args], cwd=cwd, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, check=False
    )


def change_actions(terraform: str, workdir: Path, state_name: str) -> list[str]:
    planned = run(
        terraform, workdir, "plan", "-input=false", "-no-color",
        "-refresh=false", f"-state={state_name}.tfstate", f"-out={state_name}.tfplan"
    )
    if planned.returncode != 0:
        raise RuntimeError(planned.stdout)
    shown = run(terraform, workdir, "show", "-json", f"{state_name}.tfplan")
    if shown.returncode != 0:
        raise RuntimeError(shown.stdout)
    changes = json.loads(shown.stdout).get("resource_changes", [])
    match = next((item for item in changes if item["address"] == "local_file.service"), None)
    return [] if match is None else match["change"]["actions"]


def drifted_state(base: dict, field: str, value: str) -> dict:
    state = json.loads(json.dumps(base))
    resource = next(item for item in state["resources"] if item["name"] == "service")
    attributes = resource["instances"][0]["attributes"]
    attributes[field] = value
    state["serial"] += 1
    return state


def main() -> int:
    terraform = shutil.which("terraform")
    if terraform is None:
        print("Terraform executable was not found.")
        return 2
    try:
        with tempfile.TemporaryDirectory(prefix="tfpro-lab23-") as temporary:
            workdir = Path(temporary)
            for source in STARTER.glob("*.tf"):
                shutil.copy2(source, workdir / source.name)
            init = run(terraform, workdir, "init", "-backend=false", "-input=false", "-no-color")
            if init.returncode != 0:
                print(init.stdout.rstrip())
                return init.returncode
            applied = run(
                terraform, workdir, "apply", "-auto-approve", "-input=false", "-no-color",
                "-state=base.tfstate"
            )
            if applied.returncode != 0:
                print(applied.stdout.rstrip())
                return applied.returncode
            base = json.loads((workdir / "base.tfstate").read_text(encoding="utf-8"))
            (workdir / "permission.tfstate").write_text(
                json.dumps(drifted_state(base, "file_permission", "0600")), encoding="utf-8"
            )
            (workdir / "content.tfstate").write_text(
                json.dumps(drifted_state(base, "content", '{"name":"drifted","version":"v1"}')),
                encoding="utf-8"
            )
            permission_actions = change_actions(terraform, workdir, "permission")
            content_actions = change_actions(terraform, workdir, "content")
    except (KeyError, StopIteration, ValueError, RuntimeError) as exc:
        print(f"Unexpected drift verification error: {exc}")
        return 2

    permission_ok = permission_actions in ([], ["no-op"])
    managed_ok = content_actions not in ([], ["no-op"])
    if permission_ok and managed_ok:
        print("Drift verification passed: permission drift is ignored and managed content drift is repaired.")
        return 0
    print(
        f"{MARKER}: permission actions={permission_actions!r}; managed-content actions={content_actions!r}. "
        "Ignore only the externally-owned permission field."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
