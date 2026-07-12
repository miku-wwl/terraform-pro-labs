# Lab 07：变量校验、前置条件与 Check

## 任务

为同一份部署配置补上三层不同的规则。

`environment` 只能是 `dev`、`stage` 或 `prod`，应在变量输入阶段拒绝其他值。

生产环境不能使用 `t3.micro`，应在部署资源的前置条件中阻止这种组合。

`name_prefix` 少于 5 个字符时，只发出命名质量提醒，不得阻止计划或 apply。



## 约束

- 保留现有变量、资源、输出和 `check` 名称。
- 环境名称使用变量 `validation`；生产规格使用资源 `precondition`；命名质量使用 `check`。
- `check` 只用于提示，不能替代阻塞式校验。
- 只能编辑 `starter/main.tf`。
