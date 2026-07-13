# Lab 16：筛选 `for_each` 与稳定 map 输出

## 任务

`services` 是以服务名称为键的配置 map。只有 `enabled = true` 的服务才需要部署；被禁用的服务不应生成任何 deployment record。

在 `starter/main.tf` 中，先得到已启用服务的集合，再用它创建 deployment record。资源地址必须保留服务名称，例如 `api` 和 `worker`。

分别输出已部署服务的名称和端口。两个输出都必须是以服务名称为 key 的 map；当没有任何服务启用时，应返回空 map。

## 约束

- 不使用 `count` 或位置索引。
- 不为禁用的服务创建资源。
- 不改变输入 map 的逻辑名称，也不要生成数字 key。
- 端口必须在有效 TCP 范围 `1` 到 `65535` 内。
- 只能编辑 `starter/main.tf`。
