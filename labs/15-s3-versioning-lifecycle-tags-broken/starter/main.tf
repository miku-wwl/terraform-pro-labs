variable "prefix" {
  description = "Prefix applied to mock-planned bucket names."
  type        = string
  default     = "tfpro-s3"
}

variable "buckets" {
  description = "Bucket configuration keyed by stable logical name."
  type = map(object({
    versioning     = bool
    lifecycle_days = optional(number)
    tags           = optional(map(string), {})
  }))

  default = {
    logs = {
      versioning     = true
      lifecycle_days = 30
      tags = {
        managed_by = "compliance"
        purpose    = "logs"
      }
    }
    assets = {
      versioning = false
      tags       = { purpose = "assets" }
    }
    archive = {
      versioning     = true
      lifecycle_days = 90
      tags           = { purpose = "archive" }
    }
  }

  validation {
    condition = alltrue([
      for config in values(var.buckets) :
      try(config.lifecycle_days, null) == null || try(config.lifecycle_days, 0) > 0
    ])
    error_message = "lifecycle_days must be null or a positive number."
  }
}

locals {
  base_tags = {
    managed_by = "terraform"
    lab        = "s3"
  }
}

resource "aws_s3_bucket" "this" {
  for_each = var.buckets

  bucket = "${var.prefix}-${each.key}"
  tags   = merge(local.base_tags, each.value.tags)
}

resource "aws_s3_bucket_versioning" "this" {
  for_each = {
    for name, config in var.buckets : name => config if config.versioning
  }


  bucket = aws_s3_bucket.this[each.key].id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "this" {
  for_each = {
    for name, config in var.buckets : name => config if config.lifecycle_days != null
  }


  bucket = aws_s3_bucket.this[each.key].id

  rule {
    id     = "expire-managed-objects"
    status = "Enabled"

    filter {}

    expiration {
      days = coalesce(try(each.value.lifecycle_days, null), 7)
    }
  }
}

output "bucket_names" {
  value = { for name, bucket in aws_s3_bucket.this : name => bucket.bucket }
}

output "versioned_buckets" {
  value = {
    for name in keys(aws_s3_bucket_versioning.this) :
    name => aws_s3_bucket.this[name].bucket
  }
}

output "lifecycle_buckets" {
  value = {
    for name, lifecycle in aws_s3_bucket_lifecycle_configuration.this :
    name => lifecycle.rule[0].expiration[0].days
  }
}
