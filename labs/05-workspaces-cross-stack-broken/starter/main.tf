locals {
  environment         = "dev"
  producer_state_path = "${var.producer_state_root}/terraform.tfstate.d/dev/terraform.tfstate"
}

data "terraform_remote_state" "network" {
  backend = "local"

  config = {
    path = local.producer_state_path
  }
}

resource "terraform_data" "deployment" {
  input = {
    environment   = local.environment
    network       = data.terraform_remote_state.network.outputs.network
    instance_type = var.instance_type
  }

  # TODO: Add the production safety boundary.
}

output "selected_environment" {
  value = terraform_data.deployment.output.environment
}

output "network" {
  value = terraform_data.deployment.output.network
}

output "instance_type" {
  value = terraform_data.deployment.output.instance_type
}
