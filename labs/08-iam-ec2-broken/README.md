# Lab 08：从 IAM Role 到 EC2 的依赖链

## 任务

1. 保留 EC2 信任关系和范围受限的 S3 权限文档。
2. 将托管策略附加到已声明的应用 role。
3. 保留 role 到 instance profile 的引用。
4. 将 EC2 实例连接到该 instance profile。
5. 保持所有名称均由 `name_prefix` 驱动。



## 约束

- 不得引入 AMI、VPC、subnet 或 account data lookup。
- 不得使用重复硬编码的名称替代引用。
- 不得添加凭据或执行真实 apply。
- 不得编辑受保护的测试。



## 可编辑文件

- `starter/main.tf`
