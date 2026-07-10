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

## Phase 4 — Conceptual and partial-backend pilots

Migration date: 2026-07-10

Working branch: `main`

Scope: Lab 25, Lab 31, the minimum conceptual/backend manifest and reset support required by those labs, and corresponding documentation only. No other conceptual, backend, remote-state, workspace, or state lab was modified.

### Original defects

Lab 25 encoded HCP Terraform questions as `locals` and outputs, duplicated Terraform version constraints, forced an irrelevant AWS provider download, supplied no response artifact or rubric, and documented a meaningless Terraform plan workflow for a conceptual exercise.

Lab 31 referenced a nonexistent `backend.hcl`, put empty environment fields in an S3 backend block, declared an unnecessary AWS provider and ordinary environment variable beside the backend without a valid boundary, provided no environment examples, had no offline check, and could not demonstrate backend metadata reset.

### Repository tooling enhancement

`tools/labctl.py` now validates type-specific metadata for:

- conceptual labs, including existing rubric and answer artifacts and the absence of Terraform files in the conceptual starter;
- backend labs, including safe `.example` files, declared init-metadata paths, and explicit real-init opt-in metadata.

Backend init-metadata paths are included in status and reset discovery. Existing Lab 01, Lab 07, and Lab 11 manifests remained valid after the schema extension.

### Lab 25 — HCP Terraform operations decisions

The Terraform configuration and AWS dependency were removed. The lab now uses:

- `starter/SCENARIO.md` for a production operating-model case;
- `starter/QUESTIONS.md` for eight structured decisions;
- `starter/student-answer.md` for choices and free-form rationales;
- `rubric.yaml` for public dimensions, weights, rationale requirements, and pass threshold;
- `scripts/score_answer.py` for deterministic local scoring.

The questions cover VCS-driven runs, an API-driven automation boundary, speculative plans, producer-to-consumer run triggers, production policy enforcement, cost-estimation limitations, team permissions, and auto-apply/production approvals. Correct decisions contribute 80 points; non-placeholder rationales and response completeness contribute 20. The 96-point threshold requires all key decisions to be correct. Rationales are not matched against canonical prose.

Canonical option choices are not stored in learner-facing Markdown or rubric data. The scorer stores only protected comparison digests. A canonical response was inserted transiently for verification and then the `undecided` starter was restored.

Starter gate:

```text
python tools/labctl.py reset 25
python tools/labctl.py check 25
```

Observed result: PASS as an expected scoring failure. The initial answer reported `EXPECTED_CONCEPTUAL_RESPONSE_INCOMPLETE` for the eight undecided choices and placeholder rationales.

Canonical solution gate:

```text
python tools/labctl.py check 25 --mode solution
python tools/labctl.py reset 25
python tools/labctl.py check 25 --mode solution
```

Observed result: both canonical runs scored 100/100 and passed. Reset removed recorded results while deliberately preserving the response artifact, as documented for conceptual work.

### Lab 31 — partial S3 backend configuration

The lab now has one static partial `backend "s3"` block, an ordinary `environment` input that is evaluated only as root-module configuration, and three environment-specific init examples:

```text
backend-dev.hcl.example
backend-test.hcl.example
backend-prod.hcl.example
```

The examples contain deliberately non-real bucket placeholders, isolated keys, literal regions, and no credentials. Static shared encryption and S3 lockfile settings remain in the backend block. Learner-created non-example backend files are ignored locally and are not deleted by reset.

The default manifest runs format, `terraform init -backend=false`, validate, and `scripts/verify_backend.py`. The checker does not initialize S3. Its protected negative controls prove that it detects both a backend expression and hardcoded bucket/key/region patterns before it inspects the learner configuration.

Starter gate:

```text
python tools/labctl.py reset 31
python tools/labctl.py check 31
```

Observed result: PASS as an expected behavioral failure. Format, offline init, and validate passed. The negative controls and all three example checks passed. The learner configuration then reported `EXPECTED_PARTIAL_BACKEND_INCOMPLETE` because `key` was still an init-time field hardcoded in the static block.

Canonical solution gate:

```text
python tools/labctl.py check 31 --mode solution
python tools/labctl.py reset 31
python tools/labctl.py check 31 --mode solution
```

Observed result: both solution runs passed format, offline init, validate, checker negative controls, example validation, and the actual static backend boundary check. No S3 connection or credential lookup occurred.

### Reset and repeatability

Lab 25's reset behavior was exercised between two 100/100 solution runs. It removed local result records and preserved the answer file.

Because a provider-free `terraform init -backend=false` does not create `.terraform` in this configuration, Lab 31 reset coverage used an ignored, synthetic `.terraform/terraform.tfstate` sentinel shaped as backend initialization metadata. `labctl status 31` reported both the metadata file and directory; `labctl reset 31` removed both, and an explicit path assertion confirmed the directory no longer existed. No real backend state was created or deleted.

The canonical changes were removed after repeatability checks, and both learner-facing starters were restored.

### Cloud safety

No AWS or HCP Terraform credentials were requested or read. No cloud provider was installed for Lab 25. Lab 31 used only `terraform init -backend=false`; no real S3 backend initialization, plan, apply, data lookup, or cloud API call was executed.

### Items not verified

- Linux execution: **NOT VERIFIED**. All Python code uses portable standard-library filesystem and subprocess APIs, but this phase ran on Windows and no Linux runner was available.
- Terraform versions other than v1.14.0: **NOT VERIFIED**. Lab 31 requires `>= 1.10, < 2.0` for the S3 `use_lockfile` setting, but only Terraform v1.14.0 was executed.
- Real HCP Terraform organization behavior: **NOT VERIFIED by design**. Lab 25 is a local conceptual scenario based on current HashiCorp documentation and does not create runs or require an organization.
- Real S3 backend initialization: **NOT VERIFIED by design**. It is an explicitly optional learner path requiring separate authorization, authentication, and a learner-owned bucket; default validation never connects to S3.

### Remaining risks

- A public offline conceptual scorer cannot make its expected choices cryptographically secret. Comparison digests prevent an obvious plaintext answer key but can be inspected or brute-forced; blind practice still relies on respecting protected paths.
- Rationale scoring verifies non-placeholder completeness rather than semantic equivalence. Correct structured decisions carry the decisive score, while human review remains valuable for explanation quality.
- The static backend parser is intentionally scoped to this lab's one-line assignments and approved static fields. It is protected by explicit dynamic-expression and hardcoding negative controls but is not a general-purpose HCL parser.
- HCP Terraform feature availability can vary by product edition and can change over time; the scenario was checked against HashiCorp's current official run-mode, run-trigger, workspace-setting, and permission documentation on the migration date.

## Phase 5 — Pilot Quality Gate

Migration date: 2026-07-10

Working branch: `main`

Scope: quality review and repair of Labs 01, 07, 11, 25, and 31; shared `labctl`
behavior; the root usage note; and migration documentation. No new lab was added or migrated, and
the other 27 lab directories were not modified.

### Gate defects found and fixed

The five independent starter gates already failed at their declared stages with their declared
markers. The required repository aggregate command did not exist: `python tools/labctl.py check
--all` exited from argument parsing because `check` required a positional lab ID.

`tools/labctl.py` now:

- accepts exactly one lab ID or `--all`;
- discovers only labs with a valid manifest, so the current aggregate contains exactly the five
  migrated pilots and skips all legacy inputs;
- recreates only a state-refactor lab's declared generated state before its aggregate check, then
  runs the manifest seed command;
- reports a per-lab and aggregate result;
- rejects duplicate manifest paths, directory-valued editable paths, and any overlap between
  editable and protected paths.

Lab 11's manifest now protects its whole `scripts/` directory, matching its README rather than
enumerating only the two current scripts.

Lab 25's scorer now validates option IDs against `QUESTIONS.md`, verifies that rubric weights total
the published maximum and that the threshold is valid, and reports each decision's choice and
rationale status. This preserves answer isolation while making an incomplete or below-threshold
result actionable. The scenario decisions were rechecked against current HashiCorp documentation
for [run modes](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/run/modes-and-options),
[run triggers](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/settings/run-triggers),
[workspace permissions](https://developer.hashicorp.com/terraform/cloud-docs/users-teams-organizations/permissions/workspace),
and [workspace settings](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/settings).

### Independent pilot results

| Lab | Starter gate | Canonical solution run 1 | Reset proof | Canonical solution run 2 |
| --- | --- | --- | --- | --- |
| 01 | PASS — `EXPECTED_GUARD_MISSING` at test | PASS — destroy plan blocked by `prevent_destroy` | PASS — lab-owned artifacts/results removed | PASS — same lifecycle diagnostic reproduced |
| 07 | PASS — `EXPECTED_GUARDS_INCOMPLETE` at test | PASS — 4 Terraform Test runs passed | PASS — root/starter test caches and results removed | PASS — 4 passed, 0 failed again |
| 11 | PASS — `EXPECTED_STATE_REFACTOR_INCOMPLETE` at state test | PASS — 1 import, 0 add/destroy; exact move; final no-op | PASS — `.lab-state/` absent after reset, then reseeded | PASS — addresses, identity, zero create/delete, and no-op reproduced |
| 25 | PASS — `EXPECTED_CONCEPTUAL_RESPONSE_INCOMPLETE` at scoring | PASS — 100/100 with every choice and rationale reported | PASS — results removed and response artifact preserved | PASS — 100/100 again |
| 31 | PASS — `EXPECTED_PARTIAL_BACKEND_INCOMPLETE` at static test | PASS — offline init, validate, negative controls, examples, and backend boundary | PASS — synthetic `.terraform/terraform.tfstate` metadata and directory removed | PASS — all offline checks passed again |

Canonical changes were applied only transiently. The six edited learner files were restored and
their SHA-256 hashes matched the pre-solution values before final starter regression.

### Aggregate, leakage, and consistency gates

`python tools/labctl.py check --all` ran exactly Labs 01, 07, 11, 25, and 31 and reported all five
starter gates passed as expected failures. Lab 11 was reset and freshly seeded by the aggregate
workflow.

The Phase 5 static consistency scan confirmed:

- all five READMEs contain every Starter Standard section, expected marker, validation command,
  and manifest-declared editable/protected path;
- manifests declare no cloud credentials or billable resources and have no editable/protected
  overlap;
- no pilot test relies on output non-null/existence checks;
- no answer-bearing filename, canonical `prevent_destroy`, import block, moved block, or completed
  conceptual answer remains in a starter;
- TODO comments describe behavior without containing a complete implementation expression.

### Reset and cloud safety

All five pilots were reset between canonical runs and passed on the second run. Lab 31 used an
ignored synthetic backend metadata sentinel to verify deletion without initializing S3. Terraform
apply occurred only for Lab 01's temporary built-in `terraform_data` state and Lab 11's isolated
logical `random_id` state. No AWS provider, credential lookup, real S3 initialization, HCP
Terraform request, cloud API call, or billable resource was used.

### Items not verified

- Linux execution: **NOT VERIFIED**. Path handling uses `pathlib`, subprocess argument lists, and
  lab-relative manifest paths, but this gate ran on Windows and no Linux runner was available.
- Terraform versions other than v1.14.0: **NOT VERIFIED**. The current host supplied only Terraform
  v1.14.0; the manifests permit the documented compatible ranges.
- Real HCP Terraform organization behavior: **NOT VERIFIED by design**. Lab 25 is a local
  conceptual scorer.
- Real S3 backend initialization: **NOT VERIFIED by design**. Lab 31's default gate is offline and
  the live path requires explicit learner authorization and resources.
- Remote-service import behavior: **NOT VERIFIED by design**. Lab 11 intentionally uses the local
  logical `random_id` provider to make import and address movement deterministic.

### Remaining risks

- Lab 25's public option set and comparison digests can be inspected or brute-forced. The scorer
  avoids a plaintext answer key, but blind practice still depends on respecting protected paths.
- Lab 25 grades rationale completeness rather than semantic prose quality; human review remains
  useful for reasoning depth.
- Lab 31's checker is deliberately scoped to this lab's static one-line assignments and is not a
  general HCL parser; its negative fixtures cover the prohibited expression and hardcoding cases.
- The other 27 labs remain legacy inputs and are intentionally excluded from `check --all` until
  separately migrated under Starter Standard v1.
