# Lab 02 - Dynamic Configuration with Stable Iteration

## Scenario

A platform team maintains a catalog of local storage records. The current configuration uses positional `count`, creates optional settings for every record, and returns list-shaped results. Refactor it so logical names remain stable when entries change and optional settings exist only where requested.

## Skills tested

- Stable `for_each` iteration over structured input
- Filtering conditional managed objects
- Merging shared and item-specific metadata
- Shaping outputs as maps keyed by logical name

## Difficulty and estimated time

- Difficulty: medium
- Estimated time: 25 minutes

## Execution mode

Local Terraform authoring with the built-in `terraform_data` resource.

## Cloud credentials required

No. No cloud provider is used.

## Cost risk

None. The validation path plans local logical resources only.

## Starting state

The starter uses list input and positional `count`. Its optional setting records are not filtered, and its main output is a list.

## Files allowed to edit

- `starter/main.tf`

## Files not allowed to edit

- `starter/versions.tf`
- `tests/public.tftest.hcl`
- `scripts/verify_tests.py`
- `lab.yaml`

## Tasks

1. Change the catalog input to a map of objects keyed by logical record name.
2. Give the primary records stable logical addresses.
3. Create versioning and retention setting records only for catalog entries that request them.
4. Merge base tags with entry tags, with entry tags taking precedence.
5. Return map-shaped summaries keyed by the same logical names.

## Constraints

- Do not use positional `count` for catalog iteration.
- Disabled optional behavior must not produce a managed setting record.
- Reject a retention period that is present but less than one day.
- Do not add providers, credentials, external data, or cloud resources.

## Expected initial failure

From the repository root, `python tools/labctl.py check 02` reaches the test stage and reports `EXPECTED_DYNAMIC_CONFIGURATION_INCOMPLETE`. The old implementation does not satisfy the stable map and filtering contract.

## Validation commands

```bash
python tools/labctl.py check 02
python tools/labctl.py status 02
```

## Success criteria

- Default record keys are exactly `archive`, `assets`, and `logs`.
- Optional versioning records exist only for `archive` and `logs`.
- Optional retention records exist only for `archive` and `logs`, with the requested day values.
- An empty catalog produces empty maps without errors.
- Invalid retention input is rejected.
- Item tags override shared tags while required shared tags remain present.

## Reset instructions

```bash
python tools/labctl.py reset 02
```

Reset removes only Terraform caches, lock files, plans, state artifacts, and recorded check results owned by this lab.

## Limited hints

- Resource identity should come from a business key, not a list position.
- Derive the subsets before assigning them to optional resources.
- A map comprehension can preserve the resource keys in an output.
