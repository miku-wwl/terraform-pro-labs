# Lab 32 - Dependency-Driven Replacement with `replace_triggered_by`

## Scenario

A service record does not directly store the release version, but operational policy requires a new service instance whenever its upstream release marker changes. Ordinary service-name edits should remain in-place updates.

## Skills tested

- Lifecycle dependency replacement semantics
- Difference between dependency ordering and replacement triggering
- Plan JSON actions and `action_reason`
- Scoping replacement to the intended upstream change

## Difficulty and estimated time

- Difficulty: medium
- Estimated time: 20 minutes

## Execution mode

Provider-free Terraform with state and plans isolated in a temporary verifier directory.

## Cloud credentials required

No.

## Cost risk

None.

## Starting state

The release marker and service record are separate resources. A marker update currently leaves the service unchanged because no replacement relationship is configured.

## Files allowed to edit

- `starter/main.tf`

## Files not allowed to edit

- `starter/versions.tf`
- `scripts/`
- `lab.yaml`

## Tasks

1. Configure the service lifecycle so a release-marker change replaces the service.
2. Keep the marker itself as an in-place update.
3. Keep direct service-name changes as in-place service updates.
4. Verify the dependency-triggered replacement through the protected stateful plan check.

## Constraints

- Do not copy the release version into the service input merely to manufacture argument drift.
- Do not force replacement for every service input change.
- Preserve both resource addresses and the marker's normal update behavior.
- Do not edit the protected verifier.

## Expected initial failure

`python tools/labctl.py check 32` reports `EXPECTED_REPLACE_TRIGGER_INCOMPLETE` because changing the release marker does not replace the service.

## Validation commands

```text
python tools/labctl.py check 32
python tools/labctl.py status 32
```

## Success criteria

- Release-marker change actions are exactly an update.
- The same plan replaces the service specifically with `replace_by_triggers` as its reason.
- A service-name-only change remains an update, not a replacement.
- The service input contains only its owned name; release data remains owned by the marker.
- Verification uses temporary local state and no cloud operation.

## Reset instructions

```text
python tools/labctl.py reset 32
```

## Limited hints

- An ordinary dependency controls ordering but does not automatically force replacement.
- Plan JSON identifies why Terraform selected a replacement action.
