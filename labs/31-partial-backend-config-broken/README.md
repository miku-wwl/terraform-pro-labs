# Lab 31：S3 Backend 部分配置

## 任务

1. 将所有 backend 共用的安全行为保留在静态 `backend "s3"` 块中。
2. 从该块中移除应在初始化时提供的环境专属设置。
3. 不要在 backend 块中引用 `var`、`local`、`module`、data source、resource 或插值语法。
4. 确认每个示例文件都提供了初始化时所需的环境专属 backend 值。
5. 让普通 `environment` 变量只供根模块使用。



## 约束

- 默认练习不要执行真实的 S3 backend 初始化。
- 不要在示例中放置 access key、secret key、令牌、profile、角色凭据或真实 bucket 名称。
- 不要让 backend 值依赖普通输入变量。
- 不要将 S3 backend 设置移动到 provider 配置或 `.tfvars` 文件。



## 可编辑文件

- `starter/main.tf`
