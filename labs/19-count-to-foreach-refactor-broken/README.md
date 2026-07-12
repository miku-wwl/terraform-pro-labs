# Lab 19：从 `count` 重构为 `for_each` 时保留状态

## 场景

三个本地 bucket 记录已经存在于采用 count 索引的状态地址中。请将其重构为稳定的逻辑键，同时不替换任何对象，也不更改其存储值。

## 考查技能

- count 索引与 `for_each` 寻址
- 精确的多实例 `moved` 映射
- 检查 plan JSON 和状态列表
- 保留对象身份的状态重构

## 难度与预计时间

困难，约 35 分钟。

## 执行模式

使用内置 `terraform_data`，并采用预置且隔离的本地状态。

## 是否需要云凭据

否。

## 成本风险

无。

## 初始状态

`python tools/labctl.py seed 19` 会应用受保护的旧配置，并创建 `terraform_data.bucket[0]`、`[1]` 和 `[2]`。starter 已包含所需的键控资源，但没有状态转换声明。

## 允许编辑的文件

- `starter/main.tf`

## 禁止编辑的文件

- `lab.yaml`、`bootstrap/` 和 `scripts/`
- `starter/versions.tf`

## 任务

1. 将索引 0 保留为键 `logs`，索引 1 保留为 `assets`，索引 2 保留为 `archive`。
2. 重构期间产生零个 create/delete 动作。
3. 最终状态中仅保留三个键控地址，并得到 no-op plan。

## 约束

不要删除或重建状态，不要更改记录值，不要使用 `terraform state mv`，也不要恢复使用 `count`。保留受保护的旧配置作为源 fixture。

## 预期初始失败

重新预置状态后，`python tools/labctl.py check 19` 会报告 `EXPECTED_COUNT_TO_FOREACH_REFACTOR_INCOMPLETE`；starter 会规划删除索引地址并创建键控地址。

## 验证命令

```text
python tools/labctl.py reset 19
python tools/labctl.py seed 19
python tools/labctl.py check 19
```

## 成功标准

- 重构前存在全部三个旧地址；
- plan JSON 包含精确的 0→logs、1→assets 和 2→archive no-op 映射；
- 不发生 create 或 delete 动作；
- 最终状态恰好包含三个逻辑键地址；
- 值保持不变，最终 plan 为 no-op。

## 重置说明

```text
python tools/labctl.py reset 19
```

重置只会删除 Lab 19 的 `.lab-state`、生成的初始化文件和 plan 文件，以及结果记录。

## 有限提示

Terraform 需要为每个旧实例声明单独且明确的地址转换。源代码中 map 的顺序不能替代这些转换声明。
