# Terraform Professional Labs Migration Report

## Phase 2 — Starter framework and pilot labs

Migration date: 2026-07-10

Working branch: `refactor/starter-v1`

Scope: repository-level starter tooling, Lab 01, Lab 07, and their documentation only.

### Phase 1 prerequisites

The three required Phase 1 artifacts were present and inspected before implementation:

- `docs/audit-report.md`
- `docs/lab-matrix.csv`
- `docs/lab-standard.md`

`docs/migration-report.md` did not exist at the start of Phase 2 and was created here. The Phase 1 audit findings for Labs 01 and 07 matched the legacy source. The audit report remains an unchanged baseline snapshot; the matrix now records the migrated current state.

### Upstream protection

Before editing lab files, commit `e5370c36f6f701bcdb3c3f4b065d2bf3699ec888` was preserved locally as:

- tag `upstream-snapshot`
- branch `legacy-solution-candidate`

Work then moved to `refactor/starter-v1`. No branch or tag was pushed, no history was rewritten, and no force-push was performed.

### Minimal repository framework

`tools/labctl.py` now provides the Phase 2 subset of the repository tooling contract:

- JSON-compatible YAML manifest loading and schema validation with no third-party Python dependency;
- `list`, including migrated and legacy lab visibility;
- `status`, including manifest validity, cloud/cost flags, generated artifacts, and last recorded starter/solution results;
- `check`, with ordered format/init/validate/test commands, expected starter-failure classification, optional `--mode solution`, explicit exit codes, and local JSON result recording under ignored `.labctl/results/`;
- `reset`, limited to lab-owned Terraform artifacts and that lab's recorded results.

All subprocesses use argument lists rather than shell command strings. Paths and deletion behavior use Python standard-library APIs and are portable across Windows and Linux.

### Lab 01 — Terraform CLI and `prevent_destroy`

The AWS S3 placeholder was replaced by a local `terraform_data.deployment_record`. The starter is valid but intentionally lacks lifecycle protection. The protected verifier copies the configuration to a temporary directory, initializes isolated local state, applies the built-in resource, and requests a destroy plan. A permitted destroy produces `EXPECTED_GUARD_MISSING`; the canonical solution passes only when Terraform emits a `prevent_destroy` diagnostic.

No AWS provider was installed or configured, no credentials were read, and no cloud operation was executed.

Starter gate:

```text
python tools/labctl.py check 01
```

Observed result: PASS as an expected failure. Format, init, and validate passed; the behavioral test returned `EXPECTED_GUARD_MISSING: destroy plan was allowed.`

Canonical solution gate, run transiently without retaining the answer in the starter branch:

```text
python tools/labctl.py check 01 --mode solution
python tools/labctl.py reset 01
python tools/labctl.py check 01 --mode solution
```

Observed result: both solution runs passed. On each run, the verifier reported that the destroy plan was blocked by `prevent_destroy`. The intermediate reset completed successfully.

### Lab 07 — Validation, Preconditions, Checks, and Tests

The external AWS provider declaration and all legacy solution expressions were removed. The starter retains only valid, deliberately over-permissive condition skeletons. TODO comments describe required behavior without disclosing complete expressions.

The protected Terraform Test suite contains four runs:

1. normal development input and exact output shape;
2. unsupported environment attributed to `var.environment`;
3. unsafe production size attributed to `terraform_data.deployment`;
4. short-prefix advisory attributed to `check.name_prefix_quality`.

Starter gate:

```text
python tools/labctl.py check 07
```

Observed result: PASS as an expected failure. Format, init, and validate passed. The normal run passed, the validation run reported `Missing expected failure`, and the wrapper emitted `EXPECTED_GUARDS_INCOMPLETE`. Terraform skipped later runs after the first failure, as expected for the starter gate.

Canonical solution gate, run transiently without retaining the answer in the starter branch:

```text
python tools/labctl.py check 07 --mode solution
python tools/labctl.py reset 07
python tools/labctl.py check 07 --mode solution
```

Observed result: both solution runs passed with `4 passed, 0 failed`. The intermediate reset removed the lab-root `.terraform` test-module cache and recorded results before the second clean run.

### Reset and repeatability

The canonical solution for each pilot passed, was reset, and passed again. Canonical expressions were then removed and the learner-facing starter conditions restored. Final required status/check/reset commands are recorded below after the final starter verification.

### Items not verified

- Linux execution: **NOT VERIFIED**. The implementation uses portable Python and subprocess argument lists, but this Phase 2 run occurred on Windows only and no Linux runner was available in the workspace.
- Terraform versions other than v1.14.0: **NOT VERIFIED**. Manifests allow Terraform `>= 1.6, < 2.0`, but the executed environment contained Terraform v1.14.0 only.

### Remaining risks

- Only Labs 01 and 07 have manifests and the new directory contract. The other 30 labs remain legacy inputs for later explicitly scoped phases.
- `lab.yaml` files use JSON syntax, which is valid YAML 1.2 and permits a dependency-free parser, but future schema expansion may justify adopting a YAML parser with an explicitly managed dependency.
- The canonical solutions were intentionally tested transiently and are not stored on the starter branch. A later solution-branch phase must reconstruct or preserve them without leaking answers into learner-facing files.

### Final required Phase 2 commands

The required commands were executed in the requested order against the restored starter files:

```text
python tools/labctl.py status 01
python tools/labctl.py check 01
python tools/labctl.py reset 01
python tools/labctl.py status 07
python tools/labctl.py check 07
python tools/labctl.py reset 07
```

All six commands exited successfully. Both manifests were valid and both labs reported `requires_cloud_credentials: false` and `creates_billable_resources: false`. Lab 01 reproduced `EXPECTED_GUARD_MISSING`; Lab 07 reproduced `EXPECTED_GUARDS_INCOMPLETE`; each expected failure was classified as a passing starter gate. Both resets removed only lab-owned generated artifacts and result records. Lab 07 status correctly reported the existing test-module cache before its final reset.

## Phase 3 — Lab 11 import, moved blocks, and refactor

Migration date: 2026-07-10

Working branch: `main`

Scope: Lab 11, the minimum `labctl seed` and state-artifact support required by Lab 11, and corresponding documentation only. Labs 03, 19, and 26 were not modified.

### Original defects

Lab 11 was an exact copy of the legacy Lab 03 S3 placeholder. It assumed an existing bucket and AWS credentials but supplied no import block, module, moved block, bootstrap configuration, initial state, isolated state directory, behavioral test, reset, or no-op proof.

### State-lab design

The AWS configuration was replaced by HashiCorp `random_id`, a local logical provider with a real import implementation and no remote service or billable resource. The workflow is deliberately split so import and moved semantics are not attempted in the same configuration transition:

1. `bootstrap/old-config` creates `random_id.legacy_record` in an isolated copied work directory.
2. The seed verifier confirms that exact address, captures its Base64 URL import identifier, and removes the bootstrap state binding to hand the identity to the learner workflow.
3. `starter/import-stage` must declaratively import the identity at `random_id.legacy_record`.
4. `starter/refactor-stage` uses the supplied child module and must preserve identity at `module.record.random_id.this`.

All generated fixture data, Terraform state, plans, provider metadata, and copied configurations live under the ignored Lab 11 `.lab-state/` directory. No generated identifier is committed.

### Repository tooling enhancement

`tools/labctl.py` now validates state-refactor manifest metadata and provides:

```text
python tools/labctl.py seed <lab-id>
```

The manifest supplies a portable argument list for the lab-specific seed script. State-refactor manifests also declare safe lab-relative generated paths. Status reports those paths, and reset removes them plus nested lab-owned `.terraform/`, state, plan, and lock artifacts. Existing Lab 01 and Lab 07 manifests remain valid.

### Starter gate

Executed from a clean reset and fresh seed:

```text
python tools/labctl.py reset 11
python tools/labctl.py seed 11
python tools/labctl.py status 11
python tools/labctl.py check 11
```

Observed result: PASS as an expected behavioral failure. Formatting passed. The seed established and reported `random_id.legacy_record`. The verifier then reported `EXPECTED_STATE_REFACTOR_INCOMPLETE` because the starter import stage planned a create instead of one import with zero create/delete actions.

### Canonical solution gate

Canonical import and moved blocks were added transiently, tested, and removed so the learner-facing branch retains only the genuine starter. The first complete successful run reported:

```text
Import plan summary: 1 to import, 0 to add, 0 to change, 0 to destroy.
Imported state address: random_id.legacy_record
Refactor plan summary: 0 to add, 0 to change, 0 to destroy.
Final state address: module.record.random_id.this
Final plan summary: 0 to add, 0 to change, 0 to destroy (no-op).
```

The verifier also compared the imported and final identifier values, inspected the plan's exact `previous_address` mapping, applied the address-only move, and required a final detailed-exitcode plan to return no changes.

### Reset and second run

After the first canonical pass, the following sequence was executed:

```text
python tools/labctl.py reset 11
PowerShell assertion that labs/11-import-moved-refactor-broken/.lab-state no longer existed
python tools/labctl.py seed 11
python tools/labctl.py check 11 --mode solution
```

Reset removed the learner and bootstrap `.terraform/` directories, all state/plan/fixture contents through `.lab-state/`, and the recorded solution result. The explicit path assertion passed. The second seed and canonical solution run reproduced the same old/imported/final addresses and the same import, refactor, and final no-op summaries shown above.

### Cloud safety

No AWS provider was configured, no AWS credentials were requested or read, and no cloud API or real-cloud apply was executed. Terraform apply was limited to the local logical `random_id` fixture inside Lab 11's isolated state.

### Items not verified

- Linux execution: **NOT VERIFIED**. The Python tooling uses portable filesystem and subprocess APIs, but this phase ran on Windows only and no Linux runner was available.
- Terraform versions other than v1.14.0: **NOT VERIFIED**. The manifest permits Terraform `>= 1.6, < 2.0`, but only v1.14.0 was executed.
- Remote-service import behavior: **NOT VERIFIED by design**. The default lab intentionally uses a logical provider so it can verify Terraform import/state semantics without credentials, external drift, or cloud cost.

### Remaining risks

- The logical `random_id` fixture models an importable identity but does not exercise a remote provider read API. That tradeoff is documented and keeps the default gate deterministic and cost-free.
- The canonical blocks were verified transiently and are not stored on `main`. They must remain isolated on a future solution/grader branch.
- Lab 03 remains a legacy duplicate and is intentionally deferred to its separately scoped phase.
