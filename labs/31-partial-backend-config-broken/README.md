# Lab 31：S3 Backend 的部分配置

## 任务

`backend-dev.hcl.example`、`backend-test.hcl.example` 和 `backend-prod.hcl.example` 已分别提供各环境的 backend 参数。它们包含 bucket、key、region；这些值属于环境差异，应在执行 `terraform init` 时传入。

在 `starter/main.tf` 中整理 `backend "s3"`：只保留所有环境共用的静态安全设置，移除环境专属的状态路径。backend 块不能引用 `var`、`local`、资源、数据源、模块或插值表达式。

普通的 `environment` 变量只用于根模块配置，不能用于选择或拼接 backend 参数。

## 约束

- 不执行真实 S3 backend 初始化。
- 示例中不得放入真实 bucket 名、访问密钥、令牌、profile 或角色凭据。
- 不要把 backend 参数移到 provider 或 `.tfvars`。
- 只能编辑 `starter/main.tf`。
