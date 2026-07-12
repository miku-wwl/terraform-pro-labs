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
    "场景",
    "考查技能",
    "难度与预计时间",
    "执行模式",
    "是否需要云凭据",
    "成本风险",
    "初始状态",
    "允许编辑的文件",
    "禁止编辑的文件",
    "任务",
    "约束",
    "预期初始失败",
    "验证命令",
    "成功标准",
    "重置说明",
    "有限提示",
)
DIFFICULTY_LABELS = {"easy": "简单", "medium": "中等", "hard": "困难"}
LOCALIZED_TITLES = {
    1: "Terraform CLI 与 `prevent_destroy`",
    2: "使用稳定迭代的动态配置",
    3: "导入集合并重构为模块实例",
    4: "后端边界与本地跨栈状态",
    5: "工作区隔离的跨栈消费",
    6: "Provider 要求、别名与认证边界",
    7: "验证、前置条件、检查与测试",
    8: "从 IAM Role 到 EC2 的依赖链",
    9: "使用独立规则资源的安全组",
    10: "根模块与子模块组合",
    11: "Import、moved block 与模块重构",
    12: "Remote state 消费者与 backend 分离",
    13: "Workspace 感知行为与生产环境防护规则",
    14: "将带 alias 的 provider 传入子模块",
    15: "条件式 S3 版本控制、生命周期、标签与输出",
    16: "过滤后的 for_each 与稳定的 map 输出",
    17: "数据源与跨栈查询边界",
    18: "使用 one() 和 try() 的条件 count",
    19: "从 `count` 重构为 `for_each` 时保留状态",
    20: "外部 JSON 与 CSV 数据塑形",
    21: "动态嵌套 ingress 块",
    22: "先创建后销毁的替换顺序",
    23: "精确的 `ignore_changes` 所有权边界",
    24: "敏感输入、脱敏与安全输出",
    25: "HCP Terraform 运维决策",
    26: "moved 与 removed 的状态语义",
    27: "扁平化集合、稳定键与标签合并",
    28: "Provider 版本约束语义",
    29: "Terraform Test 的顺序状态",
    30: "正则命名验证与规范化",
    31: "S3 Backend 部分配置",
    32: "使用 `replace_triggered_by` 实现依赖驱动替换",
}
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
    heading_matches = list(re.finditer(r"(?m)^##\s+(.+?)\s*$", readme))
    headings = [match.group(1).strip() for match in heading_matches]
    sections: dict[str, str] = {}
    for index, match in enumerate(heading_matches):
        start = match.end()
        end = (
            heading_matches[index + 1].start()
            if index + 1 < len(heading_matches)
            else len(readme)
        )
        sections[match.group(1).strip()] = readme[start:end]
    for required in REQUIRED_HEADINGS:
        count = headings.count(required)
        if count != 1:
            issues.append(
                f"{lab_dir.name}: README heading must appear exactly once: {required} (found {count})"
            )

    first_heading = re.search(r"(?m)^#\s+(.+?)\s*$", readme)
    localized_title = LOCALIZED_TITLES.get(manifest["id"])
    if localized_title is None:
        issues.append(f"{lab_dir.name}: no localized title contract for manifest ID {manifest['id']}")
    else:
        expected_title = f"Lab {manifest['id']:02d}：{localized_title}"
        if first_heading is None or first_heading.group(1) != expected_title:
            issues.append(f"{lab_dir.name}: README title must be exactly: {expected_title}")

    difficulty_label = DIFFICULTY_LABELS.get(manifest["difficulty"])
    if difficulty_label is None:
        issues.append(
            f"{lab_dir.name}: unsupported manifest difficulty: {manifest['difficulty']}"
        )
    else:
        difficulty_section = sections.get("难度与预计时间", "")
        if difficulty_label not in difficulty_section:
            issues.append(
                f"{lab_dir.name}: difficulty section missing localized value: {difficulty_label}"
            )
        if str(manifest["estimated_minutes"]) not in difficulty_section:
            issues.append(
                f"{lab_dir.name}: difficulty section missing estimated minutes: "
                f"{manifest['estimated_minutes']}"
            )

    expected_fragments = (
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
    issues = [f"workflow: missing required static token: {item}" for item in required if item not in text]
    forbidden = ("solution-gates:", "github.ref_name == 'solutions'", "--mode solution")
    issues.extend(
        f"workflow: persisted-solution CI contract is not allowed: {item}"
        for item in forbidden
        if item in text
    )
    return issues


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
