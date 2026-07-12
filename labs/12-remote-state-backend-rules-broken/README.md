# Lab 12：Remote state 消费者与 backend 分离

## 任务

1. 使用 `var.producer_state_path`，通过 `terraform_remote_state` 读取生产者输出。
2. 将读取到的网络传递给消费者所有的 `terraform_data` 资源和输出。
3. backend block 中仅保留共享的静态安全设置；bucket、key 和 region 应保留在环境特定的初始化文件中。



## 约束

不要复制生产者值、初始化 S3、添加凭据，或让消费者管理生产者资源。保留现有输出名称和消费者资源地址。



## 可编辑文件

- `starter/main.tf`
- `starter/backend.tf.example`
