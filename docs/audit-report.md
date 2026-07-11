# Phase 1 Read-Only Audit Report

> Phase 13 final acceptance addendum (2026-07-11): the Phase 1 findings below are retained as the
> historical baseline. All 32 labs have now been migrated and independently re-audited against
> Starter Standard v1. Current release status is recorded in `docs/lab-matrix.csv` and the Phase 13
> section of `docs/migration-report.md`.

## Phase 13 final acceptance summary

- Structure and manifest validation: **PASS, 32/32**. IDs are exactly 01-32; README titles,
  difficulty, time, expected markers, validation/reset commands, editable paths, protected paths,
  tracked files, and the directory contract are consistent.
- Starter gates: **PASS, 32/32**. Every valid starter reached its declared protected gate and
  produced its declared marker. No credential, network, placeholder-name, or unrelated syntax
  failure was accepted as evidence.
- Canonical solution gates: **PASS, 32/32**, twice with a reset between runs. State/refactor labs
  proved exact address transitions, zero unintended create/delete actions, and final no-op plans.
- Reset/repeatability: **PASS, 32/32**. Lab-owned state, plans, initialization metadata, dependency
  locks, workspaces, and recorded results were removed before the repeated solution run.
- Test-quality scan: **PASS**. No standalone `!= null` or `can(...)` assertion remains in protected
  Terraform Test files; behavioral, boundary, failure, and state cases are present where applicable.
- Default cloud safety: **PASS, 32/32**. No default workflow requires credentials or creates
  billable resources. No real AWS apply, lookup, backend connection, or API request was executed.
- Repository and CI static acceptance: **PASS**. Repository formatting, `tools/repo_check.py`,
  `tools/labctl.py list`, and `python tools/labctl.py check --all` passed. The workflow defines
  Windows and Linux starter gates and a solution-branch gate without a live-cloud job.

The release still has explicit `NOT VERIFIED` boundaries: hosted GitHub Actions execution, Linux
runtime behavior in this local phase, Terraform versions other than v1.14.0, provider versions
other than AWS v6.54.0/random v3.9.0/local v2.9.0, optional real S3 backend paths, and real cloud
service behavior. The Apache-2.0 file is present and upstream attribution is now visible in the
root README, but provenance and any applicable NOTICE obligation remain a pre-publication risk.

Audit date: 2026-07-10

Repository branch: `main`
Baseline commits inspected: `2aafcd7 phase0`, `1533ec2 Initial commit`

## Executive summary

The repository contains 32 numbered lab directories and 105 lab files: 32 README files, 64 Terraform files, 7 Terraform test files, one JSON input, and one CSV input. There are no module directories, fixtures directories, bootstrap directories, lab scripts, backend configuration files, manifests, lock files, repository validation/reset tooling, or CI workflows.

The current `main` branch is not a blind-practice starter collection. Only 2 labs are genuine starters. Eleven expose a complete implementation and four expose nearly all of one. Ten are inconsistent or unusable because their declared exercise cannot be reproduced from the committed files. Detailed evidence and remediation for every lab are in `docs/lab-matrix.csv`.

### Status statistics

| Current status | Labs | Count | Share |
| --- | --- | ---: | ---: |
| genuine starter | 01, 02 | 2 | 6.25% |
| partially completed | 05, 06, 13, 14, 20 | 5 | 15.63% |
| near-complete solution | 18, 22, 24, 29 | 4 | 12.50% |
| complete solution | 07, 08, 09, 15, 16, 17, 21, 23, 27, 30, 32 | 11 | 34.38% |
| inconsistent or unusable | 03, 04, 10, 11, 12, 19, 25, 26, 28, 31 | 10 | 31.25% |
| **Total** |  | **32** | **100%** |

Classification describes how much learner implementation is exposed. It is not a pass/fail quality score. For example, Lab 07 is a complete solution whose tests fail, and Lab 26 exposes answer blocks but remains unusable without source state.

## Scope and method

The audit read:

- root README, `.gitignore`, license, `AGENTS.md`, and the refactor master plan;
- all 32 lab README files;
- all committed `.tf` and `.tftest.hcl` files;
- the only JSON and CSV inputs;
- the complete directory inventory, including confirmation that referenced modules and backend files are absent.

Evidence was gathered through file inventory, exact SHA-256 duplicate detection, keyword searches, Terraform formatting, isolated initialization/validation, and limited local-only Terraform tests. Each lab was copied to a system temporary directory for initialization so no `.terraform/` or lock file was written under `labs/`. Temporary copies were deleted after checks.

No real AWS apply, plan, data lookup, backend initialization, credential read, or cloud API operation was performed.

## Repository-wide findings

### Starter and solution isolation

- Only Labs 01 and 02 qualify as genuine starters.
- Fourteen labs have definite solution leakage and seven more have partial leakage.
- The strongest examples are Labs 07, 08, 09, 15, 16, 17, 21, 23, 26, 27, 29, 30, and 32, where the main task implementation or answer blocks are already present.
- Lab 22 explicitly tells the learner to add `create_before_destroy` in a source comment.

### Tests

- Tests exist for only 7 of 32 labs: 07, 10, 15, 16, 18, 29, and 32.
- Zero test suites are both executable in the safe audit path and sufficiently behavioral.
- Labs 07, 29, and 32 were safe to run locally and all failed. Lab 07 uses invalid `output.<name>.value` access. Labs 29 and 32 assert planned `terraform_data` outputs that remain unknown.
- Lab 10 cannot initialize because all three referenced child modules are absent.
- Labs 15, 16, and 18 use real AWS resources without mock providers. Their tests were not run to avoid credential or cloud access. Lab 18's assertions also use the same suspect `.value` pattern.
- Labs 10, 15, 16, and 32 rely primarily on output existence/non-null assertions rather than the declared behavior.

### Duplicate and misplaced content

Exact `main.tf` duplicates were proven by SHA-256 hashes:

- Labs 03 and 11;
- Labs 04 and 12;
- Labs 05 and 13;
- Labs 06 and 14;
- Labs 15 and 16;
- Labs 23, 29, and 32.

These are not merely shared scaffolds: the declared topics differ. Lab 28's `main.tf` is a validation/precondition deployment exercise unrelated to provider version constraints. Lab 09's starting assumptions, target state, and success criteria describe S3 buckets rather than security groups.

### README quality

- All 32 README files have a title, task list, difficulty, estimated time, and success criteria.
- None has explicit sections for execution mode, cloud credentials, editable/protected files, expected initial failure, reset instructions, or hints as required by the target standard.
- Twenty-three README files repeat the same generic success criteria about validation, preconditions, and checks regardless of topic.
- README commands routinely omit the type-specific workflow. Labs 07 and 29 declare test success but tell learners only to run init, validate, and plan.
- Cost labels are not reliable proxies for credentials or external dependencies. Several `none`/`low` labs still require AWS provider installation, account authentication, a live lookup, or a real S3 backend.

### State, backend, and reset

- Labs 03, 11, 19, and 26 declare managed refactors but contain no bootstrap, initial state, old-state fixture, isolated state path, reset, second-run check, or no-op plan proof.
- Labs 03 and 11 additionally assume an existing real S3 bucket and are exact duplicates.
- Labs 04 and 12 use an expression-derived backend key, which is not permitted in backend configuration, and have no producer/consumer split or `terraform_remote_state` data source.
- Lab 31 references `backend.hcl`, but no such file or example exists anywhere in the repository.
- No lab has a reset command. Reset and repeatability are therefore unverified for all 32 labs.

### Cloud and dependency safety

- All 32 labs declare the AWS provider, including purely local, conceptual, and `terraform_data` exercises.
- No provider lock file is committed.
- AWS resource labs have no mock provider configuration. Several require globally unique names, an existing bucket, a default VPC, live AMI discovery, or a real S3 backend.
- Default plan/test execution is therefore not credential-free or deterministic across the collection.
- The repository contains no hardcoded AWS access key or account ID in the audited files. Placeholder secret text in Lab 24 is still an unsuitable training default and its debug output deliberately removes sensitivity.

### Licensing and repository surface

An Apache License 2.0 text is present. No `NOTICE` file or clear attribution appears in the minimal root README. This audit did not verify provenance of every copied lab or whether a NOTICE obligation applies; preserve the existing license and confirm upstream attribution before publishing a refactored distribution.

## Ten most severe issues

1. **The starter branch exposes answers.** Eleven complete and four near-complete solutions defeat blind practice; additional partial leakage exists in seven labs.
2. **State/refactor labs are not reproducible.** Labs 03, 11, 19, and 26 cannot establish their declared starting state or prove safe address movement and no-op results.
3. **Backend labs lack a valid offline workflow.** Labs 04/12 misuse expressions in backend configuration; Lab 31 references a nonexistent `backend.hcl`; none has producer/consumer fixtures or reset.
4. **Test coverage is both sparse and defective.** Only 7 labs have tests, none is fully meaningful, and all three safely executed suites failed.
5. **Large exact duplicates hide topic drift.** Six duplicate groups affect 13 lab directories, including a three-way lifecycle copy used for unrelated testing and replacement topics.
6. **README template pollution is pervasive.** Twenty-three labs claim unrelated validation/precondition/check criteria, and required execution, cloud, initial-failure, edit-scope, and reset sections are absent everywhere.
7. **Lab 10 is structurally broken.** It references three child modules that do not exist and cannot initialize.
8. **Local labs inherit unnecessary AWS/network dependency.** Every lab declares AWS; there are no lock files or mocks, so even conceptual/local tests require provider registry access.
9. **High-value topics are mis-modeled.** Lab 25 turns HCP decisions into outputs, and Lab 28 contains code for a different validation exercise rather than testing constraint semantics.
10. **There is no repository execution contract.** No manifest, reset/check tool, CI, fixture convention, starter/solution isolation mechanism, or repeatability evidence exists.

## Lab-specific high-risk notes

- **Lab 07:** code contains every requested validation, precondition, and check; tests fail before exercising the expected failure run.
- **Labs 08/09/15/16/17/21:** code is already a plausible answer while no mock behavioral grader exists.
- **Lab 18:** demonstrates `one()` and `try()` in the starter but retains one unsafe direct index; the exercise is almost solved.
- **Lab 24:** sensitive propagation is mostly correct, but `nonsensitive(var.db_password)` deliberately leaks the secret.
- **Lab 29:** the requested setup apply already exists; its copied lifecycle configuration and failing unknown-value assertion do not provide a good test-authoring starter.
- **Lab 32:** the complete `replace_triggered_by` answer exists, while tests never inspect replacement actions.

## Verification results

### Commands actually executed

```text
git status --short --branch
git branch --show-current
git log -5 --oneline
rg --files -g '!**/.terraform/**'
terraform version
terraform fmt -check -recursive
terraform validate -json                         # each original lab, without init
terraform init -backend=false -input=false       # each isolated temporary copy
terraform validate -json                        # each successfully initialized copy
terraform test -no-color                        # isolated copies of Labs 07, 29, 32
git status --short                              # after temporary checks
```

### Actual outcomes

- Terraform CLI: v1.14.0 on Windows amd64.
- `terraform fmt -check -recursive`: PASS, exit 0.
- Original directories without initialization: all 32 `validate` calls failed. Thirty-one reported the missing AWS provider; Lab 10 reported three uninstalled module directories before provider validation. This is expected evidence of missing initialization, not a configuration verdict.
- Isolated `init -backend=false` plus `validate`: PASS for 31 labs. Lab 10 initialization failed with `Unreadable module directory`; validate was not run there.
- Labs 06 and 14 validated with two `Deprecated attribute` warnings each.
- Lab 07 test: FAIL, 0 passed / 1 failed / 1 skipped, due to unsupported output attributes.
- Lab 29 test: FAIL, 1 passed / 1 failed, due to an unknown assertion condition.
- Lab 32 test: FAIL, 0 passed / 1 failed, due to unknown assertion conditions.
- Final Git status after checks contained only the pre-existing untracked `phase1.md`; no lab artifact was created.

### NOT VERIFIED

- **Starter gates:** NOT VERIFIED for all 32 labs. No lab declares a deterministic expected-failure contract or protected behavioral grader, and Phase 1 forbids building one.
- **Canonical solution gates:** NOT VERIFIED for all 32 labs. Complete-looking current code was not assumed to be canonical, and Phase 1 forbids creating solutions.
- **Reset and second run:** NOT VERIFIED for all 32 labs because no reset workflow exists and no stateful migration was authorized.
- **AWS plans/tests:** NOT VERIFIED. No real credentials were requested or read, no AWS plan/apply/data lookup was run, and tests for Labs 15, 16, and 18 have no mock provider.
- **Normal S3 backend initialization:** NOT VERIFIED for Labs 04, 12, and 31 because it would require nonexistent or real backend configuration; only `-backend=false` initialization was run.
- **State transitions/no-op plans:** NOT VERIFIED for Labs 03, 11, 19, and 26 because no reproducible source state exists.
- **Lab 10 validate/test:** NOT VERIFIED because required module directories are absent.
- **Upstream attribution/NOTICE requirement:** NOT VERIFIED from the repository contents alone.

## Recommended remediation batches

Do not begin broad migration until the five pilots establish and pass the frozen standard.

1. **Pilot set — 01, 07, 11, 25, 31.** Covers lifecycle authoring, validation/testing, state refactor, HCP conceptual scoring, and partial backend configuration.
2. **Local authoring and test quality — 02, 18, 20, 21, 22, 23, 24, 27, 29, 30, 32.** Remove unnecessary AWS dependencies where possible and establish behavioral public tests plus reset.
3. **AWS mock/wiring — 08, 09, 15, 16, 17.** Introduce mock providers, remove account assumptions, and decide whether overlapping S3 labs should be narrowed or merged.
4. **Modules, aliases, and constraints — 06, 10, 14, 28.** Rebuild missing module scaffolds, differentiate alias labs, and create semantic constraint validation.
5. **Remaining state/backend/workspace — 03, 04, 05, 12, 13, 19, 26.** Resolve duplicates first, then add local producer/bootstrap fixtures, address assertions, safe reset, and repeatability.

Repository-level manifest validation and portable `labctl` tooling should be implemented immediately after the pilot contract is proven, then used as the gate for each later batch. CI remains a later phase and must not be added during this audit.

## Recommended first five pilot labs

| Lab | Why it is a useful pilot | Required proof before wider migration |
| --- | --- | --- |
| 01 | Small lifecycle/CLI exercise | Genuine deterministic starter; lifecycle behavior test; no manual unique-name dependency |
| 07 | Local quality lab with severe answer leakage and broken tests | Valid normal/failure tests; expected starter failure; no AWS dependency |
| 11 | Representative import/moved state lab | Reproducible old state; address movement; no destroy/create; reset and second run |
| 25 | Conceptual HCP operations case | Scenario artifacts; structured rubric; answer isolation; deterministic scorer |
| 31 | Backend operational pattern | Safe partial config examples; offline validation; backend metadata reset |

## Files changed in Phase 1

- `docs/audit-report.md`
- `docs/lab-matrix.csv`
- `docs/lab-standard.md`

No file under `labs/` was modified. `docs/migration-report.md` remains absent because the Phase 1 prompt permits writes only to the three audit documents and migration implementation has not started.
