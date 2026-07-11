#!/usr/bin/env python3
"""Verify Lab 13 workspace-aware settings and production guardrails."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


LAB_DIR = Path(__file__).resolve().parents[1]
RUNTIME = LAB_DIR / ".lab-state"
WORK = RUNTIME / "learner"
MARKER = "EXPECTED_WORKSPACE_GUARDRAIL_INCOMPLETE"
GUARDRAIL = "Production requires t3.large or larger and must not use auto-approve."
EXPECTED = {
    "dev": {"replicas": 1, "tier": "sandbox", "instance_type": "t3.micro"},
    "staging": {"replicas": 2, "tier": "preproduction", "instance_type": "t3.small"},
    "prod": {"replicas": 4, "tier": "production", "instance_type": "t3.large"},
}


def run(terraform: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([terraform, *args], cwd=WORK, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


def require(result: subprocess.CompletedProcess[str], operation: str) -> None:
    if result.returncode:
        if result.stdout:
            print(result.stdout.rstrip())
        raise RuntimeError(f"{operation} failed with exit code {result.returncode}")


def select(terraform: str, name: str) -> None:
    result = run(terraform, "workspace", "select", name, "-no-color")
    if result.returncode:
        require(run(terraform, "workspace", "new", name, "-no-color"), f"create workspace {name}")


def workspaces(terraform: str) -> set[str]:
    result = run(terraform, "workspace", "list", "-no-color")
    require(result, "workspace list")
    return {line.replace("*", "").strip() for line in result.stdout.splitlines() if line.strip()}


def addresses(terraform: str) -> list[str]:
    result = run(terraform, "state", "list", "-no-color")
    require(result, "state list")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def action_lists(terraform: str, plan_name: str) -> list[list[str]]:
    result = run(terraform, "show", "-json", plan_name)
    require(result, "show plan")
    data: dict[str, Any] = json.loads(result.stdout)
    return [item["change"]["actions"] for item in data.get("resource_changes", [])]


def output(terraform: str, name: str) -> Any:
    result = run(terraform, "output", "-json", name)
    require(result, f"output {name}")
    return json.loads(result.stdout)


def incomplete(message: str) -> int:
    print(f"{MARKER}: {message}")
    return 1


def main() -> int:
    terraform = shutil.which("terraform")
    if terraform is None:
        print("Terraform executable was not found.")
        return 2
    try:
        if RUNTIME.exists():
            shutil.rmtree(RUNTIME)
        shutil.copytree(LAB_DIR / "starter", WORK)
        require(run(terraform, "init", "-backend=false", "-input=false", "-no-color"), "init")
        for environment, expected in EXPECTED.items():
            select(terraform, environment)
            plan_name = f"{environment}.tfplan"
            require(run(terraform, "plan", "-input=false", "-no-color", "-var",
                        f"instance_type={expected['instance_type']}", "-var", "auto_approve=false",
                        "-out", plan_name), f"{environment} plan")
            actions = action_lists(terraform, plan_name)
            if any("delete" in action for action in actions):
                raise RuntimeError(f"{environment} unexpectedly planned a destroy: {actions!r}")
            require(run(terraform, "apply", "-input=false", "-no-color", plan_name), f"{environment} apply")
            if addresses(terraform) != ["terraform_data.deployment"]:
                raise RuntimeError(f"{environment} state address is incorrect")
            selected = output(terraform, "selected_environment")
            deployment = output(terraform, "deployment")
            if selected != environment or any(deployment.get(key) != value for key, value in expected.items()):
                return incomplete(f"{environment} workspace did not select its exact settings")
            final = run(terraform, "plan", "-input=false", "-no-color", "-var",
                        f"instance_type={expected['instance_type']}", "-var", "auto_approve=false",
                        "-detailed-exitcode")
            if final.returncode != 0:
                raise RuntimeError(f"{environment} final plan was not no-op")
        if workspaces(terraform) != {"default", "dev", "staging", "prod"}:
            raise RuntimeError("runtime workspace set differs from the declared owned names")

        select(terraform, "prod")
        unsafe_cases = (("t3.micro", "false"), ("t3.large", "true"))
        for instance_type, auto_approve in unsafe_cases:
            blocked = run(terraform, "plan", "-input=false", "-no-color", "-var",
                          f"instance_type={instance_type}", "-var", f"auto_approve={auto_approve}")
            if blocked.returncode == 0 or GUARDRAIL not in blocked.stdout:
                return incomplete("prod must reject undersized capacity and auto-approve with the documented diagnostic")
        print("PASS: dev, staging, and prod used exact workspace settings and isolated state addresses.")
        print("PASS: no destroy was planned, final plans were no-op, and both prod guardrails fired.")
        return 0
    except (OSError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"Verification failed: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
