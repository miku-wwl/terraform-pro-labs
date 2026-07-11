locals {
  records = {
    api    = 6
    worker = 8
  }
}

resource "random_id" "legacy" {
  for_each    = local.records
  byte_length = each.value
}

output "import_ids" {
  value = { for name, record in random_id.legacy : name => record.b64_url }
}
