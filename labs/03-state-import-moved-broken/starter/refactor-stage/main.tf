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

# TODO: Preserve both keyed identities while moving them into module instances.

output "record_ids" {
  value = { for name, record in module.record : name => record.id }
}
