provider "aws" {
  region  = "us-east-1"
  profile = "missing-training-profile"
}

provider "aws" {
  alias  = "secondary"
  region = "us-west-2"
}

data "aws_region" "primary" {}

data "aws_region" "secondary" {}

output "provider_regions" {
  value = {
    primary   = data.aws_region.primary.region
    secondary = data.aws_region.secondary.region
  }
}
