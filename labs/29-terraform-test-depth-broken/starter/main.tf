variable "service_name" {
  description = "Service identifier recorded in each deployment."
  type        = string
  default     = "checkout"
}

variable "release_version" {
  description = "Release identifier in v<positive integer> form."
  type        = string
  default     = "v1"

  validation {
    condition     = can(regex("^v[1-9][0-9]*$", var.release_version))
    error_message = "release_version must use v followed by a positive integer."
  }
}

resource "terraform_data" "deployment" {
  input = {
    service = var.service_name
    release = var.release_version
  }

  triggers_replace = [var.release_version]
}

output "deployment" {
  value = terraform_data.deployment.output
}

output "deployment_id" {
  value = terraform_data.deployment.id
}
