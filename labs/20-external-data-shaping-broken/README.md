# Lab 20 - External JSON and CSV Data Shaping

## Scenario

An application catalog and bucket policy table arrive as JSON and CSV files. The starter decodes both files, but it retains positional identities and raw string-shaped CSV rows. Normalize the data before using it.

## Skills tested

- `file`, `jsondecode`, and `csvdecode`
- Collection normalization and type conversion
- Stable `for_each` keys
- Map-shaped outputs and empty-input behavior

## Difficulty and estimated time

- Difficulty: medium
- Estimated time: 25 minutes

## Execution mode

Local Terraform authoring with deterministic fixtures and `terraform_data`.

## Cloud credentials required

No.

## Cost risk

None.

## Starting state

The starter reads the protected fixtures and filters disabled apps, but uses numeric identities, returns a list, and leaves decoded CSV fields as strings.

## Files allowed to edit

- `starter/main.tf`

## Files not allowed to edit

- `starter/versions.tf`
- `fixtures/`
- `tests/`
- `scripts/`
- `lab.yaml`

## Tasks

1. Normalize enabled JSON app records into a map keyed by app name.
2. Use that stable map for the app records and preserve keys in the output.
3. Normalize CSV rows into a map keyed by bucket name.
4. Convert non-empty lifecycle days to numbers and represent an empty field as `null`.
5. Support the protected empty and boundary fixtures without special cases.

## Constraints

- Read data from the selected fixture files; do not reproduce fixture content in HCL.
- Do not use numeric or positional resource keys.
- Do not edit protected fixtures or tests.
- Keep the default workflow provider-free and local.

## Expected initial failure

`python tools/labctl.py check 20` reports `EXPECTED_EXTERNAL_DATA_SHAPING_INCOMPLETE` because the decoded results do not have the required stable map shapes or normalized CSV types.

## Validation commands

```text
python tools/labctl.py check 20
python tools/labctl.py status 20
```

## Success criteria

- Default app keys are exactly `assets` and `logs`.
- App values retain the exact team and versioning data.
- Bucket settings are keyed by name with numeric-or-null lifecycle days.
- Empty JSON produces no app records and an empty map.
- The zero-day CSV boundary remains numeric zero.

## Reset instructions

```text
python tools/labctl.py reset 20
```

## Limited hints

- Decode first, then reshape into the collection used by `for_each`.
- Normalize the empty CSV string before numeric conversion.
