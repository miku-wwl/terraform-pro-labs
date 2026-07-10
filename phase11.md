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


本轮是 Phase 11：State and Cross-Stack Batch A。

只迁移：

- Lab 03
- Lab 04
- Lab 05

重点：

- Lab 03：import、moved block 和 module refactor。
- Lab 04：backend rules、producer/consumer 和 terraform_remote_state。
- Lab 05：workspaces 和 cross-stack data flow。

严格复用 Lab 11 和 Lab 31 已验证的 state/backend 模式，但不得简单复制题目。

要求：

- 每题有可重复 bootstrap/fixture；
- 不允许只写“假设资源已存在”；
- producer 和 consumer 必须明确分离；
- 默认使用 local state fixture；
- workspace reset 不得污染用户其他 workspace；
- 验证 state addresses；
- 验证无非预期 destroy/create；
- 适用时验证最终 no-op plan；
- 远程 backend 只能作为可选扩展。

完成三题及全部 state pilot 回归后停止。
