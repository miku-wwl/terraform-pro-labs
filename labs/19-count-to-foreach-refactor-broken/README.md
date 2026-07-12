# Lab 19：从 `count` 重构为 `for_each` 时保留状态

## 任务

1. 将索引 0 保留为键 `logs`，索引 1 保留为 `assets`，索引 2 保留为 `archive`。
2. 重构期间产生零个 create/delete 动作。
3. 最终状态中仅保留三个键控地址，并得到 no-op plan。



## 约束

不要删除或重建状态，不要更改记录值，不要使用 `terraform state mv`，也不要恢复使用 `count`。保留受保护的旧配置作为源 fixture。



## 可编辑文件

- `starter/main.tf`
