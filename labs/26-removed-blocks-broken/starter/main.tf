resource "terraform_data" "service" {
  input = {
    name  = "payments"
    owner = "platform"
  }
}

output "service" {
  value = terraform_data.service.output
}
