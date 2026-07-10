# Lab 16 - Filtered for_each and Stable Map Outputs

## Scenario

A service catalog contains enabled and disabled entries. The current root creates deployment records for every entry and exposes positional lists. Refactor only the selected subset while preserving logical service names in resource addresses and outputs.

## Skills tested

- Filtering a map for `for_each`
- Stable logical resource keys
- Map-shaped outputs derived from managed resources
- Empty-selection boundary behavior

## Difficulty and estimated time

- Difficulty: medium
- Estimated time: 20 minutes

## Execution mode

Local Terraform authoring with `terraform_data`.

## Cloud credentials required

No.

## Cost risk

None.

## Starting state

The input is already a map, but the starter deploys disabled services too and converts results to lists, losing stable output keys.

## Files allowed to edit

- `starter/main.tf`

## Files not allowed to edit

- `starter/versions.tf`
- `tests/public.tftest.hcl`
- `scripts/verify_tests.py`
- `lab.yaml`

## Tasks

1. Derive the enabled subset of the service map.
2. Iterate deployment records only over that subset.
3. Return deployment identifiers and ports as maps keyed by service name.
4. Keep behavior safe when no services are enabled.

## Constraints

- Do not use `count` or positional indexing.
- Do not create a deployment record for a disabled service.
- Preserve input map keys without synthesizing numeric keys.
- Reject ports outside the valid TCP range.

## Expected initial failure

`python tools/labctl.py check 16` reports `EXPECTED_FILTERED_FOREACH_INCOMPLETE` at the test stage because the starter includes a disabled key and returns lists.

## Validation commands

```bash
python tools/labctl.py check 16
python tools/labctl.py status 16
```

## Success criteria

- Default output keys are exactly `api` and `worker`.
- Exact ports remain associated with their logical names.
- Reordering map declarations does not affect identity.
- An all-disabled input produces empty maps.
- An invalid port is rejected before planning resources.

## Reset instructions

```bash
python tools/labctl.py reset 16
```

## Limited hints

- Filter before assigning the collection to the resource.
- Preserve `for_each` keys when shaping outputs.
