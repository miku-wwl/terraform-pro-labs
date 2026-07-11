#!/usr/bin/env python3
"""Verify the exact Lab 19 count-index to logical-key state mapping."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


LAB_DIR = Path(__file__).resolve().parents[1]
RUNTIME = LAB_DIR / ".lab-state"
WORK = RUNTIME / "learner"
FIXTURE = RUNTIME / "fixture.json"
MARKER = "EXPECTED_COUNT_TO_FOREACH_REFACTOR_INCOMPLETE"
EXPECTED_MAPPING = {
    "terraform_data.bucket[0]": 'terraform_data.bucket["logs"]',
    "terraform_data.bucket[1]": 'terraform_data.bucket["assets"]',
    "terraform_data.bucket[2]": 'terraform_data.bucket["archive"]',
}


def run(terraform: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([terraform, *args], cwd=WORK, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


def require(result: subprocess.CompletedProcess[str], operation: str) -> None:
    if result.returncode:
        if result.stdout:
            print(result.stdout.rstrip())
        raise RuntimeError(f"{operation} failed with exit code {result.returncode}")


def plan_json(terraform: str, name: str) -> dict[str, Any]:
    result = run(terraform, "show", "-json", name)
    require(result, "show plan")
    return json.loads(result.stdout)


def state_addresses(terraform: str) -> list[str]:
    result = run(terraform, "state", "list", "-no-color")
    require(result, "state list")
    return sorted(line.strip() for line in result.stdout.splitlines() if line.strip())


def incomplete(message: str) -> int:
    print(f"{MARKER}: {message}")
    return 1


def main() -> int:
    terraform = shutil.which("terraform")
    if terraform is None:
        print("Terraform executable was not found.")
        return 2
    if not FIXTURE.is_file():
        print("Seed fixture is missing; run 'python tools/labctl.py seed 19' first.")
        return 2
    try:
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        if state_addresses(terraform) != sorted(EXPECTED_MAPPING):
            raise RuntimeError("seed state does not contain the exact old count addresses")
        for path in WORK.glob("*.tf"):
            path.unlink()
        for source in (LAB_DIR / "starter").glob("*.tf"):
            shutil.copy2(source, WORK / source.name)
        require(run(terraform, "init", "-backend=false", "-input=false", "-no-color"), "refactor init")
        require(run(terraform, "validate", "-no-color"), "refactor validate")
        planned = run(terraform, "plan", "-input=false", "-no-color", "-detailed-exitcode", "-out", "refactor.tfplan")
        if planned.returncode not in (0, 2):
            require(planned, "refactor plan")
        data = plan_json(terraform, "refactor.tfplan")
        changes = data.get("resource_changes", [])
        mappings = {
            item.get("previous_address"): item.get("address")
            for item in changes
            if item.get("previous_address") and item.get("change", {}).get("actions") == ["no-op"]
        }
        destructive = [item.get("address") for item in changes
                       if any(action in ("create", "delete") for action in item.get("change", {}).get("actions", []))]
        if mappings != EXPECTED_MAPPING or destructive:
            return incomplete("map index 0 to logs, 1 to assets, and 2 to archive with no create/delete actions")
        require(run(terraform, "apply", "-input=false", "-no-color", "refactor.tfplan"), "refactor apply")
        if state_addresses(terraform) != sorted(EXPECTED_MAPPING.values()):
            raise RuntimeError("final state list does not contain the exact logical keys")
        result = run(terraform, "output", "-json", "records")
        require(result, "final output")
        final_records = json.loads(result.stdout)
        old_records = fixture["records_by_index"]
        expected_records = {"logs": old_records["0"], "assets": old_records["1"], "archive": old_records["2"]}
        if final_records != expected_records:
            raise RuntimeError("record values changed during address refactor")
        final = run(terraform, "plan", "-input=false", "-no-color", "-detailed-exitcode")
        if final.returncode != 0:
            raise RuntimeError("final plan was not no-op")
        print("PASS: exact mappings were 0->logs, 1->assets, and 2->archive with zero create/delete actions.")
        print("PASS: final state uses all three logical keys, values are unchanged, and the final plan is no-op.")
        return 0
    except (KeyError, OSError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"Verification failed: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
