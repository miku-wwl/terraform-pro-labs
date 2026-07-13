# `removed` 块需要 Terraform 1.7+；当前 TF Pro 1.6 学习阶段了解其语义即可，不作为冲刺重点。
# 它用于从 state 忘记资源；`destroy = false` 会保留底层对象，交由外部工具或团队管理。

resource "terraform_data" "service" {
  input = {
    name  = "payments"
    owner = "platform"
  }
}

moved {
  from = terraform_data.service_old
  to   = terraform_data.service
}

removed {
  from = terraform_data.legacy_attachment
  lifecycle {
    destroy = false
  }
}

output "service" {
  value = terraform_data.service.output
}
