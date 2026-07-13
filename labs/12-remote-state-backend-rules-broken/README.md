# Lab 12：读取跨栈 State，并拆分 Backend 配置

## 任务

生产方已经将网络信息发布到自己的 state 中。

在 `starter/main.tf` 中，使用 `var.producer_state_path` 读取生产方的 state。消费者的 `terraform_data` 资源和 `consumed_network` 输出都必须使用读取到的网络信息，不能手工复制。

同时整理 `starter/backend.tf.example`：S3 backend 块只保留所有环境共用的安全设置；`bucket`、`key` 和 `region` 应在初始化时由环境配置文件提供。



## 约束

- 不要复制生产方输出，也不要让消费者管理生产方资源。
- 不要初始化真实 S3 backend 或在代码中添加凭据。
- 保留现有消费者资源地址和输出名称。
- 只能编辑 `starter/main.tf` 和 `starter/backend.tf.example`。
