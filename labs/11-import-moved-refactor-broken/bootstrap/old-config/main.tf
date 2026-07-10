resource "random_id" "legacy_record" {
  byte_length = 8
}

output "import_id" {
  value = random_id.legacy_record.b64_url
}
