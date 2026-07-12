# Lab 23：精确的 `ignore_changes` 所有权边界

## 任务

1. 将 lifecycle 例外范围缩小到仅由外部管理的权限字段。
2. 保留 Terraform 对根据服务名称和 release 版本派生的 JSON 内容的管理。
3. 权限漂移不应进入计划；内容和文件名漂移仍应由 Terraform 管理。



## 约束

- 不要使用 `ignore_changes = all`。
- 不要忽略 `content`、`filename` 或资源的全部字段。
- 不要删除或修改受保护的 lifecycle 验证器。



## 可编辑文件

- `starter/main.tf`
