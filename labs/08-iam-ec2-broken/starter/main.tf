# IAM → EC2 权限链复盘：
# 1. IAM Role：定义谁能扮演角色；EC2 信任关系为 Principal = { Service = "ec2.amazonaws.com" }。
# 2. IAM Policy：定义角色能做什么；此处仅允许 s3:GetObject 与 s3:ListBucket。
# 3. Role Policy Attachment：将 Policy 绑定到 Role；role 应引用 aws_iam_role.app.name。
# 4. Instance Profile：EC2 不能直接关联 Role，Profile 通过 role = aws_iam_role.app.name 包含该 Role。
# 5. EC2：通过 iam_instance_profile = aws_iam_instance_profile.app.name 获得这套权限。

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
  role       = aws_iam_role.app.name
  policy_arn = aws_iam_policy.app.arn
}

resource "aws_iam_instance_profile" "app" {
  name = "${var.name_prefix}-profile"
  role = aws_iam_role.app.name
}

resource "aws_instance" "app" {
  ami                  = var.ami_id
  instance_type        = "t3.micro"
  iam_instance_profile = aws_iam_instance_profile.app.name

  tags = { Name = "${var.name_prefix}-instance" }
}
