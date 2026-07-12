# Lab 29：Terraform Test 的顺序状态

## 场景

版本发布发生变化时，发布部署会替换其本地身份。现有测试只对初始值执行计划，无法证明任何状态转换。请编写包含四个 run 的 Terraform Test 流程：应用初始状态、应用升级、验证稳定状态，并检查无效输入。

## 考查技能

- 使用带有 `plan` 和 `apply` 的 `run` 块
- 在同一个测试文件内按顺序共享状态
- 跨 run 引用输出
- 断言替换后的身份
- 使用 `expect_failures` 和有用的断言消息

## 难度与预计时间

- 难度：困难
- 预计时间：30 分钟

## 执行模式

不依赖 provider 的 Terraform Test，使用由测试管理的本地状态。

## 是否需要云凭据

不需要。

## 成本风险

无。

## 初始状态

受保护的配置已经完整，但可编辑的测试只包含一个计划 run。它没有初始 apply、更新、跨 run 比较、稳定状态证明或失败场景。

## 允许编辑的文件

- `starter/tests/release_flow.tftest.hcl`

## 禁止编辑的文件

- `starter/main.tf`
- `starter/versions.tf`
- `scripts/`
- `lab.yaml`

## 任务

1. 通过 apply 将版本 `v1` 建立为初始状态，并断言精确的服务/版本输出。
2. 通过 apply 升级到版本 `v2`，断言新的输出，并证明其部署 ID 与初始状态不同。
3. 再次对 `v2` 执行计划，证明 ID 和输出仍保持升级后的值。
4. 添加一个计划 run，预期发布版本变量拒绝 `latest`。
5. 为每个行为断言提供诊断消息。

## 约束

- 在一个测试文件中保持恰好四个 run 场景。
- 至少包含两个 apply run 和一个 plan run。
- 使用跨 run 的部署 ID 引用，不要硬编码生成的 ID。
- 按初始状态、升级、稳定状态、无效输入的顺序排列场景，使共享测试状态具有清晰明确的生命周期。
- 不要修改受保护的配置或验证器。

## 预期初始失败

`python tools/labctl.py check 29` 会报告 `EXPECTED_SEQUENTIAL_TEST_FLOW_INCOMPLETE`，因为单个计划既没有建立状态，也没有改变状态。

## 验证命令

```text
terraform -chdir=labs/29-terraform-test-depth-broken/starter test
python tools/labctl.py check 29
python tools/labctl.py status 29
```

## 成功标准

- 恰好四个 run 全部通过。
- 初始场景应用 `v1`，升级场景在同一个顺序测试状态中应用 `v2`。
- 升级后的部署 ID 与初始状态不同。
- 后续的 `v2` 计划证明升级后的状态保持稳定。
- 无效的发布版本语法被归因到 `var.release_version`。
- starter 测试不会暴露外部 provider、云状态或生命周期答案。

## 重置说明

```text
python tools/labctl.py reset 29
```

## 有限提示

- 可以通过 run 标签和输出名称引用先前 run 的输出。
- apply run 会让生成的 ID 成为已知值；初始状态建立前的计划无法做到这一点。
