# Lab 19：从 `count` 迁移到 `for_each` 并保留 State

## 任务

旧配置已经在 state 中留下三个按位置编号的资源：`terraform_data.bucket[0]`、`[1]` 和 `[2]`。现在配置已改为以记录名称为 key 的 `for_each`。

将旧地址一一迁移到新地址：索引 `0` 对应 `logs`，`1` 对应 `assets`，`2` 对应 `archive`。迁移过程中不能创建或删除资源，也不能改变已有记录的值。

完成后，state 中只应保留三个带名称的地址；再次 plan 必须是 no-op。

## 约束

- 不删除或重建 state。
- 不使用命令式 `terraform state mv`，也不恢复使用 `count`。
- 不改动旧配置 fixture、记录内容或资源名称。
- 只能编辑 `starter/main.tf`。
