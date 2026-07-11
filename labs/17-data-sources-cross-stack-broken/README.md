# Lab 17 - Data Sources and Cross-Stack Lookup Boundaries

## Scenario

An application stack currently contains manually copied network identifiers. Replace them with a local cross-stack data lookup whose producer path is configurable and whose consumer output is normalized.

## Skills tested

- Built-in `terraform_remote_state` data source
- Producer/consumer output contracts
- Configurable external lookup inputs
- Deterministic normalization of looked-up collections
- Expected-failure input tests

## Difficulty and estimated time

- Difficulty: medium
- Estimated time: 20 minutes

## Execution mode

Local state fixtures only. No remote backend is initialized.

## Cloud credentials required

No.

## Cost risk

None.

## Starting state

The output shape exists, but its identifiers are manually copied and the `network_state_path` input has no effect.

## Files allowed to edit

- `starter/main.tf`

## Files not allowed to edit

- `starter/versions.tf`
- `fixtures/`
- `tests/`
- `scripts/`
- `lab.yaml`

## Tasks

1. Read producer outputs through a `terraform_remote_state` data source named `network`.
2. Use the primary fixture when no path is supplied and honor a caller-supplied state path.
3. Return the exact network contract, sorting subnet IDs and selecting the first normalized subnet.
4. Keep invalid non-state paths rejected.

## Constraints

- Do not copy fixture identifiers into the configuration.
- Preserve the variable and output addresses.
- Do not initialize a real remote backend or add a cloud provider.
- Do not edit protected fixtures or tests.

## Expected initial failure

`python tools/labctl.py check 17` reports `EXPECTED_CROSS_STACK_LOOKUP_INCOMPLETE` because the starter ignores both producer fixtures.

## Validation commands

```text
python tools/labctl.py check 17
python tools/labctl.py status 17
```

## Success criteria

- The default fixture produces the exact normalized primary network contract.
- A path input selects the secondary producer without code changes.
- Subnet ordering and selection are deterministic.
- Invalid lookup filenames fail variable validation.
- No external account, default VPC, or network API is required.

## Reset instructions

```text
python tools/labctl.py reset 17
```

## Limited hints

- The local backend accepts a filesystem path in its backend configuration map.
- Separate the raw producer outputs from the normalized consumer object.
