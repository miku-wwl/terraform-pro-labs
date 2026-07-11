# Lab 04 — Backend Boundaries and Local Cross-Stack State

## Scenario

A network producer owns an output contract. An application consumer currently maintains a copied version of that contract, while its optional S3 backend declaration incorrectly contains an environment-specific value. Correct both boundaries without contacting AWS.

## Skills tested

- Separating producer configuration, consumer configuration, and backend initialization values
- Consuming a local state fixture with `terraform_remote_state`
- Keeping expressions and environment-specific values out of backend blocks
- Inspecting state addresses and proving a final no-op plan

## Difficulty and estimated time

- Difficulty: medium
- Estimated time: 30 minutes

## Execution mode

Default validation bootstraps local producer state under `.lab-state/`. The S3 backend files are an offline, optional extension only.

## Cloud credentials required

None for the default workflow. An optional real S3 initialization requires separate authorization and learner-owned infrastructure.

## Cost risk

Default: none. Optional S3 storage/request charges are outside validation.

## Starting state

`bootstrap/producer/` is the protected producer. `starter/consumer/` uses a manually copied network value. `starter/backend.tf.example` keeps shared backend safety settings but also contains one misplaced init-time setting.

## Files allowed to edit

- `starter/consumer/main.tf`
- `starter/backend.tf.example`

## Files not allowed to edit

- `bootstrap/`, `backend-dev.hcl.example`, version files, `scripts/`, `tests/`, and `lab.yaml`

## Tasks

1. Read the producer's `network` output through the supplied local state path.
2. Feed the consumed value into the application contract and output it.
3. Leave only shared static safety settings in the optional S3 backend block.
4. Keep bucket, key, and region in the init-time example.

## Constraints

- Do not copy or hardcode producer output values.
- Do not use Terraform expressions inside the backend block.
- Do not add credentials or initialize S3 during normal validation.

## Expected initial failure

The starter passes format, offline initialization, and validation, then reports `EXPECTED_BACKEND_CROSS_STACK_INCOMPLETE` because it uses copied values and keeps an init-time key in the backend declaration.

## Validation commands

```text
python tools/labctl.py reset 04
python tools/labctl.py check 04
python tools/labctl.py check 04 --mode solution
```

Optional and not part of validation: copy both `.example` files, supply a learner-owned bucket, and explicitly initialize the resulting S3 configuration only after authorization.

## Success criteria

- Offline negative control rejects a dynamic backend expression.
- Optional S3 backend contains only `encrypt` and `use_lockfile`; init-time example contains only placeholder bucket, key, and region.
- Producer state contains exactly `terraform_data.network_contract`.
- Consumer state contains the remote-state data source and `terraform_data.application_contract`.
- Consumer output exactly matches producer output, initial consumer plan has no destroy, and final plan is no-op.

## Reset instructions

`python tools/labctl.py reset 04` removes only Lab 04 runtime state, initialization metadata, plans, locks, and recorded results.

## Limited hints

- Backend configuration is evaluated before ordinary input variables.
- The local remote-state backend accepts a filesystem path in its `config` map.
