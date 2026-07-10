variable "record_name" {
  description = "Name stored in the local deployment record."
  type        = string
  default     = "audit-log"
}

resource "terraform_data" "deployment_record" {
  input = {
    name = var.record_name
  }

  # TODO: Protect this managed object from accidental destruction.
}

output "deployment_record" {
  value = terraform_data.deployment_record.input
}
