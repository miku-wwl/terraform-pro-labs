#!/usr/bin/env python3
"""Verify Lab 31 partial backend boundaries without contacting S3."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


INIT_TIME_FIELDS = {
    "access_key",
    "assume_role",
    "bucket",
    "dynamodb_table",
    "endpoints",
    "key",
    "kms_key_id",
    "profile",
    "region",
    "secret_key",
    "session_name",
    "shared_credentials_files",
    "token",
}
ALLOWED_STATIC_FIELDS = {"encrypt", "use_lockfile"}
SENSITIVE_FIELDS = {"access_key", "secret_key", "token"}


def mask_comments(text: str) -> str:
    output = list(text)
    index = 0
    state = "normal"
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
    index = opening
    state = "normal"
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
    raise ValueError("unclosed backend block")


def backend_bodies(text: str) -> list[str]:
    masked = mask_comments(text)
    bodies: list[str] = []
    for match in re.finditer(r'\bbackend\s+"s3"\s*\{', masked):
        opening = masked.find("{", match.start())
        closing = matching_brace(text, opening)
        bodies.append(text[opening + 1 : closing])
    return bodies


def assignments(body: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for match in re.finditer(r"(?m)^\s*([A-Za-z][A-Za-z0-9_]*)\s*=\s*(.+?)\s*$", mask_comments(body)):
        result[match.group(1)] = match.group(2).strip()
    return result


def inspect_backend_text(text: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    try:
        bodies = backend_bodies(text)
    except ValueError as exc:
        return [("INVALID_BACKEND_BLOCK", str(exc))]
    if len(bodies) != 1:
        return [("BACKEND_BLOCK_COUNT", f"expected one s3 backend block, found {len(bodies)}")]

    values = assignments(bodies[0])
    for name, value in values.items():
        if re.search(r"\$\{|\b(?:var|local|module|data|terraform)\.", value):
            issues.append(("DYNAMIC_BACKEND_EXPRESSION", f"{name} uses a Terraform expression"))
        if name in INIT_TIME_FIELDS:
            issues.append(("HARDCODED_INIT_PARAMETER", f"{name} belongs in an init-time backend file"))
        elif name not in ALLOWED_STATIC_FIELDS:
            issues.append(("UNAPPROVED_STATIC_PARAMETER", f"{name} is outside this lab's static contract"))

    for required in sorted(ALLOWED_STATIC_FIELDS):
        if values.get(required) != "true":
            issues.append(("STATIC_SAFETY_SETTING", f"{required} must remain true"))
    return issues


def verify_negative_fixtures(tests_dir: Path) -> list[str]:
    failures: list[str] = []
    cases = {
        "invalid-dynamic-backend.tf.fixture": {"DYNAMIC_BACKEND_EXPRESSION", "HARDCODED_INIT_PARAMETER"},
        "invalid-hardcoded-backend.tf.fixture": {"HARDCODED_INIT_PARAMETER"},
    }
    for filename, expected_codes in cases.items():
        path = tests_dir / filename
        if not path.is_file():
            failures.append(f"missing checker fixture: {path}")
            continue
        actual_codes = {code for code, _ in inspect_backend_text(path.read_text(encoding="utf-8"))}
        missing = expected_codes - actual_codes
        if missing:
            failures.append(f"{filename} did not produce: {', '.join(sorted(missing))}")
    return failures


def parse_example(path: Path) -> tuple[dict[str, str], list[str]]:
    text = mask_comments(path.read_text(encoding="utf-8"))
    values: dict[str, str] = {}
    failures: list[str] = []
    for match in re.finditer(r'(?m)^\s*([A-Za-z][A-Za-z0-9_]*)\s*=\s*"([^"\n]*)"\s*$', text):
        name, value = match.groups()
        if name in values:
            failures.append(f"{path.name}: duplicate {name}")
        values[name] = value
    return values, failures


def verify_examples(examples_dir: Path) -> list[str]:
    failures: list[str] = []
    for environment in ("dev", "test", "prod"):
        path = examples_dir / f"backend-{environment}.hcl.example"
        if not path.is_file():
            failures.append(f"missing example: {path.name}")
            continue
        values, parse_failures = parse_example(path)
        failures.extend(parse_failures)
        if set(values) != {"bucket", "key", "region"}:
            failures.append(f"{path.name}: expected only bucket, key, and region")
        expected_bucket = f"REPLACE_WITH_{environment.upper()}_STATE_BUCKET"
        if values.get("bucket") != expected_bucket:
            failures.append(f"{path.name}: bucket must remain the documented non-real placeholder")
        if values.get("key") != f"network/{environment}.tfstate":
            failures.append(f"{path.name}: key does not isolate {environment} state")
        if not re.fullmatch(r"[a-z]{2}(?:-gov)?-[a-z]+-\d", values.get("region", "")):
            failures.append(f"{path.name}: region is not a literal AWS region name")
        if SENSITIVE_FIELDS.intersection(values):
            failures.append(f"{path.name}: credentials are forbidden")
    return failures


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--starter", type=Path, required=True)
    parser.add_argument("--examples", type=Path, required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    fixture_failures = verify_negative_fixtures(args.examples / "tests")
    if fixture_failures:
        print("ERROR: backend checker negative controls failed.", file=sys.stderr)
        for failure in fixture_failures:
            print(f"  - {failure}", file=sys.stderr)
        return 3
    print("PASS: checker rejects dynamic expressions and hardcoded init parameters in negative fixtures.")

    example_failures = verify_examples(args.examples)
    if example_failures:
        print("ERROR: backend examples are invalid.", file=sys.stderr)
        for failure in example_failures:
            print(f"  - {failure}", file=sys.stderr)
        return 3
    print("PASS: dev, test, and prod backend examples are isolated placeholders without credentials.")

    tf_files = sorted(args.starter.glob("*.tf"))
    combined = "\n".join(path.read_text(encoding="utf-8") for path in tf_files)
    issues = inspect_backend_text(combined)
    if issues:
        print("EXPECTED_PARTIAL_BACKEND_INCOMPLETE: static backend boundary is incorrect.")
        for code, message in issues:
            print(f"  - {code}: {message}")
        return 2

    print("PASS: static backend block contains only shared safety settings.")
    print("PASS: environment-specific backend parameters are supplied only by init-time example files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
