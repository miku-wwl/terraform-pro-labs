# Lab 23：精确的 `ignore_changes` 所有权边界

## 场景

Terraform 管理本地服务记录的 JSON 内容，而外部主机策略只能修改其文件权限。starter 会忽略所有变更，因此也隐藏了 Terraform 所管理内容的漂移。

## 考查技能

- `ignore_changes` 中属性路径的精确性
- 共享所有权边界
- 受控状态漂移与 plan 解读
- 区分允许的 no-op 与必要的状态修正

## 难度与预计时间

- 难度：中等
- 预计时间：20 分钟

## 执行模式

使用 local provider 的 Terraform；受控状态副本仅在验证器临时目录中创建。

## 是否需要云凭据

否。

## 成本风险

无。

## 初始状态

lifecycle 规则在语法上有效，但会忽略每个字段，其中也包括 Terraform 管理的文件内容。

## 允许编辑的文件

- `starter/main.tf`

## 禁止编辑的文件

- `starter/versions.tf`
- `scripts/`
- `lab.yaml`

## 任务

1. 将 lifecycle 例外范围缩小到仅由外部管理的权限字段。
2. 保留 Terraform 对根据服务名称和 release 版本派生的 JSON 内容的管理。
3. 使用仓库检查验证权限、内容和文件名漂移场景。

## 约束

- 不要使用 `ignore_changes = all`。
- 不要忽略 `content`、`filename` 或资源的全部字段。
- 不要删除或修改受保护的 lifecycle 验证器。

## 预期初始失败

`python tools/labctl.py check 23` 会报告 `EXPECTED_IGNORE_CHANGES_BOUNDARY_INCOMPLETE`：权限漂移可以被容忍，但 Terraform 管理的内容和文件名漂移也被错误隐藏。

## 验证命令

```text
python tools/labctl.py check 23
python tools/labctl.py status 23
```

## 成功标准

- 仅外部权限发生漂移时不产生资源动作。
- Terraform 管理的内容发生漂移时产生状态修正动作。
- Terraform 管理的文件名发生漂移时产生状态修正动作。
- lifecycle 例外不会抑制对文件名、名称或版本的管理。
- 受控状态和 plan 仅在受保护的临时检查期间存在。

## 重置说明

```text
python tools/labctl.py reset 23
```

## 有限提示

- lifecycle 忽略路径可以精确指向 provider schema 中的一个属性。
- 正确的共享所有权策略应当区分一个由外部管理的字段与两个受管理字段。
