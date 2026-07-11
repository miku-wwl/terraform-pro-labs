variable "network_state_path" {
  description = "Optional path to a producer stack's local state snapshot."
  type        = string
  default     = null

  validation {
    condition     = var.network_state_path == null || endswith(var.network_state_path, ".tfstate")
    error_message = "network_state_path must name a .tfstate file."
  }
}

locals {
  network = {
    vpc_id             = "vpc-manually-copied"
    private_subnet_ids = ["subnet-manually-copied"]
    owner              = "unknown"
  }
}

output "network_lookup" {
  value = {
    vpc_id             = local.network.vpc_id
    private_subnet_ids = local.network.private_subnet_ids
    selected_subnet_id = local.network.private_subnet_ids[0]
    owner              = local.network.owner
  }
}
