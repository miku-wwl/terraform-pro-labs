# Lab 09：使用独立规则资源的安全组

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



## 可编辑文件

- `starter/main.tf`
