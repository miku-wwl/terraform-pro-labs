locals {
  environment         = terraform.workspace
  producer_state_path = "${var.producer_state_root}/terraform.tfstate.d/${terraform.workspace}/terraform.tfstate"
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

  lifecycle {
    precondition {
      condition     = terraform.workspace != "prod" || var.instance_type != "t3.micro"
      error_message = "t3.micro is not allowed in the prod workspace."
    }
  }
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
