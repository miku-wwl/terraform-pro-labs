#!/usr/bin/env python3
"""Verify Lab 11 import and moved-block behavior against isolated local state."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any


LAB_DIR = Path(__file__).resolve().parents[1]
STARTER = LAB_DIR / "starter"
RUNTIME = LAB_DIR / ".lab-state"
FIXTURE = RUNTIME / "fixture.json"
WORK = RUNTIME / "learner"
RUNTIME_MODULES = RUNTIME / "modules"
OLD_ADDRESS = "random_id.legacy_record"
TARGET_ADDRESS = "module.record.random_id.this"
MARKER = "EXPECTED_STATE_REFACTOR_INCOMPLETE"


def run(terraform: str, cwd: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [terraform, *arguments],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def require_success(completed: subprocess.CompletedProcess[str], operation: str) -> None:
    if completed.returncode != 0:
        if completed.stdout:
            print(completed.stdout.rstrip())
        raise RuntimeError(f"{operation} failed with exit code {completed.returncode}")


def copy_stage(stage: str) -> None:
    for terraform_file in WORK.glob("*.tf"):
        terraform_file.unlink()
    for source in (STARTER / stage).glob("*.tf"):
        shutil.copy2(source, WORK / source.name)


def plan_json(terraform: str, plan_path: Path) -> dict[str, Any]:
    completed = run(terraform, WORK, "show", "-json", plan_path.name)
    require_success(completed, f"show {plan_path.name}")
    return json.loads(completed.stdout)


def action_summary(plan: dict[str, Any]) -> Counter[str]:
    summary: Counter[str] = Counter()
    for resource_change in plan.get("resource_changes", []):
        actions = resource_change.get("change", {}).get("actions", [])
        if actions == ["create"]:
            summary["add"] += 1
        elif actions == ["update"]:
            summary["change"] += 1
        elif "delete" in actions and "create" in actions:
            summary["destroy"] += 1
            summary["add"] += 1
        elif actions == ["delete"]:
            summary["destroy"] += 1
    return summary


def import_changes(plan: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        resource_change
        for resource_change in plan.get("resource_changes", [])
        if resource_change.get("change", {}).get("importing") is not None
    ]


def state_addresses(terraform: str) -> list[str]:
    completed = run(terraform, WORK, "state", "list", "-no-color")
    require_success(completed, "state list")
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def fail_incomplete(message: str) -> int:
    print(f"{MARKER}: {message}")
    return 1


def main() -> int:
    terraform = shutil.which("terraform")
    if terraform is None:
        print("Terraform executable was not found.")
        return 2
    if not FIXTURE.is_file():
        print("Seed fixture is missing; run 'python tools/labctl.py seed 11' first.")
        return 2

    try:
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        import_id = fixture["import_id"]
        if fixture.get("old_address") != OLD_ADDRESS or fixture.get("target_address") != TARGET_ADDRESS:
            raise RuntimeError("seed fixture addresses do not match the protected lab contract")

        if WORK.exists():
            shutil.rmtree(WORK)
        if RUNTIME_MODULES.exists():
            shutil.rmtree(RUNTIME_MODULES)
        WORK.mkdir(parents=True)
        shutil.copytree(STARTER / "modules", RUNTIME_MODULES)
        (WORK / "terraform.auto.tfvars.json").write_text(
            json.dumps({"import_id": import_id}, indent=2) + "\n",
            encoding="utf-8",
        )

        copy_stage("import-stage")
        require_success(
            run(terraform, WORK, "init", "-backend=false", "-input=false", "-no-color"),
            "import-stage init",
        )
        require_success(run(terraform, WORK, "validate", "-no-color"), "import-stage validate")
        import_plan_path = WORK / "import.tfplan"
        import_plan = run(
            terraform,
            WORK,
            "plan",
            "-input=false",
            "-no-color",
            "-out",
            import_plan_path.name,
        )
        require_success(import_plan, "import-stage plan")
        import_data = plan_json(terraform, import_plan_path)
        import_summary = action_summary(import_data)
        imports = import_changes(import_data)
        if (
            len(imports) != 1
            or imports[0].get("address") != OLD_ADDRESS
            or import_summary["add"]
            or import_summary["destroy"]
        ):
            return fail_incomplete(
                "the import stage must adopt the seeded identity at the old root address without create/delete actions"
            )
        print(
            "Import plan summary: "
            f"1 to import, {import_summary['add']} to add, "
            f"{import_summary['change']} to change, {import_summary['destroy']} to destroy."
        )

        require_success(
            run(terraform, WORK, "apply", "-input=false", "-no-color", import_plan_path.name),
            "import-stage apply",
        )
        imported_addresses = state_addresses(terraform)
        if imported_addresses != [OLD_ADDRESS]:
            raise RuntimeError(
                f"imported state addresses were {imported_addresses!r}; expected [{OLD_ADDRESS!r}]"
            )
        imported_output = run(terraform, WORK, "output", "-raw", "record_id")
        require_success(imported_output, "imported identity output")
        if imported_output.stdout.strip() != import_id:
            raise RuntimeError("imported resource identity does not match the seed fixture")
        print(f"Imported state address: {OLD_ADDRESS}")

        copy_stage("refactor-stage")
        require_success(
            run(terraform, WORK, "init", "-backend=false", "-input=false", "-no-color"),
            "refactor-stage init",
        )
        require_success(run(terraform, WORK, "validate", "-no-color"), "refactor-stage validate")
        refactor_plan_path = WORK / "refactor.tfplan"
        refactor_plan = run(
            terraform,
            WORK,
            "plan",
            "-input=false",
            "-no-color",
            "-detailed-exitcode",
            "-out",
            refactor_plan_path.name,
        )
        if refactor_plan.returncode not in (0, 2):
            print(refactor_plan.stdout.rstrip())
            raise RuntimeError(f"refactor-stage plan failed with exit code {refactor_plan.returncode}")
        refactor_data = plan_json(terraform, refactor_plan_path)
        refactor_summary = action_summary(refactor_data)
        target_changes = [
            change
            for change in refactor_data.get("resource_changes", [])
            if change.get("address") == TARGET_ADDRESS
        ]
        mapping_is_exact = (
            len(target_changes) == 1
            and target_changes[0].get("previous_address") == OLD_ADDRESS
            and target_changes[0].get("change", {}).get("actions") == ["no-op"]
        )
        if refactor_summary["add"] or refactor_summary["destroy"] or not mapping_is_exact:
            return fail_incomplete(
                "the module refactor must map the old address to the target address without create/delete actions"
            )
        print(
            "Refactor plan summary: "
            f"{refactor_summary['add']} to add, {refactor_summary['change']} to change, "
            f"{refactor_summary['destroy']} to destroy."
        )

        require_success(
            run(terraform, WORK, "apply", "-input=false", "-no-color", refactor_plan_path.name),
            "refactor-stage apply",
        )
        final_addresses = state_addresses(terraform)
        if final_addresses != [TARGET_ADDRESS]:
            raise RuntimeError(
                f"final state addresses were {final_addresses!r}; expected [{TARGET_ADDRESS!r}]"
            )
        final_output = run(terraform, WORK, "output", "-raw", "record_id")
        require_success(final_output, "final identity output")
        if final_output.stdout.strip() != import_id:
            raise RuntimeError("resource identity changed during the module refactor")

        final_plan = run(
            terraform,
            WORK,
            "plan",
            "-input=false",
            "-no-color",
            "-detailed-exitcode",
        )
        if final_plan.returncode != 0:
            print(final_plan.stdout.rstrip())
            raise RuntimeError("final plan was not a no-op")
        print(f"Final state address: {TARGET_ADDRESS}")
        print("Final plan summary: 0 to add, 0 to change, 0 to destroy (no-op).")
        return 0
    except (KeyError, OSError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"Verification failed: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
