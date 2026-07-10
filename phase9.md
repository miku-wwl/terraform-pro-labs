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


本轮是 Phase 9：Provider and AWS Wiring Batch A。

只迁移：

- Lab 06
- Lab 08
- Lab 09
- Lab 14

分类并记录每题执行模式：

- local
- aws-mock
- aws-plan
- aws-live-optional

重点：

- Lab 06：required_providers、provider alias 和 authentication troubleshooting。
- Lab 08：IAM role、policy attachment、instance profile 和 EC2 wiring。
- Lab 09：security group 与独立 rule resources。
- Lab 14：root aliased providers 传递给 child modules。

要求：

- 默认不执行真实 AWS apply；
- 不依赖真实账号中的 AMI、VPC 或资源；
- 可以使用 provider mocking，但必须实际验证当前 Terraform 版本支持所使用的语法；
- provider alias tests 必须验证 module provider mapping；
- IAM tests 必须验证完整 dependency chain；
- SG tests 必须检查独立规则，而不是只检查 SG 存在。

完成后停止。
