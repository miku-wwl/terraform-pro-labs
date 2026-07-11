# Lab 07 — Validation, Preconditions, Checks, and Tests

## Scenario

A local deployment descriptor accepts an environment, instance type, and naming prefix. The current condition skeletons permit unsafe or low-quality inputs. Complete the three different guard mechanisms and use Terraform Test to prove their distinct behavior.

## Skills tested

- Variable validation for invalid input
- Resource preconditions for contextual runtime rules
- Non-blocking assertions with `check` blocks
- Positive and expected-failure Terraform Test runs

## Difficulty and estimated time

- Difficulty: medium
- Estimated time: 20 minutes

## Execution mode

- Mode: local Terraform Test
- Backend: local test-managed state

## Cloud credentials required

No. This lab uses the built-in `terraform_data` resource and no external provider.

## Cost risk

None.

## Starting state

The configuration is syntactically valid, but the three condition expressions are permissive placeholders. The public test file is complete and protected. It verifies one normal case and one case for each guard mechanism.

## Files allowed to edit

- `starter/main.tf`

## Files not allowed to edit

- `starter/versions.tf`
- `tests/public.tftest.hcl`
- `scripts/verify_tests.py`
- `lab.yaml`

## Tasks

1. Make `environment` accept only `dev`, `stage`, or `prod`.
2. Prevent a production deployment from using `t3.micro`.
3. Make the naming-quality check warn when `name_prefix` is shorter than five characters.
4. Run `terraform test` and confirm expected failures are attributed to the correct variable, resource, and check block.

## Constraints

- Keep the existing variable, resource, output, and check addresses.
- Implement each rule in its designated validation mechanism.
- Do not change the protected tests to make the starter pass.
- A check block is advisory; do not turn its rule into a blocking validation or precondition.

## Expected initial failure

`python tools/labctl.py check 07` reaches the Terraform Test stage and reports `EXPECTED_GUARDS_INCOMPLETE`. The starter's permissive conditions do not produce the failures expected by the public test.

## Validation commands

From the repository root:

```text
terraform -chdir=labs/07-validation-checks-tests-broken/starter fmt -check
terraform -chdir=labs/07-validation-checks-tests-broken/starter init -backend=false
terraform -chdir=labs/07-validation-checks-tests-broken/starter validate
terraform -chdir=labs/07-validation-checks-tests-broken init -backend=false -test-directory=tests
terraform -chdir=labs/07-validation-checks-tests-broken test
python tools/labctl.py check 07
```

## Success criteria

- The normal development input produces the exact deployment summary expected by the tests.
- An unknown environment fails variable validation.
- Production with `t3.micro` fails the deployment resource precondition.
- A three-character prefix produces the expected non-blocking check diagnostic.
- `terraform test` passes all four runs without cloud credentials.

## Reset instructions

From the repository root:

```text
python tools/labctl.py reset 07
```

Reset removes only generated Terraform artifacts and recorded check results. It preserves `starter/main.tf` so learner work is not discarded.

## Limited hints

- Choose the guard type based on whether a rule concerns one input, a contextual resource operation, or advisory quality.
- `expect_failures` identifies the configuration object expected to report a diagnostic; it does not contain the implementation.
