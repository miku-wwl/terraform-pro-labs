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


本轮是 Phase 2：建立 starter 框架，并整改两个基础 pilot labs。

本轮只允许处理：

- 仓库级 starter 工具基础；
- Lab 01；
- Lab 07；
- 对应文档。

先确认 Phase 1 的三个审计文档存在且内容完整。

第一步：保护上游状态

如果尚未完成：

1. 保存当前原始状态为本地 tag 或 branch：
   - `upstream-snapshot`
   - `legacy-solution-candidate`
2. 不得 push，不得 force-push。
3. 确保当前工作位于独立整改分支，例如：
   - `refactor/starter-v1`

第二步：建立最小公共框架

创建并实现本轮实际需要的最小版本：

- `tools/labctl.py`
- manifest/schema 校验；
- `list`；
- `status`；
- `reset`；
- `check`；
- Windows 和 Linux 兼容；
- starter expected-failure 结果识别；
- solution pass 结果记录。

不要提前实现尚未需要的大型框架。

第三步：整改 Lab 01

要求：

- README、任务和验收完全围绕 Terraform CLI 与 `prevent_destroy`；
- 删除无关的 validation、precondition、check criteria；
- starter 不得包含 `prevent_destroy` 的答案；
- 避免依赖人工填写全球唯一 bucket name；
- 默认不执行真实 AWS apply；
- 测试必须真正判断 lifecycle 目标，而不是只检查 output；
- starter 必须在与本题目标相关的测试处失败；
- canonical solution 必须通过。

第四步：整改 Lab 07

要求：

- 当前完整 validation、precondition、check 和测试实现不得继续留在 starter；
- 重新建立 canonical solution；
- starter 只保留必要骨架；
- TODO 不得给出完整 condition；
- 测试覆盖：
  - 正常输入；
  - variable validation 失败；
  - precondition 失败；
  - check block 行为；
- README 必须要求运行 `terraform test`；
- starter 必须按预期失败；
- solution 必须通过。

允许修改：

- 仓库级工具文件；
- Lab 01；
- Lab 07；
- 对应 docs。

禁止修改其他 lab。

完成后运行：

- `python tools/labctl.py status 01`
- `python tools/labctl.py check 01`
- `python tools/labctl.py reset 01`
- `python tools/labctl.py status 07`
- `python tools/labctl.py check 07`
- `python tools/labctl.py reset 07`

记录 starter 和 solution 的实际验证结果。完成后停止。