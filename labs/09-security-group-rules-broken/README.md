# Lab 09：使用独立资源管理安全组规则

## 任务

安全组本体只负责定义安全组，不在其中写内联的 `ingress` 或 `egress` 规则。

根据 `ingress_rules` map 为每个键创建一条独立的入站规则，并保留规则的描述、TCP 端口、CIDR 和所属安全组。

修正独立的出站规则，使其允许所有 IPv4 出站流量。空的 `ingress_rules` 也必须正常工作，不创建任何入站规则。



## 约束

- 不要向 `aws_security_group.web` 添加内联规则。
- 使用 map 的键作为规则身份，不要改成列表索引。
- 不要查询默认 VPC，也不要读取真实账号资源。
- 只能编辑 `starter/main.tf`。
