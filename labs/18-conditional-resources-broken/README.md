# Lab 18 - Conditional count with one() and try()

## Scenario

A deployment marker is optional. Its current outputs directly index the zero-or-one resource, so the disabled path crashes during planning. Make both enabled and disabled paths safe while demonstrating the two requested collection-reading patterns.

## Skills tested

- Conditional `count` with zero or one instance
- Reading a zero-or-one splat with `one()`
- Using `try()` around an expression that can fail
- Designing nullable outputs for absent resources

## Difficulty and estimated time

- Difficulty: medium
- Estimated time: 15 minutes

## Execution mode

Local Terraform authoring with `terraform_data`.

## Cloud credentials required

No.

## Cost risk

None.

## Starting state

The resource already uses conditional count. Both outputs use unsafe direct indexing and the default disabled plan fails.

## Files allowed to edit

- `starter/main.tf`

## Files not allowed to edit

- `starter/versions.tf`
- `tests/public.tftest.hcl`
- `scripts/verify_tests.py`
- `lab.yaml`

## Tasks

1. Keep the resource count at zero when disabled and one when enabled.
2. Make `selected_name` safely read the zero-or-one collection with `one()`.
3. Make `selected_owner` safely handle a potentially invalid index with `try()`.
4. Preserve `null` as the absence value and exact configured values when enabled.

## Constraints

- Use both `one()` and `try()` in the editable configuration.
- Do not use sentinel strings for absence.
- Do not add providers or external dependencies.
- Reject an empty marker name.

## Expected initial failure

`python tools/labctl.py check 18` reports `EXPECTED_CONDITIONAL_READ_INCOMPLETE` at the test stage. The unmodified default plan fails because count is zero and the outputs index element zero.

## Validation commands

```bash
python tools/labctl.py check 18
python tools/labctl.py status 18
```

## Success criteria

- Disabled input plans successfully with a resource count of zero and both optional outputs set to `null`.
- Enabled input plans one record and returns the exact configured name and owner.
- An empty name is rejected.
- The source uses both requested safe-read functions.

## Reset instructions

```bash
python tools/labctl.py reset 18
```

## Limited hints

- A splat converts zero-or-one instances into a zero-or-one tuple.
- One output can read that tuple; the other can recover from a failing expression.
