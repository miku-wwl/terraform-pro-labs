run "default_catalog_has_stable_filtered_results" {
  command = plan
  module { source = "./starter" }

  assert {
    condition     = keys(terraform_data.record) == ["archive", "assets", "logs"]
    error_message = "Primary records must use the three logical names as for_each instance keys."
  }
  assert {
    condition     = keys(terraform_data.versioning) == ["archive", "logs"]
    error_message = "Only version-enabled records may have keyed versioning resource instances."
  }
  assert {
    condition     = keys(terraform_data.retention) == ["archive", "logs"]
    error_message = "Only records with retention configured may have keyed retention resource instances."
  }
  assert {
    condition = (
      terraform_data.record["archive"].input.name == "archive" &&
      terraform_data.record["archive"].input.tags == {
        lab        = "dynamic-config"
        managed_by = "records-team"
        purpose    = "archive"
      } &&
      terraform_data.record["assets"].input.name == "assets" &&
      terraform_data.record["assets"].input.tags == {
        lab        = "dynamic-config"
        managed_by = "terraform"
        purpose    = "assets"
      } &&
      terraform_data.record["logs"].input.name == "logs" &&
      terraform_data.record["logs"].input.tags == {
        lab        = "dynamic-config"
        managed_by = "terraform"
        purpose    = "logs"
      }
    )
    error_message = "Every primary record must contain its exact logical name and merged tag values."
  }
  assert {
    condition = (
      terraform_data.versioning["archive"].input == true &&
      terraform_data.versioning["logs"].input == true &&
      terraform_data.retention["archive"].input == 90 &&
      terraform_data.retention["logs"].input == 30
    )
    error_message = "Optional resource instances must retain their exact requested values."
  }
  assert {
    condition = (
      keys(output.records) == ["archive", "assets", "logs"] &&
      keys(output.versioning) == ["archive", "logs"] &&
      output.versioning == { archive = true, logs = true } &&
      output.retention_days == { archive = 90, logs = 30 } &&
      output.records.archive == terraform_data.record["archive"].input &&
      output.records.assets == terraform_data.record["assets"].input &&
      output.records.logs == terraform_data.record["logs"].input
    )
    error_message = "Outputs must expose exact maps derived from the keyed managed records."
  }
}

run "alternate_catalog_preserves_caller_keys_and_values" {
  command = plan
  module { source = "./starter" }

  variables {
    catalog = {
      api = {
        versioning     = true
        retention_days = 1
        tags           = { managed_by = "api-team", tier = "edge" }
      }
      cache = {
        versioning = false
        tags       = { tier = "internal" }
      }
    }
  }

  assert {
    condition = (
      keys(terraform_data.record) == ["api", "cache"] &&
      keys(terraform_data.versioning) == ["api"] &&
      keys(terraform_data.retention) == ["api"]
    )
    error_message = "Alternate caller keys must become the exact primary and filtered resource instance keys."
  }
  assert {
    condition = (
      terraform_data.record["api"].input.name == "api" &&
      terraform_data.record["api"].input.tags == {
        lab        = "dynamic-config"
        managed_by = "api-team"
        tier       = "edge"
      } &&
      terraform_data.record["cache"].input.name == "cache" &&
      terraform_data.record["cache"].input.tags == {
        lab        = "dynamic-config"
        managed_by = "terraform"
        tier       = "internal"
      } &&
      terraform_data.versioning["api"].input == true &&
      terraform_data.retention["api"].input == 1
    )
    error_message = "Alternate records must preserve exact values and tag precedence without hardcoded defaults."
  }
  assert {
    condition = (
      output.records.api == terraform_data.record["api"].input &&
      output.records.cache == terraform_data.record["cache"].input &&
      output.versioning == { api = true } &&
      output.retention_days == { api = 1 }
    )
    error_message = "Alternate outputs must be exact maps derived from the alternate resource instances."
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
