locals {
  records = {
    logs    = { name = "logs", retention_days = 90 }
    assets  = { name = "assets", retention_days = 30 }
    archive = { name = "archive", retention_days = 365 }
  }
}

moved {
  from = terraform_data.bucket[0]
  to   = terraform_data.bucket["logs"]
}

moved {
  from = terraform_data.bucket[1]
  to   = terraform_data.bucket["assets"]
}

moved {
  from = terraform_data.bucket[2]
  to   = terraform_data.bucket["archive"]
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
