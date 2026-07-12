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
MARKER = "EXPECTED_BACKEND_CROSS_STACK_INCOMPLETE"
SCENARIOS = {
    "primary": {
        "vpc_id": "vpc-lab04-dev",
        "subnet_ids": ["subnet-lab04-a", "subnet-lab04-b"],
        "security_group_id": "sg-lab04-app",
    },
    "alternate": {
        "vpc_id": "vpc-lab04-alternate",
        "subnet_ids": ["subnet-lab04-alt-a", "subnet-lab04-alt-b", "subnet-lab04-alt-c"],
        "security_group_id": "sg-lab04-alternate",
    },
}


def strip_hcl_comments(text: str) -> str:
    result: list[str] = []
    index = 0
    in_string = False
    escaped = False
    while index < len(text):
        character = text[index]
        following = text[index + 1] if index + 1 < len(text) else ""
        if in_string:
            result.append(character)
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
            index += 1
            continue
        if character == '"':
            in_string = True
            result.append(character)
            index += 1
            continue
        if character == "#" or (character == "/" and following == "/"):
            consumed = 2 if character == "/" else 1
            result.extend(" " for _ in range(consumed))
            index += consumed
            while index < len(text) and text[index] not in "\r\n":
                result.append(" ")
                index += 1
            continue
        if character == "/" and following == "*":
            result.extend((" ", " "))
            index += 2
            while index < len(text):
                if index + 1 < len(text) and text[index:index + 2] == "*/":
                    result.extend((" ", " "))
                    index += 2
                    break
                result.append(text[index] if text[index] in "\r\n" else " ")
                index += 1
            continue
        result.append(character)
        index += 1
    return "".join(result)


def run(terraform: str, cwd: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([terraform, *arguments], cwd=cwd, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


def require(completed: subprocess.CompletedProcess[str], operation: str) -> None:
    if completed.returncode:
        if completed.stdout:
            print(completed.stdout.rstrip())
        raise RuntimeError(f"{operation} failed with exit code {completed.returncode}")


def backend_issues(text: str) -> list[str]:
    text = strip_hcl_comments(text)
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


def output_json(terraform: str, cwd: Path, name: str) -> Any:
    completed = run(terraform, cwd, "output", "-json", name)
    require(completed, f"output {name}")
    return json.loads(completed.stdout)


def verify_scenario(terraform: str, name: str, expected: dict[str, Any]) -> list[str]:
    scenario = RUNTIME / name
    producer = scenario / "producer"
    consumer = scenario / "consumer"
    shutil.copytree(LAB_DIR / "bootstrap" / "producer", producer)
    shutil.copytree(LAB_DIR / "starter" / "consumer", consumer)
    (producer / "terraform.auto.tfvars.json").write_text(
        json.dumps({"network": expected}, indent=2) + "\n",
        encoding="utf-8",
    )

    require(run(terraform, producer, "init", "-backend=false", "-input=false", "-no-color"), f"{name} producer init")
    require(run(terraform, producer, "apply", "-auto-approve", "-input=false", "-no-color"), f"{name} producer apply")
    if state_addresses(terraform, producer) != ["terraform_data.network_contract"]:
        raise RuntimeError(f"{name} producer state address is not the protected contract address")
    producer_output = output_json(terraform, producer, "network")
    if producer_output != expected:
        raise RuntimeError(f"{name} producer output differs from its supplied fixture")

    (consumer / "terraform.auto.tfvars.json").write_text(
        json.dumps({"producer_state_path": str(producer / "terraform.tfstate")}, indent=2) + "\n",
        encoding="utf-8",
    )
    require(run(terraform, consumer, "init", "-backend=false", "-input=false", "-no-color"), f"{name} consumer init")
    require(run(terraform, consumer, "validate", "-no-color"), f"{name} consumer validate")
    plan = consumer / "consumer.tfplan"
    require(run(terraform, consumer, "plan", "-input=false", "-no-color", "-out", plan.name), f"{name} consumer plan")
    if plan_actions(terraform, consumer, plan) != [["create"]]:
        raise RuntimeError(f"{name} initial consumer plan must create only its local contract resource")
    require(run(terraform, consumer, "apply", "-input=false", "-no-color", plan.name), f"{name} consumer apply")

    issues: list[str] = []
    expected_addresses = ["data.terraform_remote_state.network", "terraform_data.application_contract"]
    if state_addresses(terraform, consumer) != expected_addresses:
        issues.append(f"{name} consumer state does not contain the exact remote-state and contract addresses")
    consumed = output_json(terraform, consumer, "consumed_network")
    if consumed != producer_output:
        issues.append(f"{name} consumer output does not exactly follow its producer state")

    final = run(terraform, consumer, "plan", "-input=false", "-no-color", "-detailed-exitcode")
    if final.returncode != 0:
        if final.stdout:
            print(final.stdout.rstrip())
        raise RuntimeError(f"{name} final consumer plan is not a no-op")
    return issues


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

        consumer_source = strip_hcl_comments(
            (LAB_DIR / "starter" / "consumer" / "main.tf").read_text(encoding="utf-8")
        )
        if not re.search(r'data\s+"terraform_remote_state"\s+"[^"]+"', consumer_source):
            issues.append("consumer must declare terraform_remote_state")
        if not re.search(r"data\.[A-Za-z0-9_]+\.[A-Za-z0-9_]+\.outputs", consumer_source):
            issues.append("consumer values must come from producer outputs")

        if RUNTIME.exists():
            shutil.rmtree(RUNTIME)
        for name, expected in SCENARIOS.items():
            issues.extend(verify_scenario(terraform, name, expected))
        if issues:
            return incomplete(issues)
        print("PASS: optional backend keeps only static safety settings; init values remain in the placeholder file.")
        print("PASS: two distinct producer states flowed through exact consumer addresses and values; both final plans are no-op.")
        return 0
    except (OSError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"Verification failed: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
