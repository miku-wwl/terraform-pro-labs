# Questions and option IDs

Use exactly one option ID from each question in `student-answer.md`. Explain the tradeoff in the corresponding rationale section.

## 1. Routine run workflow (`routine_run_workflow`)

- `vcs_default`: Connect each workspace to its reviewed repository and let changes to the selected branch start standard runs.
- `api_default`: Have engineers upload every routine configuration version and create every run through a custom API client.
- `ui_default`: Disconnect source control and ask workspace administrators to start all routine runs in the UI.

## 2. API-driven run boundary (`api_run_boundary`)

- `never_use_api`: Prohibit API-driven runs even for approved machine-to-machine promotion workflows.
- `approved_automation_only`: Reserve API-driven configuration uploads and runs for the exceptional release-service workflow with scoped credentials and auditability.
- `developer_tokens`: Give every developer a broad token and use API-driven runs for ordinary pull-request work.

## 3. Pull-request feedback (`pull_request_feedback`)

- `standard_apply_run`: Start a normal plan-and-apply run for every pull request.
- `speculative_plan`: Use the VCS pull-request integration to produce a plan-only run that cannot be applied.
- `skip_plan`: Wait until after merge before producing any Terraform feedback.

## 4. Workspace dependency (`workspace_dependency`)

- `network_to_application`: Configure `network-prod` as the source and queue `application-prod` after a successful network apply.
- `application_to_network`: Configure `application-prod` as the source and queue `network-prod` after an application apply.
- `pull_request_trigger`: Queue `application-prod` whenever `network-prod` opens a speculative pull-request plan.

## 5. Production policy (`production_policy`)

- `advisory_only`: Report a warning for a publicly reachable database but allow the run to continue automatically.
- `mandatory_no_routine_override`: Block the production run and require the violation to be fixed; do not grant a routine override path for this rule.
- `post_apply_audit`: Check the rule only after infrastructure has been applied.

## 6. Cost estimation (`cost_estimation`)

- `exact_invoice_gate`: Treat the estimate as a complete future invoice and automatically approve any run below it.
- `review_signal_with_limits`: Show estimate and delta during review, while retaining approval controls and acknowledging unsupported or externally priced items.
- `disable_estimation`: Disable estimates because they cannot be perfectly complete.

## 7. Team permissions (`team_permissions`)

- `developers_plan_release_apply`: Give application developers plan-level access and give the release-management team apply access; keep workspace administration separate.
- `developers_apply`: Give all application developers apply and workspace-admin access so reviews never block delivery.
- `admins_only`: Give only organization owners access to view, plan, and apply workspace runs.

## 8. Production auto-apply (`production_auto_apply`)

- `all_runs_auto_apply`: Auto-apply every production run, including dependency-triggered runs, as soon as checks finish.
- `manual_production_boundary`: Keep production applies manual, including run-triggered production runs; allow separately governed low-risk development workspaces to auto-apply.
- `no_automation_anywhere`: Require the organization owners team to manually apply every development and production run.
