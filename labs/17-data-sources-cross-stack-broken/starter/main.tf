variable "network_state_path" {
  description = "Optional path to a producer stack's local state snapshot."
  type        = string
  default     = null

  validation {
    condition     = var.network_state_path == null || endswith(var.network_state_path, ".tfstate")
    error_message = "network_state_path must name a .tfstate file."
  }
}

data "terraform_remote_state" "network" {
  backend = "local"
  config = {
    path = coalesce(
      var.network_state_path,
      "${path.module}/../fixtures/network-primary.tfstate"
    )
  }
}

output "network_lookup" {
  value = {
    vpc_id             = data.terraform_remote_state.network.outputs.vpc_id
    private_subnet_ids = sort(data.terraform_remote_state.network.outputs.private_subnet_ids)
    selected_subnet_id = sort(data.terraform_remote_state.network.outputs.private_subnet_ids)[0]
    owner              = data.terraform_remote_state.network.outputs.owner
  }
}
