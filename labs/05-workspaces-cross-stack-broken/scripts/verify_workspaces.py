#!/usr/bin/env python3
"""Verify Lab 05 workspace-isolated producer and consumer state flow."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


LAB_DIR = Path(__file__).resolve().parents[1]
RUNTIME = LAB_DIR / ".lab-state"
PRODUCER = RUNTIME / "producer"
CONSUMER = RUNTIME / "consumer"
ENVIRONMENTS = ("dev", "prod")
MARKER = "EXPECTED_WORKSPACE_FLOW_INCOMPLETE"
GUARDRAIL = "t3.micro is not allowed in the prod workspace."


def run(terraform: str, cwd: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([terraform, *arguments], cwd=cwd, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


def require(completed: subprocess.CompletedProcess[str], operation: str) -> None:
    if completed.returncode:
        if completed.stdout:
            print(completed.stdout.rstrip())
        raise RuntimeError(f"{operation} failed with exit code {completed.returncode}")


def workspaces(terraform: str, cwd: Path) -> set[str]:
    completed = run(terraform, cwd, "workspace", "list", "-no-color")
    require(completed, "workspace list")
    return {line.replace("*", "").strip() for line in completed.stdout.splitlines() if line.strip()}


def addresses(terraform: str, cwd: Path) -> list[str]:
    completed = run(terraform, cwd, "state", "list", "-no-color")
    require(completed, "state list")
    return sorted(line.strip() for line in completed.stdout.splitlines() if line.strip())


def output_json(terraform: str, cwd: Path, name: str) -> Any:
    completed = run(terraform, cwd, "output", "-json", name)
    require(completed, f"output {name}")
    return json.loads(completed.stdout)


def assert_no_delete(terraform: str, cwd: Path, plan: Path) -> None:
    shown = run(terraform, cwd, "show", "-json", plan.name)
    require(shown, "show plan")
    data = json.loads(shown.stdout)
    actions = [item.get("change", {}).get("actions", []) for item in data.get("resource_changes", [])]
    if any("delete" in action for action in actions):
        raise RuntimeError(f"unexpected destroy action in workspace plan: {actions!r}")


def select(terraform: str, cwd: Path, name: str) -> None:
    selected = run(terraform, cwd, "workspace", "select", name, "-no-color")
    if selected.returncode:
        require(run(terraform, cwd, "workspace", "new", name, "-no-color"), f"create workspace {name}")


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
        shutil.copytree(LAB_DIR / "bootstrap" / "producer", PRODUCER)
        shutil.copytree(LAB_DIR / "starter", CONSUMER)
        require(run(terraform, PRODUCER, "init", "-backend=false", "-input=false", "-no-color"), "producer init")
        for environment in ENVIRONMENTS:
            select(terraform, PRODUCER, environment)
            plan = PRODUCER / f"{environment}.tfplan"
            require(run(terraform, PRODUCER, "plan", "-input=false", "-no-color", "-out", plan.name), f"producer {environment} plan")
            assert_no_delete(terraform, PRODUCER, plan)
            require(run(terraform, PRODUCER, "apply", "-input=false", "-no-color", plan.name), f"producer {environment} apply")
            if addresses(terraform, PRODUCER) != ["terraform_data.network"]:
                raise RuntimeError(f"producer {environment} state address is incorrect")
        if workspaces(terraform, PRODUCER) != {"default", "dev", "prod"}:
            raise RuntimeError("producer created a workspace outside the lab-owned set")

        (CONSUMER / "terraform.auto.tfvars.json").write_text(
            json.dumps({"producer_state_root": str(PRODUCER)}, indent=2) + "\n", encoding="utf-8"
        )
        require(run(terraform, CONSUMER, "init", "-backend=false", "-input=false", "-no-color"), "consumer init")
        expected_addresses = ["data.terraform_remote_state.network", "terraform_data.deployment"]
        for environment in ENVIRONMENTS:
            select(terraform, CONSUMER, environment)
            instance_type = "t3.micro" if environment == "dev" else "t3.large"
            plan = CONSUMER / f"{environment}.tfplan"
            require(run(terraform, CONSUMER, "plan", "-input=false", "-no-color", "-var", f"instance_type={instance_type}", "-out", plan.name), f"consumer {environment} plan")
            assert_no_delete(terraform, CONSUMER, plan)
            require(run(terraform, CONSUMER, "apply", "-input=false", "-no-color", plan.name), f"consumer {environment} apply")
            if addresses(terraform, CONSUMER) != expected_addresses:
                raise RuntimeError(f"consumer {environment} state addresses are incorrect")
            network = output_json(terraform, CONSUMER, "network")
            selected = output_json(terraform, CONSUMER, "selected_environment")
            if selected != environment or network.get("environment") != environment:
                return incomplete(f"{environment} workspace did not select the matching producer state")
            final = run(terraform, CONSUMER, "plan", "-input=false", "-no-color", "-var", f"instance_type={instance_type}", "-detailed-exitcode")
            if final.returncode != 0:
                if final.stdout:
                    print(final.stdout.rstrip())
                raise RuntimeError(f"consumer {environment} final plan is not a no-op")

        if workspaces(terraform, CONSUMER) != {"default", "dev", "prod"}:
            raise RuntimeError("consumer created a workspace outside the lab-owned set")
        blocked = run(terraform, CONSUMER, "plan", "-input=false", "-no-color", "-var", "instance_type=t3.micro")
        if blocked.returncode == 0 or GUARDRAIL not in blocked.stdout:
            return incomplete("prod must reject t3.micro with the documented safety diagnostic")
        print("PASS: dev and prod producer/consumer states use exact isolated addresses and matching values.")
        print("PASS: both consumer reruns are no-op, no destroy was planned, and the prod guardrail rejected t3.micro.")
        return 0
    except (OSError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"Verification failed: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
