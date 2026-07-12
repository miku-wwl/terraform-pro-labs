#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parents[1]
SOURCE = LAB_DIR / "starter" / "main.tf"
MARKER = "EXPECTED_SEPARATE_SG_RULES_INCOMPLETE"


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
        print(f"{MARKER}: independent ingress or egress rule behavior is incomplete.")
        return test.returncode
    source = strip_hcl_comments(SOURCE.read_text(encoding="utf-8"))
    if re.search(r'(?m)^\s*(?:ingress|egress)\s*\{', source) or re.search(
        r'(?m)^\s*dynamic\s+"(?:ingress|egress)"\s*\{', source
    ):
        print(f"{MARKER}: inline security-group rules must not be mixed with independent rule resources.")
        return 1
    required_references = (
        ("aws_vpc_security_group_ingress_rule", "web"),
        ("aws_vpc_security_group_egress_rule", "all_ipv4"),
    )
    if any(
        not exact_assignment(resource_body(source, resource_type, name), "security_group_id", "aws_security_group.web.id")
        for resource_type, name in required_references
    ):
        print(f"{MARKER}: both independent rule types must directly reference aws_security_group.web.id.")
        return 1
    if re.search(r'(?m)^\s*data\s+"aws_', source):
        print(f"{MARKER}: live AWS data lookups are not allowed in this deterministic mock lab.")
        return 1
    print("Security-group rule verification passed: independent rule resources are exact.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
