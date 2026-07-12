# Lab 12：Remote state 消费者与 backend 分离

## 场景

一个应用栈必须读取选定网络栈的输出。它自身可选的 S3 backend 配置属于独立的初始化关注点，不能与生产者查询混在一起。

## 考查技能

- 使用 `terraform_remote_state` 读取调用方选择的本地 fixture
- 生产者与消费者的 state 所有权
- 静态的部分 backend 配置和初始化时输入
- 检查 state list 和 plan action

## 难度与预计时间

中等，约 30 分钟。

## 执行模式

使用本地生产者和消费者 state fixture。可选 S3 示例仅进行离线检查。

## 是否需要云凭据

受支持的工作流不需要云凭据。

## 成本风险

受支持的本地工作流没有成本。可选的仅初始化 S3 扩展可能会发出少量 S3 API 请求。如果初始化成功后立即停止，并且不迁移或写入任何 state，预计增量成本低于 US$0.01；实际计费、账户策略以及免费套餐适用情况由学员负责，且不受本 Lab 限制。

## 初始状态

受保护的 verifier 会构建相互独立的 dev 和 prod 生产者 state。starter 消费者使用复制的 dev 值，而可选 backend 示例错误地包含了一个环境特定的 key。

## 允许编辑的文件

- `starter/main.tf`
- `starter/backend.tf.example`

## 禁止编辑的文件

- `lab.yaml`、`bootstrap/`、`scripts/` 和 `tests/`
- `starter/versions.tf`
- `backend-dev.hcl.example` 和 `backend-prod.hcl.example`

## 任务

1. 使用 `var.producer_state_path`，通过 `terraform_remote_state` 读取生产者输出。
2. 将读取到的网络传递给消费者所有的 `terraform_data` 资源和输出。
3. backend block 中仅保留共享的静态安全设置；bucket、key 和 region 应保留在环境特定的初始化文件中。

## 约束

不要复制生产者值、初始化 S3、添加凭据，或让消费者管理生产者资源。保留现有输出名称和消费者资源地址。

## 预期初始失败

`python tools/labctl.py check 12` 会到达受保护的行为 gate，并报告 `EXPECTED_REMOTE_STATE_CONSUMER_INCOMPLETE`，因为消费者忽略了生产者路径，并且 backend 边界混杂不清。

## 验证命令

```text
python tools/labctl.py reset 12
python tools/labctl.py check 12
```

可选的真实 backend 扩展会使用学员自有的 `.example` 文件副本，但它不属于验证流程，并且需要单独授权。

### 可选的真实 S3 初始化（不纳入验证）

仅在获得明确授权并满足以下全部先决条件时使用此扩展：

- 仅能访问学员自有测试 bucket 的短期 AWS 凭据；
- `us-east-1` 中一个现有且已启用加密与版本控制的测试 bucket；
- 一个全新、未使用的 state key——绝不能使用生产或共享 state key；
- 没有需要迁移的本地 state，并且无意运行 `plan`、`apply` 或任何写入 state 的命令。

从仓库根目录创建未跟踪的工作副本，替换 bucket 占位符，然后仅运行其中一条环境特定的 init 命令：

```text
# PowerShell
Copy-Item labs/12-remote-state-backend-rules-broken/starter/backend.tf.example labs/12-remote-state-backend-rules-broken/starter/backend.tf
Copy-Item labs/12-remote-state-backend-rules-broken/backend-dev.hcl.example labs/12-remote-state-backend-rules-broken/backend-dev.hcl
# Edit backend-dev.hcl and replace only REPLACE_WITH_LAB12_CONSUMER_STATE_BUCKET.
terraform -chdir=labs/12-remote-state-backend-rules-broken/starter init -reconfigure -backend-config=../backend-dev.hcl
```

等效的 POSIX 命令如下：

```text
cp labs/12-remote-state-backend-rules-broken/starter/backend.tf.example labs/12-remote-state-backend-rules-broken/starter/backend.tf
cp labs/12-remote-state-backend-rules-broken/backend-dev.hcl.example labs/12-remote-state-backend-rules-broken/backend-dev.hcl
# Edit backend-dev.hcl and replace only REPLACE_WITH_LAB12_CONSUMER_STATE_BUCKET.
terraform -chdir=labs/12-remote-state-backend-rules-broken/starter init -reconfigure -backend-config=../backend-dev.hcl
```

对于 prod，请将 `backend-prod.hcl.example` 复制为 `backend-prod.hcl`，并改为传递该文件。初始化成功后立即停止。默认 Lab 绝不会执行这些命令。

对此处记录的仅初始化流程进行清理时，应删除本地工作副本和 backend 元数据：

```text
# PowerShell, from the repository root
Remove-Item labs/12-remote-state-backend-rules-broken/starter/backend.tf
Remove-Item labs/12-remote-state-backend-rules-broken/backend-dev.hcl -ErrorAction SilentlyContinue
Remove-Item labs/12-remote-state-backend-rules-broken/backend-prod.hcl -ErrorAction SilentlyContinue
python tools/labctl.py reset 12
```

等效的 POSIX 清理命令如下：

```text
rm -f labs/12-remote-state-backend-rules-broken/starter/backend.tf
rm -f labs/12-remote-state-backend-rules-broken/backend-dev.hcl labs/12-remote-state-backend-rules-broken/backend-prod.hcl
python tools/labctl.py reset 12
```

仅初始化运行不应创建远程 state 对象。如果曾运行任何写入 state 的命令，请停止操作，并使用 bucket 所有者支持版本感知的清理流程；只删除当前 S3 对象或 delete marker 可能会留下旧版本。主要风险包括选择已存在的 key、向权限过宽的主体暴露 state 内容、保留版本化对象，以及产生账户特定的请求或存储费用。

## 成功标准

- dev 和 prod 均解析出精确的、选定的生产者输出；
- 消费者 state 仅包含 remote-state data 地址和消费者契约资源；
- 初始消费者 plan 仅创建消费者所有的资源；
- 最终消费者 plan 均为 no-op；
- backend 表达式仅包含共享的静态安全设置。

## 重置说明

```text
python tools/labctl.py reset 12
```

重置操作仅删除 Lab 12 的运行时 state、初始化元数据、plan、lock 和结果记录。

## 有限提示

本地 backend 的 `path` 应放在 remote-state data source 配置中。S3 backend 的 bucket、key 和 region 是初始化输入，而不是普通 Terraform 表达式值。
