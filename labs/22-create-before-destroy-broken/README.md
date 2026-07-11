# Lab 22 - Create-Before-Destroy Replacement Ordering

## Scenario

Releases are immutable, so changing a release identifier must replace the local service record. The current replacement destroys the old record first. Configure lifecycle ordering appropriate for an availability-sensitive rollout.

## Skills tested

- Replacement versus in-place update
- Lifecycle action ordering
- Reading JSON plan actions
- Recognizing the capacity and uniqueness tradeoffs of overlap

## Difficulty and estimated time

- Difficulty: medium
- Estimated time: 20 minutes

## Execution mode

Provider-free Terraform with state created only in a temporary verifier directory.

## Cloud credentials required

No.

## Cost risk

None.

## Starting state

`triggers_replace` makes a release change a genuine replacement, but the starter uses Terraform's default delete-then-create ordering.

## Files allowed to edit

- `starter/main.tf`

## Files not allowed to edit

- `starter/versions.tf`
- `tests/`
- `scripts/`
- `lab.yaml`

## Tasks

1. Preserve the existing replacement trigger and resource address.
2. Configure overlapping replacement so a new service record is planned before the old one is deleted.
3. Run the stateful verifier and inspect the plan action order.

## Constraints

- Do not remove or weaken `triggers_replace`.
- Do not convert the release change into an in-place update.
- Do not change the protected verifier.
- Keep the lab provider-free.

## Expected initial failure

`python tools/labctl.py check 22` reports `EXPECTED_CREATE_BEFORE_DESTROY_INCOMPLETE`; the verifier observes `delete, create` actions after changing `release` from `v1` to `v2`.

## Validation commands

```text
python tools/labctl.py check 22
python tools/labctl.py status 22
```

## Success criteria

- A release change remains a replacement.
- Plan JSON actions for `terraform_data.service` are exactly `create, delete`.
- The check builds and removes isolated temporary state.
- No cloud operation or credential lookup occurs.

## Reset instructions

```text
python tools/labctl.py reset 22
```

## Limited hints

- Replacement causation and replacement ordering are separate concerns.
- The order of actions in plan JSON reveals which object Terraform handles first.
