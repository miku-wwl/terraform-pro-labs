# Lab 06：使用 Provider 别名管理多区域

## 任务

本 Lab 配置了两个 AWS 区域：默认 provider 使用 `us-east-1`，带 `secondary` 别名的 provider 使用 `us-west-2`。

在 `starter/main.tf` 中，让两个 `aws_region` 数据源分别使用正确的 provider 配置，使输出能反映这两个区域。

移除绑定到某台工作站的 profile 配置，让 AWS 按标准凭据链获取认证信息。不要改动 `versions.tf` 中已给定的 provider 来源和版本范围。



## 约束

- 不要在代码中写入 access key、secret key、token、账号 ID 或测试凭据。
- 不要使用 `skip_*` 参数绕过认证或校验。
- 保留两个区域，以及 `aws.secondary` 这个别名。
- 只能编辑 `starter/main.tf`。
