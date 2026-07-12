# Lab 05：按 Workspace 读取跨栈状态

## 任务

生产方和消费方都使用 `dev`、`prod` workspace。当前 consumer 运行在哪个 workspace，就应读取生产方中同名 workspace 的 state；不要把环境或网络输出写死在配置中。

在 `starter/main.tf` 中，根据当前 workspace 推导环境并读取对应的生产方输出。

生产环境不能使用 `t3.micro`。这条限制只在 `prod` 生效，并应保留题目指定的诊断信息。



## 约束

- 不得硬编码 `dev`、`prod` 的输出值或环境选择。
- 不得在受保护的运行时副本之外创建或切换 workspace。
- 不得修改 workspace 名称或 state 布局。



## 可编辑文件

- `starter/main.tf`
