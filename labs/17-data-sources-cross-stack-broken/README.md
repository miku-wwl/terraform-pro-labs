# Lab 17：通过数据源读取另一套配置的 State

## 任务

网络栈已经将网络信息写入本地 state 快照。消费者不能手工复制 VPC、子网或 owner，而要通过名为 `network` 的远程 state 数据源读取这些输出。

`network_state_path` 可以指定要读取的 state 文件；未提供时，使用仓库中的主快照 `fixtures/network-primary.tfstate`。调用方改为提供另一份有效快照后，输出中的所有网络信息也应随之变化。

输出 `network_lookup`：保留 VPC ID、owner 和全部私有子网 ID；子网 ID 需要排序，并将排序后的第一个子网作为 `selected_subnet_id`。没有有效 state 文件路径时，应拒绝输入。

## 约束

- 不把 fixture 中的网络标识符手工写入配置。
- 保留现有变量和输出地址。
- 不初始化真实远程 backend，也不添加云 provider。
- 不编辑 fixture 或测试文件。
- 只能编辑 `starter/main.tf`。
