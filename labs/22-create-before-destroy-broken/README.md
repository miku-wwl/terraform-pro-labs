# Lab 22：先创建后销毁的替换顺序

## 场景

release 是不可变的，因此更改 release 标识符时必须替换本地服务记录。当前替换会先销毁旧记录。请为重视可用性的发布配置合适的 lifecycle 顺序。

## 考查技能

- 替换与原地更新的区别
- lifecycle 动作顺序
- 读取 JSON plan 动作
- 识别重叠期间容量与唯一性之间的权衡

## 难度与预计时间

- 难度：中等
- 预计时间：20 分钟

## 执行模式

不使用 provider 的 Terraform，仅在验证器临时目录中创建状态。

## 是否需要云凭据

否。

## 成本风险

无。

## 初始状态

`triggers_replace` 使 release 变更成为真正的替换，但 starter 使用 Terraform 默认的先删除后创建顺序。

## 允许编辑的文件

- `starter/main.tf`

## 禁止编辑的文件

- `starter/versions.tf`
- `scripts/`
- `lab.yaml`

## 任务

1. 保留现有替换触发器和资源地址。
2. 配置重叠替换，使 plan 先创建新的服务记录，再删除旧记录。
3. 对未更改的输入保留 no-op plan，并让仅名称变更保持为原地更新。
4. 运行有状态验证器并检查每个 plan 的动作序列。

## 约束

- 不要移除或削弱 `triggers_replace`。
- 不要将 release 变更转换为原地更新。
- 不要更改受保护的验证器。
- 保持该 Lab 不使用 provider。

## 预期初始失败

`python tools/labctl.py check 22` 会报告 `EXPECTED_CREATE_BEFORE_DESTROY_INCOMPLETE`；验证器观察到将 `release` 从 `v1` 更改为 `v2` 后产生了 `delete, create` 动作。

## 验证命令

```text
python tools/labctl.py check 22
python tools/labctl.py status 22
```

## 成功标准

- release 变更仍然是替换。
- `terraform_data.service` 的 plan JSON 动作恰好为 `create, delete`。
- 未更改的输入产生 no-op，而仅更改 `service_name` 仍为 `update`。
- 受保护的源代码契约将 `triggers_replace` 的作用域精确限定为 `var.release`。
- 检查会创建并删除隔离的临时状态。
- 不发生云操作或凭据查询。

## 重置说明

```text
python tools/labctl.py reset 22
```

## 有限提示

- 替换原因与替换顺序是两个不同的问题。
- plan JSON 中的动作顺序揭示了 Terraform 首先处理哪个对象。
