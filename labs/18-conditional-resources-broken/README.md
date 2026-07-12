# Lab 18：使用 one() 和 try() 的条件 count

## 任务

1. 禁用时保持资源 count 为零，启用时保持为一。
2. 让 `selected_name` 使用 `one()` 安全读取零个或一个元素的集合。
3. 让 `selected_owner` 使用 `try()` 安全处理可能无效的索引。
4. 不存在时保留 `null`，启用时返回精确的配置值。



## 约束

- 在可编辑配置中同时使用 `one()` 和 `try()`。
- 不要使用哨兵字符串表示不存在。
- 不要添加 provider 或外部依赖。
- 拒绝空的标记名称。



## 可编辑文件

- `starter/main.tf`
