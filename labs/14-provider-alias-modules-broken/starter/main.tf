provider "aws" {
  region = "us-east-1"
}

provider "aws" {
  alias  = "secondary"
  region = "us-west-2"
}

module "regions" {
  source = "./modules/region_report"

  providers = {
    aws           = aws
    aws.secondary = aws.secondary
  }
}

output "module_regions" {
  value = module.regions.regions
}
