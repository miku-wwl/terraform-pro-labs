# Lab 13 — Workspace-Aware Behavior and Production Guardrails

## Scenario

One local root is deliberately reused across dev, staging, and prod workspaces. Configuration must
select workspace-specific settings, while production blocks undersized capacity and unattended
apply behavior.

## Skills tested

- `terraform.workspace`
- workspace-isolated local state
- environment-aware value selection
- lifecycle preconditions as production guardrails

## Difficulty and estimated time

Medium, about 30 minutes.

## Execution mode

Isolated local workspaces created only in a verifier-owned runtime copy.

## Cloud credentials required

None.

## Cost risk

None. The lab uses only built-in `terraform_data`.

## Starting state

The starter always selects dev settings and its production precondition is permissive. No learner
source workspace is selected or changed by the verifier.

## Files allowed to edit

- `starter/main.tf`

## Files not allowed to edit

- `lab.yaml`
- `starter/versions.tf`
- `scripts/` and `tests/`

## Tasks

1. Derive the active environment from the selected workspace.
2. Select the exact settings for dev, staging, and prod.
3. Allow production only when capacity is not `t3.micro` and `auto_approve` is false.
4. Preserve the resource and output contracts.

## Constraints

Do not add cloud resources, switch workspaces in the learner source directory, or special-case the
verifier paths. Use one production guardrail with the documented diagnostic.

## Expected initial failure

`python tools/labctl.py check 13` reports `EXPECTED_WORKSPACE_GUARDRAIL_INCOMPLETE` when the staging
or prod workspace still emits dev settings.

## Validation commands

```text
python tools/labctl.py reset 13
python tools/labctl.py check 13
```

## Success criteria

- the runtime owns exactly default, dev, staging, and prod workspaces;
- every environment has only `terraform_data.deployment` in its state;
- workspace outputs match the exact replica, tier, and instance settings;
- no plan contains a destroy and each post-apply plan is no-op;
- prod rejects both undersized capacity and auto-approve.

## Reset instructions

```text
python tools/labctl.py reset 13
```

Reset removes only Lab 13 runtime workspaces, state, plans, initialization files, and results.

## Limited hints

The default workspace is not one of the three exercised environments. The guardrail can combine
the non-production case with all production requirements in one Boolean condition.
