run "default_values_flow_across_modules" {
  command = plan
  module { source = "./starter" }
  assert {
    condition = output.stack == {
      name_prefix           = "payments-dev"
      instance_profile_name = "payments-dev-profile"
      instance_reference    = "payments-dev::payments-dev-profile"
    }
    error_message = "Root outputs must expose values produced and consumed through the child modules."
  }
}

run "alternate_inputs_are_not_bypassed" {
  command = plan
  module { source = "./starter" }
  variables {
    application = "ledger"
    environment = "prod"
  }
  assert {
    condition     = output.stack.instance_reference == "ledger-prod::ledger-prod-profile"
    error_message = "Alternate root inputs must flow through naming, identity, and compute."
  }
}

run "unsupported_environment_is_rejected" {
  command = plan
  module { source = "./starter" }
  variables { environment = "sandbox" }
  expect_failures = [var.environment]
}
