variables {
  environment   = "dev"
  instance_type = "t3.micro"
  name_prefix   = "tfpro"
}

run "normal_input_produces_expected_summary" {
  command = plan

  module {
    source = "./starter"
  }

  assert {
    condition = output.deployment_summary == {
      environment   = "dev"
      instance_type = "t3.micro"
      name          = "tfpro-dev"
    }
    error_message = "The normal input must produce the expected deployment summary."
  }
}

run "variable_validation_rejects_unknown_environment" {
  command = plan

  module {
    source = "./starter"
  }

  variables {
    environment = "sandbox"
  }

  expect_failures = [var.environment]
}

run "precondition_rejects_unsafe_production_size" {
  command = plan

  module {
    source = "./starter"
  }

  variables {
    environment   = "prod"
    instance_type = "t3.micro"
  }

  expect_failures = [terraform_data.deployment]
}

run "check_reports_short_prefix" {
  command = plan

  module {
    source = "./starter"
  }

  variables {
    name_prefix = "app"
  }

  expect_failures = [check.name_prefix_quality]
}
