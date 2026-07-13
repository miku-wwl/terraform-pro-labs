variable "project_name" {
  description = "Project identifier before normalization."
  type        = string
  default     = "Payments_API"

  validation {
    condition     = can(regex("^[A-Za-z][A-Za-z0-9_-]*[A-Za-z0-9]$", var.project_name)) && length(var.project_name) >= 3 && length(var.project_name) <= 24
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
  normalized_name = replace(
    lower(var.project_name),
    "/[-_]+/",
    "-"
  )
  name_parts = regexall("[a-z0-9]+", local.normalized_name)
  final_name = "${local.normalized_name}-${var.environment}"
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
