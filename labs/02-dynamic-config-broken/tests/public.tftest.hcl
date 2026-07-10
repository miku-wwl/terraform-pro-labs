run "default_catalog_has_stable_filtered_results" {
  command = plan
  module { source = "./starter" }

  assert {
    condition     = keys(output.records) == ["archive", "assets", "logs"]
    error_message = "Records must be a stable map keyed by the three logical names."
  }
  assert {
    condition     = keys(output.versioning) == ["archive", "logs"]
    error_message = "Only version-enabled records may have versioning settings."
  }
  assert {
    condition     = output.retention_days == { archive = 90, logs = 30 }
    error_message = "Retention settings must contain the exact filtered names and days."
  }
  assert {
    condition     = output.records.archive.tags.managed_by == "records-team" && output.records.logs.tags.managed_by == "terraform"
    error_message = "Entry tags must override base tags without dropping shared defaults."
  }
}

run "empty_catalog_produces_empty_maps" {
  command = plan
  module { source = "./starter" }
  variables { catalog = {} }

  assert {
    condition     = output.records == {} && output.versioning == {} && output.retention_days == {}
    error_message = "An empty catalog must produce three empty maps."
  }
}

run "invalid_retention_is_rejected" {
  command = plan
  module { source = "./starter" }
  variables {
    catalog = { invalid = { versioning = false, retention_days = 0 } }
  }
  expect_failures = [var.catalog]
}
