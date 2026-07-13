variable "create_marker" {
  type    = bool
  default = false
}

variable "marker_name" {
  type    = string
  default = "release"
  validation {
    condition     = trimspace(var.marker_name) != ""
    error_message = "marker_name must not be empty."
  }
}

variable "owner" {
  type    = string
  default = "platform"
}

resource "terraform_data" "marker" {
  count = var.create_marker ? 1 : 0
  input = {
    name  = var.marker_name
    owner = var.owner
  }
}

output "marker_count" {
  value = length(terraform_data.marker)
}

output "selected_name" {
  value = one(terraform_data.marker[*].input.name)
}

output "selected_owner" {
  value = try(terraform_data.marker[0].input.owner, null)
}
