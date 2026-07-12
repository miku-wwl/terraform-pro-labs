# AWS VPC 基础设施通常按以下顺序搭建：
# 1. VPC：定义 CIDR 与 DNS 配置；2. Subnet：按可用区划分公有/私有子网。
# 3. Internet Gateway / NAT Gateway：提供公网或私网出网能力。
# 4. Route Table + Association：将各子网关联到正确的路由。
# 5. Security Group：作为实例、负载均衡器等资源的有状态虚拟防火墙。
# 6. EC2、ALB、RDS 等业务资源：引用 subnet 与 security group。
# 本 Lab 假设 VPC 已存在，只接收 vpc_id；重点练习第 5 步：
# 用独立规则资源管理 Security Group，入站规则由 ingress_rules map 驱动，出站规则单独维护。

variable "vpc_id" {
  description = "Deterministic plan-only VPC ID."
  type        = string
  default     = "vpc-0123456789abcdef0"
}

variable "ingress_rules" {
  description = "Ingress rules keyed by stable purpose."
  type = map(object({
    description = string
    port        = number
    cidr_ipv4   = string
  }))

  default = {
    admin = { description = "Administrative access", port = 22, cidr_ipv4 = "10.0.0.0/8" }
    web   = { description = "HTTPS access", port = 443, cidr_ipv4 = "0.0.0.0/0" }
  }

  validation {
    condition     = alltrue([for rule in values(var.ingress_rules) : rule.port >= 1 && rule.port <= 65535])
    error_message = "Ingress ports must be between 1 and 65535."
  }
}

resource "aws_security_group" "web" {
  name        = "tfpro-separate-rules"
  description = "Security group shell with separately managed rules"
  vpc_id      = var.vpc_id
}

resource "aws_vpc_security_group_ingress_rule" "web" {
  for_each = var.ingress_rules

  security_group_id = aws_security_group.web.id
  description       = each.value.description
  ip_protocol       = "tcp"
  from_port         = each.value.port
  to_port           = each.value.port
  cidr_ipv4         = each.value.cidr_ipv4
}

resource "aws_vpc_security_group_egress_rule" "all_ipv4" {
  security_group_id = aws_security_group.web.id
  description       = "All IPv4 egress"
  ip_protocol       = "-1"
  cidr_ipv4         = "0.0.0.0/0"
}
