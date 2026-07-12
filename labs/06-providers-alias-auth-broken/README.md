# Lab 06：Provider 要求、别名与认证边界

## 场景

根配置通过默认和带别名的 provider 配置读取两个 AWS region。次要 region 的读取被意外路由到默认 provider，而默认配置固定了某台工作站专属的 profile，破坏了认证的可移植性。

## 考查技能

- 声明 `required_providers` 的 source 和 version
- 配置根 provider 别名并为每个对象选择 provider
- 排查标准 AWS 凭据链问题
- 使用无需凭据的 Terraform mock provider 测试

## 难度与预计时间

- 难度：中等
- 预计时间：25 分钟

## 执行模式

`aws-mock`。Terraform 会安装 AWS provider schema，但不会执行认证或发起 AWS API 调用。

## 是否需要云凭据

不需要。

## 成本风险

无；计划只使用 mock provider。

## 初始状态

受保护的 provider 要求是有效的。次要 data source 使用了错误的 provider 配置，而默认 provider 固定了一个不存在的本地 profile。

## 允许编辑的文件

- `starter/main.tf`

## 禁止编辑的文件

- `starter/versions.tf`
- `tests/`
- `scripts/`
- `lab.yaml`

## 任务

1. 确认 required provider 的 source 和兼容的主版本约束。
2. 将每个 region data source 路由到预期的 provider 配置。
3. 移除工作站专属的认证选择，使标准 AWS 凭据链解析保持可移植性。
4. 在不使用凭据的情况下，通过 mock 结果验证两条 provider 路径。

## 约束

- 不得添加 access key、secret key、token、account 标识符或凭据 fixture。
- 不得添加凭据验证 skip_* 标志来代替正确认证。
- 保留两个已配置的 region 和 `aws.secondary` 别名。
- 不得编辑受保护的测试或 provider 要求。

## 预期初始失败

`python tools/labctl.py check 06` 会报告 `EXPECTED_PROVIDER_ALIAS_AUTH_INCOMPLETE`，因为次要读取使用了默认 provider，并且认证固定到本地 profile。

## 验证命令

```text
python tools/labctl.py check 06
python tools/labctl.py status 06
```

## 成功标准

- AWS provider 要求保留 `hashicorp/aws` source 和 `~> 6.0` 约束。
- 默认 provider 保持为 `us-east-1`；`aws.secondary` 保持为 `us-west-2`。
- mock 输出和源代码检查证明 primary 与 secondary 读取使用各自预期的 provider 配置。
- Terraform 配置中不得固定 profile、credential/config file、显式凭据值、assume-role 块或 `skip_*` 绕过配置。
- 不发生真实 AWS 认证或 API 请求。

## 重置说明

```text
python tools/labctl.py reset 06
```

## 有限提示

- 当 data source 或资源不应使用默认配置时，需要为其显式指定 provider。
- 可移植的根模块通常让凭据来自标准外部凭据链。
