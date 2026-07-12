# Lab 10 - Root and Child Module Composition

## Scenario

An application stack has three child modules with stable contracts: naming produces a prefix, identity produces a profile name, and compute consumes both. Repair the root module so values cross module boundaries through explicit inputs and outputs.

## Skills tested

- Calling child modules from a root module
- Passing root inputs into modules
- Wiring one child module's output into another
- Exposing selected child outputs at the root
- Understanding reference-based dependency edges

## Difficulty and estimated time

- Difficulty: medium
- Estimated time: 20 minutes

## Execution mode

Local Terraform module composition with built-in resources only.

## Cloud credentials required

No. The modules model contracts with `terraform_data` and contact no service.

## Cost risk

None.

## Starting state

All three child modules exist and are protected. The root calls them, but one input and one root output bypass the intended module wiring.

## Files allowed to edit

- `starter/main.tf`

## Files not allowed to edit

- `starter/versions.tf`
- `starter/modules/`
- `tests/public.tftest.hcl`
- `scripts/verify_tests.py`
- `lab.yaml`

## Tasks

1. Pass the root application and environment values into the naming module.
2. Pass the naming result into the identity module.
3. Pass both the naming result and identity profile result into compute.
4. Expose the compute instance reference and identity profile name from the root.

## Constraints

- Do not duplicate child-module naming formulas in the root.
- Preserve all child-module interfaces and use references to establish dependencies.
- Do not add providers or cloud resources.
- Keep the root outputs keyed and named as provided.

## Expected initial failure

`python tools/labctl.py check 10` reports `EXPECTED_MODULE_COMPOSITION_INCOMPLETE` at the test stage because the starter bypasses required child-module outputs.

## Validation commands

```bash
python tools/labctl.py check 10
python tools/labctl.py status 10
```

## Success criteria

- Default inputs yield prefix `payments-dev`, profile `payments-dev-profile`, and compute reference `payments-dev::payments-dev-profile`.
- Alternate valid inputs flow through every child module without hardcoded default values.
- An unsupported environment is rejected by the protected naming module contract.
- Plan-configuration inspection proves the naming, identity, and compute module arguments use the required upstream references.
- The root output directly exposes the naming, identity, and compute module outputs instead of reconstructing equal strings.

## Reset instructions

```bash
python tools/labctl.py reset 10
```

## Limited hints

- Follow outputs from producer to consumer rather than recreating their strings.
- A reference used as a module argument also creates the dependency edge.
