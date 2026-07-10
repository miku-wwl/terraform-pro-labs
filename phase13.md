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


本轮是 Final Phase：全仓独立质量审查和发布前验收。

本轮原则：

- 不新增实验；
- 不扩大题目范围；
- 不重新设计已冻结标准；
- 只修复全仓验收发现的明确缺陷。

检查全部 32 个 lab。

一、结构检查

- 每个 lab 的 manifest 完整；
- README、代码、测试和目录一致；
- lab ID、title、type、difficulty、execution mode 正确；
- 没有 orphan files；
- 没有答案误放入 starter；
- protected paths 正确。

二、Starter Gate

- 每个 starter 在预期阶段失败；
- 失败原因直接对应学习目标；
- 不因无凭据、网络、随机名称或无关语法错误失败；
- TODO 不泄露完整答案；
- starter 不能已经通过 grader。

三、Solution Gate

- fmt 通过；
- init 通过；
- validate 通过；
- test 通过；
- 适用时 plan 通过；
- state/refactor lab 没有非预期 destroy/create；
- conceptual scoring 通过；
- reset 后能够第二次运行。

四、测试质量

查找并修复：

- 只检查 `!= null` 的弱测试；
- 只检查 `can(...)` 的弱测试；
- 未覆盖失败场景；
- 未覆盖边界场景；
- assertion 与 README 无关；
- 为通过实现而写死的脆弱 assertion；
- provider runtime unknown value 导致的不稳定测试。

五、安全和成本

- 无真实凭据；
- 无 secrets；
- 无默认 AWS apply；
- 无默认付费资源；
- live-cloud 路径明确标为 optional；
- cleanup 文档完整。

六、仓库级执行

实际运行：

- repository format check；
- manifest validation；
- README consistency check；
- starter expected-failure checks；
- solution pass checks；
- reset and rerun；
- `python tools/labctl.py check --all`；
- CI workflow syntax/static validation。

七、最终文档

完成：

- `docs/audit-report.md`
- `docs/lab-matrix.csv`
- `docs/lab-standard.md`
- `docs/migration-report.md`

输出最终汇总：

- 32 个 lab 状态；
- starter verified 数量；
- solution verified 数量；
- reset verified 数量；
- NOT VERIFIED 项目；
- 真实云依赖；
- 剩余发布风险；
- license/attribution 风险；
- 建议的 commit 划分。

不得把无法执行的项目写成 PASS。

完成最终报告后停止。