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


本轮是 Phase 4：完成 conceptual 和 partial-backend 两类 pilot。

只允许处理：

- Lab 25；
- Lab 31；
- 必需的公共评分或 manifest 工具；
- 对应文档。

Lab 25 要求：

1. 不再把 HCP Terraform 场景问题伪装成 locals 和 outputs。
2. 转换为真正的场景判断实验，例如：
   - `SCENARIO.md`
   - `QUESTIONS.md`
   - `student-answer.md`
   - `rubric.yaml`
3. canonical answer 只能存在于 solution 隔离位置。
4. 题目覆盖：
   - VCS-driven runs；
   - API-driven runs；
   - speculative plans；
   - run triggers；
   - policy enforcement；
   - cost estimation；
   - team permissions；
   - auto-apply 和 production approval boundaries。
5. 评分以关键决策点为主，不能依赖全文字符串完全相等。
6. starter 不得泄露 answer key。

Lab 31 要求：

1. 真正演示 partial backend configuration。
2. 提供：
   - 静态 backend block；
   - `backend-dev.hcl.example`
   - `backend-test.hcl.example`
   - `backend-prod.hcl.example`
3. 清楚区分：
   - backend configuration；
   -普通 input variables；
   - init-time parameters。
4. 默认验收不得连接真实 S3 backend。
5. 不得在示例中放入凭据、真实 bucket 或敏感信息。
6. 验证 README 命令真实可执行。
7. 测试或静态检查必须识别 backend block 中不允许的动态表达式和错误硬编码模式。
8. reset 必须处理 backend initialization metadata。

分别验证：

- Lab 25 的 starter、rubric 和 solution scoring；
- Lab 31 的 safe local/static validation、starter failure、solution pass 和 reset。

不得开始其他 conceptual、backend 或 state lab。完成后停止。