mock_provider "aws" {
  mock_data "aws_region" {
    defaults = { region = "mock-primary" }
  }
}

mock_provider "aws" {
  alias = "secondary"
  mock_data "aws_region" {
    defaults = { region = "mock-secondary" }
  }
}

run "each_region_data_source_uses_the_intended_provider" {
  command = plan
  module { source = "./starter" }

  assert {
    condition = output.provider_regions == {
      primary   = "mock-primary"
      secondary = "mock-secondary"
    }
    error_message = "Primary and secondary region reads must use their matching provider configurations."
  }
}
