data "aws_region" "primary" {}

data "aws_region" "secondary" {
  provider = aws.secondary
}

output "regions" {
  value = {
    primary   = data.aws_region.primary.region
    secondary = data.aws_region.secondary.region
  }
}
