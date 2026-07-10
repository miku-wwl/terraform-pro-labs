resource "random_id" "this" {
  byte_length = 8
}

output "id" {
  value = random_id.this.b64_url
}
