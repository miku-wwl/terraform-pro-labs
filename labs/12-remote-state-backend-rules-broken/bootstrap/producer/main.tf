variable "environment" {
  type = string
}

locals {
  networks = {
    dev = {
      vpc_id     = "vpc-lab12-dev"
      subnet_ids = ["subnet-lab12-dev-a", "subnet-lab12-dev-b"]
    }
    prod = {
      vpc_id     = "vpc-lab12-prod"
      subnet_ids = ["subnet-lab12-prod-a", "subnet-lab12-prod-b"]
    }
  }
}

resource "terraform_data" "network" {
  input = merge({ environment = var.environment }, local.networks[var.environment])
}

output "network" {
  value = terraform_data.network.output
}
