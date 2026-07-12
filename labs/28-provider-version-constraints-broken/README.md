# Lab 28 - Provider Version Constraint Semantics

## Scenario

A team has overly broad Terraform and AWS provider requirements. Define three intentional strategies—a bounded production range with one excluded release, a minimum-only module range, and an exact reproduction pin—and prove what each accepts.

## Skills tested

- `required_version` and `required_providers`
- Pessimistic `~>` bounds
- Explicit runtime `>=`/`<` bounds, exact `=`, and exclusion `!=` semantics
- Root versus reusable-module constraint intent
- Candidate-version evaluation beyond `terraform validate`

## Difficulty and estimated time

- Difficulty: medium
- Estimated time: 20 minutes

## Execution mode

Local initialization, validation, and deterministic semantic scoring.

## Cloud credentials required

No. Provider installation may use the registry or an existing cache, but no provider configuration or API call exists.

## Cost risk

None.

## Starting state

The runtime and provider ranges are too broad, while the exact example pins the wrong release. The previous unrelated environment-validation exercise has been removed.

## Files allowed to edit

- `starter/versions.tf`
- `starter/examples/minimum/versions.tf`
- `starter/examples/exact/versions.tf`

## Files not allowed to edit

- `fixtures/`
- `scripts/`
- `lab.yaml`

## Tasks

1. Bound Terraform CLI compatibility to the supported 1.x line beginning at 1.6.
2. Bound the root AWS provider to the 6.x line while excluding the known-bad 6.2.0 release.
3. Make the reusable minimum example accept AWS provider 6.0.0 and later.
4. Make the reproduction example accept exactly AWS provider 6.54.0.
5. Use and understand all five target operators: `~>`, `>=`, `<`, `=`, and `!=`.

## Constraints

- Keep `hashicorp/aws` as every provider source.
- Do not add resources, provider configurations, or environment validation.
- Do not edit the protected candidate matrix or scorer.
- Equivalent comma-separated constraints are accepted when their behavior and operator coverage match.

## Expected initial failure

`python tools/labctl.py check 28` reports `EXPECTED_CONSTRAINT_SEMANTICS_INCOMPLETE` because unsupported major versions remain allowed and the exact example targets the wrong release.

## Validation commands

```text
python tools/labctl.py check 28
python tools/labctl.py status 28
```

## Success criteria

- Terraform 1.6 through high future 1.x candidates is allowed, while early 1.x, adjacent pre-1.6 values, 2.0.x, and later majors are rejected.
- The bounded root strategy allows current and high future safe 6.x candidates, rejects 5.x/7.x, and excludes only 6.2.0.
- The minimum strategy allows 6.0.0 and much later majors.
- The exact strategy allows only 6.54.0.
- Each strategy uses its intended operators, and semantic scoring covers all candidate versions.

## Reset instructions

```text
python tools/labctl.py reset 28
```

## Limited hints

- A two-component pessimistic constraint has a different upper bound from a three-component one.
- Multiple comma-separated constraints form an intersection.
