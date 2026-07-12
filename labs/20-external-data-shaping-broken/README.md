# Lab 20：外部 JSON 与 CSV 数据塑形

## 场景

应用目录和 bucket 策略表分别以 JSON 与 CSV 文件的形式提供。starter 已解码这两个文件，但仍保留基于位置的身份，并保留以原始字符串为字段的 CSV 行。请在使用这些数据前完成规范化。

## 考查技能

- `file`、`jsondecode` 和 `csvdecode`
- 集合规范化与类型转换
- 稳定的 `for_each` 键
- map 形式的输出和空输入行为

## 难度与预计时间

- 难度：中等
- 预计时间：25 分钟

## 执行模式

使用确定性 fixture 和 `terraform_data` 在本地编写 Terraform 配置。

## 是否需要云凭据

否。

## 成本风险

无。

## 初始状态

starter 会读取受保护的 fixture 并过滤已禁用的应用，但它使用数字身份、返回 list，并将解码后的 CSV 字段保留为字符串。

## 允许编辑的文件

- `starter/main.tf`

## 禁止编辑的文件

- `starter/versions.tf`
- `fixtures/`
- `tests/`
- `scripts/`
- `lab.yaml`

## 任务

1. 将已启用的 JSON 应用记录规范化为以应用名称为键的 map。
2. 将该稳定 map 用于应用记录，并在输出中保留这些键。
3. 将 CSV 行规范化为以 bucket 名称为键的 map。
4. 将非空生命周期天数转换为数字，并将空字段表示为 `null`。
5. 无需特殊处理即可支持受保护的空输入和边界 fixture。
6. 保留对所选 JSON 和 CSV 输入的文件名验证边界。

## 约束

- 从所选 fixture 文件读取数据；不要在 HCL 中复写 fixture 内容。
- 不要使用数字或基于位置的资源键。
- 不要编辑受保护的 fixture 或测试。
- 保持默认工作流不使用 provider 且仅在本地运行。

## 预期初始失败

`python tools/labctl.py check 20` 会报告 `EXPECTED_EXTERNAL_DATA_SHAPING_INCOMPLETE`，因为解码结果不具备所需的稳定 map 结构，也没有规范化 CSV 类型。

## 验证命令

```text
python tools/labctl.py check 20
python tools/labctl.py status 20
```

## 成功标准

- 默认受管理应用的资源键恰好为 `assets` 和 `logs`。
- 应用值保留精确的团队和 versioning 数据。
- bucket 设置以名称为键，生命周期天数为数字或 null。
- 空 JSON 产生零个应用资源和一个空 map。
- CSV 中零天的边界值保持为数字零。
- 无效的 fixture 扩展名会被对应的输入变量拒绝。

## 重置说明

```text
python tools/labctl.py reset 20
```

## 有限提示

- 先解码，再将数据重塑为 `for_each` 使用的集合。
- 在进行数字转换前，先规范化 CSV 中的空字符串。
