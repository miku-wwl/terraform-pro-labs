mock_provider "aws" {
  mock_data "aws_region" {
    defaults = { region = "module-primary" }
  }
}

mock_provider "aws" {
  alias = "secondary"
  mock_data "aws_region" {
    defaults = { region = "module-secondary" }
  }
}

run "root_maps_both_provider_configurations_into_child" {
  command = plan
  module { source = "./starter" }

  assert {
    condition = output.module_regions == {
      primary   = "module-primary"
      secondary = "module-secondary"
    }
    error_message = "The child module must receive the default and aliased root providers under matching local names."
  }
}
