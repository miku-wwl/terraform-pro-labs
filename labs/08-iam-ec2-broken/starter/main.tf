variable "name_prefix" {
  description = "Prefix for mocked IAM and EC2 objects."
  type        = string
  default     = "tfpro-app"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,20}$", var.name_prefix))
    error_message = "name_prefix must be 3-21 lowercase letters, digits, or hyphens and start with a letter."
  }
}

variable "ami_id" {
  description = "Deterministic plan-only AMI identifier; no lookup is performed."
  type        = string
  default     = "ami-0123456789abcdef0"
}

locals {
  trust_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })

  permissions_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject", "s3:ListBucket"]
      Resource = ["arn:aws:s3:::example-app-data", "arn:aws:s3:::example-app-data/*"]
    }]
  })
}

resource "aws_iam_role" "app" {
  name               = "${var.name_prefix}-role"
  assume_role_policy = local.trust_policy
}

resource "aws_iam_policy" "app" {
  name   = "${var.name_prefix}-policy"
  policy = local.permissions_policy
}

resource "aws_iam_role_policy_attachment" "app" {
  role       = "${var.name_prefix}-other-role"
  policy_arn = aws_iam_policy.app.arn
}

resource "aws_iam_instance_profile" "app" {
  name = "${var.name_prefix}-profile"
  role = aws_iam_role.app.name
}

resource "aws_instance" "app" {
  ami                  = var.ami_id
  instance_type        = "t3.micro"
  iam_instance_profile = null

  tags = { Name = "${var.name_prefix}-instance" }
}
