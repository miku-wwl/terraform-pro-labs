# Lab 01：Terraform CLI 与 `prevent_destroy`

## 场景

你的团队使用 Terraform 维护一条本地部署记录。练习过程中可以安全地创建这条记录，但它代表一个运维人员不得意外删除的对象。请添加生命周期保护，并使用 Terraform CLI 验证销毁计划会被阻止。

## 考查技能

- 运行 `terraform fmt`、`terraform init`、`terraform validate` 和 `terraform plan`
- 理解配置验证与行为计划之间的区别
- 使用 `prevent_destroy` 保护托管对象

## 难度与预计时间

- 难度：简单
- 预计时间：10 分钟

## 执行模式

- 模式：本地 Terraform 执行
- 后端：由受保护的验证脚本创建的隔离本地状态

## 是否需要云凭据

不需要。本 Lab 使用内置的 `terraform_data` 资源。

## 成本风险

无。默认工作流不会创建任何云资源。

## 初始状态

starter 配置有效，并且能够生成正常的创建计划，但它尚未阻止销毁。自动检查只会在临时目录中创建状态，并在结束后删除该目录。

## 允许编辑的文件

- `starter/main.tf`

## 禁止编辑的文件

- `starter/versions.tf`
- `lab.yaml`
- `scripts/verify_prevent_destroy.py`

## 任务

1. 在 `starter/` 中运行标准的 Terraform CLI 初始化和验证工作流。
2. 为 `terraform_data.deployment_record` 添加生命周期保护，使 Terraform 拒绝销毁计划。
3. 运行仓库检查，并查看它所触发的生命周期诊断信息。

## 约束

- 不得替换资源类型或资源地址。
- 不得修改验证脚本。
- 不得添加 AWS provider 或任何云资源。
- 必须通过 Terraform 生命周期配置实现保护，不得通过破坏配置有效性的方式阻止销毁。

## 预期初始失败

`python tools/labctl.py check 01` 会运行到生命周期测试，并以 `EXPECTED_GUARD_MISSING` 失败，因为 starter 允许执行销毁计划。

## 验证命令

在仓库根目录运行：

```text
terraform -chdir=labs/01-lifecycle-cli-broken/starter fmt -check
terraform -chdir=labs/01-lifecycle-cli-broken/starter init -backend=false
terraform -chdir=labs/01-lifecycle-cli-broken/starter validate
python tools/labctl.py check 01
```

## 成功标准

- 格式检查、初始化和验证均通过。
- 正常的创建计划仍然有效。
- `terraform_data.deployment_record` 的销毁计划会明确因为启用了生命周期保护而被拒绝。
- 不使用任何云凭据，也不执行任何云操作。

## 重置说明

在仓库根目录运行：

```text
python tools/labctl.py reset 01
```

验证脚本使用的状态是临时的；重置仅删除本 Lab 所属的初始化文件、计划、状态和已记录的检查结果。

## 有限提示

- 生命周期规则应位于必须禁止销毁的托管资源中。
- 仅运行 `terraform validate` 无法证明销毁操作已受到保护。
