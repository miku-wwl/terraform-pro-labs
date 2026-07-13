# Lab 20：读取 JSON 与 CSV Fixture 并整理数据

## 任务

`apps_fixture` 指定应用目录 JSON，`buckets_fixture` 指定 bucket 设置 CSV。两个文件都位于 `fixtures/` 目录中，配置必须读取所选文件，不能把文件内容手工复制进 HCL。

从 JSON 中只保留已启用的应用，并以应用名称作为稳定 key 创建应用记录和输出 map。空应用目录应安全地得到零个资源与空 map。

将 CSV 的每行整理为以 bucket 名称为 key 的 map。`lifecycle_days` 有值时应成为 number；空字段表示 `null`，而 `0` 必须保留为数字 `0`。

## 约束

- 不使用数字或位置作为资源 key。
- 不编辑 fixture 或测试文件。
- 保留两个 fixture 文件名的格式校验。
- 不添加 provider；默认流程只在本地运行。
- 只能编辑 `starter/main.tf`。
