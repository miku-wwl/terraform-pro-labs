#!/usr/bin/env python3
"""Score Lab 25 decisions without requiring exact rationale prose."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
import sys
from pathlib import Path
from typing import Any


EXPECTED_SELECTION_DIGESTS = {
    "routine_run_workflow": "31ad1810a14263d63b10d89dee9be34bb9342920af96ad2c8001f3f7ee327810",
    "api_run_boundary": "21887ad8850c219914ff916a900ab74cc013bdd9eca001e1ce08a96ea4de74ec",
    "pull_request_feedback": "cc12cf71dc91b716059408f810d62a5d30c45a453d42d1d374561ede97ff5735",
    "workspace_dependency": "723873bd05726a4ee21ccf646a4d8d1deb4468a5276abb0810ba08a6fb7f66d3",
    "production_policy": "f141d4d36d1eddb6648adfb41e182bdafa29ada95ebfd75807b79d4ad90c64a1",
    "cost_estimation": "75e57c34268afef0c7a976c9f1b1c6eab5d5e908ccf837987c1b19292b5dee07",
    "team_permissions": "1cfd3069390b03d8383e400bd3b7eeea2dc7c2f14ad1e1935cd6d198b42e8d11",
    "production_auto_apply": "0b78d1fa97141b5992799f3b7d079e6ddd086d5bd3c3b2ffc723c1537b7ae2a7",
}

PLACEHOLDER_PHRASES = (
    "replace this",
    "todo",
    "tbd",
)


class ScoringError(ValueError):
    """Raised for malformed rubric or answer artifacts."""


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ScoringError(f"cannot read JSON-compatible rubric {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ScoringError("rubric root must be a mapping")
    return value


def parse_answer(path: Path) -> tuple[dict[str, str], dict[str, str]]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ScoringError(f"cannot read answer {path}: {exc}") from exc

    decisions = {
        match.group(1): match.group(2)
        for match in re.finditer(r"(?m)^-\s+([a-z][a-z0-9_]*):\s*([a-z][a-z0-9_]*)\s*$", text)
    }

    rationales: dict[str, str] = {}
    headings = list(re.finditer(r"(?m)^###\s+([a-z][a-z0-9_]*)\s*$", text))
    for index, heading in enumerate(headings):
        start = heading.end()
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        rationales[heading.group(1)] = text[start:end].strip()
    return decisions, rationales


def selection_digest(decision_id: str, selection: str) -> str:
    payload = f"lab25-evaluation-v1|{decision_id}|{selection}".encode()
    return hashlib.sha256(payload).hexdigest()


def rationale_is_substantive(text: str, minimum_words: int) -> bool:
    normalized = " ".join(text.lower().split())
    if normalized.startswith("explain ") or any(phrase in normalized for phrase in PLACEHOLDER_PHRASES):
        return False
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9'-]*", text)
    return len(words) >= minimum_words


def score(rubric: dict[str, Any], decisions: dict[str, str], rationales: dict[str, str]) -> tuple[int, list[str]]:
    model = rubric.get("scoring_model")
    dimensions = rubric.get("dimensions")
    if not isinstance(model, dict) or not isinstance(dimensions, list):
        raise ScoringError("rubric must define scoring_model and dimensions")

    ids = [item.get("id") for item in dimensions if isinstance(item, dict)]
    if len(ids) != len(dimensions) or any(not isinstance(item, str) for item in ids):
        raise ScoringError("every rubric dimension must have a string id")
    if set(ids) != set(EXPECTED_SELECTION_DIGESTS):
        raise ScoringError("rubric dimensions do not match the protected decision set")

    choice_points = int(model["correct_choice_points_per_decision"])
    rationale_points = int(model["substantive_rationale_points_per_decision"])
    bonus = int(model["complete_response_bonus"])
    minimum_words = int(model["minimum_rationale_words"])

    total = 0
    incomplete: list[str] = []
    all_rationales_complete = True
    for decision_id in ids:
        selection = decisions.get(decision_id, "")
        rationale = rationales.get(decision_id, "")
        if not selection or selection == "undecided":
            incomplete.append(f"{decision_id}: decision is missing")
        elif hmac.compare_digest(
            selection_digest(decision_id, selection), EXPECTED_SELECTION_DIGESTS[decision_id]
        ):
            total += choice_points

        if rationale_is_substantive(rationale, minimum_words):
            total += rationale_points
        else:
            all_rationales_complete = False
            incomplete.append(f"{decision_id}: rationale is incomplete")

    if all_rationales_complete:
        total += bonus
    return total, incomplete


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rubric", type=Path, required=True)
    parser.add_argument("--answer", type=Path, required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        rubric = read_json(args.rubric)
        decisions, rationales = parse_answer(args.answer)
        total, incomplete = score(rubric, decisions, rationales)
        maximum = int(rubric["maximum_score"])
        passing = int(rubric["passing_score"])
    except (KeyError, TypeError, ValueError, ScoringError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 3

    print(f"Score: {total}/{maximum} (passing: {passing})")
    if incomplete:
        print("EXPECTED_CONCEPTUAL_RESPONSE_INCOMPLETE: complete every decision and rationale.")
        for item in incomplete:
            print(f"  - {item}")
        return 2
    if total < passing:
        print("CONCEPTUAL_SCORE_BELOW_THRESHOLD: revisit the scenario tradeoffs.")
        return 1

    print("PASS: conceptual response meets the decision rubric.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
