run "valid_name_is_normalized_and_tokenized" {
  command = plan
  module { source = "./starter" }
  variables {
    project_name = "Payments_API"
    environment  = "stage"
  }
  assert {
    condition     = output.normalized_name == "payments-api"
    error_message = "Uppercase letters and underscore separators must normalize predictably."
  }
  assert {
    condition = (
      length(output.name_parts) == 2 &&
      output.name_parts[0] == "payments" &&
      output.name_parts[1] == "api" &&
      output.final_name == "payments-api-stage"
    )
    error_message = "Tokenization and the environment-qualified final name must use normalized content."
  }
}

run "minimum_length_boundary_is_valid" {
  command = plan
  module { source = "./starter" }
  variables { project_name = "A_1" }
  assert {
    condition     = output.normalized_name == "a-1"
    error_message = "A valid three-character boundary value must normalize successfully."
  }
}

run "maximum_length_boundary_is_valid" {
  command = plan
  module { source = "./starter" }
  variables { project_name = "A23456789012345678901234" }
  assert {
    condition     = length(output.normalized_name) == 24
    error_message = "A valid 24-character boundary value must be accepted unchanged except case."
  }
}

run "leading_digit_is_rejected" {
  command = plan
  module { source = "./starter" }
  variables { project_name = "1project" }
  expect_failures = [var.project_name]
}

run "trailing_separator_is_rejected" {
  command = plan
  module { source = "./starter" }
  variables { project_name = "app-" }
  expect_failures = [var.project_name]
}

run "illegal_character_is_rejected" {
  command = plan
  module { source = "./starter" }
  variables { project_name = "app.name" }
  expect_failures = [var.project_name]
}

run "length_outside_policy_is_rejected" {
  command = plan
  module { source = "./starter" }
  variables { project_name = "ab" }
  expect_failures = [var.project_name]
}

run "above_maximum_length_is_rejected" {
  command = plan
  module { source = "./starter" }
  variables { project_name = "A234567890123456789012345" }
  expect_failures = [var.project_name]
}
