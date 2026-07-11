mock_provider "aws" {
  mock_resource "aws_iam_policy" {
    defaults        = { arn = "arn:aws:iam::000000000000:policy/mock-app" }
    override_during = plan
  }
}

run "iam_documents_and_complete_attachment_chain_are_exact" {
  command = plan
  module { source = "./starter" }

  assert {
    condition = (
      jsondecode(aws_iam_role.app.assume_role_policy).Statement[0].Action == "sts:AssumeRole" &&
      jsondecode(aws_iam_role.app.assume_role_policy).Statement[0].Principal.Service == "ec2.amazonaws.com"
    )
    error_message = "The role trust policy must allow the EC2 service to assume the role."
  }

  assert {
    condition = (
      toset(jsondecode(aws_iam_policy.app.policy).Statement[0].Action) == toset(["s3:GetObject", "s3:ListBucket"]) &&
      length(jsondecode(aws_iam_policy.app.policy).Statement[0].Resource) == 2
    )
    error_message = "The managed permissions policy must contain the exact S3 actions and both resource scopes."
  }

  assert {
    condition = (
      aws_iam_role_policy_attachment.app.role == aws_iam_role.app.name &&
      aws_iam_role_policy_attachment.app.policy_arn == aws_iam_policy.app.arn &&
      aws_iam_instance_profile.app.role == aws_iam_role.app.name &&
      aws_instance.app.iam_instance_profile == aws_iam_instance_profile.app.name
    )
    error_message = "Policy attachment, role, instance profile, and EC2 must form one complete reference chain."
  }
}

run "alternate_prefix_flows_through_every_named_link" {
  command = plan
  module { source = "./starter" }
  variables { name_prefix = "orders" }

  assert {
    condition = (
      aws_iam_role.app.name == "orders-role" &&
      aws_iam_policy.app.name == "orders-policy" &&
      aws_iam_instance_profile.app.name == "orders-profile" &&
      aws_iam_role_policy_attachment.app.role == "orders-role" &&
      aws_instance.app.iam_instance_profile == "orders-profile"
    )
    error_message = "Alternate naming input must flow through every IAM-to-EC2 link without hardcoded defaults."
  }
}

run "invalid_name_prefix_is_rejected" {
  command = plan
  module { source = "./starter" }
  variables { name_prefix = "INVALID_NAME" }
  expect_failures = [var.name_prefix]
}
