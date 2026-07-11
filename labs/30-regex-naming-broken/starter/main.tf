variable "project_name" {
  description = "Project identifier before normalization."
  type        = string
  default     = "Payments_API"

  validation {
    condition     = can(regex("^[A-Za-z0-9_-]+$", var.project_name))
    error_message = "project_name does not satisfy the naming policy."
  }
}

variable "environment" {
  description = "Deployment environment suffix."
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "stage", "prod"], var.environment)
    error_message = "environment must be one of dev, stage, prod."
  }
}

locals {
  normalized_name = lower(var.project_name)
  name_parts      = regexall("[a-z0-9]+", local.normalized_name)
  final_name      = "${local.normalized_name}-${var.environment}"
}

output "normalized_name" {
  value = local.normalized_name
}

output "name_parts" {
  value = local.name_parts
}

output "final_name" {
  value = local.final_name
}
