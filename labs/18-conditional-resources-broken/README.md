# Lab 18：条件资源与可选值输出

## 任务

`create_marker` 决定是否创建一个 marker：关闭时不创建资源，开启时只创建一个。`marker_name` 和 `owner` 是这个 marker 的配置值。

输出 `marker_count`、`selected_name` 和 `selected_owner`。marker 不存在时，后两个输出必须是 `null`；存在时，必须返回该 marker 的真实名称和 owner。

在可编辑配置中分别使用 `one()` 和 `try()` 处理这个“零个或一个资源”的场景：前者读取可选集合，后者安全处理可能不存在的索引。

## 约束

- 不用哨兵字符串表示“不存在”，应返回 `null`。
- 不添加 provider 或外部依赖。
- `marker_name` 不能是空字符串或全空格。
- 只能编辑 `starter/main.tf`。
