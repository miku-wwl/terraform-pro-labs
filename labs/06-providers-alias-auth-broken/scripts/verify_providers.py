#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parents[1]
STARTER = LAB_DIR / "starter"
MARKER = "EXPECTED_PROVIDER_ALIAS_AUTH_INCOMPLETE"
PINNED_AUTH_FIELDS = {
    "profile",
    "access_key",
    "secret_key",
    "token",
    "shared_credentials_files",
    "shared_config_files",
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
            if character == "/":
                result.extend((" ", " "))
                index += 2
            else:
                result.append(" ")
                index += 1
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


def extract_blocks(text: str, pattern: str) -> list[tuple[tuple[str, ...], str]]:
    blocks: list[tuple[tuple[str, ...], str]] = []
    for match in re.finditer(pattern, text, re.MULTILINE):
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
                    blocks.append((match.groups(), text[opening + 1:index]))
                    break
        else:
            raise ValueError("unterminated HCL block")
    return blocks


def assignments(body: str) -> dict[str, str]:
    return {
        key: value.strip()
        for key, value in re.findall(
            r"(?m)^\s*([A-Za-z][A-Za-z0-9_]*)\s*=\s*([^\n#]+)", body
        )
    }


def source_issues(text: str) -> list[str]:
    text = strip_hcl_comments(text)
    issues: list[str] = []
    providers = extract_blocks(text, r'^\s*provider\s+"([^"]+)"\s*\{')
    aws_providers = [assignments(body) for labels, body in providers if labels == ("aws",)]
    if len(aws_providers) != 2:
        issues.append("exactly two aws provider configurations are required")
    else:
        default = [item for item in aws_providers if "alias" not in item]
        secondary = [item for item in aws_providers if item.get("alias") == '"secondary"']
        if len(default) != 1 or default[0].get("region") != '"us-east-1"':
            issues.append("the default aws provider must remain in us-east-1 with no alias")
        if len(secondary) != 1 or secondary[0].get("region") != '"us-west-2"':
            issues.append("aws.secondary must remain the us-west-2 provider configuration")
        if any("alias" in item and item.get("alias") != '"secondary"' for item in aws_providers):
            issues.append("no provider alias other than secondary is allowed")

    for labels, body in providers:
        if labels != ("aws",):
            continue
        configured = assignments(body)
        forbidden = sorted(
            key for key in configured
            if key in PINNED_AUTH_FIELDS or key.startswith("skip_")
        )
        if forbidden:
            issues.append(f"provider configuration pins or bypasses authentication fields: {', '.join(forbidden)}")
        if re.search(r'(?m)^\s*assume_role(?:_with_web_identity)?\s*\{', body):
            issues.append("provider configuration must not add a pinned assume-role authentication block")

    data_blocks = extract_blocks(text, r'^\s*data\s+"([^"]+)"\s+"([^"]+)"\s*\{')
    regions = {
        labels[1]: assignments(body)
        for labels, body in data_blocks
        if labels[0] == "aws_region"
    }
    if set(regions) != {"primary", "secondary"}:
        issues.append("exactly the primary and secondary aws_region data sources are required")
    else:
        primary_provider = regions["primary"].get("provider")
        if primary_provider not in (None, "aws"):
            issues.append("aws_region.primary must use the default aws provider")
        if regions["secondary"].get("provider") != "aws.secondary":
            issues.append("aws_region.secondary must explicitly use aws.secondary")
    return issues


def required_provider_ok(text: str) -> bool:
    text = strip_hcl_comments(text)
    return (
        re.search(r'source\s*=\s*"hashicorp/aws"', text) is not None
        and re.search(r'version\s*=\s*"~> 6\.0"', text) is not None
    )


def verify_comment_controls() -> None:
    source = '''
# provider "aws" { region = "comment-decoy" }
provider "aws" {
  region = "us-east-1"
  // skip_credentials_validation = true
}
provider "aws" {
  alias  = "secondary"
  region = "us-west-2"
  /* profile = "comment-decoy" */
}
data "aws_region" "primary" {}
data "aws_region" "secondary" { provider = aws.secondary }
'''
    if source_issues(source):
        raise RuntimeError("provider source checker treated commented decoys as live configuration")
    commented_requirement = '/* source = "hashicorp/aws"\nversion = "~> 6.0" */\n'
    if required_provider_ok(commented_requirement):
        raise RuntimeError("required-provider checker accepted commented source/version decoys")


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
        print(f"{MARKER}: provider alias selection is incomplete.")
        return test.returncode

    try:
        verify_comment_controls()
    except RuntimeError as exc:
        print(f"Provider verifier negative control failed: {exc}")
        return 2

    versions = (STARTER / "versions.tf").read_text(encoding="utf-8")
    main = (STARTER / "main.tf").read_text(encoding="utf-8")
    issues = source_issues(main)
    if not required_provider_ok(versions):
        issues.append("required_providers must retain hashicorp/aws with the ~> 6.0 constraint")
    if issues:
        print(
            f"{MARKER}: provider regions, alias routing, or the portable authentication boundary is incomplete."
        )
        for issue in issues:
            print(f"  - {issue}")
        return 1
    print("Provider verification passed: exact regions, alias routing, requirements, and auth boundary are correct.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
