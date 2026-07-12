# Lab 23 - Precise `ignore_changes` Ownership Boundary

## Scenario

Terraform owns a local service record's JSON content, while an external host policy may revise only its file permission. The starter ignores all changes, hiding drift in Terraform-owned content as well.

## Skills tested

- Attribute-path precision in `ignore_changes`
- Shared ownership boundaries
- Controlled state drift and plan interpretation
- Distinguishing an allowed no-op from required reconciliation

## Difficulty and estimated time

- Difficulty: medium
- Estimated time: 20 minutes

## Execution mode

Local-provider Terraform with controlled state copies created only in a temporary verifier directory.

## Cloud credentials required

No.

## Cost risk

None.

## Starting state

The lifecycle rule is syntactically valid but ignores every field, including Terraform-owned file content.

## Files allowed to edit

- `starter/main.tf`

## Files not allowed to edit

- `starter/versions.tf`
- `tests/`
- `scripts/`
- `lab.yaml`

## Tasks

1. Narrow the lifecycle exception to only the externally-owned permission field.
2. Preserve Terraform management of the JSON content derived from service name and release version.
3. Verify the permission, content, and filename drift cases with the repository check.

## Constraints

- Do not use `ignore_changes = all`.
- Do not ignore `content`, `filename`, or all resource fields.
- Do not delete or modify the protected lifecycle verifier.

## Expected initial failure

`python tools/labctl.py check 23` reports `EXPECTED_IGNORE_CHANGES_BOUNDARY_INCOMPLETE`: permission drift is tolerated, but Terraform-owned content and filename drift are incorrectly hidden too.

## Validation commands

```text
python tools/labctl.py check 23
python tools/labctl.py status 23
```

## Success criteria

- External permission-only drift produces no resource action.
- Terraform-owned content drift produces a reconciliation action.
- Terraform-owned filename drift produces a reconciliation action.
- The lifecycle exception does not suppress filename, name, or version management.
- Controlled state and plans exist only during the protected temporary check.

## Reset instructions

```text
python tools/labctl.py reset 23
```

## Limited hints

- Lifecycle ignore paths can target one provider schema attribute.
- A correct shared-ownership policy should distinguish one externally-owned field from both managed fields.
