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



本轮是 Phase 1：只读审计。

本轮任务范围严格限制为：

1. 对整个仓库进行只读审计。
2. 创建或完善：

   * `docs/audit-report.md`
   * `docs/lab-matrix.csv`
   * `docs/lab-standard.md`
3. 审计全部 32 个 lab 的 README、`.tf`、`.tftest.hcl`、modules、fixtures、JSON、CSV、backend 配置和脚本。
4. 判断每个 lab 当前属于：

   * genuine starter
   * partially completed
   * near-complete solution
   * complete solution
   * inconsistent or unusable
5. 找出 README、代码、测试和实际主题之间的不一致。
6. 找出 solution leakage、模板污染、重复实验、无效测试、无法复现的 state 前提和云凭据依赖。
7. 为每个 lab 提出整改建议和执行分类。

本轮禁止：

* 修改任何 `labs/` 下的文件；
* 创建 starter、solution、test、fixture 或 bootstrap；
* 修改现有 Terraform configuration；
* 创建或修改 CI；
* 执行真实云操作；
* 自动开始 pilot labs；
* 因为发现问题而直接修复问题。

允许修改的路径只有：

```text
docs/audit-report.md
docs/lab-matrix.csv
docs/lab-standard.md
```

可以运行安全的只读检查，例如：

```text
git status
git log
find
terraform fmt -check
terraform validate
terraform test
```

但是不得为了让检查通过而修改 lab。

对于无法在当前环境验证的项目，记录为 `NOT VERIFIED`。

完成三个文档后，输出：

* 32 个 lab 的状态统计；
* 最严重的 10 个问题；
* 推荐的整改批次；
* 建议首先处理的 5 个 pilot labs；
* 本轮实际修改的文件。

完成后立即停止。
