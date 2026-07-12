# Lab 12 — Remote-State Consumer and Backend Separation

## Scenario

An application stack must read a selected network stack's outputs. Its own optional S3 backend
configuration is a separate initialization concern and must not be mixed with the producer lookup.

## Skills tested

- `terraform_remote_state` with a caller-selected local fixture
- producer/consumer state ownership
- static partial backend configuration and init-time inputs
- state-list and plan-action inspection

## Difficulty and estimated time

Medium, about 30 minutes.

## Execution mode

Local producer and consumer state fixtures. Optional S3 examples are inspected offline only.

## Cloud credentials required

None for the supported workflow.

## Cost risk

None for the supported local workflow. The optional init-only S3 extension can make a handful of
S3 API requests. Its expected incremental cost is below US$0.01 when stopped immediately after
initialization and when no state is migrated or written; actual billing, account policy, and
free-tier treatment remain the learner's responsibility and are not capped by this lab.

## Starting state

The protected verifier builds independent dev and prod producer states. The starter consumer uses
copied dev values and the optional backend example incorrectly owns an environment-specific key.

## Files allowed to edit

- `starter/main.tf`
- `starter/backend.tf.example`

## Files not allowed to edit

- `lab.yaml`, `bootstrap/`, `scripts/`, and `tests/`
- `starter/versions.tf`
- `backend-dev.hcl.example` and `backend-prod.hcl.example`

## Tasks

1. Read the producer output through `terraform_remote_state` using `var.producer_state_path`.
2. Feed the consumed network into the consumer-owned `terraform_data` resource and output.
3. Keep only shared static safety settings in the backend block; leave bucket, key, and region in
   the environment-specific init files.

## Constraints

Do not copy producer values, initialize S3, add credentials, or make the consumer manage producer
resources. Preserve the existing output names and consumer resource address.

## Expected initial failure

`python tools/labctl.py check 12` reaches the protected behavior gate and reports
`EXPECTED_REMOTE_STATE_CONSUMER_INCOMPLETE` because the consumer ignores the producer path and the
backend boundary is mixed.

## Validation commands

```text
python tools/labctl.py reset 12
python tools/labctl.py check 12
```

The optional real-backend extension would use a learner-owned copy of an `.example` file, but it is
not part of validation and requires separate authorization.

### Optional real S3 initialization (excluded from validation)

Use this extension only with explicit authorization and all of the following prerequisites:

- short-lived AWS credentials with access only to a learner-owned test bucket;
- an existing encrypted/versioned test bucket in `us-east-1`;
- a new, unused state keyâ€”never a production or shared state key;
- no local state to migrate and no intent to run `plan`, `apply`, or any state-writing command.

From the repository root, make untracked working copies, replace the bucket placeholder, and then
run exactly one of the environment-specific init commands:

```text
# PowerShell
Copy-Item labs/12-remote-state-backend-rules-broken/starter/backend.tf.example labs/12-remote-state-backend-rules-broken/starter/backend.tf
Copy-Item labs/12-remote-state-backend-rules-broken/backend-dev.hcl.example labs/12-remote-state-backend-rules-broken/backend-dev.hcl
# Edit backend-dev.hcl and replace only REPLACE_WITH_LAB12_CONSUMER_STATE_BUCKET.
terraform -chdir=labs/12-remote-state-backend-rules-broken/starter init -reconfigure -backend-config=../backend-dev.hcl
```

Equivalent POSIX commands are:

```text
cp labs/12-remote-state-backend-rules-broken/starter/backend.tf.example labs/12-remote-state-backend-rules-broken/starter/backend.tf
cp labs/12-remote-state-backend-rules-broken/backend-dev.hcl.example labs/12-remote-state-backend-rules-broken/backend-dev.hcl
# Edit backend-dev.hcl and replace only REPLACE_WITH_LAB12_CONSUMER_STATE_BUCKET.
terraform -chdir=labs/12-remote-state-backend-rules-broken/starter init -reconfigure -backend-config=../backend-dev.hcl
```

For prod, copy `backend-prod.hcl.example` to `backend-prod.hcl` and pass that file instead. Stop
after successful initialization. The default lab never executes these commands.

Cleanup for this documented init-only path removes the local working copies and backend metadata:

```text
# PowerShell, from the repository root
Remove-Item labs/12-remote-state-backend-rules-broken/starter/backend.tf
Remove-Item labs/12-remote-state-backend-rules-broken/backend-dev.hcl -ErrorAction SilentlyContinue
Remove-Item labs/12-remote-state-backend-rules-broken/backend-prod.hcl -ErrorAction SilentlyContinue
python tools/labctl.py reset 12
```

Equivalent POSIX cleanup is:

```text
rm -f labs/12-remote-state-backend-rules-broken/starter/backend.tf
rm -f labs/12-remote-state-backend-rules-broken/backend-dev.hcl labs/12-remote-state-backend-rules-broken/backend-prod.hcl
python tools/labctl.py reset 12
```

An init-only run should not create a remote state object. If any state-writing command was run,
stop and use the bucket owner's version-aware cleanup procedure; deleting only a current S3 object
or delete marker may leave prior versions. Principal risks are selecting an existing key, exposing
state contents to an overly broad principal, retaining versioned objects, and incurring account-
specific request/storage charges.

## Success criteria

- dev and prod each resolve the exact selected producer output;
- consumer state contains only the remote-state data address and consumer contract resource;
- the initial consumer plan creates only the consumer-owned resource;
- final consumer plans are no-op;
- backend expressions contain only shared static safety settings.

## Reset instructions

```text
python tools/labctl.py reset 12
```

Reset removes only Lab 12 runtime state, initialization metadata, plans, locks, and result records.

## Limited hints

The local backend's `path` belongs in the remote-state data source configuration. S3 backend
bucket, key, and region are initialization inputs, not ordinary Terraform expression values.
