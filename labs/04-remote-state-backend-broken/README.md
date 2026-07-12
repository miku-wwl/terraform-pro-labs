# Lab 04：后端边界与本地跨栈状态

## 任务

生产方的 state 中已经提供了 `network` 输出。

在 `starter/consumer/main.tf` 中，使用给定的本地 state 路径读取这份网络信息，并将读取到的值传给应用记录，再通过现有输出返回。

同时整理 `starter/backend.tf.example`：S3 backend 块只保留所有环境共用的静态安全设置；`bucket`、`key` 和 `region` 属于环境配置，应继续放在初始化示例文件中。



## 约束

- 不得复制或硬编码 producer 输出值。
- 不得在 backend 块中使用 Terraform 表达式。
- 不得添加凭据，也不得在常规验证期间初始化 S3。



## 可编辑文件

- `starter/consumer/main.tf`
- `starter/backend.tf.example`
