# Lab 11：Import、moved block 与模块重构

## 任务

1. 在 import-stage 配置中，使用 `import_id` 以声明方式将现有对象导入旧的根资源地址；不得硬编码生成的 ID。
2. 在 refactor-stage 配置中，将该资源迁移到提供的子模块，并保留原有 state 标识。
3. 迁移不得产生 create/delete 操作，最终计划应无变更。



## 约束

- 必须先完成声明式 import，再进行模块重构。
- 使用配置驱动的地址迁移完成重构；不要用命令式 `terraform state mv` 命令替代。
- 不要更改资源类型、字节长度、模块或资源名称，也不要更改受保护的 verifier 文件。
- 不要硬编码生成的标识符，也不要在阶段之间复制 state 文件。
- 不要添加 AWS 或任何其他云 provider。



## 可编辑文件

- `starter/import-stage/main.tf`
- `starter/refactor-stage/main.tf`
