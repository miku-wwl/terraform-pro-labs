variable "apps_fixture" {
  description = "JSON fixture filename under the protected fixtures directory."
  type        = string
  default     = "apps.json"
}

variable "buckets_fixture" {
  description = "CSV fixture filename under the protected fixtures directory."
  type        = string
  default     = "buckets.csv"
}

locals {
  apps_raw    = jsondecode(file("${path.module}/../fixtures/${var.apps_fixture}"))
  buckets_raw = csvdecode(file("${path.module}/../fixtures/${var.buckets_fixture}"))

  enabled_apps = [for app in local.apps_raw : app if app.enabled]
  bucket_rows  = [for row in local.buckets_raw : row]
}

resource "terraform_data" "app" {
  for_each = { for index, app in local.enabled_apps : tostring(index) => app }

  input = {
    name       = each.value.name
    team       = each.value.team
    versioning = each.value.versioning
  }
}

output "enabled_apps" {
  value = [for app in terraform_data.app : app.input]
}

output "bucket_settings" {
  value = local.bucket_rows
}
