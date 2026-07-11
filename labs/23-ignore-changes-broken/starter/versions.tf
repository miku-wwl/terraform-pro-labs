terraform {
  required_version = ">= 1.6, < 2.0"

  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.6"
    }
  }
}
