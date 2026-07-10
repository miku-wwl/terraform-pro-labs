你正在继续整改 tf labs。

开始工作前，必须先读取并检查：

* `AGENTS.md`，如果存在；
* `docs/audit-report.md`；
* `docs/lab-matrix.csv`；
* `docs/lab-standard.md`；
* `docs/migration-report.md`，如果存在；
* 当前分支；
* `git status`；
* 最近 5 个 commit；
* 本轮涉及的全部 README、Terraform configuration、tests、fixtures 和 scripts。

仓库中的当前文件和 Git 历史是事实来源。不要依赖上一轮对话记忆。

本轮范围限制优先级高于早期总提示词。即使早期提示词要求继续后续实验，也只能完成本轮明确列出的任务。

通用限制：

1. 不得修改本轮范围之外的 lab。
2. 不得顺手重构无关文件。
3. 不得执行真实 AWS apply。
4. 不得要求或读取真实云凭据。
5. 不得通过删除、弱化或绕过测试使结果通过。
6. 不得在 starter 中留下 canonical solution 或明显泄露完整表达式的提示。
7. 不得声称未实际执行的命令已经通过。
8. 无法验证的项目必须标记为 `NOT VERIFIED` 并说明原因。
9. 如果审计文档与实际代码冲突，以代码和实际执行结果为准，并同步修正文档。
10. 不得改变已经冻结的 lab 标准，除非发现明确缺陷；任何标准变更都必须记录原因和受影响实验。

工作流程：

1. 先检查本轮范围，输出简短执行计划。
2. 再进行修改。
3. 对 starter 执行预期失败验证。
4. 对 canonical solution 执行通过验证。
5. 测试 reset 后能否再次运行。
6. 更新 `docs/lab-matrix.csv` 和 `docs/migration-report.md`。
7. 输出修改文件、验证命令、实际结果和未解决风险。
8. 本轮结束后停止，不得自动开始下一轮。


本轮是 Phase 5：Pilot Quality Gate。

本轮不得新增或迁移任何 lab。

只审核和修复以下 pilot：

- Lab 01
- Lab 07
- Lab 11
- Lab 25
- Lab 31

以及这些 lab 依赖的公共工具和文档。

逐项检查：

1. README 与代码一致。
2. `lab.yaml` 与实际执行模式一致。
3. editable/protected paths 正确。
4. starter 中没有 canonical solution。
5. TODO 没有泄露完整表达式。
6. starter 在预期阶段、因预期原因失败。
7. solution 通过全部对应验证。
8. reset 后可以第二次执行。
9. Windows 和 Linux 路径处理合理。
10. 没有真实云 apply。
11. tests 没有只检查非空 output。
12. error messages 可以定位学习目标。
13. conceptual lab 的评分规则可解释。
14. state lab 的 address 和 no-op plan 可复现。
15. backend lab 不依赖真实 S3。

执行：

- 五个 pilot 的独立检查；
- `python tools/labctl.py check --all`，但此时只应把已迁移 pilot 作为可执行对象；
- reset 后重新执行全部 pilot；
- solution leakage scan；
- README/manifest consistency scan。

允许修复 pilot 和公共框架缺陷。

不得修改其余 27 个 lab。

完成后：

- 将 `docs/lab-standard.md` 标记为 Starter Standard v1；
- 在 migration report 中记录 pilot gate；
- 输出每个 pilot 的 starter、solution、reset 状态；
- 列出仍未解决的风险。

完成后停止。