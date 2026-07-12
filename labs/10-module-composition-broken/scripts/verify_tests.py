#!/usr/bin/env python3
from __future__ import annotations
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parents[1]
STARTER = LAB_DIR / "starter"
MARKER = "EXPECTED_MODULE_COMPOSITION_INCOMPLETE"


def run(terraform: str, cwd: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [terraform, *arguments], cwd=cwd, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False
    )


def references(expression: object) -> set[str]:
    if not isinstance(expression, dict):
        return set()
    values = expression.get("references", [])
    return set(values) if isinstance(values, list) else set()


def verify_plan_references(terraform: str) -> list[str]:
    issues: list[str] = []
    with tempfile.TemporaryDirectory(prefix="tfpro-lab10-") as temporary:
        workdir = Path(temporary) / "starter"
        shutil.copytree(
            STARTER,
            workdir,
            ignore=shutil.ignore_patterns(
                ".terraform", ".terraform.lock.hcl", "*.tfplan",
                "terraform.tfstate", "terraform.tfstate.backup",
            ),
        )
        initialized = run(terraform, workdir, "init", "-backend=false", "-input=false", "-no-color")
        if initialized.returncode:
            raise RuntimeError(f"reference-check init failed:\n{initialized.stdout.rstrip()}")
        plan_path = workdir / "references.tfplan"
        planned = run(terraform, workdir, "plan", "-input=false", "-no-color", "-out", plan_path.name)
        if planned.returncode:
            raise RuntimeError(f"reference-check plan failed:\n{planned.stdout.rstrip()}")
        shown = run(terraform, workdir, "show", "-json", plan_path.name)
        if shown.returncode:
            raise RuntimeError(f"reference-check show failed:\n{shown.stdout.rstrip()}")
        configuration = json.loads(shown.stdout)["configuration"]["root_module"]

    calls = configuration.get("module_calls", {})
    expected_arguments = {
        ("naming", "application"): {"var.application"},
        ("naming", "environment"): {"var.environment"},
        ("identity", "name_prefix"): {"module.naming", "module.naming.name_prefix"},
        ("compute", "name_prefix"): {"module.naming", "module.naming.name_prefix"},
        ("compute", "instance_profile_name"): {"module.identity", "module.identity.instance_profile_name"},
    }
    for (module_name, argument), expected in expected_arguments.items():
        actual = references(calls.get(module_name, {}).get("expressions", {}).get(argument))
        if actual != expected:
            issues.append(
                f"module.{module_name}.{argument} references {sorted(actual)!r}; expected {sorted(expected)!r}"
            )

    outputs = configuration.get("outputs", {})
    stack_refs = references(outputs.get("stack", {}).get("expression"))
    expected_stack_refs = {
        "module.compute",
        "module.compute.instance_reference",
        "module.identity",
        "module.identity.instance_profile_name",
        "module.naming",
        "module.naming.name_prefix",
    }
    if stack_refs != expected_stack_refs:
        issues.append(
            f"output.stack references {sorted(stack_refs)!r}; expected {sorted(expected_stack_refs)!r}"
        )
    return issues


def main() -> int:
    terraform = shutil.which("terraform")
    if terraform is None:
        print("Terraform executable was not found."); return 2
    init = run(terraform, LAB_DIR, "init", "-backend=false", "-input=false", "-test-directory=tests", "-no-color")
    if init.returncode:
        print(init.stdout.rstrip())
        return init.returncode
    test = run(terraform, LAB_DIR, "test", "-test-directory=tests", "-no-color")
    print(test.stdout.rstrip())
    if test.returncode:
        print(f"{MARKER}: root-to-child output wiring is incomplete.")
        return test.returncode
    try:
        issues = verify_plan_references(terraform)
    except (KeyError, json.JSONDecodeError, OSError, RuntimeError) as exc:
        print(f"Reference verification failed: {exc}")
        return 2
    if issues:
        print(f"{MARKER}: equal strings do not prove the required root-to-child dependency wiring.")
        for issue in issues:
            print(f"  - {issue}")
        return 1
    print("Module composition verification passed: exact plan-configuration references are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
