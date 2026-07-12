variable "record_name" {
  description = "Name stored in the local deployment record."
  type        = string
  default     = "audit-log"
}

resource "terraform_data" "deployment_record" {
  input = {
    name = var.record_name
  }

  # lifecycle {
  #   prevent_destroy = true
  # }

}

output "deployment_record" {
  value = terraform_data.deployment_record.input
}
