#!/usr/bin/env python3
"""Verify Lab 04 backend rules and local producer/consumer state flow."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any


LAB_DIR = Path(__file__).resolve().parents[1]
RUNTIME = LAB_DIR / ".lab-state"
PRODUCER = RUNTIME / "producer"
CONSUMER = RUNTIME / "consumer"
MARKER = "EXPECTED_BACKEND_CROSS_STACK_INCOMPLETE"
EXPECTED = {
    "vpc_id": "vpc-lab04-dev",
    "subnet_ids": ["subnet-lab04-a", "subnet-lab04-b"],
    "security_group_id": "sg-lab04-app",
}


def run(terraform: str, cwd: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([terraform, *arguments], cwd=cwd, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


def require(completed: subprocess.CompletedProcess[str], operation: str) -> None:
    if completed.returncode:
        if completed.stdout:
            print(completed.stdout.rstrip())
        raise RuntimeError(f"{operation} failed with exit code {completed.returncode}")


def backend_issues(text: str) -> list[str]:
    matches = re.findall(r'backend\s+"s3"\s*\{(.*?)\}', text, re.DOTALL)
    if len(matches) != 1:
        return ["exactly one optional s3 backend block is required"]
    body = matches[0]
    issues: list[str] = []
    if re.search(r"\$\{|\b(?:var|local|module|data|terraform)\.", body):
        issues.append("backend values cannot use Terraform expressions")
    assignments = dict(re.findall(r"(?m)^\s*([A-Za-z][A-Za-z0-9_]*)\s*=\s*(.+?)\s*$", body))
    unexpected = set(assignments) - {"encrypt", "use_lockfile"}
    for field in sorted(unexpected):
        issues.append(f"{field} is not part of the shared static backend contract")
    for field in ("bucket", "key", "region", "profile", "access_key", "secret_key", "token"):
        if field in assignments:
            issues.append(f"{field} belongs in init-time configuration")
    for field in ("encrypt", "use_lockfile"):
        if assignments.get(field) != "true":
            issues.append(f"{field} must remain true")
    return issues


def state_addresses(terraform: str, cwd: Path) -> list[str]:
    completed = run(terraform, cwd, "state", "list", "-no-color")
    require(completed, "state list")
    return sorted(line.strip() for line in completed.stdout.splitlines() if line.strip())


def plan_actions(terraform: str, cwd: Path, plan: Path) -> list[list[str]]:
    shown = run(terraform, cwd, "show", "-json", plan.name)
    require(shown, "show plan")
    data: dict[str, Any] = json.loads(shown.stdout)
    return [item["change"]["actions"] for item in data.get("resource_changes", [])]


def incomplete(messages: list[str]) -> int:
    print(f"{MARKER}: backend or consumer contract is incomplete.")
    for message in messages:
        print(f"  - {message}")
    return 1


def main() -> int:
    terraform = shutil.which("terraform")
    if terraform is None:
        print("Terraform executable was not found.")
        return 2
    try:
        negative = (LAB_DIR / "tests" / "invalid-dynamic-backend.tf.fixture").read_text(encoding="utf-8")
        negative_issues = backend_issues(negative)
        if not any("expressions" in issue for issue in negative_issues) or not any("key" in issue for issue in negative_issues):
            raise RuntimeError("backend checker negative control did not detect both defects")

        issues = backend_issues((LAB_DIR / "starter" / "backend.tf.example").read_text(encoding="utf-8"))
        config = (LAB_DIR / "backend-dev.hcl.example").read_text(encoding="utf-8")
        if set(re.findall(r"(?m)^\s*([A-Za-z][A-Za-z0-9_]*)\s*=", config)) != {"bucket", "key", "region"}:
            raise RuntimeError("backend-dev.hcl.example must contain only bucket, key, and region")
        if "REPLACE_WITH_LAB04_STATE_BUCKET" not in config or re.search(r"access_key|secret_key|token", config):
            raise RuntimeError("backend example is not a safe credential-free placeholder")

        if RUNTIME.exists():
            shutil.rmtree(RUNTIME)
        shutil.copytree(LAB_DIR / "bootstrap" / "producer", PRODUCER)
        shutil.copytree(LAB_DIR / "starter" / "consumer", CONSUMER)
        require(run(terraform, PRODUCER, "init", "-backend=false", "-input=false", "-no-color"), "producer init")
        require(run(terraform, PRODUCER, "apply", "-auto-approve", "-input=false", "-no-color"), "producer apply")
        if state_addresses(terraform, PRODUCER) != ["terraform_data.network_contract"]:
            raise RuntimeError("producer state address is not the protected contract address")

        consumer_source = (LAB_DIR / "starter" / "consumer" / "main.tf").read_text(encoding="utf-8")
        if not re.search(r'data\s+"terraform_remote_state"\s+"[^"]+"', consumer_source):
            issues.append("consumer must declare terraform_remote_state")
        if not re.search(r"data\.[A-Za-z0-9_]+\.[A-Za-z0-9_]+\.outputs", consumer_source):
            issues.append("consumer values must come from producer outputs")

        (CONSUMER / "terraform.auto.tfvars.json").write_text(
            json.dumps({"producer_state_path": str(PRODUCER / "terraform.tfstate")}, indent=2) + "\n",
            encoding="utf-8",
        )
        require(run(terraform, CONSUMER, "init", "-backend=false", "-input=false", "-no-color"), "consumer init")
        require(run(terraform, CONSUMER, "validate", "-no-color"), "consumer validate")
        plan = CONSUMER / "consumer.tfplan"
        require(run(terraform, CONSUMER, "plan", "-input=false", "-no-color", "-out", plan.name), "consumer plan")
        if plan_actions(terraform, CONSUMER, plan) != [["create"]]:
            raise RuntimeError("initial consumer plan must create only its local contract resource")
        require(run(terraform, CONSUMER, "apply", "-input=false", "-no-color", plan.name), "consumer apply")
        if state_addresses(terraform, CONSUMER) != ["data.terraform_remote_state.network", "terraform_data.application_contract"]:
            issues.append("consumer state addresses do not include the expected data source and local contract")
        output = run(terraform, CONSUMER, "output", "-json", "consumed_network")
        require(output, "consumer output")
        if json.loads(output.stdout) != EXPECTED:
            issues.append("consumer output does not exactly match producer state")
        if issues:
            return incomplete(issues)
        final = run(terraform, CONSUMER, "plan", "-input=false", "-no-color", "-detailed-exitcode")
        if final.returncode != 0:
            if final.stdout:
                print(final.stdout.rstrip())
            raise RuntimeError("final consumer plan is not a no-op")
        print("PASS: optional backend keeps only static safety settings; init values remain in the placeholder file.")
        print("PASS: exact producer/consumer addresses and values verified; final consumer plan is no-op.")
        return 0
    except (OSError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"Verification failed: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
