variable "network" {
  description = "Network contract published by this protected producer fixture."
  type = object({
    vpc_id            = string
    subnet_ids        = list(string)
    security_group_id = string
  })

  default = {
    vpc_id            = "vpc-lab04-dev"
    subnet_ids        = ["subnet-lab04-a", "subnet-lab04-b"]
    security_group_id = "sg-lab04-app"
  }
}

resource "terraform_data" "network_contract" {
  input = var.network
}

output "network" {
  value = terraform_data.network_contract.output
}
