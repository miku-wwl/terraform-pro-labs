# Lab 11：导入已有资源并迁移到模块

## 任务

本 Lab 预先创建了一条随机 ID，`import_id` 是它的已有标识。

先在 `starter/import-stage/main.tf` 中使用 `import` 块，将该对象纳入 `random_id.legacy_record` 的 state 管理。

再在 `starter/refactor-stage/main.tf` 中使用 `moved` 块，把这条 state 记录迁移到 `record` 子模块中。迁移后 ID 必须保持不变，不能重新创建或销毁资源。



## 约束

- 必须先导入，再迁移。
- 使用 `import` 和 `moved` 块；不要使用 `terraform import` 或 `terraform state mv` 命令。
- 不要修改资源类型、字节长度、模块名称或资源名称。
- 不要硬编码 `import_id`，也不要复制 state 文件。
- 不要添加 AWS 或其他云 provider。
- 只能编辑 `starter/import-stage/main.tf` 和 `starter/refactor-stage/main.tf`。
