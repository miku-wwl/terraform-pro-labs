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

本轮是 Phase 6：Core Authoring Batch A。

只迁移：

- Lab 02
- Lab 10
- Lab 16
- Lab 18

严格复用 Starter Standard v1，不得重新设计目录标准。

重点：

- Lab 02：dynamic configuration、稳定 iteration、conditional resources 和 output shaping。
- Lab 10：root module 与 child modules 的真实 composition 和 output wiring。
- Lab 16：filtered for_each 和稳定 map outputs。
- Lab 18：conditional count、one()、try() 的安全读取。

对每题：

1. 重新确认当前代码是否已经是答案。
2. 建立 canonical solution。
3. 生成不泄露答案的 starter。
4. 编写行为测试，而不是 output 非空测试。
5. 覆盖正常、边界和失败场景。
6. 验证 starter fail、solution pass、reset pass。
7. 更新 matrix 和 migration report。

禁止修改其他 lab。完成四题全批次回归后停止。