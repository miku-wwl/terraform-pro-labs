variable "name_prefix" { type = string }

resource "terraform_data" "profile" { input = "${var.name_prefix}-profile" }
output "instance_profile_name" { value = terraform_data.profile.input }
