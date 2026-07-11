#!/usr/bin/env python3
"""Verify that Lab 26 distinguishes moved and destroy-false removed semantics."""

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
MARKER = "EXPECTED_MOVED_REMOVED_REFACTOR_INCOMPLETE"
OLD_SERVICE = "terraform_data.service_old"
NEW_SERVICE = "terraform_data.service"
ATTACHMENT = "terraform_data.legacy_attachment"


def run(terraform: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([terraform, *args], cwd=WORK, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


def require(result: subprocess.CompletedProcess[str], operation: str) -> None:
    if result.returncode:
        if result.stdout:
            print(result.stdout.rstrip())
        raise RuntimeError(f"{operation} failed with exit code {result.returncode}")


def addresses(terraform: str) -> list[str]:
    result = run(terraform, "state", "list", "-no-color")
    require(result, "state list")
    return sorted(line.strip() for line in result.stdout.splitlines() if line.strip())


def plan_json(terraform: str, name: str) -> dict[str, Any]:
    result = run(terraform, "show", "-json", name)
    require(result, "show plan")
    return json.loads(result.stdout)


def incomplete(message: str) -> int:
    print(f"{MARKER}: {message}")
    return 1


def main() -> int:
    terraform = shutil.which("terraform")
    if terraform is None:
        print("Terraform executable was not found.")
        return 2
    if not FIXTURE.is_file():
        print("Seed fixture is missing; run 'python tools/labctl.py seed 26' first.")
        return 2
    try:
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        if addresses(terraform) != sorted(fixture["old_addresses"]):
            raise RuntimeError("seed state does not contain both protected old addresses")
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
        by_address = {item.get("address"): item for item in data.get("resource_changes", [])}
        moved = by_address.get(NEW_SERVICE, {})
        moved_ok = (moved.get("previous_address") == OLD_SERVICE
                    and moved.get("change", {}).get("actions") == ["no-op"])
        removed = by_address.get(ATTACHMENT, {})
        removed_ok = removed.get("change", {}).get("actions") == ["forget"]
        create_delete = [item.get("address") for item in data.get("resource_changes", [])
                         if any(action in ("create", "delete") for action in item.get("change", {}).get("actions", []))]
        if not moved_ok or not removed_ok or create_delete:
            return incomplete("rename the service with a no-op move and forget the attachment with destroy=false; create/delete is forbidden")
        require(run(terraform, "apply", "-input=false", "-no-color", "refactor.tfplan"), "refactor apply")
        if addresses(terraform) != [NEW_SERVICE]:
            raise RuntimeError("final state must retain only the renamed service address")
        service = run(terraform, "output", "-json", "service")
        require(service, "service output")
        if json.loads(service.stdout) != fixture["service"]:
            raise RuntimeError("service value changed during the move")
        final = run(terraform, "plan", "-input=false", "-no-color", "-detailed-exitcode")
        if final.returncode != 0:
            raise RuntimeError("final plan was not no-op")
        print("PASS: moved produced an exact old-to-new no-op mapping; removed destroy=false produced forget.")
        print("PASS: no create/delete occurred, final state retains only the service, and the final plan is no-op.")
        return 0
    except (KeyError, OSError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"Verification failed: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
