# Lab 13：Workspace 感知行为与生产环境防护规则

## 场景

同一个本地 root 被刻意复用于 dev、staging 和 prod workspace。配置必须选择 workspace 特定的设置，同时生产环境必须阻止容量不足以及无人值守的 apply 行为。

## 考查技能

- `terraform.workspace`
- 由 workspace 隔离的本地 state
- 根据环境选择值
- 将 lifecycle precondition 用作生产环境 guardrail

## 难度与预计时间

中等，约 30 分钟。

## 执行模式

仅在 verifier 所有的运行时副本中创建隔离的本地 workspace。

## 是否需要云凭据

不需要。

## 成本风险

无。本 Lab 仅使用内置的 `terraform_data`。

## 初始状态

starter 始终选择 dev 设置，并且生产环境 precondition 过于宽松。verifier 不会在学员源码目录中选择或切换任何 workspace。

## 允许编辑的文件

- `starter/main.tf`

## 禁止编辑的文件

- `lab.yaml`
- `starter/versions.tf`
- `scripts/`

## 任务

1. 根据当前选中的 workspace 推导活动环境。
2. 为 dev、staging 和 prod 选择精确设置。
3. 仅当容量为获准规格之一（`t3.large`、`t3.xlarge` 或 `t3.2xlarge`）且 `auto_approve` 为 false 时，才允许生产环境执行。
4. 保留资源和输出契约。

## 约束

不要添加云资源，不要在学员源码目录中切换 workspace，也不要针对 verifier 路径编写特殊分支。使用一个生产环境 guardrail，并保留文档所述的诊断信息。

## 预期初始失败

当 staging 或 prod workspace 仍然输出 dev 设置时，`python tools/labctl.py check 13` 会报告 `EXPECTED_WORKSPACE_GUARDRAIL_INCOMPLETE`。

## 验证命令

```text
python tools/labctl.py reset 13
python tools/labctl.py check 13
```

## 成功标准

- 运行时必须恰好拥有 default、dev、staging 和 prod workspace；
- 每个环境的 state 中只能包含 `terraform_data.deployment`；
- workspace 输出必须与精确的 replica、tier 和 instance 设置一致；
- 任何 plan 都不得包含 destroy，并且每次 apply 后的 plan 必须为 no-op；
- prod 必须接受全部三种获准规格，拒绝 `t3.micro`、`t3.small` 和一个虽然不属于小规格、但仍未获准的其他 instance family，并独立拒绝 auto-approve。

## 重置说明

```text
python tools/labctl.py reset 13
```

重置操作仅删除 Lab 13 的运行时 workspace、state、plan、初始化文件和结果。

## 有限提示

default workspace 不属于本练习使用的三个环境。guardrail 可以在一个 Boolean 条件中组合非生产环境分支和全部生产环境要求。
