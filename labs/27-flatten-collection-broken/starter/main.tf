variable "global_tags" {
  description = "Lowest-precedence tags applied to every app."
  type        = map(string)
  default = {
    managed_by = "terraform"
    owner      = "central"
    tier       = "shared"
  }
}

variable "team_apps" {
  description = "Nested team and application definitions."
  type = map(object({
    tags = map(string)
    apps = list(object({
      name = string
      tags = map(string)
    }))
  }))

  default = {
    platform = {
      tags = { owner = "platform", cost_center = "100" }
      apps = [
        { name = "api", tags = { tier = "edge" } },
        { name = "worker", tags = {} }
      ]
    }
    payments = {
      tags = { owner = "payments", cost_center = "200" }
      apps = [{ name = "ledger", tags = { managed_by = "payments-pipeline" } }]
    }
  }

  validation {
    condition = alltrue([
      for team in values(var.team_apps) :
      length(distinct([for app in team.apps : app.name])) == length(team.apps)
    ])
    error_message = "Application names must be unique within each team."
  }
}

locals {
  app_rows = [
    for team, config in var.team_apps : {
      key  = team
      team = team
      app  = config.apps[0].name
      tags = merge(var.global_tags, config.apps[0].tags, config.tags)
    }
    if length(config.apps) > 0
  ]

  app_map = { for row in local.app_rows : row.key => row }
}

resource "terraform_data" "app" {
  for_each = local.app_map

  input = {
    team = each.value.team
    app  = each.value.app
    tags = each.value.tags
  }
}

output "app_catalog" {
  value = {
    for key, app in terraform_data.app : key => app.input
  }
}
