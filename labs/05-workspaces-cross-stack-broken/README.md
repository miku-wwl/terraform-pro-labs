# Lab 05：工作区隔离的跨栈消费

## 任务

1. 根据当前 workspace 推导所选环境。
2. 将每个 consumer workspace 路由到对应的 producer workspace 状态。
3. 仅在生产环境中使用指定的诊断信息拒绝 `t3.micro`。
4. 保持 dev 和 prod 计划成功，且不包含 destroy 动作。



## 约束

- 不得硬编码 dev/prod 输出值。
- 不得在受保护的运行时副本之外创建或选择 workspace。
- 不得更改受保护的 workspace 名称或状态布局。



## 可编辑文件

- `starter/main.tf`
