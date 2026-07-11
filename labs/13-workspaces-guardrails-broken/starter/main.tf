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
  environment = "dev"
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
      condition     = var.instance_type != ""
      error_message = "Production requires t3.large or larger and must not use auto-approve."
    }
  }
}

output "selected_environment" {
  value = local.environment
}

output "deployment" {
  value = terraform_data.deployment.output
}
