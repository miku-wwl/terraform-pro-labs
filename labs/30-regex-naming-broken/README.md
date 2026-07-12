# Lab 30 - Regex Naming Validation and Normalization

## Scenario

A shared naming module accepts project identifiers, normalizes them for downstream resources, and appends an environment. The starter allows invalid leading/trailing characters and lengths, and it fails to normalize separators.

## Skills tested

- Anchored regex validation
- Length and boundary rules
- Case and separator normalization
- `regexall` token extraction

## Difficulty and estimated time

- Difficulty: medium
- Estimated time: 20 minutes

## Execution mode

Provider-free local Terraform tests.

## Cloud credentials required

No.

## Cost risk

None.

## Starting state

The starter checks only the allowed character set and lowercases input. It does not enforce the complete naming grammar or convert separators to hyphens.

## Files allowed to edit

- `starter/main.tf`

## Files not allowed to edit

- `starter/versions.tf`
- `tests/`
- `scripts/`
- `lab.yaml`

## Tasks

1. Enforce a project name length from 3 through 24 characters.
2. Require a leading letter and a trailing alphanumeric character.
3. Permit letters, numbers, underscores, and hyphens only.
4. Normalize case and runs of underscore/hyphen separators to one hyphen.
5. Preserve token extraction and environment suffixing from the normalized value.

## Constraints

- Use regex semantics for the naming grammar rather than enumerating protected examples.
- Do not weaken environment validation.
- Do not hardcode expected output values.
- Do not edit protected tests.

## Expected initial failure

`python tools/labctl.py check 30` reports `EXPECTED_REGEX_NAMING_INCOMPLETE` because normalization is incomplete and invalid leading, trailing, and length cases are accepted.

## Validation commands

```text
python tools/labctl.py check 30
python tools/labctl.py status 30
```

## Success criteria

- Valid mixed-case input with a consecutive mixed separator run normalizes to the exact expected name.
- Both the 3-character and 24-character boundaries are accepted.
- Leading digits or separators, trailing hyphens or underscores, illegal characters, and values below or above the length range are rejected.
- Tokens and final environment-qualified names derive from normalized content.
- Unsupported environments remain rejected.

## Reset instructions

```text
python tools/labctl.py reset 30
```

## Limited hints

- Anchor a naming grammar at both ends.
- Terraform's string replacement can interpret a slash-delimited pattern as a regex.
