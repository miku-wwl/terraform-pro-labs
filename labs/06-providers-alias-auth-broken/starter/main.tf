provider "aws" {
  region = "us-east-1"
}

provider "aws" {
  alias  = "secondary"
  region = "us-west-2"
}

data "aws_region" "primary" {}

data "aws_region" "secondary" {
  provider = aws.secondary
}

output "provider_regions" {
  value = {
    primary   = data.aws_region.primary.region
    secondary = data.aws_region.secondary.region
  }
}
