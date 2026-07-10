#!/usr/bin/env python3
"""Minimal, portable lab runner for migrated Terraform practice labs."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LABS_DIR = ROOT / "labs"
RESULTS_DIR = ROOT / ".labctl" / "results"

REQUIRED_TOP_LEVEL = {
    "schema_version": int,
    "id": int,
    "title": str,
    "type": str,
    "tier": str,
    "difficulty": str,
    "estimated_minutes": int,
    "execution": dict,
    "validation": dict,
    "editable_paths": list,
    "protected_paths": list,
}

REQUIRED_EXECUTION = {
    "mode": str,
    "terraform_version": str,
    "requires_cloud_credentials": bool,
    "creates_billable_resources": bool,
    "backend": str,
}

REQUIRED_VALIDATION = {
    "starter_expected_result": str,
    "expected_failure_stage": str,
    "expected_error_category": str,
    "expected_failing_test": str,
    "expected_failure_marker": str,
    "solution_expected_result": str,
    "commands": list,
}

REQUIRED_STATE = {
    "seed_argv": list,
    "generated_paths": list,
}

REQUIRED_CONCEPTUAL = {
    "rubric_path": str,
    "answer_path": str,
}

REQUIRED_BACKEND = {
    "example_files": list,
    "init_metadata_paths": list,
    "real_init_opt_in": bool,
}


class ManifestError(ValueError):
    """Raised when a lab manifest does not satisfy the supported schema."""


def path_contains(parent: Path, child: Path) -> bool:
    """Return whether child is the same as, or is contained by, parent."""

    try:
        child.relative_to(parent)
    except ValueError:
        return False
    return True


def lab_directories() -> list[Path]:
    return sorted(path for path in LABS_DIR.glob("[0-9][0-9]-*") if path.is_dir())


def resolve_lab(lab_id: str) -> Path:
    normalized = lab_id.zfill(2)
    matches = [path for path in lab_directories() if path.name.startswith(f"{normalized}-")]
    if len(matches) != 1:
        raise ManifestError(f"expected exactly one lab matching id {normalized}, found {len(matches)}")
    return matches[0]


def require_fields(value: dict[str, Any], fields: dict[str, type], context: str) -> None:
    for name, expected_type in fields.items():
        if name not in value:
            raise ManifestError(f"{context}: missing required field '{name}'")
        if not isinstance(value[name], expected_type):
            raise ManifestError(
                f"{context}.{name}: expected {expected_type.__name__}, "
                f"got {type(value[name]).__name__}"
            )


def load_manifest(lab_dir: Path) -> dict[str, Any]:
    manifest_path = lab_dir / "lab.yaml"
    if not manifest_path.is_file():
        raise ManifestError(f"{lab_dir.name}: lab.yaml is missing")

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ManifestError(f"{lab_dir.name}: lab.yaml must be JSON-compatible YAML: {exc}") from exc

    if not isinstance(manifest, dict):
        raise ManifestError(f"{lab_dir.name}: manifest root must be a mapping")

    require_fields(manifest, REQUIRED_TOP_LEVEL, lab_dir.name)
    require_fields(manifest["execution"], REQUIRED_EXECUTION, f"{lab_dir.name}.execution")
    require_fields(manifest["validation"], REQUIRED_VALIDATION, f"{lab_dir.name}.validation")

    directory_id = int(lab_dir.name[:2])
    if manifest["schema_version"] != 1:
        raise ManifestError(f"{lab_dir.name}: unsupported schema_version")
    if manifest["id"] != directory_id:
        raise ManifestError(f"{lab_dir.name}: manifest id does not match directory")
    if manifest["validation"]["starter_expected_result"] != "fail":
        raise ManifestError(f"{lab_dir.name}: starter_expected_result must be 'fail'")
    if manifest["validation"]["solution_expected_result"] != "pass":
        raise ManifestError(f"{lab_dir.name}: solution_expected_result must be 'pass'")
    if not manifest["validation"]["commands"]:
        raise ManifestError(f"{lab_dir.name}: validation.commands must not be empty")

    stages: list[str] = []
    for index, command in enumerate(manifest["validation"]["commands"]):
        context = f"{lab_dir.name}.validation.commands[{index}]"
        require_fields(command, {"name": str, "stage": str, "argv": list}, context)
        if not command["argv"] or not all(isinstance(item, str) for item in command["argv"]):
            raise ManifestError(f"{context}.argv must be a non-empty list of strings")
        stages.append(command["stage"])

    if manifest["validation"]["expected_failure_stage"] not in stages:
        raise ManifestError(f"{lab_dir.name}: expected_failure_stage is not present in commands")

    for field in ("editable_paths", "protected_paths"):
        if not manifest[field] or not all(isinstance(item, str) for item in manifest[field]):
            raise ManifestError(f"{lab_dir.name}.{field} must be a non-empty list of paths")
        if len(manifest[field]) != len(set(manifest[field])):
            raise ManifestError(f"{lab_dir.name}.{field} must not contain duplicate paths")
        for relative in manifest[field]:
            if Path(relative).is_absolute() or ".." in Path(relative).parts:
                raise ManifestError(f"{lab_dir.name}.{field}: unsafe path '{relative}'")
            if not (lab_dir / relative).exists():
                raise ManifestError(f"{lab_dir.name}.{field}: path does not exist: {relative}")
            if field == "editable_paths" and not (lab_dir / relative).is_file():
                raise ManifestError(
                    f"{lab_dir.name}.{field}: editable path must be a file: {relative}"
                )

    editable_paths = [Path(relative) for relative in manifest["editable_paths"]]
    protected_paths = [Path(relative) for relative in manifest["protected_paths"]]
    for editable in editable_paths:
        for protected in protected_paths:
            if path_contains(protected, editable) or path_contains(editable, protected):
                raise ManifestError(
                    f"{lab_dir.name}: editable path '{editable.as_posix()}' overlaps "
                    f"protected path '{protected.as_posix()}'"
                )

    if manifest["type"] == "state-refactor":
        if "state" not in manifest or not isinstance(manifest["state"], dict):
            raise ManifestError(f"{lab_dir.name}: state-refactor labs require a state mapping")
        state = manifest["state"]
        require_fields(state, REQUIRED_STATE, f"{lab_dir.name}.state")
        if not state["seed_argv"] or not all(isinstance(item, str) for item in state["seed_argv"]):
            raise ManifestError(f"{lab_dir.name}.state.seed_argv must be a non-empty list of strings")
        if not state["generated_paths"] or not all(
            isinstance(item, str) for item in state["generated_paths"]
        ):
            raise ManifestError(f"{lab_dir.name}.state.generated_paths must be a non-empty list of paths")
        for relative in state["generated_paths"]:
            relative_path = Path(relative)
            if (
                relative_path.is_absolute()
                or ".." in relative_path.parts
                or relative_path in (Path("."), Path(""))
            ):
                raise ManifestError(f"{lab_dir.name}.state.generated_paths: unsafe path '{relative}'")

    if manifest["type"] == "conceptual":
        if "conceptual" not in manifest or not isinstance(manifest["conceptual"], dict):
            raise ManifestError(f"{lab_dir.name}: conceptual labs require a conceptual mapping")
        conceptual = manifest["conceptual"]
        require_fields(conceptual, REQUIRED_CONCEPTUAL, f"{lab_dir.name}.conceptual")
        for field in REQUIRED_CONCEPTUAL:
            relative = Path(conceptual[field])
            if relative.is_absolute() or ".." in relative.parts or not (lab_dir / relative).is_file():
                raise ManifestError(
                    f"{lab_dir.name}.conceptual.{field}: unsafe or missing file '{conceptual[field]}'"
                )
        if list((lab_dir / "starter").glob("*.tf")):
            raise ManifestError(f"{lab_dir.name}: conceptual starter must not contain Terraform files")

    if manifest["type"] == "backend-remote-state":
        if "backend" not in manifest or not isinstance(manifest["backend"], dict):
            raise ManifestError(f"{lab_dir.name}: backend labs require a backend mapping")
        backend = manifest["backend"]
        require_fields(backend, REQUIRED_BACKEND, f"{lab_dir.name}.backend")
        if not backend["example_files"] or not all(
            isinstance(item, str) for item in backend["example_files"]
        ):
            raise ManifestError(f"{lab_dir.name}.backend.example_files must be a non-empty list")
        for relative in backend["example_files"]:
            relative_path = Path(relative)
            if (
                relative_path.is_absolute()
                or ".." in relative_path.parts
                or relative_path.suffix != ".example"
                or not (lab_dir / relative_path).is_file()
            ):
                raise ManifestError(
                    f"{lab_dir.name}.backend.example_files: unsafe or missing example '{relative}'"
                )
        if not backend["init_metadata_paths"] or not all(
            isinstance(item, str) for item in backend["init_metadata_paths"]
        ):
            raise ManifestError(f"{lab_dir.name}.backend.init_metadata_paths must be a non-empty list")
        for relative in backend["init_metadata_paths"]:
            relative_path = Path(relative)
            if (
                relative_path.is_absolute()
                or ".." in relative_path.parts
                or relative_path in (Path("."), Path(""))
            ):
                raise ManifestError(
                    f"{lab_dir.name}.backend.init_metadata_paths: unsafe path '{relative}'"
                )

    return manifest


def result_path(lab_id: int, mode: str) -> Path:
    return RESULTS_DIR / f"{lab_id:02d}-{mode}.json"


def write_result(lab_id: int, mode: str, outcome: str, command_name: str, returncode: int) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "lab_id": f"{lab_id:02d}",
        "mode": mode,
        "outcome": outcome,
        "command": command_name,
        "returncode": returncode,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    result_path(lab_id, mode).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def generated_artifacts(lab_dir: Path, manifest: dict[str, Any]) -> list[Path]:
    starter = lab_dir / "starter"
    candidates = [
        lab_dir / ".terraform",
        starter / ".terraform",
        starter / "terraform.tfstate",
        starter / "terraform.tfstate.backup",
        starter / "terraform.tfstate.d",
        starter / "crash.log",
    ]
    candidates.extend(lab_dir.rglob(".terraform"))
    candidates.extend(starter.rglob(".terraform.lock.hcl"))
    candidates.extend(starter.rglob("terraform.tfstate"))
    candidates.extend(starter.rglob("terraform.tfstate.backup"))
    candidates.extend(starter.rglob("terraform.tfstate.d"))
    candidates.extend(starter.rglob("*.tfplan"))
    if manifest["type"] == "state-refactor":
        candidates.extend(lab_dir / relative for relative in manifest["state"]["generated_paths"])
    if manifest["type"] == "backend-remote-state":
        candidates.extend(lab_dir / relative for relative in manifest["backend"]["init_metadata_paths"])
    existing = {path for path in candidates if path.exists()}
    return sorted(existing, key=lambda path: len(path.parts), reverse=True)


def display_relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def command_list(_: argparse.Namespace) -> int:
    invalid = False
    for lab_dir in lab_directories():
        manifest_path = lab_dir / "lab.yaml"
        if not manifest_path.exists():
            print(f"{lab_dir.name[:2]}  legacy      {lab_dir.name[3:]}")
            continue
        try:
            manifest = load_manifest(lab_dir)
        except ManifestError as exc:
            invalid = True
            print(f"{lab_dir.name[:2]}  INVALID     {exc}")
            continue
        print(f"{manifest['id']:02d}  migrated    {manifest['title']}")
    return 1 if invalid else 0


def command_status(args: argparse.Namespace) -> int:
    try:
        lab_dir = resolve_lab(args.lab_id)
        manifest = load_manifest(lab_dir)
    except ManifestError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    artifacts = generated_artifacts(lab_dir, manifest)
    print(f"Lab: {manifest['id']:02d} - {manifest['title']}")
    print("Manifest: valid")
    print(f"Working directory: {display_relative(lab_dir / 'starter')}")
    print(f"Cloud credentials required: {str(manifest['execution']['requires_cloud_credentials']).lower()}")
    print(f"Creates billable resources: {str(manifest['execution']['creates_billable_resources']).lower()}")
    print(f"Generated artifacts: {len(artifacts)}")
    for path in artifacts:
        print(f"  - {display_relative(path)}")
    for mode in ("starter", "solution"):
        path = result_path(manifest["id"], mode)
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            print(f"Last {mode} result: {data['outcome']} at {data['recorded_at']}")
        else:
            print(f"Last {mode} result: not recorded")
    return 0


def expanded_argv(argv: list[str]) -> list[str]:
    return [sys.executable if value == "{python}" else value for value in argv]


def run_check(lab_dir: Path, manifest: dict[str, Any], mode: str) -> int:
    validation = manifest["validation"]
    expected_stage = validation["expected_failure_stage"]
    marker = validation["expected_failure_marker"]

    for command in validation["commands"]:
        argv = expanded_argv(command["argv"])
        print(f"==> {command['name']}: {' '.join(argv)}")
        completed = subprocess.run(
            argv,
            cwd=lab_dir / "starter",
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if completed.stdout:
            print(completed.stdout.rstrip())

        if mode == "starter" and command["stage"] == expected_stage:
            if completed.returncode != 0 and marker in completed.stdout:
                print(f"PASS: observed expected starter failure at stage '{expected_stage}'.")
                write_result(
                    manifest["id"],
                    mode,
                    "expected_failure_observed",
                    command["name"],
                    completed.returncode,
                )
                return 0
            outcome = "unexpected_failure" if completed.returncode else "unexpected_pass"
            print(f"FAIL: starter gate {outcome} at stage '{expected_stage}'.", file=sys.stderr)
            write_result(manifest["id"], mode, outcome, command["name"], completed.returncode)
            return 1

        if completed.returncode != 0:
            print(f"FAIL: command '{command['name']}' exited {completed.returncode}.", file=sys.stderr)
            write_result(
                manifest["id"], mode, "unexpected_failure", command["name"], completed.returncode
            )
            return 1

    if mode == "starter":
        print(f"FAIL: expected failure stage '{expected_stage}' was not reached.", file=sys.stderr)
        write_result(manifest["id"], mode, "unexpected_pass", "none", 0)
        return 1

    print("PASS: all canonical solution checks passed.")
    write_result(manifest["id"], mode, "pass", "all", 0)
    return 0


def run_seed(lab_dir: Path, manifest: dict[str, Any]) -> int:
    argv = expanded_argv(manifest["state"]["seed_argv"])
    print(f"==> seed: {' '.join(argv)}")
    completed = subprocess.run(
        argv,
        cwd=lab_dir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if completed.stdout:
        print(completed.stdout.rstrip())
    if completed.returncode != 0:
        print(f"FAIL: seed command exited {completed.returncode}.", file=sys.stderr)
        return completed.returncode
    print(f"PASS: Lab {manifest['id']:02d} state seed completed.")
    return 0


def prepare_state_lab(lab_dir: Path, manifest: dict[str, Any]) -> int:
    """Create a deterministic fresh seed before an aggregate state-lab check."""

    for relative in manifest["state"]["generated_paths"]:
        generated = lab_dir / relative
        if generated.exists():
            remove_path(generated)
            print(f"Removed {display_relative(generated)} before aggregate state check.")
    return run_seed(lab_dir, manifest)


def command_check(args: argparse.Namespace) -> int:
    if bool(args.lab_id) == bool(args.check_all):
        print("ERROR: provide one lab_id or --all, but not both.", file=sys.stderr)
        return 2

    if not args.check_all:
        try:
            lab_dir = resolve_lab(args.lab_id)
            manifest = load_manifest(lab_dir)
        except ManifestError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        return run_check(lab_dir, manifest, args.mode)

    migrated: list[tuple[Path, dict[str, Any]]] = []
    for lab_dir in lab_directories():
        if not (lab_dir / "lab.yaml").is_file():
            continue
        try:
            migrated.append((lab_dir, load_manifest(lab_dir)))
        except ManifestError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1

    if not migrated:
        print("ERROR: no migrated labs with manifests were found.", file=sys.stderr)
        return 1

    print(f"Running {args.mode} gates for {len(migrated)} migrated labs; legacy labs are skipped.")
    outcomes: list[tuple[int, int]] = []
    for lab_dir, manifest in migrated:
        print(f"\n===== Lab {manifest['id']:02d} - {manifest['title']} =====")
        if manifest["type"] == "state-refactor":
            prepared = prepare_state_lab(lab_dir, manifest)
            if prepared != 0:
                outcomes.append((manifest["id"], prepared))
                continue
        outcomes.append((manifest["id"], run_check(lab_dir, manifest, args.mode)))

    failed = [lab_id for lab_id, returncode in outcomes if returncode != 0]
    passed = [lab_id for lab_id, returncode in outcomes if returncode == 0]
    print("\n===== Aggregate summary =====")
    print(f"Passed: {', '.join(f'{lab_id:02d}' for lab_id in passed) or 'none'}")
    print(f"Failed: {', '.join(f'{lab_id:02d}' for lab_id in failed) or 'none'}")
    return 1 if failed else 0


def command_seed(args: argparse.Namespace) -> int:
    try:
        lab_dir = resolve_lab(args.lab_id)
        manifest = load_manifest(lab_dir)
    except ManifestError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if manifest["type"] != "state-refactor":
        print(f"ERROR: Lab {manifest['id']:02d} does not define a state seed workflow.", file=sys.stderr)
        return 1

    return run_seed(lab_dir, manifest)


def remove_path(path: Path) -> None:
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink()


def command_reset(args: argparse.Namespace) -> int:
    try:
        lab_dir = resolve_lab(args.lab_id)
        manifest = load_manifest(lab_dir)
    except ManifestError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    removed: list[Path] = []
    for path in generated_artifacts(lab_dir, manifest):
        remove_path(path)
        removed.append(path)
    for mode in ("starter", "solution"):
        path = result_path(manifest["id"], mode)
        if path.exists():
            path.unlink()
            removed.append(path)

    if removed:
        for path in removed:
            print(f"Removed {display_relative(path)}")
    else:
        print(f"Lab {manifest['id']:02d} is already clean.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="list labs and manifest status")
    list_parser.set_defaults(func=command_list)

    status_parser = subparsers.add_parser("status", help="show one lab's status")
    status_parser.add_argument("lab_id")
    status_parser.set_defaults(func=command_status)

    check_parser = subparsers.add_parser("check", help="run a starter or solution gate")
    check_parser.add_argument("lab_id", nargs="?")
    check_parser.add_argument(
        "--all",
        action="store_true",
        dest="check_all",
        help="run every migrated lab and skip legacy labs without manifests",
    )
    check_parser.add_argument("--mode", choices=("starter", "solution"), default="starter")
    check_parser.set_defaults(func=command_check)

    seed_parser = subparsers.add_parser("seed", help="create isolated starting state for a state lab")
    seed_parser.add_argument("lab_id")
    seed_parser.set_defaults(func=command_seed)

    reset_parser = subparsers.add_parser("reset", help="remove lab-owned generated artifacts")
    reset_parser.add_argument("lab_id")
    reset_parser.set_defaults(func=command_reset)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
