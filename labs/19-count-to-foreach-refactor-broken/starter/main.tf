locals {
  records = {
    logs    = { name = "logs", retention_days = 90 }
    assets  = { name = "assets", retention_days = 30 }
    archive = { name = "archive", retention_days = 365 }
  }
}

resource "terraform_data" "bucket" {
  for_each = local.records

  input = each.value
}

output "records" {
  value = {
    for key, record in terraform_data.bucket : key => record.output
  }
}
