mock_provider "aws" {}

run "default_rules_render_exact_nested_blocks" {
  command = plan
  module { source = "./starter" }

  assert {
    condition     = length(aws_security_group.web.ingress) == 2
    error_message = "The default input must render exactly two ingress blocks."
  }

  assert {
    condition = alltrue([
      for rule in aws_security_group.web.ingress :
      rule.from_port == rule.to_port &&
      rule.protocol == "tcp" &&
      contains([80, 443], rule.from_port) &&
      one(rule.cidr_blocks) == "0.0.0.0/0"
    ])
    error_message = "Every default nested block must preserve its port, protocol, and CIDR content."
  }
}

run "alternate_input_controls_count_and_content" {
  command = plan
  module { source = "./starter" }
  variables {
    ingress_rules = [
      { description = "Admin", port = 22, cidr_block = "10.0.0.0/8" },
      { description = "App", port = 8080, cidr_block = "10.20.0.0/16" },
      { description = "Metrics", port = 9090, cidr_block = "10.30.0.0/16" }
    ]
  }

  assert {
    condition     = length(aws_security_group.web.ingress) == 3
    error_message = "Nested ingress block count must follow the input collection."
  }

  assert {
    condition = {
      for rule in aws_security_group.web.ingress : rule.description => {
        port = rule.from_port
        cidr = one(rule.cidr_blocks)
      }
      } == {
      Admin   = { port = 22, cidr = "10.0.0.0/8" }
      App     = { port = 8080, cidr = "10.20.0.0/16" }
      Metrics = { port = 9090, cidr = "10.30.0.0/16" }
    }
    error_message = "Each generated block must retain the matching description, port, and CIDR."
  }
}

run "invalid_port_is_rejected" {
  command = plan
  module { source = "./starter" }
  variables {
    ingress_rules = [{ description = "Invalid", port = 70000, cidr_block = "10.0.0.0/8" }]
  }
  expect_failures = [var.ingress_rules]
}
