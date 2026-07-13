variable "service_name" {
  description = "Mutable service display name."
  type        = string
  default     = "checkout"
}

variable "release_version" {
  description = "Version tracked by the upstream release marker."
  type        = string
  default     = "v1"
}

resource "terraform_data" "release_marker" {
  input = {
    version = var.release_version
  }
}

resource "terraform_data" "service" {
  input = {
    name = var.service_name
  }

  lifecycle {
    replace_triggered_by = [terraform_data.release_marker]
  }
}

output "service_state" {
  value = terraform_data.service.output
}
