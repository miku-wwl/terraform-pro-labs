mock_provider "aws" {
  mock_resource "aws_security_group" {
    defaults        = { id = "sg-0123456789abcdef0" }
    override_during = plan
  }
}

run "default_separate_rules_have_exact_keys_and_content" {
  command = plan
  module { source = "./starter" }

  assert {
    condition     = keys(aws_vpc_security_group_ingress_rule.web) == ["admin", "web"]
    error_message = "Ingress rules must use the stable input map keys."
  }

  assert {
    condition = (
      aws_vpc_security_group_ingress_rule.web["admin"].security_group_id == aws_security_group.web.id &&
      aws_vpc_security_group_ingress_rule.web["admin"].description == "Administrative access" &&
      aws_vpc_security_group_ingress_rule.web["admin"].ip_protocol == "tcp" &&
      aws_vpc_security_group_ingress_rule.web["admin"].from_port == 22 &&
      aws_vpc_security_group_ingress_rule.web["admin"].to_port == 22 &&
      aws_vpc_security_group_ingress_rule.web["admin"].cidr_ipv4 == "10.0.0.0/8" &&
      aws_vpc_security_group_ingress_rule.web["web"].security_group_id == aws_security_group.web.id &&
      aws_vpc_security_group_ingress_rule.web["web"].description == "HTTPS access" &&
      aws_vpc_security_group_ingress_rule.web["web"].ip_protocol == "tcp" &&
      aws_vpc_security_group_ingress_rule.web["web"].from_port == 443 &&
      aws_vpc_security_group_ingress_rule.web["web"].to_port == 443 &&
      aws_vpc_security_group_ingress_rule.web["web"].cidr_ipv4 == "0.0.0.0/0"
    )
    error_message = "Each independent ingress rule must preserve its exact SG reference, description, protocol, ports, and CIDR."
  }

  assert {
    condition = (
      aws_vpc_security_group_egress_rule.all_ipv4.security_group_id == aws_security_group.web.id &&
      aws_vpc_security_group_egress_rule.all_ipv4.description == "All IPv4 egress" &&
      aws_vpc_security_group_egress_rule.all_ipv4.ip_protocol == "-1" &&
      aws_vpc_security_group_egress_rule.all_ipv4.from_port == null &&
      aws_vpc_security_group_egress_rule.all_ipv4.to_port == null &&
      aws_vpc_security_group_egress_rule.all_ipv4.cidr_ipv4 == "0.0.0.0/0"
    )
    error_message = "The independent egress rule must allow unbounded IPv4 protocols through the same security group."
  }
}

run "alternate_valid_map_preserves_new_stable_key_and_content" {
  command = plan
  module { source = "./starter" }
  variables {
    ingress_rules = {
      metrics = {
        description = "Metrics endpoint"
        port        = 9090
        cidr_ipv4   = "10.20.0.0/16"
      }
    }
  }

  assert {
    condition     = keys(aws_vpc_security_group_ingress_rule.web) == ["metrics"]
    error_message = "An alternate valid caller key must become the exact ingress resource instance key."
  }
  assert {
    condition = (
      aws_vpc_security_group_ingress_rule.web["metrics"].security_group_id == aws_security_group.web.id &&
      aws_vpc_security_group_ingress_rule.web["metrics"].description == "Metrics endpoint" &&
      aws_vpc_security_group_ingress_rule.web["metrics"].ip_protocol == "tcp" &&
      aws_vpc_security_group_ingress_rule.web["metrics"].from_port == 9090 &&
      aws_vpc_security_group_ingress_rule.web["metrics"].to_port == 9090 &&
      aws_vpc_security_group_ingress_rule.web["metrics"].cidr_ipv4 == "10.20.0.0/16"
    )
    error_message = "The alternate rule must preserve every caller-supplied field and the direct SG reference."
  }
}

run "empty_ingress_keeps_only_independent_egress" {
  command = plan
  module { source = "./starter" }
  variables { ingress_rules = {} }

  assert {
    condition     = length(aws_vpc_security_group_ingress_rule.web) == 0
    error_message = "An empty ingress map must create no ingress rule resources."
  }
  assert {
    condition     = aws_vpc_security_group_egress_rule.all_ipv4.ip_protocol == "-1"
    error_message = "The separate egress rule must remain present when ingress is empty."
  }
}

run "invalid_ingress_port_is_rejected" {
  command = plan
  module { source = "./starter" }
  variables {
    ingress_rules = {
      invalid = { description = "Invalid", port = 70000, cidr_ipv4 = "10.0.0.0/8" }
    }
  }
  expect_failures = [var.ingress_rules]
}

run "port_below_lower_boundary_is_rejected" {
  command = plan
  module { source = "./starter" }
  variables {
    ingress_rules = {
      invalid = { description = "Invalid", port = 0, cidr_ipv4 = "10.0.0.0/8" }
    }
  }
  expect_failures = [var.ingress_rules]
}
