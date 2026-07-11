#!/usr/bin/env python3
"""Static release checks for lab manifests, READMEs, paths, and safety."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import labctl


ROOT = Path(__file__).resolve().parents[1]
LABS = ROOT / "labs"
REQUIRED_HEADINGS = (
    "scenario",
    "skills tested",
    "difficulty and estimated time",
    "execution mode",
    "cloud credentials required",
    "cost risk",
    "starting state",
    "files allowed to edit",
    "files not allowed to edit",
    "tasks",
    "constraints",
    "expected initial failure",
    "validation commands",
    "success criteria",
    "reset instructions",
    "limited hints",
)
ALLOWED_LAB_ROOT_FILES = {
    ".gitignore",
    "README.md",
    "lab.yaml",
    "rubric.yaml",
}
ALLOWED_LAB_DIRECTORIES = {"starter", "tests", "fixtures", "bootstrap", "scripts"}
ANSWER_NAME = re.compile(r"(?i)(?:^|[-_.])(solution|solutions|answer[-_]?key)(?:$|[-_.])")
LEAKING_TODO = re.compile(
    r"(?i)TODO[^\n]*(?:for_each\s*=|prevent_destroy\s*=|ignore_changes\s*=|"
    r"replace_triggered_by\s*=|\{\s*for\s+)"
)
SECRET_PATTERNS = (
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?i)aws_secret_access_key\s*="),
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"),
)
WEAK_ASSERTION = re.compile(
    r"(?ms)\bassert\s*\{\s*condition\s*=\s*(?:can\s*\([^\n]+\)|[^\n]+!=\s*null)\s*\n"
)


def is_within(relative: Path, declared: Path) -> bool:
    try:
        relative.relative_to(declared)
    except ValueError:
        return False
    return True


def normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def check_lab(lab_dir: Path) -> list[str]:
    issues: list[str] = []
    try:
        manifest = labctl.load_manifest(lab_dir)
    except labctl.ManifestError as exc:
        return [str(exc)]

    readme_path = lab_dir / "README.md"
    if not readme_path.is_file():
        return [f"{lab_dir.name}: README.md is missing"]
    readme = readme_path.read_text(encoding="utf-8")
    headings = {
        normalized(match.group(1))
        for match in re.finditer(r"(?m)^##\s+(.+?)\s*$", readme)
    }
    for required in REQUIRED_HEADINGS:
        if required not in headings:
            issues.append(f"{lab_dir.name}: README heading missing: {required}")

    first_heading = re.search(r"(?m)^#\s+(.+?)\s*$", readme)
    expected_id = f"lab {manifest['id']:02d}"
    if first_heading is None or expected_id not in normalized(first_heading.group(1)):
        issues.append(f"{lab_dir.name}: README title does not contain {expected_id}")
    elif normalized(manifest["title"]) not in normalized(first_heading.group(1)):
        issues.append(f"{lab_dir.name}: README title differs from manifest title")

    expected_fragments = (
        manifest["difficulty"],
        str(manifest["estimated_minutes"]),
        manifest["validation"]["expected_failure_marker"],
        f"python tools/labctl.py check {manifest['id']:02d}",
        f"python tools/labctl.py reset {manifest['id']:02d}",
    )
    for fragment in expected_fragments:
        if fragment.lower() not in readme.lower():
            issues.append(f"{lab_dir.name}: README missing manifest/workflow value: {fragment}")

    for declared in manifest["editable_paths"] + manifest["protected_paths"]:
        declared_path = Path(declared.rstrip("/"))
        if (
            declared not in readme
            and f"`{declared.rstrip('/')}/`" not in readme
            and f"`{declared_path.name}`" not in readme
        ):
            issues.append(f"{lab_dir.name}: README does not name declared path: {declared}")

    editable = {Path(item) for item in manifest["editable_paths"]}
    protected = [Path(item) for item in manifest["protected_paths"]]
    tracked = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "--", lab_dir.relative_to(ROOT).as_posix()],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if tracked.returncode:
        return [f"{lab_dir.name}: cannot enumerate tracked files: {tracked.stderr.strip()}"]
    for repository_relative in sorted(line for line in tracked.stdout.splitlines() if line):
        path = ROOT / repository_relative
        relative = path.relative_to(lab_dir)
        if relative.parts[0] not in ALLOWED_LAB_DIRECTORIES and (
            relative.name not in ALLOWED_LAB_ROOT_FILES
            and not relative.name.startswith("backend-")
        ):
            issues.append(f"{lab_dir.name}: orphan file outside the directory contract: {relative}")
        if relative not in editable and relative != Path("README.md") and not any(
            is_within(relative, item) for item in protected
        ):
            issues.append(f"{lab_dir.name}: file is neither editable nor protected: {relative}")
        if ANSWER_NAME.search(relative.name):
            issues.append(f"{lab_dir.name}: answer-bearing filename in starter repository: {relative}")

        if path.suffix.lower() in {".tf", ".hcl", ".md", ".py", ".json", ".yaml", ".example", ".fixture"}:
            text = path.read_text(encoding="utf-8")
            if LEAKING_TODO.search(text):
                issues.append(f"{lab_dir.name}: TODO discloses an implementation expression: {relative}")
            if path.suffix.lower() == ".hcl" and WEAK_ASSERTION.search(text):
                issues.append(f"{lab_dir.name}: weak standalone Terraform Test assertion: {relative}")
            for pattern in SECRET_PATTERNS:
                if pattern.search(text):
                    issues.append(f"{lab_dir.name}: possible credential or private key: {relative}")

    if manifest["execution"]["requires_cloud_credentials"]:
        issues.append(f"{lab_dir.name}: default validation requires cloud credentials")
    if manifest["execution"]["creates_billable_resources"]:
        issues.append(f"{lab_dir.name}: default validation creates billable resources")
    return issues


def check_workflow() -> list[str]:
    path = ROOT / ".github" / "workflows" / "terraform-labs.yml"
    if not path.is_file():
        return ["repository: .github/workflows/terraform-labs.yml is missing"]
    text = path.read_text(encoding="utf-8")
    required = (
        "pull_request:",
        "workflow_dispatch:",
        "terraform fmt -check -recursive",
        "python tools/repo_check.py",
        "python tools/labctl.py check --all",
        "ubuntu-latest",
        "windows-latest",
    )
    return [f"workflow: missing required static token: {item}" for item in required if item not in text]


def main() -> int:
    labs = labctl.lab_directories()
    issues: list[str] = []
    if len(labs) != 32:
        issues.append(f"repository: expected 32 lab directories, found {len(labs)}")
    ids: list[int] = []
    for lab_dir in labs:
        issues.extend(check_lab(lab_dir))
        try:
            ids.append(labctl.load_manifest(lab_dir)["id"])
        except labctl.ManifestError:
            pass
    if ids and ids != list(range(1, 33)):
        issues.append(f"repository: manifest IDs are not exactly 01-32: {ids}")
    issues.extend(check_workflow())

    if issues:
        print("Repository release checks failed:")
        for issue in issues:
            print(f"  - {issue}")
        return 1
    print("PASS: 32 manifests, READMEs, path contracts, safety rules, and CI static checks are consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
