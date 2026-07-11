variable "service_name" {
  description = "Terraform-owned service identity."
  type        = string
  default     = "checkout"
}

variable "release_version" {
  description = "Terraform-owned release version."
  type        = string
  default     = "v1"
}

variable "external_permission" {
  description = "File permission maintained by an external host policy after creation."
  type        = string
  default     = "0644"
}

resource "local_file" "service" {
  filename = "${path.module}/service.json"
  content = jsonencode({
    name    = var.service_name
    version = var.release_version
  })
  file_permission = var.external_permission

  lifecycle {
    ignore_changes = all
  }
}

output "service_content" {
  value = jsondecode(local_file.service.content)
}
