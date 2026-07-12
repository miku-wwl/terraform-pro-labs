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
