#!/usr/bin/env python3
"""Verify Lab 03 collection import and module-instance refactor."""

from __future__ import annotations

import json
import shutil
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any


LAB_DIR = Path(__file__).resolve().parents[1]
STARTER = LAB_DIR / "starter"
RUNTIME = LAB_DIR / ".lab-state"
FIXTURE = RUNTIME / "fixture.json"
WORK = RUNTIME / "learner"
MODULES = RUNTIME / "modules"
MARKER = "EXPECTED_COLLECTION_REFACTOR_INCOMPLETE"


def run(terraform: str, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([terraform, *arguments], cwd=WORK, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


def require(completed: subprocess.CompletedProcess[str], operation: str) -> None:
    if completed.returncode:
        if completed.stdout:
            print(completed.stdout.rstrip())
        raise RuntimeError(f"{operation} failed with exit code {completed.returncode}")


def copy_stage(name: str) -> None:
    for path in WORK.glob("*.tf"):
        path.unlink()
    for source in (STARTER / name).glob("*.tf"):
        shutil.copy2(source, WORK / source.name)


def show_plan(terraform: str, path: Path) -> dict[str, Any]:
    completed = run(terraform, "show", "-json", path.name)
    require(completed, f"show {path.name}")
    return json.loads(completed.stdout)


def actions(plan: dict[str, Any]) -> Counter[str]:
    result: Counter[str] = Counter()
    for item in plan.get("resource_changes", []):
        value = item.get("change", {}).get("actions", [])
        if "create" in value:
            result["create"] += 1
        if "delete" in value:
            result["delete"] += 1
    return result


def addresses(terraform: str) -> list[str]:
    completed = run(terraform, "state", "list", "-no-color")
    require(completed, "state list")
    return sorted(line.strip() for line in completed.stdout.splitlines() if line.strip())


def incomplete(message: str) -> int:
    print(f"{MARKER}: {message}")
    return 1


def main() -> int:
    terraform = shutil.which("terraform")
    if terraform is None:
        print("Terraform executable was not found.")
        return 2
    if not FIXTURE.is_file():
        print("Seed fixture is missing; run 'python tools/labctl.py seed 03' first.")
        return 2
    try:
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        import_ids = fixture["import_ids"]
        old = sorted(fixture["old_addresses"])
        target = sorted(fixture["target_addresses"])
        if WORK.exists():
            shutil.rmtree(WORK)
        if MODULES.exists():
            shutil.rmtree(MODULES)
        WORK.mkdir(parents=True)
        shutil.copytree(STARTER / "modules", MODULES)
        (WORK / "terraform.auto.tfvars.json").write_text(
            json.dumps({"import_ids": import_ids}, indent=2) + "\n", encoding="utf-8"
        )

        copy_stage("import-stage")
        require(run(terraform, "init", "-backend=false", "-input=false", "-no-color"), "import init")
        require(run(terraform, "validate", "-no-color"), "import validate")
        import_path = WORK / "import.tfplan"
        require(run(terraform, "plan", "-input=false", "-no-color", "-out", import_path.name), "import plan")
        import_plan = show_plan(terraform, import_path)
        imported = sorted(
            change["address"] for change in import_plan.get("resource_changes", [])
            if change.get("change", {}).get("importing") is not None
        )
        summary = actions(import_plan)
        if imported != old or summary["create"] or summary["delete"]:
            return incomplete("both keyed objects must be imported at their old addresses without create/delete actions")
        require(run(terraform, "apply", "-input=false", "-no-color", import_path.name), "import apply")
        if addresses(terraform) != old:
            raise RuntimeError("imported state addresses do not match the protected contract")
        output = run(terraform, "output", "-json", "record_ids")
        require(output, "import output")
        if json.loads(output.stdout) != import_ids:
            raise RuntimeError("imported identities differ from the seed fixture")
        print(f"Import gate: {len(imported)} imports, 0 create, 0 delete; exact keyed addresses preserved.")

        copy_stage("refactor-stage")
        require(run(terraform, "init", "-backend=false", "-input=false", "-no-color"), "refactor init")
        require(run(terraform, "validate", "-no-color"), "refactor validate")
        refactor_path = WORK / "refactor.tfplan"
        planned = run(terraform, "plan", "-input=false", "-no-color", "-detailed-exitcode", "-out", refactor_path.name)
        if planned.returncode not in (0, 2):
            require(planned, "refactor plan")
        refactor = show_plan(terraform, refactor_path)
        summary = actions(refactor)
        mappings = {
            change.get("previous_address"): change.get("address")
            for change in refactor.get("resource_changes", [])
            if change.get("previous_address")
            and change.get("change", {}).get("actions") == ["no-op"]
        }
        expected = dict(zip(old, target))
        if mappings != expected or summary["create"] or summary["delete"]:
            return incomplete("each keyed root address must move to its matching module instance without create/delete actions")
        require(run(terraform, "apply", "-input=false", "-no-color", refactor_path.name), "refactor apply")
        if addresses(terraform) != target:
            raise RuntimeError("final state addresses do not match the module instances")
        output = run(terraform, "output", "-json", "record_ids")
        require(output, "final output")
        if json.loads(output.stdout) != import_ids:
            raise RuntimeError("an identity changed during refactor")
        final = run(terraform, "plan", "-input=false", "-no-color", "-detailed-exitcode")
        if final.returncode != 0:
            if final.stdout:
                print(final.stdout.rstrip())
            raise RuntimeError("final plan was not a no-op")
        print("Refactor gate: 2 exact moves, 0 create, 0 delete; final plan is no-op.")
        return 0
    except (KeyError, OSError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"Verification failed: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
