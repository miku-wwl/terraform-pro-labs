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


本轮是 Phase 3：整改 Lab 11 Import、Moved Blocks 和 Refactor。

本轮只允许处理：

- Lab 11；
- 为 Lab 11 必需的通用工具增强；
- 对应文档。

目标不是写一个“假设资源已经存在”的 README，而是建立可重复执行的 state-aware refactor lab。

要求建立明确阶段：

- `bootstrap/old-config`
- starter refactor configuration
- canonical solution
- fixtures 或隔离 state 目录
- seed/reset/check 流程

完整流程必须能够：

1. 使用旧 configuration 建立初始 Terraform state。
2. 确认旧 resource address。
3. 切换到 starter configuration。
4. 让学习者完成 import/module refactor/moved block。
5. 验证新 resource address。
6. 验证没有非预期 destroy/create。
7. 验证最终 no-op plan。
8. reset 后再次完整执行。

优先使用不产生云费用的本地资源或 `terraform_data` 模拟 state identity。

只有在 Terraform 语义无法通过本地 fixture 有效训练时，才保留可选 AWS 路径；AWS 路径不得成为默认验收方式。

必须检查：

- import 和 moved 是否在同一题中造成语义混乱；
- 是否应该拆成明确的多个阶段；
- moved block 的 from/to 地址是否真实有效；
- module 地址是否正确；
- reset 是否真正删除临时 state 和 `.terraform`；
- starter 是否因目标行为缺失而失败；
- solution 是否完成 no-op plan。

不得修改 Lab 03、19、26，它们将在后续单独处理。

完成后运行 Lab 11 的 seed、starter gate、solution gate、reset 和第二次重跑。把实际 state addresses 与 plan summary 写入 migration report。完成后停止。