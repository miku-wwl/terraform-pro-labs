terraform {
  backend "s3" {
    encrypt      = true
    use_lockfile = true
  }
}

locals {
  deployment_label = "network-${var.environment}"
}

output "deployment_label" {
  description = "Ordinary configuration derived after backend initialization."
  value       = local.deployment_label
}
