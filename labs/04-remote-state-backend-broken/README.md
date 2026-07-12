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

Default validation bootstraps two distinct local producer states under `.lab-state/`. The S3 backend files are an offline, explicitly optional extension only.

## Cloud credentials required

None for the default workflow. An optional real S3 initialization requires separate authorization and learner-owned infrastructure.

## Cost risk

Default: none. The optional path writes at most one small Terraform state object and makes a small number of S3 requests. For a single short practice session the incremental charge is normally below US$0.01, but AWS, replication, KMS, data-transfer, and organization-specific charges are not capped by this lab; check current pricing before opting in.

## Starting state

`bootstrap/producer/` is the protected producer. `starter/consumer/` uses a manually copied network value. `starter/backend.tf.example` keeps shared backend safety settings but also contains one misplaced init-time setting.

## Files allowed to edit

- `starter/consumer/main.tf`
- `starter/backend.tf.example`

## Files not allowed to edit

- `bootstrap/`, `backend-dev.hcl.example`, `starter/consumer/versions.tf`, `scripts/`, `tests/`,
  and `lab.yaml`

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

### Optional real S3 initialization — explicit opt-in only

Prerequisites: a learner-owned S3 bucket, permission to read/write/delete only the chosen state key, a configured external AWS credential chain, and confirmation that no other operator uses `network/dev.tfstate`. The lab does not create the bucket, credentials, KMS keys, or locking infrastructure.

Create local, untracked working copies. On PowerShell:

```powershell
Copy-Item labs/04-remote-state-backend-broken/starter/backend.tf.example labs/04-remote-state-backend-broken/starter/consumer/backend.tf
Copy-Item labs/04-remote-state-backend-broken/backend-dev.hcl.example labs/04-remote-state-backend-broken/backend-dev.hcl
```

On a POSIX shell:

```bash
cp labs/04-remote-state-backend-broken/starter/backend.tf.example labs/04-remote-state-backend-broken/starter/consumer/backend.tf
cp labs/04-remote-state-backend-broken/backend-dev.hcl.example labs/04-remote-state-backend-broken/backend-dev.hcl
```

Replace only the bucket placeholder in `backend-dev.hcl`, then review the bucket, key, region, encryption, credential source, and access policy before explicitly running:

```text
terraform -chdir=labs/04-remote-state-backend-broken/starter/consumer init -reconfigure -backend-config=../../backend-dev.hcl
```

Initialization can upload or migrate an existing local state snapshot. Remote state can contain sensitive values, concurrent use can overwrite state, and deleting or changing the key can orphan it. Do not run this command against a shared or production state path.

## Success criteria

- Offline negative control rejects a dynamic backend expression.
- Optional S3 backend contains only `encrypt` and `use_lockfile`; init-time example contains only placeholder bucket, key, and region.
- Both distinct producer states contain exactly `terraform_data.network_contract`.
- Each consumer state contains the remote-state data source and `terraform_data.application_contract`.
- Each consumer output exactly follows its selected producer, including changed IDs and collection length; initial plans have no destroy and final plans are no-op.

## Reset instructions

For the default local workflow, `python tools/labctl.py reset 04` removes only Lab 04 runtime state, initialization metadata, plans, locks, and recorded results.

For an optional real S3 attempt, first preserve any state you still need. To migrate the selected state back to the local backend, remove the copied backend declaration and reinitialize before reset:

```powershell
Remove-Item labs/04-remote-state-backend-broken/starter/consumer/backend.tf
terraform -chdir=labs/04-remote-state-backend-broken/starter/consumer init -migrate-state
python tools/labctl.py reset 04
Remove-Item labs/04-remote-state-backend-broken/backend-dev.hcl
```

POSIX equivalents use `rm` for the two copied files. If the learner-owned bucket no longer needs the remote object, delete only the exact `network/dev.tfstate` object through approved AWS tooling after confirming it is not shared. `labctl reset` deliberately does not contact S3 or delete learner-owned backend configuration.

## Limited hints

- Backend configuration is evaluated before ordinary input variables.
- The local remote-state backend accepts a filesystem path in its `config` map.
