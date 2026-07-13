# Lab 15：按条件配置 S3 版本控制、生命周期和标签

## 任务

`buckets` 是以逻辑名称为键的 bucket 配置。每个键都应成为一个稳定的 S3 bucket 资源地址。

只有 `versioning = true` 的 bucket 才创建版本控制；只有提供了 `lifecycle_days` 的 bucket 才创建生命周期规则，并使用对应的天数。

合并公共标签和 bucket 专属标签；同名时，以 bucket 专属标签为准。输出 bucket 名称、启用版本控制的 bucket，以及生命周期保留天数时，都要保留原始逻辑名称作为 key。



## 约束

- 保留现有资源和输出地址。
- 不要硬编码 bucket 键。
- 不要执行真实 AWS plan 或 apply，也不要添加凭据。
- 只能编辑 `starter/main.tf`。
