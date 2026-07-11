#!/usr/bin/env python3
"""Verify Lab 12 remote-state consumption and backend separation."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any


LAB_DIR = Path(__file__).resolve().parents[1]
RUNTIME = LAB_DIR / ".lab-state"
MARKER = "EXPECTED_REMOTE_STATE_CONSUMER_INCOMPLETE"
ENVIRONMENTS = ("dev", "prod")


def run(terraform: str, cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([terraform, *args], cwd=cwd, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


def require(result: subprocess.CompletedProcess[str], operation: str) -> None:
    if result.returncode:
        if result.stdout:
            print(result.stdout.rstrip())
        raise RuntimeError(f"{operation} failed with exit code {result.returncode}")


def addresses(terraform: str, cwd: Path) -> list[str]:
    result = run(terraform, cwd, "state", "list", "-no-color")
    require(result, "state list")
    return sorted(line.strip() for line in result.stdout.splitlines() if line.strip())


def plan_actions(terraform: str, cwd: Path, plan_name: str) -> list[list[str]]:
    shown = run(terraform, cwd, "show", "-json", plan_name)
    require(shown, "show plan")
    data: dict[str, Any] = json.loads(shown.stdout)
    return [item["change"]["actions"] for item in data.get("resource_changes", [])]


def backend_issues(text: str) -> list[str]:
    matches = re.findall(r'backend\s+"s3"\s*\{(.*?)\}', text, re.DOTALL)
    if len(matches) != 1:
        return ["exactly one S3 backend block is required"]
    body = matches[0]
    issues: list[str] = []
    if re.search(r"\$\{|(?<![A-Za-z0-9_\"/.-])(?:var|local|module|data|terraform)\.", body):
        issues.append("backend values cannot use Terraform expressions")
    assignments = dict(re.findall(r"(?m)^\s*([A-Za-z][A-Za-z0-9_]*)\s*=\s*(.+?)\s*$", body))
    if set(assignments) != {"encrypt", "use_lockfile"}:
        issues.append("only shared static safety settings belong in backend.tf.example")
    if assignments.get("encrypt") != "true" or assignments.get("use_lockfile") != "true":
        issues.append("backend encryption and S3 lockfile settings must remain enabled")
    return issues


def incomplete(issues: list[str]) -> int:
    print(f"{MARKER}: consumer or backend separation is incomplete.")
    for issue in issues:
        print(f"  - {issue}")
    return 1


def main() -> int:
    terraform = shutil.which("terraform")
    if terraform is None:
        print("Terraform executable was not found.")
        return 2
    try:
        negative = (LAB_DIR / "tests" / "invalid-mixed-backend.tf.fixture").read_text(encoding="utf-8")
        detected = backend_issues(negative)
        if not any("expressions" in issue for issue in detected):
            raise RuntimeError("backend negative control did not detect an expression")
        issues = backend_issues((LAB_DIR / "starter" / "backend.tf.example").read_text(encoding="utf-8"))
        source = (LAB_DIR / "starter" / "main.tf").read_text(encoding="utf-8")
        if not re.search(r'data\s+"terraform_remote_state"\s+"[^\"]+"', source):
            issues.append("consumer must declare terraform_remote_state")
        if not re.search(r"data\.[A-Za-z0-9_]+\.[A-Za-z0-9_]+\.outputs", source):
            issues.append("consumer values must be derived from producer outputs")
        for example in ("backend-dev.hcl.example", "backend-prod.hcl.example"):
            text = (LAB_DIR / example).read_text(encoding="utf-8")
            fields = set(re.findall(r"(?m)^\s*([A-Za-z][A-Za-z0-9_]*)\s*=", text))
            if fields != {"bucket", "key", "region"} or re.search(r"access_key|secret_key|token", text):
                raise RuntimeError(f"{example} is not a safe init-time backend example")

        if RUNTIME.exists():
            shutil.rmtree(RUNTIME)
        for environment in ENVIRONMENTS:
            producer = RUNTIME / f"producer-{environment}"
            consumer = RUNTIME / f"consumer-{environment}"
            shutil.copytree(LAB_DIR / "bootstrap" / "producer", producer)
            shutil.copytree(LAB_DIR / "starter", consumer)
            require(run(terraform, producer, "init", "-backend=false", "-input=false", "-no-color"), "producer init")
            require(run(terraform, producer, "apply", "-auto-approve", "-input=false", "-no-color",
                        "-var", f"environment={environment}"), "producer apply")
            if addresses(terraform, producer) != ["terraform_data.network"]:
                raise RuntimeError(f"{environment} producer state address is incorrect")
            (consumer / "terraform.auto.tfvars.json").write_text(json.dumps({
                "producer_state_path": str(producer / "terraform.tfstate"),
                "consumer_name": f"payments-{environment}",
            }, indent=2) + "\n", encoding="utf-8")
            require(run(terraform, consumer, "init", "-backend=false", "-input=false", "-no-color"), "consumer init")
            require(run(terraform, consumer, "validate", "-no-color"), "consumer validate")
            require(run(terraform, consumer, "plan", "-input=false", "-no-color", "-out", "consumer.tfplan"), "consumer plan")
            if plan_actions(terraform, consumer, "consumer.tfplan") != [["create"]]:
                raise RuntimeError("initial consumer plan must create only its own contract resource")
            require(run(terraform, consumer, "apply", "-input=false", "-no-color", "consumer.tfplan"), "consumer apply")
            expected_addresses = ["data.terraform_remote_state.network", "terraform_data.consumer_contract"]
            if addresses(terraform, consumer) != expected_addresses:
                issues.append(f"{environment} consumer state boundary is incorrect")
            output = run(terraform, consumer, "output", "-json", "consumed_network")
            require(output, "consumer output")
            expected = {
                "environment": environment,
                "vpc_id": f"vpc-lab12-{environment}",
                "subnet_ids": [f"subnet-lab12-{environment}-a", f"subnet-lab12-{environment}-b"],
            }
            if json.loads(output.stdout) != expected:
                issues.append(f"{environment} consumer did not select the caller-provided producer state")
            final = run(terraform, consumer, "plan", "-input=false", "-no-color", "-detailed-exitcode")
            if final.returncode != 0:
                raise RuntimeError(f"{environment} final consumer plan was not no-op")
        if issues:
            return incomplete(issues)
        print("PASS: dev and prod consumers used the selected producer state and exact state boundaries.")
        print("PASS: initial actions were local creates; both final plans were no-op; backend inputs stayed separate.")
        return 0
    except (OSError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"Verification failed: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
