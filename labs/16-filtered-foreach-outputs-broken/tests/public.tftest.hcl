run "default_selection_preserves_exact_keys_and_values" {
  command = plan
  module { source = "./starter" }
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
    condition     = output.deployment_names == {} && output.deployment_ports == {}
    error_message = "An all-disabled catalog must create no deployment entries."
  }
}

run "invalid_port_is_rejected" {
  command = plan
  module { source = "./starter" }
  variables { services = { api = { enabled = true, port = 70000 } } }
  expect_failures = [var.services]
}
