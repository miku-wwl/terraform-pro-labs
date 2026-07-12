# Lab 05：工作区隔离的跨栈消费

## 场景

网络 producer 会从其 `dev` 和 `prod` workspace 发布不同的契约。应用 consumer 拥有相匹配的 workspace，但其路由被硬编码为开发环境，而且生产环境缺少实例规格安全边界。

## 考查技能

- 在普通配置中使用 `terraform.workspace`
- 通过 `terraform_remote_state` 读取相匹配的 workspace 状态
- 检查隔离 workspace 状态中的地址
- 强制实施仅适用于生产环境的前置条件
- 仅重置本 Lab 所属的 workspace 和状态

## 难度与预计时间

- 难度：中等
- 预计时间：35 分钟

## 执行模式

受保护的验证脚本会将 producer 和 consumer 配置复制到 Lab 05 的 `.lab-state/` 下，只在其中创建 `dev` 和 `prod`，并使用本地状态。

## 是否需要云凭据

不需要。

## 成本风险

无。仅使用内置 `terraform_data` 和本地状态。

## 初始状态

受保护的 producer 会根据其 workspace 推导网络契约。consumer 已使用本地 `terraform_remote_state`，但其环境标签和 producer 状态路径均固定为开发环境，并且其部署没有生产环境防护规则。

## 允许编辑的文件

- `starter/main.tf`

## 禁止编辑的文件

- `starter/variables.tf`、`starter/versions.tf`、`bootstrap/`、`scripts/` 和 `lab.yaml`

## 任务

1. 根据当前 workspace 推导所选环境。
2. 将每个 consumer workspace 路由到对应的 producer workspace 状态。
3. 仅在生产环境中使用指定的诊断信息拒绝 `t3.micro`。
4. 保持 dev 和 prod 计划成功，且不包含 destroy 动作。

## 约束

- 不得硬编码 dev/prod 输出值。
- 不得在受保护的运行时副本之外创建或选择 workspace。
- 不得更改受保护的 workspace 名称或状态布局。

## 预期初始失败

starter 会通过格式检查、离线初始化和验证，随后在 prod consumer 仍选择开发状态时报告 `EXPECTED_WORKSPACE_FLOW_INCOMPLETE`。

## 验证命令

```text
python tools/labctl.py reset 05
python tools/labctl.py check 05
python tools/labctl.py check 05 --mode solution
python tools/labctl.py status 05
```

## 成功标准

- producer 和 consumer 的运行时根目录只包含 `default`、`dev` 和 `prod` workspace。
- 每个 producer workspace 均恰好包含 `terraform_data.network`。
- 每个 consumer workspace 均包含远程状态 data source 和 `terraform_data.deployment`。
- Dev 消费完整的 dev 网络对象，prod 消费完整的 prod 网络对象，包括精确的 environment、VPC 和 subnet 值。
- 两个 consumer 的初始计划均不销毁资源，且最终计划均为 no-op。
- 使用 `t3.micro` 的 prod 计划会以 `t3.micro is not allowed in the prod workspace.` 失败。

## 重置说明

`python tools/labctl.py reset 05` 会删除 Lab 05 的 `.lab-state/` 运行时目录树和已记录的结果。它绝不会进入或修改源目录或任何无关 Terraform 根目录中的 workspace。

## 有限提示

- 命名的本地 backend workspace 状态位于 `terraform.tfstate.d/<workspace>/` 下。
- 生命周期前置条件可以同时引用当前 workspace 和输入值。
