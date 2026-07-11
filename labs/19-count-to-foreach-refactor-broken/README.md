# Lab 19 — Preserve State from `count` to `for_each`

## Scenario

Three local bucket records already exist at count-indexed state addresses. Refactor them to stable
logical keys without replacing any object or changing its stored values.

## Skills tested

- count-index and `for_each` addressing
- exact multi-instance `moved` mappings
- plan JSON and state-list inspection
- identity-preserving state refactors

## Difficulty and estimated time

Hard, about 35 minutes.

## Execution mode

Seeded, isolated local state using built-in `terraform_data`.

## Cloud credentials required

None.

## Cost risk

None.

## Starting state

`python tools/labctl.py seed 19` applies the protected old configuration and creates
`terraform_data.bucket[0]`, `[1]`, and `[2]`. The starter already has the desired keyed resources
but no state-transition declarations.

## Files allowed to edit

- `starter/main.tf`

## Files not allowed to edit

- `lab.yaml`, `bootstrap/`, `scripts/`, and `tests/`
- `starter/versions.tf`

## Tasks

1. Preserve index 0 as key `logs`, index 1 as `assets`, and index 2 as `archive`.
2. Produce zero create/delete actions during the refactor.
3. Finish with only the three keyed addresses and a no-op plan.

## Constraints

Do not delete or recreate state, change record values, use `terraform state mv`, or return to
`count`. Preserve the protected old configuration as the source fixture.

## Expected initial failure

After a fresh seed, `python tools/labctl.py check 19` reports
`EXPECTED_COUNT_TO_FOREACH_REFACTOR_INCOMPLETE`; the starter plans indexed deletes and keyed creates.

## Validation commands

```text
python tools/labctl.py reset 19
python tools/labctl.py seed 19
python tools/labctl.py check 19
```

## Success criteria

- all three old addresses are present before the refactor;
- plan JSON contains the exact 0→logs, 1→assets, and 2→archive no-op mappings;
- no create or delete action occurs;
- final state contains exactly the three logical-key addresses;
- values remain unchanged and the final plan is no-op.

## Reset instructions

```text
python tools/labctl.py reset 19
```

Reset deletes only Lab 19's `.lab-state`, generated initialization/plan files, and results.

## Limited hints

Terraform needs a separate explicit address transition for every old instance. The order of the
map in source is not a substitute for declaring those transitions.
