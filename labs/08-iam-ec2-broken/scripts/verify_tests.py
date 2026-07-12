#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parents[1]
MARKER = "EXPECTED_IAM_EC2_CHAIN_INCOMPLETE"


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


def resource_body(text: str, resource_type: str, name: str) -> str | None:
    match = re.search(
        rf'(?m)^\s*resource\s+"{re.escape(resource_type)}"\s+"{re.escape(name)}"\s*\{{',
        text,
    )
    if match is None:
        return None
    opening = match.end() - 1
    depth = 0
    in_string = False
    escaped = False
    for index in range(opening, len(text)):
        character = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
            continue
        if character == '"':
            in_string = True
        elif character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth == 0:
                return text[opening + 1:index]
    return None


def exact_assignment(body: str | None, key: str, value: str) -> bool:
    if body is None:
        return False
    match = re.search(rf'(?m)^\s*{re.escape(key)}\s*=\s*([^\n#]+)', body)
    return match is not None and match.group(1).strip() == value


def reference_issues(source: str) -> list[str]:
    source = strip_hcl_comments(source)
    issues: list[str] = []
    required = (
        ("aws_iam_role_policy_attachment", "app", "role", "aws_iam_role.app.name"),
        ("aws_iam_role_policy_attachment", "app", "policy_arn", "aws_iam_policy.app.arn"),
        ("aws_iam_instance_profile", "app", "role", "aws_iam_role.app.name"),
        ("aws_instance", "app", "iam_instance_profile", "aws_iam_instance_profile.app.name"),
    )
    for resource_type, name, argument, reference in required:
        if not exact_assignment(resource_body(source, resource_type, name), argument, reference):
            issues.append(f"{resource_type}.{name}.{argument} must directly reference {reference}")
    if re.search(r'(?m)^\s*data\s+"aws_', source):
        issues.append("AWS data lookups are not allowed in this deterministic mock lab")
    if re.search(r'(?m)^\s*(?:profile|access_key|secret_key|token)\s*=', source):
        issues.append("credential values must not be configured in learner source")
    return issues


def main() -> int:
    terraform = shutil.which("terraform")
    if terraform is None:
        print("Terraform executable was not found.")
        return 2
    init = subprocess.run(
        [terraform, "init", "-backend=false", "-input=false", "-test-directory=tests", "-no-color"],
        cwd=LAB_DIR, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False
    )
    if init.returncode:
        print(init.stdout.rstrip())
        return init.returncode
    test = subprocess.run(
        [terraform, "test", "-test-directory=tests", "-no-color"],
        cwd=LAB_DIR, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False
    )
    print(test.stdout.rstrip())
    if test.returncode:
        print(f"{MARKER}: the IAM trust, permission, attachment, profile, and EC2 chain is incomplete.")
        return test.returncode

    source = (LAB_DIR / "starter" / "main.tf").read_text(encoding="utf-8")
    issues = reference_issues(source)
    if issues:
        print(f"{MARKER}: value equality is insufficient; the required Terraform graph references are incomplete.")
        for issue in issues:
            print(f"  - {issue}")
        return 1
    print("IAM/EC2 verification passed: exact policies, values, and direct graph references are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
