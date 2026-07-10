variable "name_prefix" { type = string }
variable "instance_profile_name" { type = string }

resource "terraform_data" "instance" {
  input = {
    name_prefix           = var.name_prefix
    instance_profile_name = var.instance_profile_name
  }
}

output "instance_reference" {
  value = "${terraform_data.instance.input.name_prefix}::${terraform_data.instance.input.instance_profile_name}"
}
