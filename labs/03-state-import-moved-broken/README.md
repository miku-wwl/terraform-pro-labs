# Lab 03：导入已有资源并迁移到模块

## 任务

这里有两个已经存在的资源：`api` 和 `worker`。`var.import_ids` 是一个以资源名称为键、已有资源 ID 为值的 map：`api` 对应 `api` 的 ID，`worker` 同理。

第一步，在 `starter/import-stage/main.tf` 中使用 `import` 块导入资源。导入规则必须按名称配对：`api` 的 ID 导入 `random_id.legacy["api"]`，`worker` 的 ID 导入 `random_id.legacy["worker"]`。

第二步，在 `starter/refactor-stage/main.tf` 中使用 `moved` 块，将它们迁移到对应的模块资源：

```text
module.record["api"].random_id.this
module.record["worker"].random_id.this
```

迁移后，资源的 ID 必须保持不变；最终计划不能出现创建、销毁或替换操作。

## 约束

- 只能编辑 `starter/import-stage/main.tf` 和 `starter/refactor-stage/main.tf`。
- 导入 ID 必须使用 `var.import_ids`，不能直接写死。
- 必须使用 Terraform 的 `import` 块和 `moved` 块；不能使用 `terraform import` 或 `terraform state mv` 命令。
- 不得修改 `api`、`worker`、资源名称、模块名称或 `byte_length`。
