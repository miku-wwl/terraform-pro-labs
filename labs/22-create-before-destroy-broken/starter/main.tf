# triggers_replace：替换触发条件（replacement triggers）；同一资源只能写一次，但值可由多个字段组成。
# 例如：triggers_replace = [var.release, var.service_name]
# 或：  triggers_replace = { release = var.release, service_name = var.service_name }
# 集合中任意值变化都会触发替换；本 Lab 只让 release 触发替换，名称变化应原地更新。

variable "service_name" {
  description = "Stable logical service name."
  type        = string
  default     = "api"
}

variable "release" {
  description = "Immutable release identifier."
  type        = string
  default     = "v1"
}

resource "terraform_data" "service" {
  input = {
    name    = var.service_name
    release = var.release
  }

  triggers_replace = var.release

  lifecycle {
    create_before_destroy = true
  }
}

output "service_payload" {
  value = terraform_data.service.output
}
