run "default_fixture_is_read_through_the_data_boundary" {
  command = plan
  module { source = "./starter" }

  assert {
    condition = (
      toset(keys(output.network_lookup)) == toset(["vpc_id", "private_subnet_ids", "selected_subnet_id", "owner"]) &&
      output.network_lookup.vpc_id == "vpc-shared-primary" &&
      output.network_lookup.private_subnet_ids == tolist(["subnet-primary-a", "subnet-primary-b"]) &&
      output.network_lookup.selected_subnet_id == "subnet-primary-a" &&
      output.network_lookup.owner == "network-platform"
    )
    error_message = "The default producer snapshot must be read and normalized into the exact consumer output contract."
  }
}

run "caller_can_select_an_alternate_producer_snapshot" {
  command = plan
  module { source = "./starter" }

  variables {
    network_state_path = "fixtures/network-secondary.tfstate"
  }

  assert {
    condition = (
      toset(keys(output.network_lookup)) == toset(["vpc_id", "private_subnet_ids", "selected_subnet_id", "owner"]) &&
      output.network_lookup.vpc_id == "vpc-shared-secondary" &&
      output.network_lookup.private_subnet_ids == tolist(["subnet-secondary-only"]) &&
      output.network_lookup.selected_subnet_id == "subnet-secondary-only" &&
      output.network_lookup.owner == "payments-network"
    )
    error_message = "Changing only the lookup path must change every value at the cross-stack output boundary."
  }
}

run "non_state_input_is_rejected" {
  command = plan
  module { source = "./starter" }

  variables {
    network_state_path = "fixtures/network.json"
  }

  expect_failures = [var.network_state_path]
}
