# Lab 29 - Sequential Terraform Test State

## Scenario

A release deployment replaces its local identity when the release changes. The existing test only plans the initial value and proves no state transition. Author a four-run Terraform Test flow that applies setup state, applies an upgrade, verifies steady state, and checks invalid input.

## Skills tested

- `run` blocks with `plan` and `apply`
- State shared sequentially within one test file
- Cross-run output references
- Replacement identity assertions
- `expect_failures` and useful assertion messages

## Difficulty and estimated time

- Difficulty: hard
- Estimated time: 30 minutes

## Execution mode

Provider-free Terraform Test with test-managed local state.

## Cloud credentials required

No.

## Cost risk

None.

## Starting state

The protected configuration is complete, but the editable test contains only one plan run. It has no setup apply, update, cross-run comparison, steady-state proof, or failure scenario.

## Files allowed to edit

- `starter/tests/release_flow.tftest.hcl`

## Files not allowed to edit

- `starter/main.tf`
- `starter/versions.tf`
- `scripts/`
- `lab.yaml`

## Tasks

1. Apply release `v1` as setup and assert its exact service/release output.
2. Apply release `v2`, assert the new output, and prove its deployment ID differs from setup.
3. Plan `v2` again and prove the ID and output remain the upgraded values.
4. Add a plan run that expects the release variable to reject `latest`.
5. Give each behavioral assertion a diagnostic message.

## Constraints

- Keep exactly four run scenarios in one test file.
- Include at least two apply runs and one plan run.
- Use a cross-run deployment ID reference rather than hardcoding generated IDs.
- Keep the scenarios in setup, upgrade, steady-state, then invalid-input order so shared test state has an unambiguous lifecycle.
- Do not modify the protected configuration or verifier.

## Expected initial failure

`python tools/labctl.py check 29` reports `EXPECTED_SEQUENTIAL_TEST_FLOW_INCOMPLETE` because the single plan neither establishes nor changes state.

## Validation commands

```text
terraform -chdir=labs/29-terraform-test-depth-broken/starter test
python tools/labctl.py check 29
python tools/labctl.py status 29
```

## Success criteria

- Exactly four runs pass.
- Setup applies `v1` and the upgrade applies `v2` in the same sequential test state.
- The upgrade receives a different deployment ID from setup.
- A later `v2` plan proves the upgraded state is stable.
- Invalid release syntax is attributed to `var.release_version`.
- No external provider, cloud state, or lifecycle answer is exposed in the starter test.

## Reset instructions

```text
python tools/labctl.py reset 29
```

## Limited hints

- Outputs from an earlier run can be referenced by the run label and output name.
- Apply runs make generated IDs known; a plan before setup does not.
