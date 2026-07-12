# Lab 08：为 EC2 配置 IAM 权限

## 任务

需要让 EC2 通过 IAM Role 访问指定 S3 bucket。

保留现有的 EC2 信任策略和最小化 S3 权限策略。将应用策略附加到已有的应用 Role，再让 Instance Profile 引用这个 Role，最后把 EC2 实例关联到该 Instance Profile。

所有 IAM 和 EC2 名称都应从 `name_prefix` 派生，避免重复写死名称。



## 约束

- 不要新增 AMI、VPC、subnet 或账号信息的数据查询。
- 不要用硬编码名称替代资源引用。
- 不要在代码中添加凭据，也不要执行真实 apply。
- 只能编辑 `starter/main.tf`。
