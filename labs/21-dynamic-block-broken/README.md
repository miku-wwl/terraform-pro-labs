# Lab 21：动态嵌套 ingress 块

## 场景

虽然 ingress 策略已经以结构化输入提供，但某个 security group 目前仍重复定义两个静态 ingress 块。请将重复内容替换为输入驱动的嵌套块，使其适用于任何有效的规则列表。

## 考查技能

- `dynamic` 嵌套块与迭代器作用域
- 资源 `for_each` 与嵌套块重复之间的区别
- 在 provider schema 块中保留对象内容
- Terraform mock provider 测试

## 难度与预计时间

- 难度：中等
- 预计时间：20 分钟

## 执行模式

通过 Terraform mock provider 使用 AWS provider schema 生成 plan。不调用 AWS API。

## 是否需要云凭据

否。

## 成本风险

无。测试只创建模拟 plan。

## 初始状态

输入类型和验证已经存在，但资源包含两个硬编码的 ingress 块，因此会忽略替代规则集合。

## 允许编辑的文件

- `starter/main.tf`

## 禁止编辑的文件

- `starter/versions.tf`
- `tests/`
- `scripts/`
- `lab.yaml`

## 任务

1. 使用一个动态嵌套块结构替换重复的静态 ingress 块。
2. 使用 `var.ingress_rules` 驱动其重复生成。
3. 在生成的 provider 块中保留每条规则的描述、端口和 CIDR。
4. 保持固定的出站规则和端口验证不变。

## 约束

- 不要创建多个 security group 资源。
- 不要保留静态 ingress 块。
- 不要硬编码受保护测试中的替代测试值。
- 不要移除或编辑与 lifecycle 无关的受保护测试。

## 预期初始失败

`python tools/labctl.py check 21` 会报告 `EXPECTED_DYNAMIC_BLOCK_INCOMPLETE`，因为由三条规则组成的替代输入仍会渲染两个硬编码块。

## 验证命令

```text
python tools/labctl.py check 21
python tools/labctl.py status 21
```

## 成功标准

- 默认输入恰好渲染两个内容匹配的 ingress 块。
- 替代输入恰好渲染三个块，且描述、端口和 CIDR 完全匹配。
- 固定的出站边界保持为恰好一条指向 `0.0.0.0/0` 的全协议 egress 规则。
- 无效端口会被拒绝。
- 源代码使用动态 ingress 结构，且不包含重复的静态 ingress 块。
- 验证不会执行 AWS 身份验证或 API 操作。

## 重置说明

```text
python tools/labctl.py reset 21
```

## 有限提示

- dynamic 块包含集合表达式、迭代器和 content 块体。
- content 块体中的值来自当前迭代器元素。
