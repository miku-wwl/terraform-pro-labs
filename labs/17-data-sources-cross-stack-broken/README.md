# Lab 17：数据源与跨栈查询边界

## 场景

某个应用栈目前包含手动复制的网络标识符。请将其替换为本地跨栈数据查询，并使生产者路径可配置、消费者输出规范化。

## 考查技能

- 内置 `terraform_remote_state` 数据源
- 生产者与消费者之间的输出契约
- 可配置的外部查询输入
- 对查询所得集合进行确定性规范化
- 预期失败的输入测试

## 难度与预计时间

- 难度：中等
- 预计时间：20 分钟

## 执行模式

仅使用本地状态 fixture。不初始化远程 backend。

## 是否需要云凭据

否。

## 成本风险

无。

## 初始状态

输出结构已经存在，但其中的标识符是手动复制的，`network_state_path` 输入不会产生任何作用。

## 允许编辑的文件

- `starter/main.tf`

## 禁止编辑的文件

- `starter/versions.tf`
- `fixtures/`
- `tests/`
- `scripts/`
- `lab.yaml`

## 任务

1. 通过名为 `network` 的 `terraform_remote_state` 数据源读取生产者输出。
2. 未提供路径时使用主 fixture，并正确采用调用方提供的状态路径。
3. 返回精确的网络契约：对子网 ID 排序，并选择规范化后的第一个子网。
4. 继续拒绝无效的非状态文件路径。

## 约束

- 不要将 fixture 中的标识符复制到配置中。
- 保留变量和输出地址。
- 不要初始化真实远程 backend，也不要添加云 provider。
- 不要编辑受保护的 fixture 或测试。

## 预期初始失败

`python tools/labctl.py check 17` 会报告 `EXPECTED_CROSS_STACK_LOOKUP_INCOMPLETE`，因为 starter 忽略了两个生产者 fixture。

## 验证命令

```text
python tools/labctl.py check 17
python tools/labctl.py status 17
```

## 成功标准

- 默认 fixture 生成精确且规范化的主网络契约。
- 路径输入可以选择次级生产者，无需修改代码。
- 可编辑源代码使用 `data.terraform_remote_state.network.outputs`，且不包含复制的生产者输出值。
- 子网排序和选择具有确定性。
- 无效的查询文件名无法通过变量验证。
- 不需要外部账户、默认 VPC 或网络 API。

## 重置说明

```text
python tools/labctl.py reset 17
```

## 有限提示

- local backend 可在其 backend 配置映射中接受文件系统路径。
- 将生产者的原始输出与规范化后的消费者对象分开处理。
