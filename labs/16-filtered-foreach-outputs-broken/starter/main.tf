variable "services" {
  description = "Service configuration keyed by stable logical name."
  type = map(object({
    enabled = bool
    port    = number
  }))

  default = {
    api    = { enabled = true, port = 8080 }
    docs   = { enabled = false, port = 8081 }
    worker = { enabled = true, port = 9090 }
  }

  validation {
    condition     = alltrue([for service in values(var.services) : service.port >= 1 && service.port <= 65535])
    error_message = "Each service port must be between 1 and 65535."
  }
}

resource "terraform_data" "deployment" {
  for_each = { for name, service in var.services : name => service if service.enabled }

  input = {
    name = each.key
    port = each.value.port
  }
}

output "deployment_names" {
  value = { for name, deployment in terraform_data.deployment : name => deployment.input.name }
}

output "deployment_ports" {
  value = { for name, deployment in terraform_data.deployment : name => deployment.input.port }
}
