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
  for_each = {}

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
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
  cidr_ipv4         = "0.0.0.0/0"
}
