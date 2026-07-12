# Lab 04：后端边界与本地跨栈状态

## 任务

1. 通过提供的本地状态路径读取 producer 的 `network` 输出。
2. 将消费到的值传入应用契约并输出该值。
3. 在可选 S3 backend 块中只保留共享的静态安全设置。
4. 将 bucket、key 和 region 保留在初始化示例中。



## 约束

- 不得复制或硬编码 producer 输出值。
- 不得在 backend 块中使用 Terraform 表达式。
- 不得添加凭据，也不得在常规验证期间初始化 S3。



## 可编辑文件

- `starter/consumer/main.tf`
- `starter/backend.tf.example`
