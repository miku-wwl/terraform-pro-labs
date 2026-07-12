variable "producer_state_path" {
  description = "Absolute path to the protected local producer state fixture."
  type        = string
}

data "terraform_remote_state" "network" {
  backend = "local"

  config = {
    path = var.producer_state_path
  }
}

locals {
  network = data.terraform_remote_state.network.outputs.network
}

resource "terraform_data" "application_contract" {
  input = local.network
}

output "consumed_network" {
  value = terraform_data.application_contract.output
}
