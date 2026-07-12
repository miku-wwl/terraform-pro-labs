#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parents[1]
SOURCE = LAB_DIR / "starter" / "main.tf"
MARKER = "EXPECTED_NESTED_COLLECTION_TRANSFORM_INCOMPLETE"


def mask_comments_and_strings(text: str) -> str:
    """Return HCL-shaped text with comments and quoted string contents masked."""

    output = list(text)
    state = "normal"
    index = 0
    while index < len(text):
        char = text[index]
        next_char = text[index + 1] if index + 1 < len(text) else ""
        if state == "normal":
            if char == '"':
                output[index] = " "
                state = "string"
            elif char == "#":
                output[index] = " "
                state = "line_comment"
            elif char == "/" and next_char == "/":
                output[index] = output[index + 1] = " "
                index += 1
                state = "line_comment"
            elif char == "/" and next_char == "*":
                output[index] = output[index + 1] = " "
                index += 1
                state = "block_comment"
        elif state == "string":
            if char == "\\":
                output[index] = " "
                if index + 1 < len(text):
                    output[index + 1] = " "
                    index += 1
            else:
                output[index] = "\n" if char == "\n" else " "
                if char == '"':
                    state = "normal"
        elif state == "line_comment":
            if char == "\n":
                state = "normal"
            else:
                output[index] = " "
        elif state == "block_comment":
            if char == "*" and next_char == "/":
                output[index] = output[index + 1] = " "
                index += 1
                state = "normal"
            elif char != "\n":
                output[index] = " "
        index += 1
    return "".join(output)


def target_call_counts(text: str) -> tuple[int, int]:
    executable = mask_comments_and_strings(text)
    return (
        len(re.findall(r"\bflatten\s*\(", executable)),
        len(re.findall(r"\bmerge\s*\(", executable)),
    )


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
        print(f"{MARKER}: nested rows, stable keys, or merged tag precedence is incomplete.")
        return test.returncode
    negative_control = '# flatten([[]])\nvalue = "merge("\n// merge({}, {})\n'
    if target_call_counts(negative_control) != (0, 0):
        print("Protected source checker failed its comment/string negative control.")
        return 2
    source = SOURCE.read_text(encoding="utf-8")
    flatten_count, merge_count = target_call_counts(source)
    if flatten_count != 1 or merge_count != 1:
        print(f"{MARKER}: use the target flatten and layered merge constructs exactly once.")
        return 1
    print("Nested collection verification passed: behavior and target constructs are correct.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
