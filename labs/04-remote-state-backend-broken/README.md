# Lab 04：后端边界与本地跨栈状态

## 场景

网络 producer 负责维护一份输出契约。应用 consumer 当前保存了这份契约的复制版本，同时其可选 S3 backend 声明错误地包含了一个环境专属值。请在不连接 AWS 的前提下修正这两个边界。

## 考查技能

- 分离 producer 配置、consumer 配置与 backend 初始化值
- 使用 `terraform_remote_state` 消费本地状态 fixture
- 确保 backend 块中不包含表达式和环境专属值
- 检查状态地址并证明最终计划为 no-op

## 难度与预计时间

- 难度：中等
- 预计时间：30 分钟

## 执行模式

默认验证会在 `.lab-state/` 下引导生成两个互相独立的本地 producer 状态。S3 backend 文件仅作为离线且必须明确选择启用的可选扩展。

## 是否需要云凭据

默认工作流不需要。可选的真实 S3 初始化需要单独授权以及学习者自有的基础设施。

## 成本风险

默认：无。可选路径最多写入一个很小的 Terraform 状态对象，并发起少量 S3 请求。在一次短暂的练习中，增量费用通常低于 0.01 美元，但 AWS、复制、KMS、数据传输及组织专属费用不受本 Lab 限制；选择启用前请查看当前价格。

## 初始状态

`bootstrap/producer/` 是受保护的 producer。`starter/consumer/` 使用手工复制的网络值。`starter/backend.tf.example` 保留了共享 backend 安全设置，但同时包含一个放错位置的初始化时设置。

## 允许编辑的文件

- `starter/consumer/main.tf`
- `starter/backend.tf.example`

## 禁止编辑的文件

- `bootstrap/`、`backend-dev.hcl.example`、`starter/consumer/versions.tf`、`scripts/`、`tests/`
  和 `lab.yaml`

## 任务

1. 通过提供的本地状态路径读取 producer 的 `network` 输出。
2. 将消费到的值传入应用契约并输出该值。
3. 在可选 S3 backend 块中只保留共享的静态安全设置。
4. 将 bucket、key 和 region 保留在初始化示例中。

## 约束

- 不得复制或硬编码 producer 输出值。
- 不得在 backend 块中使用 Terraform 表达式。
- 不得添加凭据，也不得在常规验证期间初始化 S3。

## 预期初始失败

starter 会通过格式检查、离线初始化和验证，随后报告 `EXPECTED_BACKEND_CROSS_STACK_INCOMPLETE`，因为它使用了复制值，并在 backend 声明中保留了一个初始化时 key。

## 验证命令

```text
python tools/labctl.py reset 04
python tools/labctl.py check 04
python tools/labctl.py check 04 --mode solution
```

### 可选的真实 S3 初始化——仅限明确选择启用

前提条件：学习者自有的 S3 bucket、仅对所选状态 key 具有读/写/删除权限、已配置的外部 AWS 凭据链，以及确认没有其他操作者使用 `network/dev.tfstate`。本 Lab 不会创建 bucket、凭据、KMS key 或锁定基础设施。

创建未被跟踪的本地工作副本。在 PowerShell 中运行：

```powershell
Copy-Item labs/04-remote-state-backend-broken/starter/backend.tf.example labs/04-remote-state-backend-broken/starter/consumer/backend.tf
Copy-Item labs/04-remote-state-backend-broken/backend-dev.hcl.example labs/04-remote-state-backend-broken/backend-dev.hcl
```

在 POSIX shell 中运行：

```bash
cp labs/04-remote-state-backend-broken/starter/backend.tf.example labs/04-remote-state-backend-broken/starter/consumer/backend.tf
cp labs/04-remote-state-backend-broken/backend-dev.hcl.example labs/04-remote-state-backend-broken/backend-dev.hcl
```

仅替换 `backend-dev.hcl` 中的 bucket 占位符，然后检查 bucket、key、region、加密、凭据来源和访问策略，再明确运行：

```text
terraform -chdir=labs/04-remote-state-backend-broken/starter/consumer init -reconfigure -backend-config=../../backend-dev.hcl
```

初始化可能上传或迁移现有的本地状态快照。远程状态可能包含敏感值，并发使用可能覆盖状态，删除或更改 key 可能使状态失去引用。不得对共享或生产状态路径运行此命令。

## 成功标准

- 离线负向对照会拒绝动态 backend 表达式。
- 可选 S3 backend 只包含 `encrypt` 和 `use_lockfile`；初始化示例只包含占位 bucket、key 和 region。
- 两个不同的 producer 状态均恰好包含 `terraform_data.network_contract`。
- 每个 consumer 状态均包含远程状态 data source 和 `terraform_data.application_contract`。
- 每个 consumer 输出都精确跟随其所选 producer，包括变化后的 ID 和集合长度；初始计划不包含 destroy，最终计划为 no-op。

## 重置说明

对于默认本地工作流，`python tools/labctl.py reset 04` 仅删除 Lab 04 的运行时状态、初始化元数据、计划、锁和已记录的结果。

如果尝试了可选的真实 S3 路径，请先保留仍然需要的所有状态。要将所选状态迁回本地 backend，请删除复制的 backend 声明并重新初始化，然后再重置：

```powershell
Remove-Item labs/04-remote-state-backend-broken/starter/consumer/backend.tf
terraform -chdir=labs/04-remote-state-backend-broken/starter/consumer init -migrate-state
python tools/labctl.py reset 04
Remove-Item labs/04-remote-state-backend-broken/backend-dev.hcl
```

在 POSIX 中，使用 `rm` 删除这两个复制文件。如果学习者自有的 bucket 不再需要该远程对象，请在确认它未被共享后，通过获批的 AWS 工具仅删除准确的 `network/dev.tfstate` 对象。`labctl reset` 有意不会连接 S3，也不会删除学习者自有的 backend 配置。

## 有限提示

- backend 配置的求值早于普通输入变量。
- 本地 remote-state backend 的 `config` map 接受文件系统路径。
