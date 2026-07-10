terraform {
  backend "s3" {
    # TODO: Correct the boundary between static and init-time backend settings.
    encrypt      = true
    use_lockfile = true
    key          = "network/shared.tfstate"
  }
}

locals {
  deployment_label = "network-${var.environment}"
}

output "deployment_label" {
  description = "Ordinary configuration derived after backend initialization."
  value       = local.deployment_label
}
