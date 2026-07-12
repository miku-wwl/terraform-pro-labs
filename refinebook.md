## 核心知识

- `lifecycle`：配置资源生命周期行为。
- `prevent_destroy = true`：阻止 Terraform 销毁资源。
- 该规则必须写在需要保护的资源内部；只影响销毁，不影响创建。

## 最小代码

```hcl
resource "terraform_data" "deployment_record" {
  input = {
    name = "audit-log"
  }

  lifecycle {
    prevent_destroy = true
  }
}
```

## 核心知识（Lab 2）

- `map + for_each`：用业务键创建稳定资源地址，如 `record["logs"]`。
- `each.key` 是 map 的键；`each.value` 是对应对象。
- map 推导式：`for key, value in map : key => value if 条件`，用于筛选可选资源。
- `merge(base, item)`：键名冲突时，后面的 `item` 会覆盖前面的 `base`。
- `optional(...)` 未提供时为 `null`；用变量 `validation` 拒绝无效输入。

## 最小代码（Lab 2）

```hcl
resource "terraform_data" "record" {
  for_each = var.catalog

  input = {
    name = each.key
    tags = merge(local.base_tags, each.value.tags)
  }
}

resource "terraform_data" "retention" {
  for_each = {
    for key, item in var.catalog : key => item
    if item.retention_days != null
  }

  input = each.value.retention_days
}

output "records" {
  value = { for key, item in terraform_data.record : key => item.input }
}
```

## 核心知识（Lab 3）

- `import`：将已有资源 ID 登记到 Terraform state 地址，不创建资源。
- `moved`：将 state 中的旧地址迁移到新地址，不重建资源。
- `import` 是“外部 ID → Terraform 地址”；`moved` 是“旧地址 → 新地址”。

## 最小代码（Lab 3）

```hcl
import {
  for_each = var.import_ids
  to       = random_id.legacy[each.key]
  id       = each.value
}

moved {
  from = random_id.legacy["api"]
  to   = module.record["api"].random_id.this
}
```

## 核心知识（Lab 4）

- `terraform_remote_state`：读取另一份 state 的根模块输出。
- `backend` 决定当前配置的 state 存放位置；不能引用变量或表达式。
- S3 backend：共享安全设置写在 `.tf` 中，`bucket`、`key`、`region` 在初始化时提供。

## 最小代码（Lab 4）

```hcl
data "terraform_remote_state" "network" {
  backend = "local"
  config  = { path = var.producer_state_path }
}

locals {
  network = data.terraform_remote_state.network.outputs.network
}

terraform {
  backend "s3" {
    encrypt      = true
    use_lockfile = true
  }
}
```

## 核心知识（Lab 5）

- `terraform.workspace`：返回当前 workspace 名称。
- local backend 的非默认 workspace state 位于 `terraform.tfstate.d/<workspace>/terraform.tfstate`。
- consumer 应读取同名 producer workspace 的 state。
- `precondition`：在计划前阻止不符合条件的资源配置。

## 最小代码（Lab 5）

```hcl
locals {
  environment = terraform.workspace
  state_path  = "${var.state_root}/terraform.tfstate.d/${terraform.workspace}/terraform.tfstate"
}

resource "terraform_data" "deployment" {
  lifecycle {
    precondition {
      condition     = terraform.workspace != "prod" || var.instance_type != "t3.micro"
      error_message = "t3.micro is not allowed in prod."
    }
  }
}
```

## 核心知识（Lab 6）

- `alias`：为同一 provider 定义多套配置。
- 未指定 `provider` 时使用默认配置；别名配置需显式选择。
- `provider = aws.secondary` 是 Terraform 元参数，不是数据源专属字段。
- 不写死 `profile` 或密钥，让 AWS 使用标准凭据链。

## 最小代码（Lab 6）

```hcl
provider "aws" {
  region = "us-east-1"
}

provider "aws" {
  alias  = "secondary"
  region = "us-west-2"
}

data "aws_region" "primary" {}

data "aws_region" "secondary" {
  provider = aws.secondary
}
```

## 核心知识（Lab 7）

- `validation`：在输入阶段拒绝无效变量值。
- `precondition`：在资源计划前阻止不安全的配置组合。
- `check`：断言失败只发出警告，不阻止计划或 apply。

## 最小代码（Lab 7）

```hcl
variable "environment" {
  type = string
  validation {
    condition     = contains(["dev", "stage", "prod"], var.environment)
    error_message = "Unsupported environment."
  }
}

resource "terraform_data" "deployment" {
  lifecycle {
    precondition {
      condition     = var.environment != "prod" || var.instance_type != "t3.micro"
      error_message = "t3.micro is not allowed in prod."
    }
  }
}

check "name_quality" {
  assert {
    condition     = length(var.name_prefix) >= 5
    error_message = "Prefix is too short."
  }
}
```

## 核心知识（Lab 8）

- EC2 权限链：`EC2 → Instance Profile → IAM Role → IAM Policy`。
- Role 的信任策略决定“谁能扮演”；Policy 决定“能做什么”。
- 用资源引用连接 Role、Policy 与 Profile，避免硬编码名称。
- IAM Policy 应遵循最小权限原则。

## 最小代码（Lab 8）

```hcl
resource "aws_iam_role_policy_attachment" "app" {
  role       = aws_iam_role.app.name
  policy_arn = aws_iam_policy.app.arn
}

resource "aws_iam_instance_profile" "app" {
  role = aws_iam_role.app.name
}

resource "aws_instance" "app" {
  iam_instance_profile = aws_iam_instance_profile.app.name
}
```
