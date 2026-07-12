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

resource "random_id" "legacy" {
  for_each    = local.records
  byte_length = each.value
}

import {
  for_each = var.import_ids

  to = random_id.legacy[each.key]
  id = each.value
}

output "record_ids" {
  value = { for name, record in random_id.legacy : name => record.b64_url }
}
