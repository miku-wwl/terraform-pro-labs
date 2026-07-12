# Lab 14：将带 alias 的 provider 传入子模块

## 场景

一个受保护的子模块同时需要默认 AWS provider 和本地 `aws.secondary` alias。当前根模块把子模块的两个 provider 名称都映射到默认配置，因此子模块始终无法收到 secondary region provider。

## 考查技能

- 根模块 provider alias
- 子模块 `configuration_aliases`
- 模块 `providers` 映射
- 使用 mock 跨模块边界验证 provider 身份

## 难度与预计时间

- 难度：中等
- 预计时间：25 分钟

## 执行模式

`aws-mock`。在不使用凭据或 API 调用的情况下，对 AWS provider schema 和模块连接关系执行 plan。

## 是否需要云凭据

不需要。

## 成本风险

无。

## 初始状态

子模块已经正确声明并使用 `aws.secondary`。根模块映射却把默认 provider 同时传给了两个子模块 provider 名称。

## 允许编辑的文件

- `starter/main.tf`

## 禁止编辑的文件

- `starter/versions.tf`
- `starter/modules/`
- `tests/`
- `scripts/`
- `lab.yaml`

## 任务

1. 检查子模块声明的 provider alias 及其 provider 用法。
2. 修正根模块调用，使每个子模块 provider 名称都收到与之匹配的根模块配置。
3. 将 provider 配置保留在根模块中，不要向子模块添加 provider block。
4. 使用两个可区分的 mock provider 结果验证映射。

## 约束

- 不要修改受保护的子模块。
- 不要删除 `configuration_aliases` 或 secondary data source 的 provider 选择。
- 不要通过复制子模块来规避 provider 映射。
- 不要使用凭据或真实 AWS data lookup。

## 预期初始失败

`python tools/labctl.py check 14` 会报告 `EXPECTED_MODULE_PROVIDER_MAPPING_INCOMPLETE`，因为两个子模块 provider 名称都解析到了根模块的默认 provider。

## 验证命令

```text
python tools/labctl.py check 14
python tools/labctl.py status 14
```

## 成功标准

- 子模块必须保留 `configuration_aliases = [aws.secondary]`。
- 模块调用必须将子模块 `aws` 映射到根模块 `aws`，并将子模块 `aws.secondary` 映射到根模块 `aws.secondary`。
- 受保护的源码契约必须验证这一精确映射，同时验证可编辑的根输出仍委托给子模块，而不是重新生成 mock 值。
- Mock 输出必须证明子模块使用了两个不同的 provider 配置。
- 不使用 AWS 凭据或 API 调用。

## 重置说明

```text
python tools/labctl.py reset 14
```

## 有限提示

- 模块 `providers` map 中的键是子模块本地的 provider 名称；值是调用方的配置。
- 子模块不会自动继承 provider alias。
