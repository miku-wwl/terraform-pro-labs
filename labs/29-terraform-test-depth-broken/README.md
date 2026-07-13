# Lab 29：Terraform Test 的连续状态

## 任务

在 `starter/tests/release_flow.tftest.hcl` 中补全一次发布流程测试。测试 run 必须按下面的状态顺序执行：

先用 `apply` 部署 `v1`，确认服务和版本输出正确；再用 `apply` 升级到 `v2`，确认输出已更新，且新的 deployment ID 不等于 `v1` 时的 ID；随后对 `v2` 再执行一次 `plan`，确认输出和 ID 都保持为升级后的状态；最后用一个 `plan` 验证 `release_version = "latest"` 会被变量校验拒绝。

共有且仅有四个 run。每个断言都要写清失败原因；比较 deployment ID 时，引用前一个 run 的输出，不要写死 ID。

## 约束

- 至少有两个 `apply` run，并包含 `plan` run。
- run 的顺序不可调换：`v1` → `v2` → `v2` 稳定 → 无效输入。
- 只能编辑 `starter/tests/release_flow.tftest.hcl`。
