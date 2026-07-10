variable "catalog" {
  description = "Storage records in their current positional form."
  type = list(object({
    name           = string
    versioning     = bool
    retention_days = optional(number)
    tags           = optional(map(string), {})
  }))

  default = [
    { name = "logs", versioning = true, retention_days = 30, tags = { purpose = "logs" } },
    { name = "assets", versioning = false, tags = { purpose = "assets" } },
    { name = "archive", versioning = true, retention_days = 90, tags = { purpose = "archive", managed_by = "records-team" } }
  ]
}

locals {
  base_tags = {
    managed_by = "terraform"
    lab        = "dynamic-config"
  }
}

resource "terraform_data" "record" {
  count = length(var.catalog)

  input = {
    name = var.catalog[count.index].name
    tags = merge(local.base_tags, var.catalog[count.index].tags)
  }
}

resource "terraform_data" "versioning" {
  count = length(var.catalog)

  input = var.catalog[count.index].versioning
}

resource "terraform_data" "retention" {
  count = length(var.catalog)

  input = try(var.catalog[count.index].retention_days, null)
}

output "records" {
  value = [for record in terraform_data.record : record.input]
}

output "versioning" {
  value = [for setting in terraform_data.versioning : setting.input]
}

output "retention_days" {
  value = [for setting in terraform_data.retention : setting.input]
}
