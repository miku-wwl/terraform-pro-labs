# Lab 18：使用 one() 和 try() 的条件 count

## 场景

部署标记是可选的。当前输出直接对零个或一个资源的集合使用索引，因此禁用路径会在 plan 阶段崩溃。请在展示两种指定集合读取模式的同时，确保启用和禁用路径均安全可用。

## 考查技能

- 使用条件 `count` 创建零个或一个实例
- 使用 `one()` 读取零个或一个元素的 splat
- 对可能失败的表达式使用 `try()`
- 为不存在的资源设计可空输出

## 难度与预计时间

- 难度：中等
- 预计时间：15 分钟

## 执行模式

使用 `terraform_data` 在本地编写 Terraform 配置。

## 是否需要云凭据

否。

## 成本风险

无。

## 初始状态

资源已经使用条件 count。两个输出都使用不安全的直接索引，因此默认的禁用 plan 会失败。

## 允许编辑的文件

- `starter/main.tf`

## 禁止编辑的文件

- `starter/versions.tf`
- `tests/public.tftest.hcl`
- `scripts/verify_tests.py`
- `lab.yaml`

## 任务

1. 禁用时保持资源 count 为零，启用时保持为一。
2. 让 `selected_name` 使用 `one()` 安全读取零个或一个元素的集合。
3. 让 `selected_owner` 使用 `try()` 安全处理可能无效的索引。
4. 不存在时保留 `null`，启用时返回精确的配置值。

## 约束

- 在可编辑配置中同时使用 `one()` 和 `try()`。
- 不要使用哨兵字符串表示不存在。
- 不要添加 provider 或外部依赖。
- 拒绝空的标记名称。

## 预期初始失败

`python tools/labctl.py check 18` 会在测试阶段报告 `EXPECTED_CONDITIONAL_READ_INCOMPLETE`。未修改的默认 plan 会失败，因为 count 为零，而输出却索引了第零个元素。

## 验证命令

```bash
python tools/labctl.py check 18
python tools/labctl.py status 18
```

## 成功标准

- 禁用输入可以成功生成 plan，资源 count 为零，两个可选输出均为 `null`。
- 启用输入会规划一个记录，并返回精确的已配置名称和所有者。
- 空名称会被拒绝。
- `selected_name` 对零个或一个名称的 splat 使用 `one()`，而 `selected_owner` 对可能无效的所有者索引使用 `try()`，并以 `null` 作为回退值。
- 注释和带引号字符串中的仿冒内容不能满足受保护的源代码契约。

## 重置说明

```bash
python tools/labctl.py reset 18
```

## 有限提示

- splat 会将零个或一个实例转换为包含零个或一个元素的 tuple。
- 一个输出可以读取该 tuple，另一个输出可以从失败的表达式中恢复。
