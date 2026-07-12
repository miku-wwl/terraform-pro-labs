# Lab 11：Import、moved block 与模块重构

## 场景

某个标识符由旧 Terraform 配置创建，随后从其 bootstrap state 中解除绑定。先将该标识符采用到新的学员 state 中，并保留其原有的根资源地址。确认 import 后，将资源重构到提供的子模块中，同时不得改变其标识，也不得计划 replacement。

Import 与重构被刻意拆分为两个独立阶段，从而避免在一次配置转换中同时出现 import 目标和 moved 源地址。

## 考查技能

- 为隔离的 Terraform state 播种并进行检查
- 以声明式 import 导入到精确的资源地址
- 将根资源地址移动到子模块
- 在重构期间读取 plan JSON 和 state 地址
- 证明标识连续性并得到最终 no-op plan

## 难度与预计时间

- 难度：困难
- 预计时间：35 分钟

## 执行模式

- 模式：本地 state-refactor 工作流
- Backend：位于 `.lab-state/` 下、归本 Lab 所有的本地 state
- Provider：HashiCorp `random`，不访问远程服务的逻辑 provider

## 是否需要云凭据

不需要。该工作流不会配置 AWS，也不会读取任何云凭据。

## 成本风险

无。播种流程和学员工作流仅操作本地 Terraform state。

## 初始状态

每次尝试前先执行 reset 和 seed。seed 命令会将 `bootstrap/old-config` 复制到已忽略的 `.lab-state/` 工作区，执行 apply，验证旧地址 `random_id.legacy_record`，捕获其 import 标识符，然后从 bootstrap state 中移除该绑定。此后，该标识可供学员隔离的 import state 使用。

学员工作流包含两个有序配置：

1. `starter/import-stage` 在旧的根地址采用该标识。
2. `starter/refactor-stage` 将配置形态改为使用提供的模块。

受保护的 verifier 在两个阶段中使用同一个 state。

## 允许编辑的文件

- `starter/import-stage/main.tf`
- `starter/refactor-stage/main.tf`

## 禁止编辑的文件

- `lab.yaml`
- `bootstrap/old-config/`
- `starter/import-stage/versions.tf`
- `starter/refactor-stage/versions.tf`
- `starter/modules/`
- `scripts/`

## 任务

1. 重置并播种本 Lab，然后检查 seed 工作流输出的旧资源地址。
2. 在 import-stage 配置中，以声明方式在现有根资源地址采用生成的标识符。使用提供的 `import_id` 变量；不要硬编码生成值。
3. 运行 solution-mode 检查，确认 imported state 在进入重构 gate 前仅包含旧的根地址。
4. 在 refactor-stage 配置中，将资源移入提供的子模块，同时保留该 state 标识。
5. 运行完整检查，确认目标模块地址、零 create/delete action、标识符不变以及最终 no-op plan。

## 约束

- 必须先完成声明式 import，再进行模块重构。
- 使用配置驱动的地址迁移完成重构；不要用命令式 `terraform state mv` 命令替代。
- 不要更改资源类型、字节长度、模块或资源名称，也不要更改受保护的 verifier 文件。
- 不要硬编码生成的标识符，也不要在阶段之间复制 state 文件。
- 不要添加 AWS 或任何其他云 provider。

## 预期初始失败

播种后，`python tools/labctl.py check 11` 会到达行为 state gate，并报告 `EXPECTED_STATE_REFACTOR_INCOMPLETE`。初始 import 阶段会计划创建一个新标识，而不是采用已播种的标识。修正 import 后，同一个 gate 会继续进入重构阶段，并拒绝任何从根地址到模块地址的 delete/create plan。

## 验证命令

从仓库根目录运行：

```text
python tools/labctl.py reset 11
python tools/labctl.py seed 11
python tools/labctl.py status 11
python tools/labctl.py check 11
python tools/labctl.py check 11 --mode solution
```

普通 check 用于证明未修改的 starter 会因预期原因失败。编辑完两个允许修改的文件后，使用 `--mode solution` 执行通过 gate。这两种模式都会格式化 Lab 11 的所有 Terraform 文件；verifier 会在隔离工作目录中初始化并验证每个阶段，仅 apply 本地逻辑资源，检查保存的 plan JSON，列出 state 地址，并执行最终使用 detailed-exitcode 的 plan。

## 成功标准

- Seed 在释放 state 绑定前建立并报告 `random_id.legacy_record`。
- Import plan 报告一次 import，以及零 add/destroy action。
- Imported state 必须恰好包含 `random_id.legacy_record`，且其标识符与 fixture 一致。
- Refactor plan 必须记录一次到 `module.record.random_id.this` 的精确 move，并包含零 add/destroy action。
- 最终 state 必须恰好包含模块地址，并保留 imported 标识符。
- 后续 plan 报告 `0 to add, 0 to change, 0 to destroy`。
- Reset 会移除 `.lab-state/`，包括其中的 state、plan、fixture 以及嵌套的 `.terraform/` 数据。

## 重置说明

从仓库根目录运行：

```text
python tools/labctl.py reset 11
```

重置操作仅删除 Lab 11 生成的产物和已记录的检查结果，并保留两个允许学员编辑的配置文件。

## 有限提示

- 第一阶段的目标是把提供的标识符与现有配置地址关联起来，而不是生成 replacement。
- 第二阶段只更改地址。Terraform 需要旧地址和新地址的显式记录，才能将此次变更识别为 move，而不是 delete/create。
