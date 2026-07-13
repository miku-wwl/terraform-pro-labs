# Lab 32：由依赖变化触发资源替换

## 任务

`release_marker` 记录发布版本，`service` 记录服务名称。发布版本改变时，marker 本身应原地更新，但 service 必须因此被替换；直接修改服务名称时，service 仍应原地更新。

在 `starter/main.tf` 中，为 service 配置生命周期依赖：让 Terraform 监听 `release_marker` 的变化，并在它发生变化时替换 service。不要把发布版本复制到 service 的输入中来制造差异。

## 约束

- 不要让 service 的所有输入变化都触发替换。
- 保留 `release_marker` 和 `service` 两个资源地址。
- 只能编辑 `starter/main.tf`。
