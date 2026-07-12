# Lab 21：动态嵌套 ingress 块

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



## 可编辑文件

- `starter/main.tf`
