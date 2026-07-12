# Lab 03：导入集合并重构为模块实例

## 场景

学习者状态之外已存在两个本地生成的服务身份。请先将二者纳入各自旧有的带键根资源地址，再将它们重构为对应的子模块实例，同时保持两个身份均不发生变化。

## 考查技能

- 使用带键实例进行声明式导入
- 检查精确的状态地址
- 使用 `moved` 块将根实例迁移到模块实例
- 检查计划 JSON 并最终证明计划为 no-op

## 难度与预计时间

- 难度：困难
- 预计时间：40 分钟

## 执行模式

在 `.lab-state/` 下使用隔离本地状态，并使用逻辑型 HashiCorp `random` provider。

## 是否需要云凭据

不需要。本 Lab 不使用云 provider 或远程服务。

## 成本风险

无。

## 初始状态

`python tools/labctl.py seed 03` 会应用 `bootstrap/old-config`，验证两个旧地址，捕获它们的导入标识符，然后只解除这些 bootstrap 绑定。之后，受保护的验证脚本会在 `starter/import-stage` 和 `starter/refactor-stage` 之间持续使用同一份全新的学习者状态。

## 允许编辑的文件

- `starter/import-stage/main.tf`
- `starter/refactor-stage/main.tf`

## 禁止编辑的文件

- `lab.yaml`、`bootstrap/`、`starter/modules/`、`starter/import-stage/versions.tf`、
  `starter/refactor-stage/versions.tf` 和 `scripts/`

## 任务

1. 为本 Lab 执行 seed，并检查两个旧的带键地址。
2. 将每个提供的标识符声明式导入其对应的根地址。
3. 将两个对象重构到所提供的带键模块实例中。
4. 保留两个身份，并最终得到 no-op 计划。

## 约束

- 不得硬编码生成的标识符，也不得复制状态文件。
- 不得使用命令式 `terraform import` 或 `terraform state mv` 作为解决方案。
- 不得更改键、字节长度、模块名称或资源名称。

## 预期初始失败

未经修改的 starter 会通过格式检查、初始化和验证，随后报告 `EXPECTED_COLLECTION_REFACTOR_INCOMPLETE`，因为它计划创建两个身份，而不是导入它们。

## 验证命令

```text
python tools/labctl.py reset 03
python tools/labctl.py seed 03
python tools/labctl.py status 03
python tools/labctl.py check 03
python tools/labctl.py check 03 --mode solution
```

## 成功标准

- 导入计划恰好包含两个受保护的旧地址，且不包含任何 create/delete 动作。
- 导入后的状态和标识符与 fixture 完全匹配。
- 重构计划记录两个精确的旧地址到模块地址映射，且不包含任何 create/delete 动作。
- 最终状态只包含两个目标模块地址，保留两个标识符，并且计划无任何变更。

## 重置说明

`python tools/labctl.py reset 03` 仅删除 Lab 03 的 `.lab-state/`、Terraform 产物和已记录的结果。

## 有限提示

- 导入集合与资源集合应使用相同的稳定键。
- 带键实例之间的迁移必须明确指定无歧义的源地址和目标地址。
