#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parents[1]
SOURCE = LAB_DIR / "starter" / "main.tf"
MARKER = "EXPECTED_CONDITIONAL_READ_INCOMPLETE"


def strip_comments(text: str) -> str:
    """Remove HCL comments without treating comment markers inside strings as comments."""
    result: list[str] = []
    index = 0
    quoted = False
    escaped = False
    while index < len(text):
        character = text[index]
        following = text[index + 1] if index + 1 < len(text) else ""
        if quoted:
            result.append(character)
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                quoted = False
            index += 1
            continue
        if character == '"':
            quoted = True
            result.append(character)
            index += 1
            continue
        if character == "#" or (character == "/" and following == "/"):
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
                result.append("\n" if text[index] == "\n" else " ")
                index += 1
            continue
        result.append(character)
        index += 1
    return "".join(result)


def mask_quoted_strings(text: str) -> str:
    """Mask quoted strings so source-contract tokens must occur in executable HCL."""
    result: list[str] = []
    quoted = False
    escaped = False
    for character in text:
        if quoted:
            result.append("\n" if character == "\n" else " ")
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                quoted = False
            continue
        if character == '"':
            quoted = True
            result.append(" ")
        else:
            result.append(character)
    return "".join(result)


def output_body(source: str, name: str) -> str | None:
    code = strip_comments(source)
    match = re.search(rf'\boutput\s+"{re.escape(name)}"\s*\{{', code)
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


def source_issues(source: str) -> list[str]:
    selected_name = output_body(source, "selected_name")
    selected_owner = output_body(source, "selected_owner")
    issues: list[str] = []
    name_code = mask_quoted_strings(selected_name) if selected_name is not None else ""
    owner_code = mask_quoted_strings(selected_owner) if selected_owner is not None else ""
    if not re.search(
        r"\bvalue\s*=\s*one\s*\(\s*terraform_data\.marker\s*\[\s*\*\s*\]"
        r"\s*\.input\.name\s*\)",
        name_code,
    ):
        issues.append("selected_name must use one() with the marker name splat")
    if not re.search(
        r"\bvalue\s*=\s*try\s*\(\s*terraform_data\.marker\s*\[\s*0\s*\]"
        r"\s*\.input\.owner\s*,\s*null\s*\)",
        owner_code,
    ):
        issues.append("selected_owner must use try() around the potentially invalid owner index with null fallback")
    return issues


def verify_string_decoy_control() -> None:
    decoy = '''
output "selected_name" {
  value       = terraform_data.marker[0].input.name
  description = "one(terraform_data.marker[*].input.name)"
}
output "selected_owner" {
  value       = terraform_data.marker[0].input.owner
  description = "try(terraform_data.marker[0].input.owner, null)"
}
'''
    if len(source_issues(decoy)) != 2:
        raise RuntimeError("quoted-string negative control did not detect both unsafe output expressions")


def main() -> int:
    try:
        verify_string_decoy_control()
    except RuntimeError as exc:
        print(f"Verifier self-check failed: {exc}")
        return 2
    terraform = shutil.which("terraform")
    if terraform is None:
        print("Terraform executable was not found.")
        return 2
    init = subprocess.run(
        [terraform, "init", "-backend=false", "-input=false", "-test-directory=tests", "-no-color"],
        cwd=LAB_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if init.returncode:
        print(init.stdout.rstrip())
        return init.returncode
    test = subprocess.run(
        [terraform, "test", "-test-directory=tests", "-no-color"],
        cwd=LAB_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    print(test.stdout.rstrip())
    issues = source_issues(SOURCE.read_text(encoding="utf-8"))
    if test.returncode or issues:
        for issue in issues:
            print(f"Required source contract is incomplete: {issue}.")
        print(f"{MARKER}: the zero-or-one reads are not both safe and explicit.")
        return 1
    print("Safe-read source contract passed: executable one() and try() expressions are bound to their required outputs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
