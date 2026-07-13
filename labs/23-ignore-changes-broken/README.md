# Lab 23：精确划分 `ignore_changes` 的管理边界

## 任务

Terraform 管理一份 `service.json`：服务名称和发布版本决定文件内容，文件路径也由 Terraform 管理。创建后，主机策略会在 Terraform 之外维护文件权限。

将 `ignore_changes` 缩小到仅忽略外部维护的文件权限。权限漂移不应进入 plan；文件内容或文件路径的漂移仍必须由 Terraform 检测并管理。

## 约束

- 不使用 `ignore_changes = all`。
- 不忽略 `content`、`filename` 或整个资源。
- 不编辑验证脚本。
- 只能编辑 `starter/main.tf`。
