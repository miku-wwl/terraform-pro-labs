# Lab 15：条件式 S3 版本控制、生命周期、标签与输出

## 场景

一个应用组合按逻辑名称定义 S3 bucket。当前配置会为每个 bucket 创建可选资源，赋予 common tag 错误的优先级，并返回基于位置的输出。在不访问 AWS 的情况下修正该模型。

## 考查技能

- 使用 `for_each` 获得稳定的资源标识
- 条件式 versioning 和 lifecycle 资源
- 分层 tag 合并和覆盖优先级
- map 形态的输出
- AWS mock-provider 测试

## 难度与预计时间

- 难度：中等
- 预计时间：25 分钟

## 执行模式

通过 Terraform mock provider 对 AWS provider schema 执行 plan。

## 是否需要云凭据

不需要。测试不会进行身份验证，也不会调用 AWS API。

## 成本风险

无。该工作流只创建 mock plan。

## 初始状态

所有 bucket 都会获得 versioning 和 lifecycle 资源；缺失的 retention 会被替换为七天；common tag 会覆盖 bucket tag；输出为 list。

## 允许编辑的文件

- `starter/main.tf`

## 禁止编辑的文件

- `starter/versions.tf`
- `tests/`
- `scripts/`
- `lab.yaml`

## 任务

1. 让普通 bucket 以输入 map 的每个键作为资源键。
2. 仅在 `versioning` 为 true 时创建版本控制。
3. 仅在设置了 `lifecycle_days` 时创建 lifecycle configuration，并保留匹配的天数值。
4. 合并 common tag 和 bucket 特定 tag，使 bucket 层在键冲突时获胜。
5. 为 bucket 名称、启用版本控制的 bucket 和 lifecycle retention 返回精确的 keyed map。

## 约束

- 保留资源和输出地址。
- 不要硬编码受保护场景中的键。
- 不要引入真实的 AWS plan 或 apply。
- 不要编辑或削弱受保护的测试。

## 预期初始失败

在 format、init 和 validation 通过后，`python tools/labctl.py check 15` 会报告 `EXPECTED_S3_CONDITIONAL_CONFIGURATION_INCOMPLETE`。

## 验证命令

```text
python tools/labctl.py check 15
python tools/labctl.py status 15
```

## 成功标准

- Bucket 键必须与输入 map 完全一致。
- 只有选定的 bucket 才能获得已启用的 versioning 和 lifecycle 资源。
- Lifecycle 天数必须与逻辑 bucket 键保持对应。
- Bucket tag 必须覆盖 common tag。
- 三个输出都必须是精确的 map，包括空的条件式 map。
- 无效的非正 retention 必须在不访问云的情况下被拒绝。

## 重置说明

```text
python tools/labctl.py reset 15
```

## 有限提示

- 为每种可选行为分别构建 collection。
- Merge 顺序决定重复键由哪个 map 获胜。
