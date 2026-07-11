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

## Phase 6 - Core Authoring Batch A

Migration date: 2026-07-11

Working branch: `main`

Scope: Labs 02, 10, 16, and 18 plus their matrix and migration-report records. No other lab,
shared tool, frozen standard, CI configuration, or later-phase artifact was modified.

### Original defects and migration design

- Lab 02 was a credential-dependent S3 `count` starter with no tests, conditional objects, safe
  names, or deterministic failure. It is now a provider-free catalog refactor exercise. The
  starter deliberately retains positional iteration, unfiltered setting records, and list outputs.
- Lab 10 referenced three missing module directories, could not initialize, and tested only
  non-null outputs with invalid `.value` access. It now has protected local naming, identity, and
  compute child modules. The learner repairs two root references without changing module contracts.
- Lab 16 was a complete duplicate of Lab 15's S3 solution and its tests checked only output
  presence. It is now narrowly scoped to filtering enabled services and preserving exact map keys
  and values; the starter intentionally deploys every entry and emits lists.
- Lab 18 exposed almost all requested S3 answer patterns while retaining one unsafe output and
  requiring AWS for its enabled path. It now models a zero-or-one local marker. Both starter
  outputs are unsafe, while the protected verifier requires the canonical source to demonstrate
  both `one()` and `try()` after its behavioral tests pass.

All four labs use only the built-in `terraform_data` resource. No AWS provider, provider download,
credential lookup, globally unique name, backend initialization, real apply, or billable resource
is part of the default workflow.

### Starter gates

For each lab, the following sequence was executed:

```text
python tools/labctl.py reset <lab-id>
python tools/labctl.py check <lab-id>
```

All four starters passed format, offline init, and validate before failing at the protected test
stage for the intended behavior:

| Lab | Marker | Observed target failure |
| --- | --- | --- |
| 02 | `EXPECTED_DYNAMIC_CONFIGURATION_INCOMPLETE` | tuple/list results did not satisfy stable maps or conditional filtering |
| 10 | `EXPECTED_MODULE_COMPOSITION_INCOMPLETE` | compute and root outputs bypassed the identity module output |
| 16 | `EXPECTED_FILTERED_FOREACH_INCOMPLETE` | disabled `docs` remained and outputs were positional lists |
| 18 | `EXPECTED_CONDITIONAL_READ_INCOMPLETE` | disabled count produced invalid index errors and the source contract lacked both safe-read functions |

After canonical verification and restoration, the same four starter gates were rerun and reproduced
the same markers and failure categories.

### Canonical solution gates

Canonical edits were applied transiently and removed after verification. For each lab,
`python tools/labctl.py check <lab-id> --mode solution` passed format, offline init, validate, and
three Terraform Test runs:

- Lab 02: exact default keys/filtering/tag precedence, empty-map boundary, and invalid retention.
- Lab 10: exact default wiring, alternate root inputs, and unsupported environment failure.
- Lab 16: exact enabled keys/ports, all-disabled empty maps, and invalid port failure.
- Lab 18: disabled null behavior, enabled exact values, invalid name failure, plus protected
  confirmation that both `one()` and `try()` occur in the editable source.

Each suite reported `3 passed, 0 failed` on canonical run 1.

### Reset and second run

Between canonical runs, `python tools/labctl.py reset <lab-id>` was executed for every lab, followed
by `python tools/labctl.py status <lab-id>`. Every status reported `Generated artifacts: 0` and no
recorded starter or solution result. A second canonical solution check then reported `3 passed,
0 failed` for each lab again. Lab 10 reset removed both root and starter module initialization
caches; the other labs removed their root test initialization caches and result records.

### Batch and repository regression

The four restored learner starters were reset and checked together; all reproduced their expected
test-stage failures. The repository aggregate starter gate was then run with:

```text
python tools/labctl.py check --all
```

It covered the five Phase 5 pilots and these four Phase 6 labs while skipping legacy labs. The
observed summary was `Passed: 01, 02, 07, 10, 11, 16, 18, 25, 31` and `Failed: none`.

### Items not verified

- Linux execution: **NOT VERIFIED**. This phase ran on Windows only; the new scripts use `pathlib`,
  subprocess argument lists, and no shell-specific commands.
- Terraform versions other than v1.14.0: **NOT VERIFIED**. Only the installed v1.14.0 binary was
  executed; manifests permit `>= 1.6, < 2.0`.
- Real AWS behavior: **NOT VERIFIED by design**. These are local authoring/module-semantics labs and
  intentionally contain no AWS provider or resource.

### Remaining risks

- `terraform_data` verifies Terraform graph, collection, output, and module semantics but does not
  exercise an external provider schema. That is intentional for this core-authoring batch.
- Public behavioral tests reveal required result shapes and example values, but do not include the
  canonical HCL expressions. Blind practice still depends on respecting protected paths.
- Canonical implementations were verified transiently and are not retained on the learner-facing
  branch; they must remain isolated in a future solution/grader branch.

## Phase 10 - AWS, Constraints, and Terraform Test Batch B

Migration date: 2026-07-11

Working branch: `main`

Scope: Labs 15, 17, 28, and 29, their matrix and migration-report records, and two narrow
`.gitignore` exceptions required to commit Lab 17's synthetic state fixtures. No other lab,
shared repository tool, frozen standard, CI configuration, or later-phase artifact was modified.

### Migration design

- Lab 15 is now an `aws-mock` exercise. Its valid starter deliberately creates versioning and
  lifecycle configuration for every bucket, reverses tag precedence, supplies an invented
  retention value, and returns lists. Three Terraform Test runs verify exact bucket keys,
  conditional resource keys, enabled versioning, lifecycle days, bucket-specific tag precedence,
  exact map outputs, the all-disabled boundary, and invalid retention. No AWS request is made.
- Lab 17 no longer reads a live default VPC. It uses two protected local Terraform state snapshots
  to model producer stacks. The starter contains manually copied identifiers and ignores its path
  input. Three runs verify the default producer, an alternate caller-selected producer, sorted and
  selected subnet outputs, the exact consumer boundary, and invalid lookup filenames. A protected
  source check requires the built-in `terraform_remote_state` data source. Exact `.gitignore`
  exceptions make only these two synthetic snapshots trackable while generated state remains
  ignored repository-wide.
- Lab 28 no longer contains the unrelated environment, instance-size, precondition, and deployment
  template. It contains only Terraform and provider requirements plus root, minimum-only, and exact
  strategies. A protected semantic scorer evaluates allowed and rejected candidates and confirms
  actual `~>`, `>=`, `=`, and `!=` operator coverage rather than treating `terraform validate` as
  proof of range correctness.
- Lab 29 is now a genuine test-authoring lab. The protected provider-free deployment configuration
  replaces identity when a release changes, while the learner test contains only one plan. The
  canonical four-run suite applies `v1`, applies `v2`, compares generated IDs across runs, proves a
  steady `v2` plan retains the upgraded state, and attributes invalid syntax to the variable. The
  protected verifier executes the suite and checks its run, command, assertion, cross-run, and
  expected-failure coverage.

The Lab 15 and 17 canonical runs exposed strict Terraform collection-type comparisons in two test
assertions. Those assertions were corrected with explicit map/list conversions or exact per-field
checks while retaining the same key set and values. No test requirement was removed or weakened.
The frozen lab standard and `tools/labctl.py` required no change.

### Starter gates

Before canonical verification and again after starter restoration, each lab was reset and checked:

```text
python tools/labctl.py reset <lab-id>
python tools/labctl.py check <lab-id>
```

All four starters passed format, initialization, and validation before failing at their intended
protected stage:

| Lab | Marker | Observed target failure |
| --- | --- | --- |
| 15 | `EXPECTED_S3_CONDITIONAL_CONFIGURATION_INCOMPLETE` | optional resources included `assets`, tag precedence was reversed, and outputs were lists |
| 17 | `EXPECTED_CROSS_STACK_LOOKUP_INCOMPLETE` | both producer selections returned manually copied values |
| 28 | `EXPECTED_CONSTRAINT_SEMANTICS_INCOMPLETE` | unsupported majors and 6.2.0 were allowed, the exact pin was wrong, and `~>`/`!=` were absent |
| 29 | `EXPECTED_SEQUENTIAL_TEST_FLOW_INCOMPLETE` | only one passing plan existed, with no apply, state change, cross-run identity, or failure case |

### Canonical solution gates

Canonical edits were applied transiently and removed after verification. Every lab passed
`python tools/labctl.py check <lab-id> --mode solution` twice with reset and clean status between
runs:

- Lab 15: `3 passed, 0 failed` for exact default behavior, the disabled boundary, and invalid
  retention through AWS provider mocking.
- Lab 17: `3 passed, 0 failed` for primary and alternate local producer states plus invalid input;
  the protected data-source source contract also passed.
- Lab 28: initialization selected AWS provider v6.54.0, root validation passed, and every protected
  runtime, bounded, minimum, exact, and excluded candidate produced the expected result.
- Lab 29: `4 passed, 0 failed`; sequential test state proved setup identity, replacement identity,
  stable upgraded state, and the expected validation failure.

### Reset, repeatability, and regression

Between canonical runs, `python tools/labctl.py reset <lab-id>` removed initialization directories,
dependency locks, and result records. `python tools/labctl.py status <lab-id>` reported
`Generated artifacts: 0` and no recorded results for all four labs. The second canonical run
reproduced every pass, and restored starters reproduced every expected marker.

The aggregate learner-starter gate was then executed:

```text
python tools/labctl.py check --all
```

It covered 25 migrated labs and reported
`Passed: 01, 02, 06, 07, 08, 09, 10, 11, 14, 15, 16, 17, 18, 20, 21, 22, 23, 24, 25, 27, 28, 29, 30, 31, 32`
and `Failed: none`.

### Cloud safety

No real AWS apply, plan, authentication, data lookup, or API call was performed. Lab 15 used the
Terraform AWS mock provider. Lab 17 used the built-in remote-state data source against committed
synthetic state snapshots. Lab 28 initialized provider metadata only and contains no provider
configuration or resource. Lab 29 used only the built-in `terraform_data` resource and Terraform
Test-managed temporary state. No billable or persistent cloud resource was created.

### Items not verified

- Linux execution: **NOT VERIFIED**. This phase ran on Windows only. New scripts use `pathlib`,
  subprocess argument lists, and no shell-specific commands.
- Terraform versions other than v1.14.0: **NOT VERIFIED**. Only the installed v1.14.0 binary was
  executed; manifests permit `>= 1.6, < 2.0`.
- AWS provider versions other than v6.54.0: **NOT VERIFIED**. That version was selected from the
  configured shared cache for mock tests and constraint initialization.
- Real AWS S3 behavior: **NOT VERIFIED by design**. Lab 15 validates Terraform graph and provider
  schema behavior through mocks and never contacts S3.
- Real remote backends or live producer stacks: **NOT VERIFIED by design**. Lab 17 deliberately
  validates the cross-stack contract with synthetic local state fixtures.

### Remaining risks

- Labs 15 and 28 require registry access or a populated AWS provider cache for initialization,
  although neither needs credentials or service access.
- AWS mock tests validate Terraform configuration and the selected provider schema, not AWS
  service-side authorization, account policy, or lifecycle execution.
- Lab 17's committed state fixtures use Terraform state format version 4; compatibility was
  executed only with Terraform v1.14.0 in this phase.
- Public behavioral cases expose required result shapes and candidate versions but do not include
  canonical HCL expressions. Blind practice still depends on respecting protected paths.
- Canonical implementations were verified transiently and are not retained on the learner-facing
  branch; they must remain isolated in a future solution/grader branch.

## Phase 7 - Core Authoring Batch B

Migration date: 2026-07-11

Working branch: `main`

Scope: Labs 20, 21, 22, and 23; their matrix and migration-report records; and one required
`labctl` reset correction. No other lab, frozen standard, CI configuration, or later-phase
artifact was modified.

### Migration design

- Lab 20 now reads four deterministic protected JSON/CSV fixtures. The valid starter deliberately
  retains numeric app identities, list outputs, and raw CSV strings. Public tests require exact
  stable maps, filtering, numeric-or-null conversion, empty JSON behavior, and a zero-day CSV
  boundary. The lab uses only built-in `terraform_data`.
- Lab 21 now keeps two static ingress blocks as the genuine defect. Terraform tests use an AWS mock
  provider to inspect exact nested-block count and content for default and alternate collections,
  plus invalid-port behavior. A protected source check requires one dynamic ingress construct and
  rejects retained static ingress blocks. No AWS authentication or API request occurs.
- Lab 22 now has one direct immutable-release replacement trigger. Its protected verifier applies
  release `v1` in a temporary directory, plans `v2`, reads plan JSON, and distinguishes the
  starter's exact `delete, create` order from the canonical `create, delete` order.
- Lab 23 uses separate `local_file` schema fields because `terraform_data.input` is a single dynamic
  value and did not preserve a verifiable nested ownership boundary. The starter uses
  `ignore_changes = all`. The protected verifier injects permission-only and content-only state
  drift, plans with refresh disabled so fixtures remain deterministic, and requires only permission
  drift to be a no-op. The canonical lifecycle rule ignores only `file_permission`.

The Lab 21 mock workflow revealed that root-level Terraform Test initialization creates a lab-root
`.terraform.lock.hcl`. `tools/labctl.py` previously discovered lock files only below `starter/`.
Reset discovery now scans the current lab directory for lock files; this is bounded to the selected
lab and was required to satisfy the existing reset contract. The frozen lab standard was unchanged.

### Starter gates

For every lab, the following commands were run before and after canonical verification:

```text
python tools/labctl.py reset <lab-id>
python tools/labctl.py check <lab-id>
```

All four starters passed format, initialization, and validation, then failed at the intended
protected behavior stage:

| Lab | Marker | Observed target failure |
| --- | --- | --- |
| 20 | `EXPECTED_EXTERNAL_DATA_SHAPING_INCOMPLETE` | app and CSV results remained positional/raw rather than normalized stable maps |
| 21 | `EXPECTED_DYNAMIC_BLOCK_INCOMPLETE` | alternate three-rule input still rendered the two static default blocks |
| 22 | `EXPECTED_CREATE_BEFORE_DESTROY_INCOMPLETE` | real replacement actions were exactly `delete, create` |
| 23 | `EXPECTED_IGNORE_CHANGES_BOUNDARY_INCOMPLETE` | both permission and managed-content drift were hidden as no-op |

### Canonical solution gates

Canonical edits were applied transiently. Each lab passed
`python tools/labctl.py check <lab-id> --mode solution` twice, with reset and clean status between
runs:

- Lab 20: 2 Terraform Test runs passed for exact default shaping and empty/zero boundaries.
- Lab 21: 3 mock Terraform Test runs passed for default blocks, alternate exact count/content, and
  invalid ports; the protected dynamic-source contract also passed.
- Lab 22: stateful apply/plan inspection proved a genuine release replacement with exact
  `create, delete` actions.
- Lab 23: controlled plan inspection proved permission drift was no-op while content drift produced
  reconciliation actions.

Canonical changes were then removed, leaving only the learner-facing starters.

### Reset, repeatability, and regression

Between canonical runs, reset removed initialization directories, lock files, and recorded results;
`python tools/labctl.py status <lab-id>` reported `Generated artifacts: 0` and no recorded results
for every Phase 7 lab. Stateful lifecycle verification used temporary directories that were removed
on exit.

After starter restoration, all four expected failures were reproduced. The repository aggregate
starter command was then run:

```text
python tools/labctl.py check --all
```

It covered 13 migrated labs and reported
`Passed: 01, 02, 07, 10, 11, 16, 18, 20, 21, 22, 23, 25, 31` and `Failed: none`.

### Cloud safety

No real AWS apply, plan, credential lookup, data lookup, or API call was performed. Lab 21 used the
Terraform mock provider only. Labs 20 and 22 used Terraform's built-in provider. Lab 23 used the
local provider only inside a temporary directory. No billable resource or persistent lifecycle-test
state was created.

### Items not verified

- Linux execution: **NOT VERIFIED**. This phase ran on Windows only. New scripts use `pathlib`,
  subprocess argument lists, and temporary directories, but no Linux runner was available.
- Terraform versions other than v1.14.0: **NOT VERIFIED**. Only Terraform v1.14.0 was executed;
  manifests allow `>= 1.6, < 2.0`.
- AWS provider versions other than v6.54.0 and local provider versions other than v2.9.0:
  **NOT VERIFIED**. Those were the versions selected by the current shared provider cache.
- Real AWS security-group behavior: **NOT VERIFIED by design**. Lab 21 validates AWS provider schema
  planning through a mock and never contacts AWS.
- Real external filesystem permission drift after refresh: **NOT VERIFIED by design**. Lab 23 uses
  controlled state drift with refresh disabled to make the lifecycle boundary deterministic across
  hosts rather than relying on platform-specific chmod behavior.

### Remaining risks

- Provider installation still requires registry access or a populated provider cache for Labs 21
  and 23, although neither lab requires credentials or service access.
- Mock-provider tests validate the selected provider schema and Terraform configuration behavior,
  not AWS service-side authorization or quota behavior.
- Public tests necessarily reveal expected result shapes and scenario values, but do not expose the
  canonical HCL expressions. Blind practice still depends on respecting protected paths.
- Canonical implementations were verified transiently and are not stored on the learner-facing
  branch; they must remain isolated in a future solution/grader branch.

## Phase 8 - Core Authoring Batch C

Migration date: 2026-07-11

Working branch: `main`

Scope: Labs 24, 27, 30, and 32 plus their matrix and migration-report records. No other lab,
shared repository tool, frozen standard, CI configuration, or later-phase artifact was modified.

### Migration design

- Lab 24 no longer commits a password-like default or depends on AWS. Its valid starter has one
  focused defect: a debug output explicitly declassifies the runtime password. A protected verifier
  supplies a clearly synthetic probe only through a temporary process environment and checks the
  sensitive variable declaration, exact output set, sensitive and non-sensitive output metadata,
  exact safe diagnostic content, and normal CLI plan redaction. It never prints the probe.
- Lab 27 now models nested team/app objects with global, team, and app tag layers. The starter keeps
  only the first app per non-empty team, keys records by team alone, and gives team tags precedence
  over app tags. Three Terraform Test runs verify exact compound keys and tag values, same-named apps
  across teams, empty teams, and duplicate-name rejection. A protected source contract additionally
  requires the target flatten and layered merge constructs.
- Lab 30 is now provider-free and has one incomplete naming implementation: it validates only the
  character set and lowercases without normalizing separators. Eight Terraform Test runs cover a
  valid mixed-case value, minimum and maximum length boundaries, leading digit, trailing separator,
  illegal character, short input, and above-maximum input. Tests also verify tokenization and
  final-name construction.
- Lab 32 is no longer a duplicate lifecycle solution. Its service deliberately omits the dependency
  replacement relationship. A protected verifier applies local state, separately plans an upstream
  release-marker update and a direct service-name update, and checks actions plus `action_reason`.
  The canonical solution replaces the service only for the marker change with
  `replace_by_triggers`; the direct name change remains an update.

All four default workflows are local and use only Terraform's built-in provider. No AWS provider,
credential, API request, real secret, cloud resource, or billable operation is involved.

### Starter gates

For each lab, the following sequence was executed before and after canonical verification:

```text
python tools/labctl.py reset <lab-id>
python tools/labctl.py check <lab-id>
```

Every starter passed format, offline initialization, and validation before the intended protected
behavior failure:

| Lab | Marker | Observed target failure |
| --- | --- | --- |
| 24 | `EXPECTED_SENSITIVE_BOUNDARY_INCOMPLETE` | unsafe extra output existed and normal plan rendering contained the synthetic probe; the verifier did not print it |
| 27 | `EXPECTED_NESTED_COLLECTION_TRANSFORM_INCOMPLETE` | only team keys/first apps existed and required compound keys were absent |
| 30 | `EXPECTED_REGEX_NAMING_INCOMPLETE` | separator normalization failed and invalid leading/length forms were accepted |
| 32 | `EXPECTED_REPLACE_TRIGGER_INCOMPLETE` | marker updated, service was no-op, direct name remained an update, and no replacement reason existed |

### Canonical solution gates

Canonical edits were applied transiently and removed after verification. Every lab passed
`python tools/labctl.py check <lab-id> --mode solution` twice with reset and clean status between
runs:

- Lab 24: exact metadata/output-set checks and CLI redaction passed without printing the synthetic
  probe or persisting its generated plan outside the temporary verifier directory.
- Lab 27: all 3 Terraform Test runs passed and the flatten/merge source contract passed.
- Lab 30: all 8 legal, illegal, normalization, and boundary runs passed.
- Lab 32: the marker action was `update`; the dependent service was replaced with
  `action_reason = replace_by_triggers`; and a name-only service change remained `update`.

### Reset, repeatability, and regression

Between canonical runs, `python tools/labctl.py reset <lab-id>` removed generated initialization
and result artifacts. `python tools/labctl.py status <lab-id>` reported `Generated artifacts: 0`
and no recorded results for all four labs. Labs 24 and 32 created plan/state artifacts only inside
temporary directories, which were deleted when their verifiers exited.

After canonical changes were removed, all four starter markers and failure categories were
reproduced. The aggregate starter gate was then run with:

```text
python tools/labctl.py check --all
```

It covered 17 migrated labs and reported
`Passed: 01, 02, 07, 10, 11, 16, 18, 20, 21, 22, 23, 24, 25, 27, 30, 31, 32`
and `Failed: none`.

### Items not verified

- Linux execution: **NOT VERIFIED**. This phase ran on Windows only. Scripts use `pathlib`,
  subprocess argument lists, explicit environments, and temporary directories, but no Linux runner
  was available.
- Terraform versions other than v1.14.0: **NOT VERIFIED**. Only the installed Terraform v1.14.0
  binary was executed; manifests permit `>= 1.6, < 2.0`.
- Behavior with real credentials: **NOT VERIFIED by design**. Lab 24 intentionally uses only a
  synthetic probe and must never require or read a real secret.
- Remote-provider replacement behavior: **NOT VERIFIED by design**. Lab 32 isolates Terraform
  lifecycle semantics with built-in `terraform_data` rather than claiming a cloud API result.

### Remaining risks

- Terraform `sensitive` metadata redacts normal CLI rendering but does not encrypt plan or state
  payloads. Lab 24 therefore uses only a synthetic value and deletes its temporary plan; production
  systems still require secured remote state and access controls.
- Public behavioral tests expose required result shapes and scenario values but not canonical HCL
  expressions. Blind practice still depends on respecting protected paths.
- Lab 27's source contract is intentionally narrow: it confirms target constructs after behavioral
  correctness, not arbitrary HCL equivalence.
- Canonical implementations were verified transiently and are not retained on the learner-facing
  branch; they must remain isolated in a future solution/grader branch.
