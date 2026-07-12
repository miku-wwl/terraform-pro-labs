# Lab 15：条件式 S3 版本控制、生命周期、标签与输出

## 任务

1. 让普通 bucket 以输入 map 的每个键作为资源键。
2. 仅在 `versioning` 为 true 时创建版本控制。
3. 仅在设置了 `lifecycle_days` 时创建 lifecycle configuration，并保留匹配的天数值。
4. 合并 common tag 和 bucket 特定 tag，使 bucket 层在键冲突时获胜。
5. 为 bucket 名称、启用版本控制的 bucket 和 lifecycle retention 返回精确的 keyed map。



## 约束

- 保留资源和输出地址。
- 不要硬编码受保护场景中的键。
- 不要引入真实的 AWS plan 或 apply。
- 不要编辑或削弱受保护的测试。



## 可编辑文件

- `starter/main.tf`
