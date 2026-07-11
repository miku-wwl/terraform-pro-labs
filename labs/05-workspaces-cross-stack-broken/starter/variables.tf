variable "producer_state_root" {
  description = "Absolute path to the isolated producer root used by protected validation."
  type        = string
}

variable "instance_type" {
  description = "Compute shape selected for the current workspace."
  type        = string
  default     = "t3.micro"
}
