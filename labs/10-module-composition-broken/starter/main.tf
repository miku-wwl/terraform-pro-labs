variable "application" {
  type    = string
  default = "payments"
}

variable "environment" {
  type    = string
  default = "dev"

  validation {
    condition     = contains(["dev", "test", "prod"], var.environment)
    error_message = "environment must be dev, test, or prod."
  }
}

# TODO: Declare and connect the naming, identity, and compute modules.

output "stack" {
  value = {
    name_prefix           = module.naming.name_prefix
    instance_profile_name = module.naming.name_prefix
    instance_reference    = module.compute.instance_reference
  }
}
