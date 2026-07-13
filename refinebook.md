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
- ⚠ `import` 块中的 `for_each` 需要 Terraform 1.7+；当前 TF Pro 1.6 只需掌握普通单资源 `import`。

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
- ⚠ `use_lockfile = true` 需要 Terraform 1.10+；当前 TF Pro 1.6 的 S3 状态锁使用 `dynamodb_table`。

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

## 核心知识（Lab 9）

- Security Group 本体与规则分开管理，不使用内联 `ingress` / `egress`。
- `for_each = var.ingress_rules`：map 的键就是稳定的规则地址。
- `ip_protocol = "-1"`：允许所有协议；不设置端口。

## 最小代码（Lab 9）

```hcl
resource "aws_vpc_security_group_ingress_rule" "web" {
  for_each = var.ingress_rules

  security_group_id = aws_security_group.web.id
  ip_protocol       = "tcp"
  from_port         = each.value.port
  to_port           = each.value.port
  cidr_ipv4         = each.value.cidr_ipv4
}

resource "aws_vpc_security_group_egress_rule" "all_ipv4" {
  security_group_id = aws_security_group.web.id
  ip_protocol       = "-1"
  cidr_ipv4         = "0.0.0.0/0"
}
```

## 核心知识（Lab 10）

- 根模块通过 `module` 块调用子模块，并传入子模块声明的变量。
- 读取子模块输出：`module.<模块名>.<输出名>`。
- 根模块只负责编排模块，不重复子模块内部逻辑。

## 最小代码（Lab 10）

```hcl
module "naming" {
  source      = "./modules/naming"
  application = var.application
  environment = var.environment
}

module "identity" {
  source      = "./modules/identity"
  name_prefix = module.naming.name_prefix
}

module "compute" {
  source                = "./modules/compute"
  name_prefix           = module.naming.name_prefix
  instance_profile_name = module.identity.instance_profile_name
}

output "stack" {
  value = {
    instance_profile_name = module.identity.instance_profile_name
    instance_reference    = module.compute.instance_reference
  }
}
```

## 核心知识（Lab 11）

- `import`：使用 provider ID 将已有资源纳入指定 state 地址。
- `moved`：不使用 ID，只将已有 state 从旧地址迁移到新地址。
- 重构顺序：先导入，再迁移；最终计划应为 no-op。

## 最小代码（Lab 11）

```hcl
import {
  to = random_id.legacy_record
  id = var.import_id
}

moved {
  from = random_id.legacy_record
  to   = module.record.random_id.this
}
```

## 核心知识（Lab 12）

- 读取另一份 state 的输出：`data.terraform_remote_state.<名称>.outputs.<输出名>`。
- 消费者直接使用生产方 output，不复制网络值。
- 当前配置的 backend 与读取的 remote state 是两件事。
- S3 backend 的 `bucket`、`key`、`region` 在初始化时按环境提供。
- 输出引用：同模块用原始值；父模块读子模块用 `module.child.output_name`；跨 state 用 `terraform_remote_state.x.outputs.output_name`；命令行用 `terraform output output_name`。
- ⚠ `use_lockfile = true` 需要 Terraform 1.10+；当前 TF Pro 1.6 的 S3 状态锁使用 `dynamodb_table`。

## 最小代码（Lab 12）

```hcl
data "terraform_remote_state" "producer" {
  backend = "local"
  config  = { path = var.producer_state_path }
}

resource "terraform_data" "consumer" {
  input = {
    network = data.terraform_remote_state.producer.outputs.network
  }
}

terraform {
  backend "s3" {
    encrypt      = true
    use_lockfile = true
  }
}
```


## 核心知识（Lab 13）

- `terraform.workspace` 可作为环境键，从设置 map 中选择对应配置。
- `precondition` 用于阻止不安全的资源配置组合。
- 生产环境允许规格与审批开关应同时满足。

## 最小代码（Lab 13）

```hcl
locals {
  environment = terraform.workspace
  selected    = local.settings[local.environment]
}

resource "terraform_data" "deployment" {
  lifecycle {
    precondition {
      condition = local.environment != "prod" || (
        contains(["t3.large", "t3.xlarge", "t3.2xlarge"], var.instance_type) &&
        var.auto_approve == false
      )
      error_message = "Production requires an approved size and must not use auto-approve."
    }
  }
}
```

## 核心知识（Lab 14）

- `alias`：同一 provider 的另一套配置，例如另一 AWS 区域。
- 子模块不配置 provider；由根模块在 `providers` map 中传入。
- `configuration_aliases`：子模块声明它需要的别名 provider。
- `aws = aws` 是默认配置映射；`aws.secondary = aws.secondary` 是别名映射。

## 最小代码（Lab 14）

```hcl
provider "aws" {
  region = "us-east-1"
}

provider "aws" {
  alias  = "secondary"
  region = "us-west-2"
}

module "regions" {
  source = "./modules/region_report"
  providers = {
    aws           = aws
    aws.secondary = aws.secondary
  }
}
```

## 核心知识（Lab 15）

- bucket map 的 key 就是稳定的 `for_each` 资源地址。
- 过滤后的 `for_each`：只为满足条件的条目创建独立资源。
- `merge(base_tags, each.value.tags)`：bucket 专属标签覆盖公共标签。
- 输出过滤资源时，用其 key 回查主资源，仍保留原始逻辑名称。

## 最小代码（Lab 15）

```hcl
resource "aws_s3_bucket" "this" {
  for_each = var.buckets
  bucket   = "${var.prefix}-${each.key}"
  tags     = merge(local.base_tags, each.value.tags)
}

resource "aws_s3_bucket_versioning" "this" {
  for_each = {
    for key, item in var.buckets : key => item
    if item.versioning
  }
  bucket = aws_s3_bucket.this[each.key].id
}

resource "aws_s3_bucket_lifecycle_configuration" "this" {
  for_each = {
    for key, item in var.buckets : key => item
    if item.lifecycle_days != null
  }
  bucket = aws_s3_bucket.this[each.key].id
}
```

## 核心知识（Lab 16）

- map 推导式加 `if`：筛出需要创建的资源；禁用项没有资源实例。
- `for_each` 的 key 直接成为资源地址，例如 `deployment["api"]`。
- 资源 map 本身可直接推导为输出；没有实例时自然得到 `{}`。
- 用变量 `validation` 拒绝无效端口，而不是静默筛掉它。

## 最小代码（Lab 16）

```hcl
resource "terraform_data" "deployment" {
  for_each = {
    for key, item in var.services : key => item
    if item.enabled
  }

  input = {
    name = each.key
    port = each.value.port
  }
}

output "deployment_ports" {
  value = {
    for key, item in terraform_data.deployment :
    key => item.input.port
  }
}
```

## 核心知识（Lab 17）

- `terraform_remote_state` 只能读取另一份 state 的根模块 `output`。
- `coalesce(调用方路径, 默认路径)`：优先使用传入值，未提供时回退到 fixture。
- `sort(...)` 后再取 `[0]`，避免集合原始顺序影响选中的子网。
- 路径格式可用变量 `validation` 提前拒绝无效输入。

## 最小代码（Lab 17）

```hcl
data "terraform_remote_state" "network" {
  backend = "local"
  config = {
    path = coalesce(var.network_state_path, "${path.module}/../fixtures/network-primary.tfstate")
  }
}

locals {
  subnet_ids = sort(data.terraform_remote_state.network.outputs.private_subnet_ids)
}

output "selected_subnet_id" {
  value = local.subnet_ids[0]
}
```

## 核心知识（Lab 18）

- `count = 条件 ? 1 : 0`：条件创建零个或一个资源；资源引用变为列表。
- `one(零或一项列表)`：零项返回 `null`，一项返回该值。
- `try(可能报错的表达式, null)`：安全读取可能不存在的 `[0]`。
- 可选资源不存在时，输出 `null`，不使用哨兵字符串。

## 最小代码（Lab 18）

```hcl
resource "terraform_data" "marker" {
  count = var.create_marker ? 1 : 0
  input = { name = var.marker_name, owner = var.owner }
}

output "selected_name" {
  value = one(terraform_data.marker[*].input.name)
}

output "selected_owner" {
  value = try(terraform_data.marker[0].input.owner, null)
}
```

## 核心知识（Lab 19）

- `count` 实例地址用数字索引，如 `resource.x[0]`；`for_each` 用业务 key，如 `resource.x["logs"]`。
- 地址从索引改为 key 时，资源配置相同也需要 `moved` 块迁移 state。
- `moved` 只改 state 地址，不创建、销毁或替换真实资源。
- 每个旧实例必须对应一个新地址；迁移后 `plan` 应为 no-op。

## 最小代码（Lab 19）

```hcl
moved {
  from = terraform_data.bucket[0]
  to   = terraform_data.bucket["logs"]
}

resource "terraform_data" "bucket" {
  for_each = local.records
  input    = each.value
}
```

## 核心知识（Lab 20）

- `jsondecode(file(...))` / `csvdecode(file(...))`：读取并解析本地 JSON、CSV。
- map 推导式用业务字段做 key；筛选后直接用于 `for_each`。
- `row.value == "" ? null : tonumber(row.value)`：空字符串转 `null`，`"0"` 保留为数字 `0`。
- `path.module`：当前模块目录，适合拼接相对 fixture 路径。

## 最小代码（Lab 20）

```hcl
locals {
  apps = jsondecode(file("${path.module}/../fixtures/apps.json"))

  enabled_apps = {
    for app in local.apps : app.name => app
    if app.enabled
  }

  bucket_settings = {
    for row in csvdecode(file("${path.module}/../fixtures/buckets.csv")) :
    row.name => {
      lifecycle_days = row.lifecycle_days == "" ? null : tonumber(row.lifecycle_days)
    }
  }
}
```

## 核心知识（Lab 21）

- `dynamic "块名"`：在资源内部按集合动态生成嵌套 block。
- `content {}`：定义每个动态 block 的内容。
- 默认迭代器名与块名相同：`ingress.value`；可用 `iterator` 自定义。
- `dynamic` 生成嵌套配置，不是创建多个独立资源。

## 最小代码（Lab 21）

```hcl
resource "aws_security_group" "web" {
  dynamic "ingress" {
    for_each = var.ingress_rules

    content {
      description = ingress.value.description
      from_port   = ingress.value.port
      to_port     = ingress.value.port
      protocol    = "tcp"
      cidr_blocks = [ingress.value.cidr_block]
    }
  }
}
```

## 核心知识（Lab 22）

- `triggers_replace`：监听值变化，变化时强制替换资源。
- 同一资源只能写一个 `triggers_replace`；可传单值、列表或 map，任一成员变化都会触发替换。
- `create_before_destroy = true`：替换时先创建新实例，再销毁旧实例。
- 只把不可原地更新的值放入 `triggers_replace`；其他值仍可原地更新。

## 最小代码（Lab 22）

```hcl
resource "terraform_data" "service" {
  input = {
    name    = var.service_name
    release = var.release
  }

  triggers_replace = var.release

  lifecycle {
    create_before_destroy = true
  }
}
```

## 核心知识（Lab 23）

- drift：真实对象被 Terraform 外部改动，导致 state/配置与现实不一致。
- `ignore_changes = [字段]`：忽略该字段的 drift；其余字段仍由 Terraform 检测和管理。
- 不用 `ignore_changes = all`，也不要忽略整个资源或 Terraform 自己负责的字段。
- 忽略的是“该字段的差异”，不是停止管理或删除配置中的该字段。

## 最小代码（Lab 23）

```hcl
resource "local_file" "service" {
  filename        = "${path.module}/service.json"
  content         = jsonencode({ name = var.service_name, version = var.release_version })
  file_permission = var.external_permission

  lifecycle {
    ignore_changes = [file_permission]
  }
}
```

## 核心知识（Lab 24）

- `sensitive = true`：隐藏变量或输出在 CLI 中的显示，不会加密 state。
- 敏感输入参与表达式后，结果会继承敏感性；含密码的 URI、对象输出也应标为敏感。
- 非敏感元数据可以单独输出，例如用户名、是否已配置密码。
- `nonsensitive()` 只能用于确认不会泄露秘密的派生结果；不要用它输出密码。

## 最小代码（Lab 24）

```hcl
variable "db_password" {
  type      = string
  sensitive = true
  nullable  = false
}

output "connection_uri" {
  value     = local.connection_uri
  sensitive = true
}

output "credential_metadata" {
  value = {
    username            = var.db_username
    password_configured = nonsensitive(length(var.db_password) > 0)
  }
}
```

## 核心知识（Lab 25）

- 常规工作流用 VCS；API run 只给可审计的例外发布自动化。
- Pull Request 用 speculative plan：提供反馈，但绝不 apply。
- Run Trigger：上游 workspace 成功 apply 后触发下游 workspace。
- 生产安全策略用强制执行；成本估算是评审信号，不是准确账单或自动审批依据。
- 最小权限分离 plan、apply 与 workspace 管理；生产 apply 保持人工审批。

## 最小代码（Lab 25）

```text
常规变更：VCS → speculative plan → 评审 → 手工生产 apply
依赖顺序：network-prod 成功 apply → 触发 application-prod
权限边界：开发者 plan；发布团队 apply；workspace 管理权单独授予
```


## 核心知识（Lab 26，了解即可）

- ⚠ `removed` 块需要 Terraform 1.7+，不属于当前 TF Pro 1.6 范围。
- `destroy = false`：只从 state 忘记资源，保留真实对象。

## 最小代码（Lab 26，Terraform 1.7+）

```hcl
removed {
  from = aws_instance.legacy
  lifecycle {
    destroy = false
  }
}
```

## 核心知识（Lab 27）

- 双层 `for` 先生成“团队 × 应用”的嵌套列表；`flatten` 将其压成每应用一行。
- 组合 key `${team}.${app.name}` 同时保留团队与应用身份，避免跨团队同名冲突。
- `merge(global, team, app)`：越靠后的标签优先级越高。
- 空应用列表自然生成空行；同团队重复名用 `distinct` + `validation` 拒绝。

## 最小代码（Lab 27）

```hcl
locals {
  app_rows = flatten([
    for team, config in var.team_apps : [
      for app in config.apps : {
        key  = "${team}.${app.name}"
        team = team
        app  = app.name
        tags = merge(var.global_tags, config.tags, app.tags)
      }
    ]
  ])

  app_map = { for row in local.app_rows : row.key => row }
}
```

## 核心知识（Lab 28）

- 多个版本条件用逗号分隔，不能用 `&&`。
- `>= 1.6, < 2.0`：限定 1.x 范围；`~> 6.0`：限定 6.x 范围。
- `!= 6.2.0`：在允许范围内排除单个问题版本。
- `= 6.54.0`：只允许精确版本；`>= 6.0.0`：只设最低版本。

## 最小代码（Lab 28）

```hcl
terraform {
  required_version = ">= 1.6, < 2.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0, != 6.2.0"
    }
  }
}
```

## 核心知识（Lab 29）

- `.tftest.hcl` 中每个 `run` 是一个测试场景；`apply` 会建立/更新测试 state，后续 run 可继续使用。
- `plan` 不改 state，适合验证升级后的稳定状态或无变更。
- `run.场景名.输出名`：引用前一个 run 的根模块 output，比较真实生成的 ID。
- `expect_failures = [var.x]`：预期变量校验失败；失败归因正确时该 run 通过。

## 最小代码（Lab 29）

```hcl
run "deploy_v1" {
  command = apply
  variables { release_version = "v1" }
}

run "upgrade_v2" {
  command = apply
  variables { release_version = "v2" }
  assert {
    condition     = output.deployment_id != run.deploy_v1.deployment_id
    error_message = "版本变化应替换资源。"
  }
}

run "invalid_release" {
  command = plan
  variables { release_version = "latest" }
  expect_failures = [var.release_version]
}
```
