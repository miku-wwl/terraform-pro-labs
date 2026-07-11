variable "byte_length" {
  type = number
}

resource "random_id" "this" {
  byte_length = var.byte_length
}

output "id" {
  value = random_id.this.b64_url
}
