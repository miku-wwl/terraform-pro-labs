# Lab 31 - Partial S3 Backend Configuration

## Scenario

Northstar uses one Terraform root module for development, test, and production. The backend type and organization-wide safety controls are static, while the state bucket, object key, and AWS region are selected during `terraform init` for each environment.

The starter currently places an environment-specific setting in the static backend block. Correct the split without initializing or contacting a real S3 backend.

## Skills tested

- Declaring a static partial backend block
- Separating backend configuration from ordinary Terraform input variables
- Supplying environment-specific backend settings at initialization time
- Recognizing expressions and inappropriate hardcoding inside backend blocks
- Safely resetting backend initialization metadata

## Difficulty and estimated time

- Difficulty: medium
- Estimated time: 20 minutes

## Execution mode

- Default mode: local format, `init -backend=false`, validate, static checks, and a temporary backend-free ordinary-expression plan
- Optional mode: explicitly authorized real S3 backend initialization

## Cloud credentials required

No credentials are required or read by the default validation path. The optional real-backend path requires separately configured AWS authentication and a bucket owned by the learner.

## Cost risk

- Default path: none
- Optional real S3 backend: low storage and request cost; not part of validation

## Starting state

- `starter/main.tf` has a valid S3 backend block with shared static safety settings and one intentionally misplaced init-time setting.
- `backend-dev.hcl.example`, `backend-test.hcl.example`, and `backend-prod.hcl.example` contain safe placeholders and no credentials.
- `starter/variables.tf` demonstrates that `var.environment` is a normal module input, not a backend input.

## Files allowed to edit

- `starter/main.tf`

## Files not allowed to edit

- `starter/variables.tf`
- `starter/versions.tf`
- `backend-dev.hcl.example`
- `backend-test.hcl.example`
- `backend-prod.hcl.example`
- `tests/`
- `scripts/verify_backend.py`
- `lab.yaml`
- `.gitignore`

## Tasks

1. Keep backend-wide safety behavior in the static `backend "s3"` block.
2. Remove environment-specific init-time settings from that block.
3. Do not reference `var`, `local`, `module`, data sources, resources, or interpolation syntax from the backend block.
4. Confirm that each example file supplies the environment-specific backend values required at init time.
5. Leave the ordinary `environment` variable available to the root module only.

## Constraints

- Do not run a real S3 backend initialization for the default exercise.
- Do not place access keys, secret keys, tokens, profiles, role credentials, or real bucket names in examples.
- Do not make backend values depend on ordinary input variables.
- Do not move the S3 backend settings into provider configuration or `.tfvars` files.

## Expected initial failure

From the repository root, the unmodified starter passes format, offline init, and Terraform validation, then fails the static behavior stage with `EXPECTED_PARTIAL_BACKEND_INCOMPLETE` because an init-time parameter remains hardcoded in the backend block.

## Validation commands

Run the complete safe gate from the repository root:

```bash
python tools/labctl.py check 31
```

The manifest executes these commands without contacting S3:

```bash
terraform -chdir=labs/31-partial-backend-config-broken/starter fmt -check -recursive
terraform -chdir=labs/31-partial-backend-config-broken/starter init -backend=false -input=false
terraform -chdir=labs/31-partial-backend-config-broken/starter validate
python labs/31-partial-backend-config-broken/scripts/verify_backend.py --starter labs/31-partial-backend-config-broken/starter --examples labs/31-partial-backend-config-broken
```

Optional real-backend demonstration, only after creating an ignored `backend-dev.hcl` with your own non-placeholder bucket and explicitly authorizing AWS access:

```bash
terraform -chdir=labs/31-partial-backend-config-broken/starter init -reconfigure -backend-config=../backend-dev.hcl
```

The optional command is not part of `labctl check` and must not use an `.example` file unchanged.

Optional-path safety boundary:

- Prerequisites: a learner-owned S3 bucket, separately configured AWS authentication, and confirmation that the selected key is not shared with another stack.
- Maximum expected cost for the documented init-only demonstration: less than USD 0.01 in ordinary use; it creates no infrastructure, but current S3 request pricing and account policy remain the learner's responsibility.
- Cleanup: run `python tools/labctl.py reset 31` to remove local backend metadata. The documented init-only path has no managed resources to destroy. If you later write state to the bucket, inspect ownership and remove only your own state/lock objects through your normal S3 process; this lab never deletes remote objects automatically.
- Known risks: a wrong bucket or key can select shared state, backend state can contain secrets, and interrupted or unauthorized initialization can leave local metadata that must be reset before changing environments.

## Success criteria

- The static configuration contains exactly one S3 backend block.
- Shared encryption and S3 state-lock safety settings remain static.
- Bucket, key, region, authentication, and other environment-specific init parameters are absent from the backend block.
- No Terraform expression is used inside the backend block.
- All three example files are distinct, contain only placeholder backend values, and contain no credentials.
- `var.environment` affects only ordinary configuration evaluation.
- The default verifier strips the backend only in a temporary copy and proves dev, test, and prod each produce their matching deployment label without any provider configuration.
- Format, offline initialization, Terraform validation, checker self-tests, and the actual static check all pass.

## Reset instructions

```bash
python tools/labctl.py reset 31
```

Reset removes lab-owned `.terraform/` directories, including S3 backend initialization metadata, lock files, plans, state artifacts, and recorded results. It does not delete learner-created backend configuration files.

## Limited hints

- Backend initialization happens before ordinary Terraform variables are evaluated.
- Values that differ among dev, test, and prod belong in the files passed with `-backend-config`.
- Static safety behavior that is identical in every environment can remain in the backend block.
