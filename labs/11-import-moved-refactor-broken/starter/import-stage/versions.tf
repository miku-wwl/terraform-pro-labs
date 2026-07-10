terraform {
  required_version = ">= 1.6, < 2.0"

  required_providers {
    random = {
      source  = "hashicorp/random"
      version = "~> 3.7"
    }
  }
}
