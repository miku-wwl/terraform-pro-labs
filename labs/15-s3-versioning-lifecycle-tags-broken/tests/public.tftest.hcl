mock_provider "aws" {}

run "default_configuration_has_exact_filtered_resources" {
  command = plan
  module { source = "./starter" }

  assert {
    condition     = toset(keys(aws_s3_bucket.this)) == toset(["archive", "assets", "logs"])
    error_message = "All configured buckets must use their logical names as stable resource keys."
  }

  assert {
    condition     = toset(keys(aws_s3_bucket_versioning.this)) == toset(["archive", "logs"])
    error_message = "Versioning resources must exist only for buckets whose versioning flag is true."
  }

  assert {
    condition     = toset(keys(aws_s3_bucket_lifecycle_configuration.this)) == toset(["archive", "logs"])
    error_message = "Lifecycle resources must exist only where lifecycle_days is configured."
  }

  assert {
    condition = {
      for name, resource in aws_s3_bucket_versioning.this :
      name => resource.versioning_configuration[0].status
      } == {
      archive = "Enabled"
      logs    = "Enabled"
    }
    error_message = "Every selected versioning resource must be enabled."
  }

  assert {
    condition = {
      for name, resource in aws_s3_bucket_lifecycle_configuration.this :
      name => resource.rule[0].expiration[0].days
      } == {
      archive = 90
      logs    = 30
    }
    error_message = "Lifecycle expiration days must remain paired with the matching bucket key."
  }

  assert {
    condition = aws_s3_bucket.this["logs"].tags == tomap({
      lab        = "s3"
      managed_by = "compliance"
      purpose    = "logs"
    })
    error_message = "Bucket-specific tags must override common tags on key collisions."
  }

  assert {
    condition = output.bucket_names == {
      archive = "tfpro-s3-archive"
      assets  = "tfpro-s3-assets"
      logs    = "tfpro-s3-logs"
    }
    error_message = "bucket_names must be an exact logical-name-to-bucket-name map."
  }

  assert {
    condition = output.versioned_buckets == {
      archive = "tfpro-s3-archive"
      logs    = "tfpro-s3-logs"
    }
    error_message = "versioned_buckets must be a filtered map with stable logical keys."
  }

  assert {
    condition = output.lifecycle_buckets == {
      archive = 90
      logs    = 30
    }
    error_message = "lifecycle_buckets must map only selected logical keys to their retention days."
  }
}

run "unmanaged_boundary_produces_empty_conditional_maps" {
  command = plan
  module { source = "./starter" }

  variables {
    prefix = "boundary"
    buckets = {
      cache = {
        versioning = false
        tags       = { purpose = "cache" }
      }
    }
  }

  assert {
    condition     = keys(aws_s3_bucket.this) == ["cache"]
    error_message = "The ordinary bucket must still be planned for the boundary input."
  }

  assert {
    condition     = length(aws_s3_bucket_versioning.this) == 0 && length(aws_s3_bucket_lifecycle_configuration.this) == 0
    error_message = "No conditional resource may be planned when both optional behaviors are disabled."
  }

  assert {
    condition     = output.versioned_buckets == {} && output.lifecycle_buckets == {}
    error_message = "Conditional outputs must be empty maps rather than positional lists."
  }
}

run "invalid_retention_is_rejected" {
  command = plan
  module { source = "./starter" }

  variables {
    buckets = {
      invalid = { versioning = false, lifecycle_days = 0 }
    }
  }

  expect_failures = [var.buckets]
}
