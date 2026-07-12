# Lab 26 — Moved and Removed State Semantics

## Scenario

An existing service record is renamed in configuration. A separate legacy attachment must leave
Terraform management while the externally owned object is retained. These are different state
transitions and must be expressed separately.

## Skills tested

- `moved` address transitions
- `removed` configuration removal
- `destroy = false` and the plan `forget` action
- plan JSON, state list, and final no-op verification

## Difficulty and estimated time

Medium, about 30 minutes.

## Execution mode

Seeded isolated local state using built-in `terraform_data`.

## Cloud credentials required

None.

## Cost risk

None.

## Starting state

The protected old configuration creates `terraform_data.service_old` and
`terraform_data.legacy_attachment`. The starter contains only the renamed service resource and no
transition declarations.

## Files allowed to edit

- `starter/main.tf`

## Files not allowed to edit

- `lab.yaml`, `bootstrap/`, and `scripts/`
- `starter/versions.tf`

## Tasks

1. Preserve the service identity at `terraform_data.service` through an address move.
2. Remove the legacy attachment from state without planning destruction.
3. Finish with only the service address and a no-op plan.

## Constraints

Do not delete state, use CLI state-move/remove commands, retain the legacy resource block, or allow
any create/delete action. The attachment must use removal semantics that explicitly retain the
underlying object.

## Expected initial failure

After seeding, `python tools/labctl.py check 26` reports
`EXPECTED_MOVED_REMOVED_REFACTOR_INCOMPLETE`; the starter plans service creation and both old
resources' destruction.

## Validation commands

```text
python tools/labctl.py reset 26
python tools/labctl.py seed 26
python tools/labctl.py check 26
```

## Success criteria

- old state initially contains both protected addresses;
- the renamed service has an exact no-op `previous_address` mapping;
- the attachment has the exact `forget` action, not `delete`;
- no create/delete action occurs;
- final state contains only `terraform_data.service`, its value is unchanged, and plan is no-op.

## Reset instructions

```text
python tools/labctl.py reset 26
```

Reset removes only Lab 26's generated state, plans, initialization files, and results.

## Limited hints

A rename still manages the same object. A removal stops managing an object. Only one of those
transitions needs a lifecycle setting controlling whether Terraform destroys the object.
