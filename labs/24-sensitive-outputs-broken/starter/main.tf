variable "db_username" {
  description = "Non-secret database username."
  type        = string
  default     = "app_user"
}

variable "db_password" {
  description = "Database password supplied at runtime."
  type        = string
  sensitive   = true
  nullable    = false
}

locals {
  connection_uri = format(
    "postgres://%s:%s@db.internal:5432/app",
    var.db_username,
    var.db_password,
  )
}

resource "terraform_data" "database_config" {
  input = {
    username = var.db_username
    password = var.db_password
  }
}

output "connection_uri" {
  value     = local.connection_uri
  sensitive = true
}

output "database_config" {
  value     = terraform_data.database_config.output
  sensitive = true
}

output "credential_metadata" {
  value = {
    username            = var.db_username
    password_configured = nonsensitive(length(var.db_password) > 0)
  }
}

output "password_debug" {
  value = nonsensitive(var.db_password)
}
