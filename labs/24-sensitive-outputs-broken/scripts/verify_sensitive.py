#!/usr/bin/env python3
"""Verify sensitive metadata and CLI redaction without logging the probe value."""

from __future__ import annotations

import json
import os
import secrets
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

STARTER = Path(__file__).resolve().parents[1] / "starter"
MARKER = "EXPECTED_SENSITIVE_BOUNDARY_INCOMPLETE"


def run(terraform: str, cwd: Path, env: dict[str, str], *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [terraform, *args], cwd=cwd, env=env, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False
    )


def redacted(text: str, probe: str) -> str:
    return text.replace(probe, "[REDACTED]")


def main() -> int:
    terraform = shutil.which("terraform")
    if terraform is None:
        print("Terraform executable was not found.")
        return 2

    probe = f"synthetic-lab24-{secrets.token_hex(18)}"
    env = os.environ.copy()
    env["TF_VAR_db_password"] = probe
    env["TF_IN_AUTOMATION"] = "1"
    with tempfile.TemporaryDirectory(prefix="tfpro-lab24-") as temporary:
        workdir = Path(temporary)
        for source in STARTER.glob("*.tf"):
            shutil.copy2(source, workdir / source.name)
        init = run(terraform, workdir, env, "init", "-backend=false", "-input=false", "-no-color")
        if init.returncode != 0:
            print(redacted(init.stdout.rstrip(), probe))
            return init.returncode
        plan = run(
            terraform, workdir, env, "plan", "-input=false", "-no-color", "-out=redaction.tfplan"
        )
        if plan.returncode != 0:
            print(redacted(plan.stdout.rstrip(), probe))
            return plan.returncode
        shown = run(terraform, workdir, env, "show", "-json", "redaction.tfplan")
        if shown.returncode != 0:
            print(redacted(shown.stdout.rstrip(), probe))
            return shown.returncode
        payload = json.loads(shown.stdout)
        applied = run(
            terraform, workdir, env, "apply", "-input=false", "-no-color", "redaction.tfplan"
        )
        if applied.returncode != 0:
            print(redacted(applied.stdout.rstrip(), probe))
            return applied.returncode
        rendered_outputs = run(terraform, workdir, env, "output", "-json")
        if rendered_outputs.returncode != 0:
            print(redacted(rendered_outputs.stdout.rstrip(), probe))
            return rendered_outputs.returncode
        applied_outputs = json.loads(rendered_outputs.stdout)

    variables = payload["configuration"]["root_module"]["variables"]
    outputs = payload["planned_values"]["outputs"]
    expected_outputs = {"connection_uri", "database_config", "credential_metadata"}
    metadata = outputs.get("credential_metadata", {})
    password_variable = variables.get("db_password", {})
    failures: list[str] = []
    if not password_variable.get("sensitive", False):
        failures.append("db_password is not declared sensitive")
    if "default" in password_variable:
        failures.append("db_password must be supplied at runtime and must not have a default")
    if set(outputs) != expected_outputs:
        failures.append("the root output set contains a missing or unsafe extra output")
    for name in ("connection_uri", "database_config"):
        if not outputs.get(name, {}).get("sensitive", False):
            failures.append(f"{name} is not sensitive")
    if metadata.get("sensitive", True):
        failures.append("credential_metadata is unnecessarily sensitive")
    if metadata.get("value") != {"password_configured": True, "username": "app_user"}:
        failures.append("credential_metadata does not contain the exact safe diagnostics")
    if probe in plan.stdout:
        failures.append("CLI plan output exposes the runtime probe")
    if probe in applied.stdout:
        failures.append("CLI apply output exposes the runtime probe")

    expected_connection = f"postgres://app_user:{probe}@db.internal:5432/app"
    if applied_outputs.get("connection_uri", {}).get("value") != expected_connection:
        failures.append("connection_uri does not preserve the complete runtime connection value")
    if applied_outputs.get("database_config", {}).get("value") != {
        "password": probe,
        "username": "app_user",
    }:
        failures.append("database_config does not preserve the complete runtime configuration")

    if failures:
        print(f"{MARKER}: secret redaction or sensitivity metadata is incomplete.")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print(
        "Sensitive verification passed: required runtime input, exact output values, metadata, "
        "safe diagnostics, and CLI redaction are correct."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
