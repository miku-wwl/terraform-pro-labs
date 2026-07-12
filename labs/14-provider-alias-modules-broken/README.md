# Lab 14 - Passing Aliased Providers into Child Modules

## Scenario

A protected child module expects both a default AWS provider and a local `aws.secondary` alias. The root module currently maps both child provider names to its default configuration, so the child never receives the secondary region provider.

## Skills tested

- Root provider aliases
- Child-module `configuration_aliases`
- Module `providers` mapping
- Mock verification of provider identity across module boundaries

## Difficulty and estimated time

- Difficulty: medium
- Estimated time: 25 minutes

## Execution mode

`aws-mock`. AWS provider schema and module wiring are planned without credentials or API calls.

## Cloud credentials required

No.

## Cost risk

None.

## Starting state

The child module correctly declares and uses `aws.secondary`. The root mapping sends the default provider under both child provider names.

## Files allowed to edit

- `starter/main.tf`

## Files not allowed to edit

- `starter/versions.tf`
- `starter/modules/`
- `tests/`
- `scripts/`
- `lab.yaml`

## Tasks

1. Inspect the child's declared provider aliases and provider usage.
2. Correct the root module call so each child provider name receives the matching root configuration.
3. Preserve provider configuration in the root rather than adding provider blocks to the child.
4. Verify the mapping with two distinguishable mock provider results.

## Constraints

- Do not modify the protected child module.
- Do not remove `configuration_aliases` or the secondary data-source provider selection.
- Do not duplicate child modules to avoid provider mapping.
- Do not use credentials or real AWS data lookups.

## Expected initial failure

`python tools/labctl.py check 14` reports `EXPECTED_MODULE_PROVIDER_MAPPING_INCOMPLETE` because both child provider names resolve to the root default provider.

## Validation commands

```text
python tools/labctl.py check 14
python tools/labctl.py status 14
```

## Success criteria

- The child retains `configuration_aliases = [aws.secondary]`.
- The module call maps child `aws` to root `aws` and child `aws.secondary` to root `aws.secondary`.
- The protected source contract verifies that exact map and that the editable root output still
  delegates to the child instead of reproducing mock values.
- Mock outputs prove the child used two distinct provider configurations.
- No AWS credentials or API calls are used.

## Reset instructions

```text
python tools/labctl.py reset 14
```

## Limited hints

- Keys in a module `providers` map are child-local provider names; values are caller configurations.
- A provider alias is not inherited automatically by a child module.
