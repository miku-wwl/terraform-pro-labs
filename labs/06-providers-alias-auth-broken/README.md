# Lab 06：Provider 要求、别名与认证边界

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



## 可编辑文件

- `starter/main.tf`
