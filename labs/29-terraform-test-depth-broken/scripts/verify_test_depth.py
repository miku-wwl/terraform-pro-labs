#!/usr/bin/env python3
"""Run the learner-authored suite and require meaningful sequential state coverage."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parents[1]
STARTER = LAB_DIR / "starter"
TEST_FILE = STARTER / "tests" / "release_flow.tftest.hcl"
MARKER = "EXPECTED_SEQUENTIAL_TEST_FLOW_INCOMPLETE"


def mask_comments(text: str) -> str:
    output = list(text)
    state = "normal"
    index = 0
    while index < len(text):
        char = text[index]
        next_char = text[index + 1] if index + 1 < len(text) else ""
        if state == "normal":
            if char == '"':
                state = "string"
            elif char == "#":
                output[index] = " "
                state = "line"
            elif char == "/" and next_char == "/":
                output[index] = output[index + 1] = " "
                index += 1
                state = "line"
            elif char == "/" and next_char == "*":
                output[index] = output[index + 1] = " "
                index += 1
                state = "block"
        elif state == "string":
            if char == "\\":
                index += 1
            elif char == '"':
                state = "normal"
        elif state == "line":
            if char == "\n":
                state = "normal"
            else:
                output[index] = " "
        elif state == "block":
            if char == "*" and next_char == "/":
                output[index] = output[index + 1] = " "
                index += 1
                state = "normal"
            elif char != "\n":
                output[index] = " "
        index += 1
    return "".join(output)


def matching_brace(text: str, opening: int) -> int:
    depth = 0
    state = "normal"
    index = opening
    while index < len(text):
        char = text[index]
        next_char = text[index + 1] if index + 1 < len(text) else ""
        if state == "normal":
            if char == '"':
                state = "string"
            elif char == "#":
                state = "line"
            elif char == "/" and next_char == "/":
                index += 1
                state = "line"
            elif char == "/" and next_char == "*":
                index += 1
                state = "block"
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return index
        elif state == "string":
            if char == "\\":
                index += 1
            elif char == '"':
                state = "normal"
        elif state == "line" and char == "\n":
            state = "normal"
        elif state == "block" and char == "*" and next_char == "/":
            index += 1
            state = "normal"
        index += 1
    raise ValueError("unclosed test block")


def extract_blocks(text: str, pattern: str) -> list[tuple[str, str]]:
    masked = mask_comments(text)
    blocks: list[tuple[str, str]] = []
    for match in re.finditer(pattern, masked):
        opening = masked.find("{", match.start())
        closing = matching_brace(text, opening)
        blocks.append((match.group(1) if match.lastindex else "", text[opening + 1:closing]))
    return blocks


def assertion_conditions(run_body: str) -> str:
    conditions: list[str] = []
    for _, assertion in extract_blocks(run_body, r"(?m)^\s*(assert)\s*\{"):
        masked = mask_comments(assertion)
        match = re.search(r"\bcondition\s*=\s*(.*?)\berror_message\s*=", masked, re.DOTALL)
        if match:
            conditions.append(match.group(1))
    return " ".join(" ".join(value.split()) for value in conditions)


def assignment(body: str, name: str) -> str:
    match = re.search(rf'\b{re.escape(name)}\s*=\s*"([^"\n]+)"', mask_comments(body))
    return "" if match is None else match.group(1)


def command(body: str) -> str:
    match = re.search(r"\bcommand\s*=\s*(apply|plan)\b", mask_comments(body))
    return "" if match is None else match.group(1)


def exact_deployment(conditions: str, service: str, release: str) -> bool:
    return bool(
        re.search(rf'\boutput\.deployment\.service\s*==\s*"{re.escape(service)}"', conditions)
        and re.search(rf'\boutput\.deployment\.release\s*==\s*"{re.escape(release)}"', conditions)
    )


def compares_ids(conditions: str, left: str, operator: str, right: str) -> bool:
    escaped_left = re.escape(left)
    escaped_right = re.escape(right)
    escaped_operator = re.escape(operator)
    return bool(re.search(
        rf"(?:{escaped_left}\s*{escaped_operator}\s*{escaped_right}|"
        rf"{escaped_right}\s*{escaped_operator}\s*{escaped_left})",
        conditions,
    ))


def main() -> int:
    terraform = shutil.which("terraform")
    if terraform is None:
        print("Terraform executable was not found.")
        return 2
    if command('variables { release_version = "v2" }') != "":
        print("Protected run-role checker failed its omitted-command negative control.")
        return 2
    initialized = subprocess.run(
        [terraform, "init", "-backend=false", "-input=false", "-no-color"],
        cwd=STARTER, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False
    )
    print(initialized.stdout.rstrip())
    if initialized.returncode:
        return initialized.returncode
    tested = subprocess.run(
        [terraform, "test", "-no-color"], cwd=STARTER, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False
    )
    print(tested.stdout.rstrip())
    if tested.returncode:
        print(f"{MARKER}: the authored sequential Terraform Test suite does not pass.")
        return tested.returncode

    source = TEST_FILE.read_text(encoding="utf-8")
    try:
        runs = extract_blocks(source, r'(?m)^\s*run\s+"([A-Za-z0-9_-]+)"\s*\{')
    except ValueError as exc:
        print(f"{MARKER}: cannot inspect run responsibilities: {exc}.")
        return 1
    if len(runs) != 4:
        print(f"{MARKER}: expected exactly four ordered run blocks, found {len(runs)}.")
        return 1

    (setup_name, setup), (upgrade_name, upgrade), (_, steady), (_, invalid) = runs
    setup_conditions = assertion_conditions(setup)
    upgrade_conditions = assertion_conditions(upgrade)
    steady_conditions = assertion_conditions(steady)
    expected_failure = re.search(
        r"\bexpect_failures\s*=\s*\[[^\]]*\bvar\.release_version\b[^\]]*\]",
        mask_comments(invalid), re.DOTALL,
    ) is not None
    responsibilities = {
        "setup applies v1 and checks the exact deployment output": (
            command(setup) == "apply"
            and assignment(setup, "service_name") == "checkout"
            and assignment(setup, "release_version") == "v1"
            and exact_deployment(setup_conditions, "checkout", "v1")
        ),
        "upgrade applies v2 and proves replacement identity": (
            command(upgrade) == "apply"
            and assignment(upgrade, "service_name") == "checkout"
            and assignment(upgrade, "release_version") == "v2"
            and exact_deployment(upgrade_conditions, "checkout", "v2")
            and compares_ids(
                upgrade_conditions,
                "output.deployment_id",
                "!=",
                f"run.{setup_name}.deployment_id",
            )
        ),
        "steady plan keeps the upgraded v2 identity": (
            command(steady) == "plan"
            and assignment(steady, "service_name") == "checkout"
            and assignment(steady, "release_version") == "v2"
            and exact_deployment(steady_conditions, "checkout", "v2")
            and compares_ids(
                steady_conditions,
                "output.deployment_id",
                "==",
                f"run.{upgrade_name}.deployment_id",
            )
        ),
        "invalid latest is attributed to release_version": (
            command(invalid) == "plan"
            and assignment(invalid, "release_version") == "latest"
            and expected_failure
        ),
    }
    missing = [description for description, present in responsibilities.items() if not present]
    if missing:
        print(f"{MARKER}: run responsibilities are incomplete.")
        for description in missing:
            print(f"  - {description}")
        return 1
    if "4 passed, 0 failed" not in tested.stdout:
        print(f"{MARKER}: the suite must contain exactly four passing run scenarios.")
        return 1
    print("Sequential Terraform Test verification passed: setup, replacement, steady state, and failure coverage are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
