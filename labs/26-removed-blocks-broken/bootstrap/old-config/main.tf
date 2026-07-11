resource "terraform_data" "service_old" {
  input = {
    name  = "payments"
    owner = "platform"
  }
}

resource "terraform_data" "legacy_attachment" {
  input = {
    name   = "external-monitoring-binding"
    policy = "retained-outside-terraform"
  }
}

output "service" {
  value = terraform_data.service_old.output
}

output "attachment" {
  value = terraform_data.legacy_attachment.output
}
