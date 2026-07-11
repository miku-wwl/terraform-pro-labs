# Lab 06 - Provider Requirements, Aliases, and Authentication Boundary

## Scenario

A root configuration reads two AWS regions through default and aliased provider configurations. The secondary read is accidentally routed through the default provider, and the default configuration pins a workstation-specific profile that breaks portable authentication.

## Skills tested

- `required_providers` source and version declarations
- Root provider aliases and per-object provider selection
- Standard AWS credential-chain troubleshooting
- Credential-free Terraform mock-provider testing

## Difficulty and estimated time

- Difficulty: medium
- Estimated time: 25 minutes

## Execution mode

`aws-mock`. Terraform installs the AWS provider schema but performs no authentication or AWS API call.

## Cloud credentials required

No.

## Cost risk

None; plans use mock providers only.

## Starting state

The protected provider requirement is valid. The secondary data source uses the wrong provider configuration, while the default provider pins a nonexistent local profile.

## Files allowed to edit

- `starter/main.tf`

## Files not allowed to edit

- `starter/versions.tf`
- `tests/`
- `scripts/`
- `lab.yaml`

## Tasks

1. Confirm the required provider source and compatible major-version constraint.
2. Route each region data source through its intended provider configuration.
3. Remove workstation-specific authentication selection so normal AWS credential-chain resolution remains portable.
4. Verify both provider paths through mock results without using credentials.

## Constraints

- Do not add access keys, secret keys, tokens, account identifiers, or credential fixtures.
- Do not add credential-validation skip flags as a substitute for correct authentication.
- Preserve the two configured regions and the `aws.secondary` alias.
- Do not edit protected tests or provider requirements.

## Expected initial failure

`python tools/labctl.py check 06` reports `EXPECTED_PROVIDER_ALIAS_AUTH_INCOMPLETE` because the secondary read uses the default provider and authentication is pinned to a local profile.

## Validation commands

```text
python tools/labctl.py check 06
python tools/labctl.py status 06
```

## Success criteria

- The AWS provider requirement retains the `hashicorp/aws` source and `~> 6.0` constraint.
- Mock outputs prove primary and secondary reads use different intended provider configurations.
- No profile or credential value is pinned in Terraform configuration.
- No real AWS authentication or API request occurs.

## Reset instructions

```text
python tools/labctl.py reset 06
```

## Limited hints

- Provider selection is explicit on a data source or resource when it should not use the default configuration.
- A portable root module normally lets credentials come from the standard external chain.
