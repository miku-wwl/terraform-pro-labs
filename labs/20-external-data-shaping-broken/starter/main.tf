variable "apps_fixture" {
  description = "JSON fixture filename under the protected fixtures directory."
  type        = string
  default     = "apps.json"

  validation {
    condition     = can(regex("^[A-Za-z0-9][A-Za-z0-9_-]*\\.json$", var.apps_fixture))
    error_message = "apps_fixture must be a simple .json filename."
  }
}

variable "buckets_fixture" {
  description = "CSV fixture filename under the protected fixtures directory."
  type        = string
  default     = "buckets.csv"

  validation {
    condition     = can(regex("^[A-Za-z0-9][A-Za-z0-9_-]*\\.csv$", var.buckets_fixture))
    error_message = "buckets_fixture must be a simple .csv filename."
  }
}

locals {
  apps_raw    = jsondecode(file("${path.module}/../fixtures/${var.apps_fixture}"))
  buckets_raw = csvdecode(file("${path.module}/../fixtures/${var.buckets_fixture}"))

  enabled_apps = {
    for app in local.apps_raw : app.name => app
    if app.enabled
  }

  bucket_settings = {
    for row in local.buckets_raw : row.name => {
      lifecycle_days = row.lifecycle_days == "" ? null : tonumber(row.lifecycle_days)
      owner          = row.owner
    }
  }
}

resource "terraform_data" "app" {
  for_each = local.enabled_apps

  input = {
    name       = each.value.name
    team       = each.value.team
    versioning = each.value.versioning
  }
}

output "enabled_apps" {
  value = {
    for name, app in terraform_data.app : name => app.input
  }
}

output "bucket_settings" {
  value = local.bucket_settings
}
