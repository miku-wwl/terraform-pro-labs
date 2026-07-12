variable "import_ids" {
  description = "Identifiers released by the protected bootstrap workflow."
  type        = map(string)
}

locals {
  records = {
    api    = 6
    worker = 8
  }
}

module "record" {
  for_each    = local.records
  source      = "../modules/record"
  byte_length = each.value
}

moved {
  from = random_id.legacy["api"]
  to   = module.record["api"].random_id.this
}

moved {
  from = random_id.legacy["worker"]
  to   = module.record["worker"].random_id.this
}

output "record_ids" {
  value = { for name, record in module.record : name => record.id }
}
