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

STOPWORDS = {
    "about", "after", "against", "allow", "allows", "also", "and", "are", "because",
    "before", "being", "between", "can", "cannot", "change", "changes", "configure",
    "create", "each", "every", "for", "from", "give", "have", "into", "its", "let",
    "more", "must", "not", "only", "option", "our", "run", "runs", "should", "than",
    "that", "the", "their", "them", "then", "these", "they", "this", "through", "to",
    "use", "uses", "using", "when", "where", "while", "with", "without", "workspace",
    "workspaces", "would",
}


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


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9][A-Za-z0-9'-]*", text.casefold())


def meaningful_terms(text: str) -> set[str]:
    return {word for word in words(text) if len(word) >= 3 and word not in STOPWORDS}


def rationale_evidence(
    text: str,
    selected_option: str,
    focus: str,
    scenario: str,
    model: dict[str, Any],
) -> tuple[bool, list[str]]:
    normalized = " ".join(text.lower().split())
    failures: list[str] = []
    if normalized.startswith("explain ") or any(phrase in normalized for phrase in PLACEHOLDER_PHRASES):
        failures.append("still contains placeholder language")
    rationale_words = words(text)
    if len(rationale_words) < int(model["minimum_rationale_words"]):
        failures.append("is shorter than the published minimum")

    rationale_terms = meaningful_terms(text)
    option_terms = meaningful_terms(selected_option)
    focus_terms = meaningful_terms(focus)
    scenario_terms = meaningful_terms(scenario)
    if len(rationale_terms & option_terms) < int(model["minimum_selected_option_terms"]):
        failures.append("does not explain the selected option in its own terms")
    if len(rationale_terms & focus_terms) < int(model["minimum_focus_terms"]):
        failures.append("does not address the rubric focus")
    if len(rationale_terms & scenario_terms) < int(model["minimum_scenario_terms"]):
        failures.append("does not connect the choice to the scenario")
    if len(rationale_terms - option_terms) < int(model["minimum_novel_terms"]):
        failures.append("does not add enough independent explanation beyond the option text")
    return not failures, failures


def parse_question_options(path: Path) -> dict[str, dict[str, str]]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ScoringError(f"cannot read questions {path}: {exc}") from exc

    headings = list(
        re.finditer(r"(?m)^##\s+\d+\..*\(`([a-z][a-z0-9_]*)`\)\s*$", text)
    )
    options: dict[str, dict[str, str]] = {}
    for index, heading in enumerate(headings):
        start = heading.end()
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        options[heading.group(1)] = {
            option_id: description.strip()
            for option_id, description in re.findall(
                r"(?m)^-\s+`([a-z][a-z0-9_]*)`:\s*(.+?)\s*$", text[start:end]
            )
        }
    if not options or any(not values for values in options.values()):
        raise ScoringError("every question must define a decision id and at least one option")
    return options


def score(
    rubric: dict[str, Any],
    decisions: dict[str, str],
    rationales: dict[str, str],
    question_options: dict[str, dict[str, str]],
    scenario: str,
) -> tuple[int, list[str], list[str]]:
    model = rubric.get("scoring_model")
    dimensions = rubric.get("dimensions")
    if not isinstance(model, dict) or not isinstance(dimensions, list):
        raise ScoringError("rubric must define scoring_model and dimensions")

    ids = [item.get("id") for item in dimensions if isinstance(item, dict)]
    if len(ids) != len(dimensions) or any(not isinstance(item, str) for item in ids):
        raise ScoringError("every rubric dimension must have a string id")
    if set(ids) != set(EXPECTED_SELECTION_DIGESTS):
        raise ScoringError("rubric dimensions do not match the protected decision set")
    if len(ids) != len(set(ids)):
        raise ScoringError("rubric dimension ids must be unique")
    if set(ids) != set(question_options):
        raise ScoringError("question decision ids do not match rubric dimensions")

    choice_points = int(model["correct_choice_points_per_decision"])
    rationale_points = int(model["substantive_rationale_points_per_decision"])
    bonus = int(model["complete_response_bonus"])
    minimum_words = int(model["minimum_rationale_words"])
    for field in (
        "minimum_selected_option_terms",
        "minimum_focus_terms",
        "minimum_scenario_terms",
        "minimum_novel_terms",
    ):
        if int(model[field]) < 1:
            raise ScoringError(f"{field} must be positive")
    if minimum_words < 1:
        raise ScoringError("minimum_rationale_words must be positive")

    total = 0
    incomplete: list[str] = []
    details: list[str] = []
    all_rationales_complete = True
    dimensions_by_id = {item["id"]: item for item in dimensions}
    for decision_id in ids:
        selection = decisions.get(decision_id, "")
        rationale = rationales.get(decision_id, "")
        valid_selection = selection in question_options[decision_id]
        if not selection or selection == "undecided":
            incomplete.append(f"{decision_id}: decision is missing")
            choice_status = "missing"
        elif not valid_selection:
            incomplete.append(f"{decision_id}: option '{selection}' is not defined")
            choice_status = "invalid"
        elif hmac.compare_digest(
            selection_digest(decision_id, selection), EXPECTED_SELECTION_DIGESTS[decision_id]
        ):
            total += choice_points
            choice_status = "correct"
        else:
            choice_status = "incorrect"

        rationale_failures: list[str] = []
        if valid_selection:
            rationale_ok, rationale_failures = rationale_evidence(
                rationale,
                question_options[decision_id][selection],
                str(dimensions_by_id[decision_id]["focus"]),
                scenario,
                model,
            )
        else:
            rationale_ok = False
            rationale_failures = ["cannot be checked until a valid option is selected"]
        if rationale_ok:
            total += rationale_points
            rationale_status = "evidence-complete"
        else:
            all_rationales_complete = False
            incomplete.extend(
                f"{decision_id}: rationale {failure}" for failure in rationale_failures
            )
            rationale_status = "incomplete"
        details.append(
            f"{decision_id}: choice={choice_status}, rationale={rationale_status}"
        )

    if all_rationales_complete:
        total += bonus
    return total, incomplete, details


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
        question_options = parse_question_options(args.answer.parent / "QUESTIONS.md")
        scenario = (args.answer.parent / "SCENARIO.md").read_text(encoding="utf-8")
        first_dimension = rubric["dimensions"][0]
        first_id = first_dimension["id"]
        first_option = question_options[first_id][sorted(question_options[first_id])[0]]
        filler_ok, _ = rationale_evidence(
            "alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi omicron pi rho sigma",
            first_option,
            first_dimension["focus"],
            scenario,
            rubric["scoring_model"],
        )
        copied_ok, _ = rationale_evidence(
            first_option,
            first_option,
            first_dimension["focus"],
            scenario,
            rubric["scoring_model"],
        )
        if filler_ok or copied_ok:
            raise ScoringError("rationale-evidence negative controls failed")
        total, incomplete, details = score(
            rubric, decisions, rationales, question_options, scenario
        )
        maximum = int(rubric["maximum_score"])
        passing = int(rubric["passing_score"])
        model = rubric["scoring_model"]
        calculated_maximum = len(rubric["dimensions"]) * (
            int(model["correct_choice_points_per_decision"])
            + int(model["substantive_rationale_points_per_decision"])
        ) + int(model["complete_response_bonus"])
        if calculated_maximum != maximum:
            raise ScoringError(
                f"rubric scoring weights total {calculated_maximum}, expected {maximum}"
            )
        if not 0 < passing <= maximum:
            raise ScoringError("passing_score must be between 1 and maximum_score")
    except (KeyError, OSError, TypeError, ValueError, ScoringError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 3

    print(f"Score: {total}/{maximum} (passing: {passing})")
    print("Decision results:")
    for detail in details:
        print(f"  - {detail}")
    if incomplete:
        print("EXPECTED_CONCEPTUAL_RESPONSE_INCOMPLETE: complete every decision and rationale.")
        for item in incomplete:
            print(f"  - {item}")
        return 2
    if total < passing:
        print("CONCEPTUAL_SCORE_BELOW_THRESHOLD: revisit the scenario tradeoffs.")
        return 1

    print("PASS: conceptual response meets the local decision and rationale-evidence rubric.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
