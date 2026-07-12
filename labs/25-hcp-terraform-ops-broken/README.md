# Lab 25：HCP Terraform 运维决策

## 场景

Northstar 通过 HCP Terraform 运行生产基础设施。请阅读 `starter/SCENARIO.md`，然后为源代码驱动运行、例外自动化、拉取请求计划、工作区依赖关系、治理、权限和生产审批选择一种运维模型。

这是一个概念决策 Lab。它不包含 Terraform 配置，也不会连接 HCP Terraform。

## 考查技能

- 区分 VCS 驱动运行与 API 驱动运行
- 使用推测性计划为拉取请求提供反馈
- 在相互依赖的工作区之间确定运行触发器的方向
- 选择生产策略的执行模式并正确解读成本估算
- 分离计划、应用和管理权限
- 定义自动应用与生产审批的边界

## 难度与预计时间

- 难度：困难
- 预计时间：30 分钟

## 执行模式

- 模式：本地概念评分
- Terraform CLI：不使用

## 是否需要云凭据

不需要。本 Lab 不需要 HCP Terraform、AWS 或其他云平台的凭据。

## 成本风险

无。验证过程只读取本地 Markdown 和评分规则文件。

## 初始状态

`starter/student-answer.md` 包含八项值为 `undecided` 的决策以及用于填写理由的占位提示。公开评分规则说明了评分内容，但不包含标准选项。

## 允许编辑的文件

- `starter/student-answer.md`

## 禁止编辑的文件

- `starter/SCENARIO.md`
- `starter/QUESTIONS.md`
- `rubric.yaml`
- `scripts/score_answer.py`
- `lab.yaml`

## 任务

1. 阅读场景和所有选项定义。
2. 将每个 `undecided` 值替换为对应问题中的一个且仅一个选项 ID。
3. 在每个对应的决策标题下编写简明理由：解释所选选项、回应公开评分重点，并用自己的语言将选择与场景事实联系起来。
4. 保持所有决策 ID 和 Markdown 标题不变，以便评分器能够定位它们。

## 约束

- 每个问题必须作出一个决策；不要组合多个选项 ID。
- 设计必须基于最小权限原则，并明确生产审批边界。
- 将成本估算视为运维证据，而不是完整的账单保证。
- 不要添加 Terraform、provider、令牌、组织或工作区凭据。

## 预期初始失败

从仓库根目录运行时，未经修改的 starter 会在评分阶段以 `EXPECTED_CONCEPTUAL_RESPONSE_INCOMPLETE` 失败，因为决策和理由被有意留空。

## 验证命令

在仓库根目录运行仓库门禁：

```bash
python tools/labctl.py check 25
```

直接调用评分器：

```bash
python labs/25-hcp-terraform-ops-broken/scripts/score_answer.py --rubric labs/25-hcp-terraform-ops-broken/rubric.yaml --answer labs/25-hcp-terraform-ops-broken/starter/student-answer.md
```

## 成功标准

- 八项运维决策全部使用有效的选项 ID。
- 选项能够正确区分常规 VCS 运行与例外 API 自动化。
- 拉取请求使用无法执行 apply 的推测性计划路径。
- 工作区依赖方向遵循“生产者成功 apply 后触发消费者”。
- 生产策略、权限和自动应用选项保留明确的审批边界。
- 明确说明成本估算的局限性。
- 每项决策都有理由，并提供可在本地验证的证据，将所选选项与评分重点及场景联系起来，且总分达到公开阈值。

## 本地评分边界

评分器会验证结构化选项、理由的最小长度、理由与所选选项的词汇一致性、对公开评分重点和场景的覆盖，以及是否包含超出复制选项文本的独立解释。所有选项使用完全相同的检查方式，不会暴露标准选项，也不要求使用完全一致的表述。

本地评分无法证明自由文本推理足够细致、事实完整或具有说服力。通过评分表示回答满足确定性的练习评分规则；若没有人工审核，其语义深度仍为 **NOT VERIFIED**。

## 重置说明

```bash
python tools/labctl.py reset 25
```

重置只会删除记录的验证结果，并会有意保留 `student-answer.md`。如需放弃自己的答案，请明确使用版本控制工作流处理。

## 有限提示

- 合并前使用无法执行 apply 的计划很有价值。
- 依赖触发器应从已成功 apply 的工作区指向使用其结果的工作区。
- 拥有发起运行的权限，并不意味着必须拥有执行 apply 的权限。

## 官方参考资料

- [运行模式与选项](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/run/modes-and-options)
- [运行触发器](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/settings/run-triggers)
- [工作区权限](https://developer.hashicorp.com/terraform/cloud-docs/users-teams-organizations/permissions/workspace)
- [工作区设置](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/settings)
