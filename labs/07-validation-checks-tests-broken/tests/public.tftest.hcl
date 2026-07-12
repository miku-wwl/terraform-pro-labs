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

run "stage_is_a_supported_environment" {
  command = plan

  module {
    source = "./starter"
  }

  variables {
    environment = "stage"
  }

  assert {
    condition = output.deployment_summary == {
      environment   = "stage"
      instance_type = "t3.micro"
      name          = "tfpro-stage"
    }
    error_message = "Stage must remain a supported environment with the normal deployment shape."
  }
}

run "safe_production_size_is_accepted" {
  command = plan

  module {
    source = "./starter"
  }

  variables {
    environment   = "prod"
    instance_type = "t3.large"
  }

  assert {
    condition = output.deployment_summary == {
      environment   = "prod"
      instance_type = "t3.large"
      name          = "tfpro-prod"
    }
    error_message = "The precondition must allow a production deployment that uses a safe size."
  }
}

run "five_character_prefix_meets_the_quality_boundary" {
  command = plan

  module {
    source = "./starter"
  }

  variables {
    name_prefix = "abcde"
  }

  assert {
    condition     = output.deployment_summary.name == "abcde-dev"
    error_message = "A five-character prefix must pass the advisory quality boundary."
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

run "check_reports_four_character_prefix" {
  command = plan

  module {
    source = "./starter"
  }

  variables {
    name_prefix = "apps"
  }

  expect_failures = [check.name_prefix_quality]
}
