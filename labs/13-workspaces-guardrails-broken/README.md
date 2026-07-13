# Lab 13：按 Workspace 选择环境，并保护生产部署

## 任务

使用 `dev`、`staging`、`prod` 三个 workspace。当前选中哪个 workspace，就以它作为部署环境，并从已有设置表中选择对应的副本数和环境层级。

生产环境需要额外保护：只有实例规格为 `t3.large`、`t3.xlarge` 或 `t3.2xlarge`，且 `auto_approve` 为 `false` 时，才允许继续执行。

保留现有资源地址、输出名称和生产环境的诊断信息。



## 约束

- 不要添加云资源。
- 不要在源码目录中手动创建或切换 workspace。
- 不要为验证器使用的文件路径编写特殊分支。
- 使用一条生产环境保护规则，并保留既定诊断信息。
- 只能编辑 `starter/main.tf`。
