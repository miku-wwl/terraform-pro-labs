# 输出引用速查：
# 同模块内部         → 引用资源 / local / module 的原始值
# 父模块读子模块     → module.child.output_name
# 另一套配置读 state → data.terraform_remote_state.x.outputs.output_name
# 命令行查看输出     → terraform output output_name

variable "producer_state_path" {
  description = "Absolute path to the selected producer's local state fixture."
  type        = string
}

variable "consumer_name" {
  description = "Name recorded in this consumer's own state."
  type        = string
  default     = "payments"
}

data "terraform_remote_state" "network" {
  backend = "local"
  config = {
    path = var.producer_state_path
  }
}


resource "terraform_data" "consumer_contract" {
  input = {
    consumer = var.consumer_name
    network  = data.terraform_remote_state.network.outputs.network
  }
}

output "consumed_network" {
  value = terraform_data.consumer_contract.output.network
}

output "consumer_name" {
  value = terraform_data.consumer_contract.output.consumer
}
