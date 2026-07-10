variable "application" { type = string }
variable "environment" {
  type = string
  validation {
    condition     = contains(["dev", "test", "prod"], var.environment)
    error_message = "environment must be dev, test, or prod."
  }
}

locals { name_prefix = "${var.application}-${var.environment}" }

resource "terraform_data" "name" { input = local.name_prefix }
output "name_prefix" { value = terraform_data.name.input }
