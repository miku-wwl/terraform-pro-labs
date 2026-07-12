# Lab 03：导入资源集合并迁移到模块实例

## 任务

本 Lab 有两条已存在的资源身份：`api` 和 `worker`。它们的导入 ID 已通过 `var.import_ids` 提供。

在 `starter/import-stage/main.tf` 中，为以下带键的根资源声明式导入对应 ID：

```text
random_id.legacy["api"]
random_id.legacy["worker"]
```

在 `starter/refactor-stage/main.tf` 中，将这两个根资源分别迁移到对应的模块资源：

```text
module.record["api"].random_id.this
module.record["worker"].random_id.this
```

迁移后，两个资源的身份和 ID 必须保持不变，最终不应产生任何创建、销毁或替换操作。

## 约束

- 只能编辑 `starter/import-stage/main.tf` 和 `starter/refactor-stage/main.tf`。
- 导入 ID 必须来自 `var.import_ids`，不能硬编码。
- 使用 Terraform 的 `import` 块和 `moved` 块；不能使用命令式 `terraform import` 或 `terraform state mv`。
- 不得修改 `api`、`worker`、资源名称、模块名称或 `byte_length`。
