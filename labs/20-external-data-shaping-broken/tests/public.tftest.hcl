run "default_files_are_normalized_with_stable_keys" {
  command = plan
  module { source = "./starter" }

  assert {
    condition = output.enabled_apps == {
      assets = { name = "assets", team = "web", versioning = false }
      logs   = { name = "logs", team = "platform", versioning = true }
    }
    error_message = "Enabled apps must be a map keyed by logical app name, with disabled entries removed."
  }

  assert {
    condition = output.bucket_settings == {
      archive = { lifecycle_days = 90, owner = "ops" }
      assets  = { lifecycle_days = null, owner = "web" }
      logs    = { lifecycle_days = 30, owner = "platform" }
    }
    error_message = "CSV rows must be keyed by name and lifecycle_days must be normalized to number or null."
  }
}

run "empty_json_and_zero_day_csv_are_safe" {
  command = plan
  module { source = "./starter" }
  variables {
    apps_fixture    = "apps-empty.json"
    buckets_fixture = "buckets-boundary.csv"
  }

  assert {
    condition     = output.enabled_apps == {}
    error_message = "An empty JSON catalog must create no app records and return an empty map."
  }

  assert {
    condition = output.bucket_settings == {
      scratch = { lifecycle_days = 0, owner = "qa" }
    }
    error_message = "The CSV boundary fixture must preserve zero as a number."
  }
}
