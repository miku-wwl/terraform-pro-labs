run "default_selection_preserves_exact_keys_and_values" {
  command = plan
  module { source = "./starter" }
  assert {
    condition     = toset(keys(terraform_data.deployment)) == toset(["api", "worker"])
    error_message = "The managed resource instances themselves must exclude the disabled service."
  }
  assert {
    condition     = output.deployment_names == { api = "api", worker = "worker" }
    error_message = "Only enabled services may appear, keyed by their stable logical names."
  }
  assert {
    condition     = output.deployment_ports == { api = 8080, worker = 9090 }
    error_message = "Ports must remain associated with their logical service keys."
  }
}

run "all_disabled_produces_empty_maps" {
  command = plan
  module { source = "./starter" }
  variables {
    services = {
      second = { enabled = false, port = 2000 }
      first  = { enabled = false, port = 1000 }
    }
  }
  assert {
    condition     = length(terraform_data.deployment) == 0
    error_message = "An all-disabled catalog must create zero managed deployment records."
  }
  assert {
    condition     = output.deployment_names == {} && output.deployment_ports == {}
    error_message = "An all-disabled catalog must return empty maps."
  }
}

run "alternate_keys_remain_resource_identities" {
  command = plan
  module { source = "./starter" }
  variables {
    services = {
      zeta  = { enabled = true, port = 3000 }
      alpha = { enabled = false, port = 1000 }
      beta  = { enabled = true, port = 2000 }
    }
  }
  assert {
    condition     = toset(keys(terraform_data.deployment)) == toset(["beta", "zeta"])
    error_message = "Alternate enabled service names must become the exact managed resource keys."
  }
  assert {
    condition = (
      output.deployment_names == { beta = "beta", zeta = "zeta" } &&
      output.deployment_ports == { beta = 2000, zeta = 3000 }
    )
    error_message = "Alternate output maps must preserve the same logical keys and values as the resources."
  }
}

run "invalid_port_is_rejected" {
  command = plan
  module { source = "./starter" }
  variables { services = { api = { enabled = true, port = 70000 } } }
  expect_failures = [var.services]
}
