variable "environment" {
  description = "Deployment environment."
  type        = string
  default     = "dev"

  validation {
    # TODO: Reject unsupported environment names.
    condition     = var.environment != ""
    error_message = "environment is not supported."
  }
}

variable "instance_type" {
  description = "Requested instance type."
  type        = string
  default     = "t3.micro"
}

variable "name_prefix" {
  description = "Name prefix for generated resources."
  type        = string
  default     = "tfpro"
}

locals {
  deployment_name = format("%s-%s", var.name_prefix, var.environment)
}

resource "terraform_data" "deployment" {
  input = {
    environment   = var.environment
    instance_type = var.instance_type
    name          = local.deployment_name
  }

  lifecycle {
    precondition {
      # TODO: Reject the unsafe production size combination.
      condition     = var.instance_type != ""
      error_message = "production instance type is unsafe."
    }
  }
}

output "deployment_summary" {
  value = terraform_data.deployment.input
}

check "name_prefix_quality" {
  assert {
    # TODO: Warn when the prefix does not meet the naming-quality rule.
    condition     = var.name_prefix != ""
    error_message = "name_prefix does not meet the readability guideline."
  }
}
