# Lab 09：使用独立规则资源的安全组

## 场景

一个安全组外壳必须完全通过独立的 AWS 规则资源管理入站和出站流量。starter 已声明这些资源类型，但没有创建任何入站规则实例，并且将出站流量限制为 HTTPS，而不是允许所有 IPv4 流量。

## 考查技能

- 不含内联规则的安全组外壳资源
- `aws_vpc_security_group_ingress_rule`
- `aws_vpc_security_group_egress_rule`
- 稳定的 `for_each` 键和精确的规则内容

## 难度与预计时间

- 难度：简单
- 预计时间：15 分钟

## 执行模式

`aws-mock`。使用确定性的、仅用于 plan 的 VPC ID；不会查询真实 VPC，也不会发出 AWS 请求。

## 是否需要云凭据

不需要。

## 成本风险

无。

## 初始状态

SG 不包含内联规则。独立的入站规则资源遍历一个空 map，出站规则资源则使用了错误的协议边界。

## 允许编辑的文件

- `starter/main.tf`

## 禁止编辑的文件

- `starter/versions.tf`
- `tests/`
- `scripts/`
- `lab.yaml`

## 任务

1. 为每个稳定的输入键创建一条独立入站规则。
2. 保留每条规则的描述、TCP 端口、CIDR 和 SG 引用。
3. 修正独立出站规则，使其允许所有 IPv4 协议。
4. 确保 SG 外壳不包含内联 ingress 和 egress block。
5. 安全支持空的入站规则 map。

## 约束

- 不要向 `aws_security_group.web` 添加内联规则 block。
- 不要用 list 索引替换稳定的输入键。
- 不要查询默认 VPC，也不要使用真实账户资源。
- 不要编辑受保护的测试。

## 预期初始失败

`python tools/labctl.py check 09` 会报告 `EXPECTED_SEPARATE_SG_RULES_INCOMPLETE`，因为没有创建入站规则，且出站流量仅限 TCP 443。

## 验证命令

```text
python tools/labctl.py check 09
python tools/labctl.py status 09
```

## 成功标准

- 默认入站资源键必须恰好为 `admin` 和 `web`。
- 一个有效的替代键必须成为精确的资源实例键，而不能被过滤或替换为默认键。
- 每条规则都必须保留其精确描述、TCP 协议、端口上下界、CIDR 以及对安全组的直接引用。
- 独立出站规则必须使用协议 `-1`，不设置端口边界，并使用 IPv4 CIDR `0.0.0.0/0`。
- 空入站规则集合不会创建任何入站资源，同时保留出站规则。
- 无效端口的下界和上界都必须被拒绝。
- 不使用静态或动态内联规则、凭据、VPC 查询或 AWS API 请求。

## 重置说明

```text
python tools/labctl.py reset 09
```

## 有限提示

- 当资源标识已经具有有意义的键时，直接使用该 map。
- 允许所有协议的出站规则不使用 TCP 端口边界。
