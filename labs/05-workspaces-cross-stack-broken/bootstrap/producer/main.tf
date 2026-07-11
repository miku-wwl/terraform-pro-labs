locals {
  networks = {
    dev = {
      vpc_id      = "vpc-lab05-dev"
      subnet_id   = "subnet-lab05-dev"
      environment = "dev"
    }
    prod = {
      vpc_id      = "vpc-lab05-prod"
      subnet_id   = "subnet-lab05-prod"
      environment = "prod"
    }
  }
}

resource "terraform_data" "network" {
  input = local.networks[terraform.workspace]
}

output "network" {
  value = terraform_data.network.output
}
