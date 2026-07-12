# Lab 07：验证、前置条件、检查与测试

## 场景

本地部署描述符接收环境、实例类型和命名前缀。当前的条件骨架会允许不安全或质量不佳的输入。请补全三种不同的防护机制，并使用 Terraform Test 证明它们各自不同的行为。

## 考查技能

- 使用变量验证拒绝无效输入
- 使用资源前置条件实施上下文相关的运行时规则
- 使用 `check` 块执行非阻塞断言
- 编写正向和预期失败的 Terraform Test run

## 难度与预计时间

- 难度：中等
- 预计时间：20 分钟

## 执行模式

- 模式：本地 Terraform Test
- 后端：由本地测试管理的状态

## 是否需要云凭据

不需要。本 Lab 使用内置 `terraform_data` 资源，不使用外部 provider。

## 成本风险

无。

## 初始状态

配置在语法上有效，但三个条件表达式都是宽松的占位实现。公共测试文件完整且受保护。它会验证正常行为、所有受支持的环境类别、安全的生产场景、前缀边界，以及每种防护机制各自的一个失败场景。

## 允许编辑的文件

- `starter/main.tf`

## 禁止编辑的文件

- `starter/versions.tf`
- `tests/public.tftest.hcl`
- `scripts/verify_tests.py`
- `lab.yaml`

## 任务

1. 让 `environment` 只接受 `dev`、`stage` 或 `prod`。
2. 阻止生产部署使用 `t3.micro`。
3. 当 `name_prefix` 少于五个字符时，让命名质量检查发出警告。
4. 运行 `terraform test`，并确认预期失败分别归属正确的变量、资源和 check 块。

## 约束

- 保留现有变量、资源、输出和 check 地址。
- 在指定的验证机制中实现每条规则。
- 不得为了让 starter 通过而修改受保护的测试。
- check 块仅提供建议；不得将其规则改为阻塞式变量验证或前置条件。

## 预期初始失败

`python tools/labctl.py check 07` 会运行到 Terraform Test 阶段并报告 `EXPECTED_GUARDS_INCOMPLETE`。starter 中宽松的条件不会产生公共测试预期的失败。

## 验证命令

在仓库根目录运行：

```text
terraform -chdir=labs/07-validation-checks-tests-broken/starter fmt -check
terraform -chdir=labs/07-validation-checks-tests-broken/starter init -backend=false
terraform -chdir=labs/07-validation-checks-tests-broken/starter validate
terraform -chdir=labs/07-validation-checks-tests-broken init -backend=false -test-directory=tests
terraform -chdir=labs/07-validation-checks-tests-broken test
python tools/labctl.py check 07
```

## 成功标准

- 正常的开发环境输入会生成测试预期的精确部署摘要。
- `stage` 仍然有效，使用安全实例类型的生产环境也会成功。
- 未知环境会在变量验证阶段失败。
- 生产环境使用 `t3.micro` 会在部署资源前置条件处失败。
- 五字符前缀会通过，四字符前缀会产生预期的非阻塞 check 诊断。
- `terraform test` 无需云凭据即可通过全部七个 run。

## 重置说明

在仓库根目录运行：

```text
python tools/labctl.py reset 07
```

重置仅删除生成的 Terraform 产物和已记录的检查结果。它会保留 `starter/main.tf`，因此不会丢弃学习者的工作。

## 有限提示

- 应根据规则涉及单个输入、上下文相关的资源操作还是建议性质量要求，选择相应的防护类型。
- `expect_failures` 标识预期会报告诊断信息的配置对象；它不包含具体实现。
