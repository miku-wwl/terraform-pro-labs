resource "terraform_data" "network_contract" {
  input = {
    vpc_id            = "vpc-lab04-dev"
    subnet_ids        = ["subnet-lab04-a", "subnet-lab04-b"]
    security_group_id = "sg-lab04-app"
  }
}

output "network" {
  value = terraform_data.network_contract.output
}
