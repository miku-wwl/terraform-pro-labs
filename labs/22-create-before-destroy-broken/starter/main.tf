variable "service_name" {
  description = "Stable logical service name."
  type        = string
  default     = "api"
}

variable "release" {
  description = "Immutable release identifier."
  type        = string
  default     = "v1"
}

resource "terraform_data" "service" {
  input = {
    name    = var.service_name
    release = var.release
  }

  triggers_replace = var.release
}

output "service_payload" {
  value = terraform_data.service.output
}
