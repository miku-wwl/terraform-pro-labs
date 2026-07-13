variable "instance_type" {
  description = "Instance class recorded for the active environment."
  type        = string
  default     = "t3.micro"
}

variable "auto_approve" {
  description = "Whether the deployment workflow is allowed to apply without review."
  type        = bool
  default     = false
}

locals {
  environment = terraform.workspace
  settings = {
    default = {
      replicas = 1
      tier     = "sandbox"
    }
    dev = {
      replicas = 1
      tier     = "sandbox"
    }
    staging = {
      replicas = 2
      tier     = "preproduction"
    }
    prod = {
      replicas = 4
      tier     = "production"
    }
  }
  selected = local.settings[local.environment]
}

resource "terraform_data" "deployment" {
  input = {
    environment   = local.environment
    instance_type = var.instance_type
    auto_approve  = var.auto_approve
    replicas      = local.selected.replicas
    tier          = local.selected.tier
  }

  lifecycle {
    precondition {
      condition     = local.environment != "prod" || ((var.instance_type == "t3.large" || var.instance_type == "t3.xlarge" || var.instance_type == "t3.2xlarge") && var.auto_approve == false)
      error_message = "Production requires an approved size and must not use auto-approve."
    }
  }
}

output "selected_environment" {
  value = local.environment
}

output "deployment" {
  value = terraform_data.deployment.output
}
