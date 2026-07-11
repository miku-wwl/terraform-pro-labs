run "default_nested_catalog_has_exact_keys_and_tag_precedence" {
  command = plan
  module { source = "./starter" }

  assert {
    condition     = keys(output.app_catalog) == ["payments.ledger", "platform.api", "platform.worker"]
    error_message = "Every nested app must have a stable team-and-app key."
  }

  assert {
    condition = (
      length(output.app_catalog["platform.api"].tags) == 4 &&
      output.app_catalog["platform.api"].tags.managed_by == "terraform" &&
      output.app_catalog["platform.api"].tags.owner == "platform" &&
      output.app_catalog["platform.api"].tags.tier == "edge" &&
      output.app_catalog["platform.api"].tags.cost_center == "100"
    )
    error_message = "App tags must override team tags, which must override global tags."
  }

  assert {
    condition     = output.app_catalog["payments.ledger"].tags.managed_by == "payments-pipeline"
    error_message = "The most specific app tag must win merge precedence."
  }
}

run "same_app_name_in_different_teams_keeps_distinct_identity" {
  command = plan
  module { source = "./starter" }
  variables {
    team_apps = {
      alpha = { tags = { owner = "a" }, apps = [{ name = "api", tags = {} }] }
      beta  = { tags = { owner = "b" }, apps = [{ name = "api", tags = {} }] }
      empty = { tags = { owner = "nobody" }, apps = [] }
    }
  }

  assert {
    condition     = keys(output.app_catalog) == ["alpha.api", "beta.api"]
    error_message = "Team identity must disambiguate repeated app names and empty teams must add nothing."
  }
}

run "duplicate_name_within_one_team_is_rejected" {
  command = plan
  module { source = "./starter" }
  variables {
    team_apps = {
      alpha = {
        tags = {}
        apps = [
          { name = "api", tags = {} },
          { name = "api", tags = { tier = "duplicate" } }
        ]
      }
    }
  }
  expect_failures = [var.team_apps]
}
