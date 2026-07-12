# Lab 01 — Terraform CLI and `prevent_destroy`

## Scenario

Your team tracks a local deployment record with Terraform. The record is safe to create during practice, but it represents an object that operators must not remove accidentally. Add lifecycle protection and use the Terraform CLI to verify that a destroy plan is blocked.

## Skills tested

- Running `terraform fmt`, `terraform init`, `terraform validate`, and `terraform plan`
- Understanding the difference between configuration validation and a behavioral plan
- Protecting a managed object with `prevent_destroy`

## Difficulty and estimated time

- Difficulty: easy
- Estimated time: 10 minutes

## Execution mode

- Mode: local Terraform execution
- Backend: isolated local state created by the protected verifier

## Cloud credentials required

No. This lab uses the built-in `terraform_data` resource.

## Cost risk

None. The default workflow creates no cloud resources.

## Starting state

The starter configuration is valid and can produce a normal create plan, but it does not yet block destruction. The automated check creates state only inside a temporary directory and removes that directory when finished.

## Files allowed to edit

- `starter/main.tf`

## Files not allowed to edit

- `starter/versions.tf`
- `lab.yaml`
- `scripts/verify_prevent_destroy.py`

## Tasks

1. From `starter/`, run the standard Terraform CLI initialization and validation workflow.
2. Add lifecycle protection to `terraform_data.deployment_record` so Terraform refuses a destroy plan.
3. Run the repository check and inspect the lifecycle diagnostic it exercises.

## Constraints

- Do not replace the resource type or resource address.
- Do not change the verifier.
- Do not add an AWS provider or any cloud resource.
- The protection must be expressed in Terraform lifecycle configuration, not by making the configuration invalid.

## Expected initial failure

`python tools/labctl.py check 01` reaches the lifecycle test and fails with `EXPECTED_GUARD_MISSING` because the starter permits a destroy plan.

## Validation commands

From the repository root:

```text
terraform -chdir=labs/01-lifecycle-cli-broken/starter fmt -check
terraform -chdir=labs/01-lifecycle-cli-broken/starter init -backend=false
terraform -chdir=labs/01-lifecycle-cli-broken/starter validate
python tools/labctl.py check 01
```

## Success criteria

- Formatting, initialization, and validation pass.
- A normal create plan remains valid.
- A destroy plan for `terraform_data.deployment_record` is rejected specifically because lifecycle protection is enabled.
- No cloud credentials or cloud operations are used.

## Reset instructions

From the repository root:

```text
python tools/labctl.py reset 01
```

The verifier's state is temporary; reset removes only lab-owned initialization files, plans, state, and recorded check results.

## Limited hints

- Lifecycle rules belong to the managed resource whose destruction must be blocked.
- `terraform validate` alone cannot prove that a destroy operation is protected.
