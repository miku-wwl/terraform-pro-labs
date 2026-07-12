# Lab 24 - Sensitive Inputs, Redaction, and Safe Outputs

## Scenario

A local database configuration correctly propagates a runtime password as sensitive data, but one debug output explicitly declassifies and exposes it. Preserve useful non-secret diagnostics without publishing credential material.

## Skills tested

- Sensitive input and output metadata
- Automatic sensitivity propagation and CLI redaction
- Safe, deliberate declassification of derived non-secret metadata
- Avoiding secret-bearing debug outputs and defaults

## Difficulty and estimated time

- Difficulty: medium
- Estimated time: 20 minutes

## Execution mode

Provider-free Terraform planning and apply in a protected temporary directory using only the built-in provider.

## Cloud credentials required

No.

## Cost risk

None.

## Starting state

The password has no committed default and the intended secret-bearing outputs are sensitive. One extra debug output removes protection from the raw password.

## Files allowed to edit

- `starter/main.tf`

## Files not allowed to edit

- `starter/versions.tf`
- `scripts/`
- `lab.yaml`

## Tasks

1. Remove the output path that publishes raw credential material.
2. Preserve sensitive metadata on the connection URI and complete database configuration.
3. Preserve the non-sensitive credential metadata output without including the password.
4. Keep the password runtime-supplied; do not add a default or fixture value.

## Constraints

- Do not place a password or secret-like value in source, fixtures, README examples, or logs.
- Do not declassify the raw password or connection URI.
- Do not make every output sensitive merely to bypass the safe-diagnostics requirement.
- Do not edit the protected verifier.

## Expected initial failure

`python tools/labctl.py check 24` reports `EXPECTED_SENSITIVE_BOUNDARY_INCOMPLETE` because the starter includes an unsafe extra output and exposes the runtime probe in normal plan rendering.

## Validation commands

```text
python tools/labctl.py check 24
python tools/labctl.py status 24
```

## Success criteria

- `db_password` is a required sensitive variable.
- Secret-bearing outputs retain their exact runtime-derived values and sensitive metadata.
- Normal CLI plan and apply rendering redact the runtime probe.
- Root outputs contain no raw-password debug channel.
- `credential_metadata` remains non-sensitive and contains only username and configured-status data.
- No real secret is stored or printed by the default workflow.

## Reset instructions

```text
python tools/labctl.py reset 24
```

## Limited hints

- Sensitivity is metadata that propagates through expressions.
- Declassify only a derived value that cannot reconstruct the secret.
