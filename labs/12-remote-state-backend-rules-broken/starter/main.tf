variable "producer_state_path" {
  description = "Absolute path to the selected producer's local state fixture."
  type        = string
}

variable "consumer_name" {
  description = "Name recorded in this consumer's own state."
  type        = string
  default     = "payments"
}

locals {
  copied_network = {
    environment = "dev"
    vpc_id      = "vpc-lab12-dev"
    subnet_ids  = ["subnet-lab12-dev-a", "subnet-lab12-dev-b"]
  }
}

resource "terraform_data" "consumer_contract" {
  input = {
    consumer = var.consumer_name
    network  = local.copied_network
  }
}

output "consumed_network" {
  value = local.copied_network
}

output "consumer_name" {
  value = terraform_data.consumer_contract.output.consumer
}
