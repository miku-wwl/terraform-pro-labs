# Lab 05 — Workspace-Isolated Cross-Stack Consumption

## Scenario

A network producer publishes different contracts from its `dev` and `prod` workspaces. The application consumer has matching workspaces, but its routing is hardcoded to development and production lacks an instance-size safety boundary.

## Skills tested

- Using `terraform.workspace` in ordinary configuration
- Reading matching workspace state through `terraform_remote_state`
- Inspecting addresses in isolated workspace states
- Enforcing a production-only precondition
- Resetting only lab-owned workspaces and state

## Difficulty and estimated time

- Difficulty: medium
- Estimated time: 35 minutes

## Execution mode

The protected verifier copies producer and consumer configurations under Lab 05 `.lab-state/`, creates only `dev` and `prod` there, and uses local state.

## Cloud credentials required

None.

## Cost risk

None. Only built-in `terraform_data` and local state are used.

## Starting state

The protected producer derives its network contract from its workspace. The consumer already uses local `terraform_remote_state`, but both its environment label and producer-state path are fixed to development, and its deployment has no production guardrail.

## Files allowed to edit

- `starter/main.tf`

## Files not allowed to edit

- `starter/variables.tf`, `starter/versions.tf`, `bootstrap/`, `scripts/`, `tests/`, and `lab.yaml`

## Tasks

1. Derive the selected environment from the current workspace.
2. Route each consumer workspace to the matching producer workspace state.
3. Reject `t3.micro` only in production with the documented diagnostic.
4. Preserve successful dev and prod plans without destroy actions.

## Constraints

- Do not hardcode dev/prod output values.
- Do not create or select workspaces outside the protected runtime copy.
- Do not change protected workspace names or state layouts.

## Expected initial failure

The starter passes format, offline initialization, and validation, then reports `EXPECTED_WORKSPACE_FLOW_INCOMPLETE` when the prod consumer still selects development state.

## Validation commands

```text
python tools/labctl.py reset 05
python tools/labctl.py check 05
python tools/labctl.py check 05 --mode solution
python tools/labctl.py status 05
```

## Success criteria

- Producer and consumer runtime roots contain only `default`, `dev`, and `prod` workspaces.
- Each producer workspace contains exactly `terraform_data.network`.
- Each consumer workspace contains the remote-state data source and `terraform_data.deployment`.
- Dev consumes the complete dev network object and prod consumes the complete prod network object, including exact environment, VPC, and subnet values.
- Neither initial consumer plan destroys resources, and both final plans are no-op.
- A prod plan using `t3.micro` fails with `t3.micro is not allowed in the prod workspace.`

## Reset instructions

`python tools/labctl.py reset 05` deletes the Lab 05 `.lab-state/` runtime tree and recorded results. It never enters or modifies workspaces in the source directory or any unrelated Terraform root.

## Limited hints

- Named local-backend workspace states live below `terraform.tfstate.d/<workspace>/`.
- A lifecycle precondition can refer to both the current workspace and an input value.
