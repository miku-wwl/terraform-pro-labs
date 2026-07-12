variable "environment" {
  description = "Deployment environment."
  type        = string
  default     = "dev"

  validation {
    condition     = var.environment == "dev" || var.environment == "stage" || var.environment == "prod"
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
      condition     = var.environment != "prod" || var.instance_type != "t3.micro"
      error_message = "production instance type is unsafe."
    }
  }
}

output "deployment_summary" {
  value = terraform_data.deployment.input
}

check "name_prefix_quality" {
  assert {
    condition     = length(var.name_prefix) >= 5
    error_message = "name_prefix does not meet the readability guideline."
  }
}
