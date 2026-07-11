locals {
  records = [
    { name = "logs", retention_days = 90 },
    { name = "assets", retention_days = 30 },
    { name = "archive", retention_days = 365 },
  ]
}

resource "terraform_data" "bucket" {
  count = length(local.records)

  input = local.records[count.index]
}

output "records" {
  value = {
    for index, record in terraform_data.bucket : tostring(index) => record.output
  }
}
