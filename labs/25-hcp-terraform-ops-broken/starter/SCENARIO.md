# Northstar HCP Terraform operating model

Northstar is moving its shared infrastructure delivery into HCP Terraform.

Two remote-execution workspaces are already planned:

- `network-prod` owns production VPCs and publishes network outputs.
- `application-prod` consumes those outputs and deploys production applications.

Each workspace has configuration in a reviewed Git repository. Engineers open pull requests, and merges to the protected default branch are the normal change path. A release service also exists for exceptional, pre-approved promotion workflows where it must upload a previously assembled configuration version and create a run programmatically.

Production constraints:

- A security rule forbidding publicly reachable databases is non-negotiable.
- A cost increase should be visible to reviewers, but estimates may not cover every provider, resource, discount, or external charge.
- Application developers may propose and inspect production changes, but a smaller release-management team owns production apply approval.
- Development environments are low risk and may use more automation.
- A production application run should be queued when a production network change has applied successfully.

Your task is to choose an operating model that gives quick feedback without allowing review-only activity, dependency automation, or incomplete cost data to bypass production controls.
