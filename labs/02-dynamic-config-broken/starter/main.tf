variable "catalog" {
  description = "Storage records in their current positional form."
  type = map(object({
    versioning     = bool
    retention_days = optional(number)
    tags           = optional(map(string), {})
  }))

  default = {
    logs    = { name = "logs", versioning = true, retention_days = 30, tags = { purpose = "logs" } },
    assets  = { name = "assets", versioning = false, tags = { purpose = "assets" } },
    archive = { name = "archive", versioning = true, retention_days = 90, tags = { purpose = "archive", managed_by = "records-team" } }
  }

  validation {
    condition = alltrue([
      for record in values(var.catalog) :
      record.retention_days == null || record.retention_days >= 1
    ])

    error_message = "retention_days 提供时必须大于或等于 1。"
  }
}

locals {
  base_tags = {
    managed_by = "terraform"
    lab        = "dynamic-config"
  }
}

resource "terraform_data" "record" {
  for_each = var.catalog

  input = {
    name = each.key
    tags = merge(local.base_tags, each.value.tags)
  }
}

resource "terraform_data" "versioning" {
  for_each = {
    for key, value in var.catalog : key => value if value.versioning
  }

  input = each.value.versioning
}

resource "terraform_data" "retention" {
  for_each = {
    for key, value in var.catalog : key => value if value.retention_days != null
  }

  input = each.value.retention_days
}

output "records" {
  value = {
    for key, record in terraform_data.record : key => record.input
  }
}

output "versioning" {
  value = {
    for key, record in terraform_data.versioning : key => record.input
  }
}

output "retention_days" {
  value = {
    for key, record in terraform_data.retention : key => record.input
  }
}
