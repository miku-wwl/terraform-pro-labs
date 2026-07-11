#!/usr/bin/env python3
"""Evaluate declared Terraform constraints against protected version cases."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parents[1]
CASES = LAB_DIR / "fixtures" / "constraint-cases.json"
MARKER = "EXPECTED_CONSTRAINT_SEMANTICS_INCOMPLETE"


def version(value: str) -> tuple[int, int, int]:
    parts = value.strip().split(".")
    if not 1 <= len(parts) <= 3 or not all(part.isdigit() for part in parts):
        raise ValueError(f"unsupported version {value!r}")
    return tuple((int(part) for part in parts + ["0"] * (3 - len(parts))))  # type: ignore[return-value]


def allows_one(candidate: tuple[int, int, int], expression: str) -> bool:
    match = re.fullmatch(r"(>=|<=|!=|=|>|<|~>)?\s*(\d+(?:\.\d+){0,2})", expression.strip())
    if match is None:
        raise ValueError(f"unsupported constraint component {expression!r}")
    operator = match.group(1) or "="
    raw_target = match.group(2)
    target = version(raw_target)
    if operator == ">=":
        return candidate >= target
    if operator == "<=":
        return candidate <= target
    if operator == ">":
        return candidate > target
    if operator == "<":
        return candidate < target
    if operator == "=":
        return candidate == target
    if operator == "!=":
        return candidate != target
    segments = len(raw_target.split("."))
    upper = (target[0] + 1, 0, 0) if segments <= 2 else (target[0], target[1] + 1, 0)
    return target <= candidate < upper


def allows(candidate: str, constraint: str) -> bool:
    parsed = version(candidate)
    return all(allows_one(parsed, item) for item in constraint.split(","))


def block(text: str, start: int) -> str:
    opening = text.find("{", start)
    if opening < 0:
        raise ValueError("block opening brace not found")
    depth = 0
    for index in range(opening, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[opening + 1:index]
    raise ValueError("unterminated block")


def read_constraint(path: Path, subject: str) -> str:
    text = path.read_text(encoding="utf-8")
    if subject == "required_version":
        match = re.search(r'\brequired_version\s*=\s*"([^"]+)"', text)
    else:
        required = re.search(r"\brequired_providers\s*\{", text)
        if required is None:
            raise ValueError(f"required_providers missing in {path}")
        body = block(text, required.start())
        provider = re.search(rf"\b{re.escape(subject)}\s*=\s*\{{", body)
        if provider is None:
            raise ValueError(f"provider {subject!r} missing in {path}")
        provider_body = block(body, provider.start())
        source = re.search(r'\bsource\s*=\s*"([^"]+)"', provider_body)
        if source is None or source.group(1) != "hashicorp/aws":
            raise ValueError(f"{subject} must retain source hashicorp/aws")
        match = re.search(r'\bversion\s*=\s*"([^"]+)"', provider_body)
    if match is None:
        raise ValueError(f"constraint for {subject!r} missing in {path}")
    return match.group(1)


def main() -> int:
    cases = json.loads(CASES.read_text(encoding="utf-8"))
    failures: list[str] = []
    operators: set[str] = set()
    try:
        for name, case in cases.items():
            constraint = read_constraint(LAB_DIR / case["path"], case["subject"])
            operators.update(re.findall(r">=|!=|(?<![<>!])=|~>", constraint))
            for candidate, expected in case["candidates"].items():
                actual = allows(candidate, constraint)
                if actual != expected:
                    failures.append(f"{name}: {candidate} expected {expected}, got {actual}")
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"Constraint verification error: {exc}")
        return 2
    missing = {">=", "=", "!=", "~>"} - operators
    if missing:
        failures.append(f"required operator coverage missing: {sorted(missing)}")
    if failures:
        print(f"{MARKER}: " + "; ".join(failures))
        return 1
    print("Constraint semantics passed for runtime, bounded, minimum, exact, and excluded versions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
