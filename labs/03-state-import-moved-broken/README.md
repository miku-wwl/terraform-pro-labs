# Lab 03 — Import a Collection and Refactor into Module Instances

## Scenario

Two locally generated service identities exist outside the learner state. Adopt both at their legacy keyed root addresses, then refactor them into matching child-module instances without changing either identity.

## Skills tested

- Declarative import with keyed instances
- Exact state-address inspection
- `moved` blocks from root instances to module instances
- Plan JSON inspection and final no-op proof

## Difficulty and estimated time

- Difficulty: hard
- Estimated time: 40 minutes

## Execution mode

Isolated local state under `.lab-state/` using the logical HashiCorp `random` provider.

## Cloud credentials required

None. No cloud provider or remote service is used.

## Cost risk

None.

## Starting state

`python tools/labctl.py seed 03` applies `bootstrap/old-config`, verifies two old addresses, captures their import identifiers, and releases only those bootstrap bindings. The protected verifier then uses one fresh learner state across `starter/import-stage` and `starter/refactor-stage`.

## Files allowed to edit

- `starter/import-stage/main.tf`
- `starter/refactor-stage/main.tf`

## Files not allowed to edit

- `lab.yaml`, `bootstrap/`, `starter/modules/`, version files, `scripts/`, and `tests/`

## Tasks

1. Seed the lab and inspect both old keyed addresses.
2. Declaratively import every supplied identifier at its corresponding root address.
3. Refactor both objects into the supplied keyed module instances.
4. Preserve both identities and finish with a no-op plan.

## Constraints

- Do not hardcode generated identifiers or copy state files.
- Do not use imperative `terraform import` or `terraform state mv` as the solution.
- Do not change keys, byte lengths, module names, or resource names.

## Expected initial failure

The untouched starter passes formatting, initialization, and validation, then reports `EXPECTED_COLLECTION_REFACTOR_INCOMPLETE` because it proposes creating both identities instead of importing them.

## Validation commands

```text
python tools/labctl.py reset 03
python tools/labctl.py seed 03
python tools/labctl.py status 03
python tools/labctl.py check 03
python tools/labctl.py check 03 --mode solution
```

## Success criteria

- Import plan contains exactly the two protected old addresses and no create/delete action.
- Imported state and identifiers exactly match the fixture.
- Refactor plan records both exact old-to-module address mappings with no create/delete action.
- Final state contains only the two target module addresses, preserves both identifiers, and plans no changes.

## Reset instructions

`python tools/labctl.py reset 03` removes only Lab 03 `.lab-state/`, Terraform artifacts, and recorded results.

## Limited hints

- The import collection and resource collection should share stable keys.
- A move between keyed instances must identify an unambiguous source and destination.
