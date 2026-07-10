run "disabled_marker_is_safe_and_null" {
  command = plan
  module { source = "./starter" }
  variables { create_marker = false }
  assert {
    condition     = output.marker_count == 0 && output.selected_name == null && output.selected_owner == null
    error_message = "The disabled path must create zero records and expose null optional values."
  }
}

run "enabled_marker_returns_exact_values" {
  command = plan
  module { source = "./starter" }
  variables {
    create_marker = true
    marker_name   = "candidate"
    owner         = "delivery"
  }
  assert {
    condition     = output.marker_count == 1 && output.selected_name == "candidate" && output.selected_owner == "delivery"
    error_message = "The enabled path must create one record and return its exact inputs."
  }
}

run "empty_name_is_rejected" {
  command = plan
  module { source = "./starter" }
  variables { marker_name = "  " }
  expect_failures = [var.marker_name]
}
