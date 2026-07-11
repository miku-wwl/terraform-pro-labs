# Lab 27 - Flattened Collections, Stable Keys, and Tag Merging

## Scenario

Teams own nested application lists with global, team, and app tag layers. The starter keeps only the first app per team, keys records only by team, and applies tag precedence incorrectly. Produce a complete, stable catalog.

## Skills tested

- Nested collection comprehensions and `flatten`
- Stable compound keys for `for_each`
- Layered `merge` precedence
- Empty nested collections and duplicate-name validation

## Difficulty and estimated time

- Difficulty: medium
- Estimated time: 25 minutes

## Execution mode

Provider-free local Terraform using `terraform_data`.

## Cloud credentials required

No.

## Cost risk

None.

## Starting state

The input contract and duplicate validation are present. The transform emits at most one app per team and lets team tags overwrite app-specific values.

## Files allowed to edit

- `starter/main.tf`

## Files not allowed to edit

- `starter/versions.tf`
- `tests/`
- `scripts/`
- `lab.yaml`

## Tasks

1. Transform every nested app into one flat row.
2. Build a stable map whose keys include both team and app identity.
3. Merge tags in global, team, then app precedence order.
4. Create one record per app and preserve exact keys in the output.
5. Keep empty teams safe and same-named apps in different teams distinct.

## Constraints

- Use the target flatten and merge constructs rather than hardcoded app records.
- Do not use list indexes as resource identity.
- Do not weaken duplicate-name validation.
- Do not edit protected tests.

## Expected initial failure

`python tools/labctl.py check 27` reports `EXPECTED_NESTED_COLLECTION_TRANSFORM_INCOMPLETE` because apps are missing, keys are unstable for the scenario, and tag precedence is wrong.

## Validation commands

```text
python tools/labctl.py check 27
python tools/labctl.py status 27
```

## Success criteria

- Default keys are exactly `payments.ledger`, `platform.api`, and `platform.worker`.
- Every nested app becomes one record.
- App tags override team tags, and team tags override global tags.
- Same-named apps in different teams retain distinct addresses.
- Empty teams create nothing and duplicate names within one team are rejected.

## Reset instructions

```text
python tools/labctl.py reset 27
```

## Limited hints

- First produce nested row lists, then collapse one collection level.
- Argument order determines which value wins a tag merge.
