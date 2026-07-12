# Lab 13：Workspace 感知行为与生产环境防护规则

## 任务

1. 根据当前选中的 workspace 推导活动环境。
2. 为 dev、staging 和 prod 选择精确设置。
3. 仅当容量为获准规格之一（`t3.large`、`t3.xlarge` 或 `t3.2xlarge`）且 `auto_approve` 为 false 时，才允许生产环境执行。
4. 保留资源和输出契约。



## 约束

不要添加云资源，不要在学员源码目录中切换 workspace，也不要针对 verifier 路径编写特殊分支。使用一个生产环境 guardrail，并保留文档所述的诊断信息。



## 可编辑文件

- `starter/main.tf`
