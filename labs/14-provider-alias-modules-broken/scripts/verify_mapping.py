#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parents[1]
SOURCE = LAB_DIR / "starter" / "main.tf"
MARKER = "EXPECTED_MODULE_PROVIDER_MAPPING_INCOMPLETE"


def strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    return re.sub(r"(?m)(?<!:)//.*$|#.*$", "", text)


def braced_body(text: str, opening: re.Pattern[str]) -> str | None:
    match = opening.search(text)
    if match is None:
        return None
    start = text.find("{", match.start())
    depth = 0
    quoted = False
    escaped = False
    for index in range(start, len(text)):
        character = text[index]
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
                return text[start + 1:index]
    return None


def source_issues(source: str) -> list[str]:
    code = strip_comments(source)
    module_body = braced_body(code, re.compile(r'\bmodule\s+"regions"\s*\{'))
    if module_body is None:
        return ['module "regions" must remain present']

    providers_body = braced_body(module_body, re.compile(r"\bproviders\s*=\s*\{"))
    issues: list[str] = []
    if providers_body is None:
        issues.append("module regions must have an explicit providers map")
    else:
        assignments = dict(re.findall(
            r"(?m)^\s*([A-Za-z][A-Za-z0-9_.]*)\s*=\s*([A-Za-z][A-Za-z0-9_.]*)\s*$",
            providers_body,
        ))
        expected = {"aws": "aws", "aws.secondary": "aws.secondary"}
        if assignments != expected:
            issues.append("providers map must pass the matching default and secondary configurations")

    output_body = braced_body(code, re.compile(r'\boutput\s+"module_regions"\s*\{'))
    if output_body is None or re.search(
        r"(?m)^\s*value\s*=\s*module\.regions\.regions\s*$", output_body
    ) is None:
        issues.append("module_regions must delegate to the protected child output")
    return issues


def main() -> int:
    terraform = shutil.which("terraform")
    if terraform is None:
        print("Terraform executable was not found.")
        return 2
    issues = source_issues(SOURCE.read_text(encoding="utf-8"))
    if issues:
        print(f"{MARKER}: root-to-child provider mapping is incomplete.")
        for issue in issues:
            print(f"  - {issue}")
        return 1
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
        print(f"{MARKER}: root-to-child provider mapping is incomplete.")
    else:
        print("Provider mapping source contract passed: both child names receive matching root providers.")
    return test.returncode


if __name__ == "__main__":
    raise SystemExit(main())
