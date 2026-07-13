# `.tftest.hcl` 写法速查：
# - `run "名称"`：一个测试场景；后续 run 可引用前面 run 的 output。
# - `command = apply`：创建/更新测试 state；`command = plan`：只验证计划。
# - `variables {}`：仅覆盖当前 run 的输入变量。
# - `assert {}`：`condition` 为 true 才通过；失败时显示 `error_message`。
# - `run.前一场景名.输出名`：读取前一个 run 的根模块 output。
# - `expect_failures = [var.变量名]`：声明预期由该变量校验触发的失败。

run "single_plan" {
  command = plan

  variables {
    service_name    = "checkout"
    release_version = "v1"
  }

  assert {
    condition     = terraform_data.deployment.input.release == "v1"
    error_message = "The proposed release must match the input."
  }
}
