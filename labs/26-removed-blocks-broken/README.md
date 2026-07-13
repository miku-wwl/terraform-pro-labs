# Lab 26：`moved` 与 `removed` 的 State 语义

## 任务

旧 state 中有两个对象：`terraform_data.service_old` 是仍由 Terraform 管理的服务；`terraform_data.legacy_attachment` 是已交给外部系统保留和管理的旧附件。

将服务的 state 地址迁移到现有的 `terraform_data.service`，保留它的身份和值。将旧附件从 Terraform state 中移除，但必须保留底层对象，不能计划销毁。

完成后，state 中只保留服务的新地址，且再次 plan 为 no-op；整个迁移过程不得产生 create 或 delete。

## 约束

- 不使用命令式 `terraform state mv` 或 `terraform state rm`。
- 不保留旧资源块，也不删除或重建 state。
- 不改变服务或附件的已有值。
- 不编辑旧配置 fixture 或验证脚本。
- 只能编辑 `starter/main.tf`。
