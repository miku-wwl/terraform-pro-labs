#!/usr/bin/env python3
"""Prove release-only replacement scope and create-before-destroy ordering."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

STARTER = Path(__file__).resolve().parents[1] / "starter"
MARKER = "EXPECTED_CREATE_BEFORE_DESTROY_INCOMPLETE"


def run(terraform: str, cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [terraform, *args], cwd=cwd, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, check=False
    )


def require(result: subprocess.CompletedProcess[str], operation: str) -> None:
    if result.returncode:
        if result.stdout:
            print(result.stdout.rstrip())
        raise RuntimeError(f"{operation} failed with exit code {result.returncode}")


def strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    return re.sub(r"(?m)(?<!:)//.*$|#.*$", "", text)


def service_body(source: str) -> str | None:
    code = strip_comments(source)
    match = re.search(r'\bresource\s+"terraform_data"\s+"service"\s*\{', code)
    if match is None:
        return None
    start = code.find("{", match.start())
    depth = 0
    quoted = False
    escaped = False
    for index in range(start, len(code)):
        character = code[index]
        if quoted:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                quoted = False
            continue
        if character == '"':
            quoted = True
        elif character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth == 0:
                return code[start + 1:index]
    return None


def trigger_is_release_only(source: str) -> bool:
    body = service_body(source)
    if body is None:
        return False
    assignments = re.findall(r"(?m)^\s*triggers_replace\s*=\s*([^\r\n]+?)\s*$", body)
    return assignments == ["var.release"]


def actions(terraform: str, cwd: Path, plan_name: str) -> list[str] | None:
    shown = run(terraform, cwd, "show", "-json", plan_name)
    require(shown, f"show {plan_name}")
    plan: dict[str, Any] = json.loads(shown.stdout)
    change = next(
        (item for item in plan.get("resource_changes", [])
         if item.get("address") == "terraform_data.service"),
        None,
    )
    if change is None:
        return None
    return change["change"]["actions"]


def incomplete(message: str) -> int:
    print(f"{MARKER}: {message}")
    return 1


def main() -> int:
    terraform = shutil.which("terraform")
    if terraform is None:
        print("Terraform executable was not found.")
        return 2
    if not trigger_is_release_only((STARTER / "main.tf").read_text(encoding="utf-8")):
        return incomplete("triggers_replace must remain scoped exactly to var.release")
    try:
        with tempfile.TemporaryDirectory(prefix="tfpro-lab22-") as temporary:
            workdir = Path(temporary)
            for source in STARTER.glob("*.tf"):
                shutil.copy2(source, workdir / source.name)
            require(run(terraform, workdir, "init", "-backend=false", "-input=false", "-no-color"), "init")
            require(run(
                terraform, workdir, "apply", "-auto-approve", "-input=false", "-no-color",
                "-var", "service_name=api", "-var", "release=v1",
            ), "baseline apply")

            steady = run(
                terraform, workdir, "plan", "-input=false", "-no-color", "-detailed-exitcode",
                "-var", "service_name=api", "-var", "release=v1",
            )
            if steady.returncode != 0:
                raise RuntimeError("unchanged release and name must produce a no-op plan")

            require(run(
                terraform, workdir, "plan", "-input=false", "-no-color", "-out=name.tfplan",
                "-var", "service_name=payments", "-var", "release=v1",
            ), "name-only plan")
            name_actions = actions(terraform, workdir, "name.tfplan")
            if name_actions != ["update"]:
                return incomplete(f"a name-only change must remain an update, observed {name_actions!r}")

            require(run(
                terraform, workdir, "plan", "-input=false", "-no-color", "-out=release.tfplan",
                "-var", "service_name=api", "-var", "release=v2",
            ), "release plan")
            release_actions = actions(terraform, workdir, "release.tfplan")
            if release_actions == ["create", "delete"]:
                print("PASS: unchanged inputs were no-op and a name-only change remained an update.")
                print("PASS: the release-only replacement planned create then delete.")
                return 0
            if release_actions == ["delete", "create"]:
                return incomplete("release replacement is still ordered delete then create")
            raise RuntimeError(f"release change did not produce a genuine replacement: {release_actions!r}")
    except (OSError, RuntimeError, json.JSONDecodeError, KeyError) as exc:
        print(f"Verification failed: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
