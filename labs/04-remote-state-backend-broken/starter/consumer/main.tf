variable "producer_state_path" {
  description = "Absolute path to the protected local producer state fixture."
  type        = string
}

locals {
  network = {
    vpc_id            = "vpc-manually-copied"
    subnet_ids        = ["subnet-manually-copied"]
    security_group_id = "sg-manually-copied"
  }
}

# TODO: Read the producer contract from its state instead of maintaining a copied value.

resource "terraform_data" "application_contract" {
  input = local.network
}

output "consumed_network" {
  value = terraform_data.application_contract.output
}
