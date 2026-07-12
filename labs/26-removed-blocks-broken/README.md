# Lab 26：moved 与 removed 的状态语义

## 场景

现有服务记录在配置中被重命名。另一个旧版附件必须退出 Terraform 管理，但由外部拥有的对象需要保留。这是两种不同的状态转换，必须分别表达。

## 考查技能

- 使用 `moved` 转换资源地址
- 使用 `removed` 从配置中移除资源
- `destroy = false` 与计划中的 `forget` 动作
- 通过计划 JSON、状态列表和最终空操作计划进行验证

## 难度与预计时间

难度：中等，预计约 30 分钟。

## 执行模式

使用内置 `terraform_data`，并采用经过 seed 初始化的隔离本地状态。

## 是否需要云凭据

不需要。

## 成本风险

无。

## 初始状态

受保护的旧配置创建 `terraform_data.service_old` 和 `terraform_data.legacy_attachment`。starter 只包含重命名后的服务资源，没有任何转换声明。

## 允许编辑的文件

- `starter/main.tf`

## 禁止编辑的文件

- `lab.yaml`、`bootstrap/` 和 `scripts/`
- `starter/versions.tf`

## 任务

1. 通过地址移动，将服务身份保留在 `terraform_data.service`。
2. 从状态中移除旧版附件，但不得计划销毁它。
3. 最终状态中只保留服务地址，并得到空操作计划。

## 约束

不要删除状态，不要使用 CLI 的状态移动或移除命令，不要保留旧版资源块，也不要允许任何 create/delete 动作。附件必须使用明确保留底层对象的移除语义。

## 预期初始失败

完成种子初始化后，`python tools/labctl.py check 26` 会报告 `EXPECTED_MOVED_REMOVED_REFACTOR_INCOMPLETE`；starter 会计划创建服务，并销毁两个旧资源。

## 验证命令

```text
python tools/labctl.py reset 26
python tools/labctl.py seed 26
python tools/labctl.py check 26
```

## 成功标准

- 初始旧状态包含两个受保护的地址；
- 重命名后的服务具有精确的空操作 `previous_address` 映射；
- 附件的动作必须精确为 `forget`，而不是 `delete`；
- 不发生任何 create/delete 动作；
- 最终状态只包含 `terraform_data.service`，其值保持不变，且计划为空操作。

## 重置说明

```text
python tools/labctl.py reset 26
```

重置只会删除 Lab 26 生成的状态、计划、初始化文件和结果。

## 有限提示

重命名后管理的仍是同一个对象；移除则意味着停止管理某个对象。这两种转换中，只有一种需要通过生命周期设置来控制 Terraform 是否销毁对象。
