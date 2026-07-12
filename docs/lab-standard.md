# Terraform Professional Lab Standard

Status: Starter Standard v1, frozen after the Phase 5 pilot quality gate.

Phase 13 release review: all 32 labs were accepted against this unchanged standard. No contract
defect was found and no requirement was redesigned. The final repository checker operationalizes
the existing manifest, README, path, starter-leakage, test-quality, cloud-safety, and CI checks.

Storage-model amendment (2026-07-12): at the repository owner's direction, canonical solutions are
not stored on any repository branch. This changes only answer storage, not the solution gate: every
lab must still be verified with a transient canonical implementation, reset, and verified again.
The amendment affects all 32 labs and removes the unused solution-branch CI contract.

This document defines the frozen contract for future migration phases. The Phase 5 migration report records the five pilots certified against this version. A later change to this standard requires a concrete defect, a recorded reason, the affected lab list, and remediation notes in the migration report.

## 1. Goals

Every lab must be suitable for blind practice, deterministic, resettable, automatically verifiable, safe by default, and internally consistent. A learner must be able to identify the scenario and allowed work without seeing the canonical answer.

The default workflow must not require real cloud credentials or create billable resources. A live-cloud extension is permitted only when explicitly labelled optional and isolated from normal validation.

## 2. Classification vocabulary

The audit and migration reports use these current-state classifications:

- `genuine starter`: the core behavior is withheld or meaningfully incorrect, while the scenario remains understandable.
- `partially completed`: several target elements exist, but meaningful implementation remains.
- `near-complete solution`: nearly all target behavior or answer patterns are visible.
- `complete solution`: the learner-facing configuration already implements the declared tasks.
- `inconsistent or unusable`: missing prerequisites or contradictions prevent the declared exercise from being performed reproducibly.

These labels describe the learner-facing implementation, not overall quality. A `complete solution` can still have broken tests or unsafe execution requirements.

## 3. Canonical lab types

Each manifest must select one primary type:

- `authoring-local`: expressions, variables, locals, outputs, `terraform_data`, files, and collection transforms.
- `aws-mock`: AWS provider schema and graph behavior verified without account access.
- `aws-plan`: optional credentialed plan with no apply; must state why mocking is insufficient.
- `aws-live`: optional apply path with prerequisites, maximum expected cost, cleanup, and explicit user opt-in.
- `state-refactor`: import, moved, removed, count-to-for_each, or module address migration with seeded isolated state.
- `backend-remote-state`: backend syntax or producer/consumer state sharing with a local default fixture.
- `workspace`: isolated workspace creation, verification, and reset.
- `terraform-test`: writing or repairing tests with observable behavioral assertions.
- `conceptual`: scenario, response, and rubric artifacts; no meaningless Terraform outputs.
- `constraint`: Terraform/provider version constraint semantics verified beyond `terraform validate`.

## 4. Directory contract

Use only the directories required by the selected type:

```text
labs/NN-topic/
├── README.md
├── lab.yaml
├── starter/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── versions.tf
│   └── terraform.tfvars.example
├── tests/
│   └── public.tftest.hcl
├── fixtures/
├── bootstrap/
└── scripts/
```

The repository must not contain `solution/`, `SOLUTION.md`, answer keys, disabled solution blocks,
or filenames that reveal exact answers. Canonical implementations are reconstructed only in an
isolated temporary copy for acceptance and are deleted afterward. A learner validates their own
completed starter locally with `labctl check <lab-id> --mode solution`.

## 5. Manifest contract

Every `lab.yaml` must include at least:

```yaml
id: 7
title: Validation, Preconditions, Checks, and Tests
type: terraform-test
tier: quality
difficulty: medium
estimated_minutes: 20

execution:
  mode: local
  terraform_version: ">= 1.6, < 2.0"
  requires_cloud_credentials: false
  creates_billable_resources: false
  backend: local

validation:
  starter_expected_result: fail
  expected_failure_stage: test
  expected_error_category: behavior
  expected_failing_test: public.tftest.hcl
  solution_expected_result: pass

editable_paths:
  - starter/main.tf
protected_paths:
  - tests/
  - fixtures/
```

Additional type-specific fields are required for state ownership, fixture generation, workspace names, backend examples, cloud cost, and cleanup where applicable.

## 6. README contract

Every README must contain these explicit sections:

1. Title
2. Scenario
3. Skills tested
4. Difficulty and estimated time
5. Execution mode
6. Cloud credentials required
7. Cost risk
8. Starting state
9. Files allowed to edit
10. Files not allowed to edit
11. Tasks
12. Constraints
13. Expected initial failure
14. Validation commands
15. Success criteria
16. Reset instructions
17. Limited hints

Commands must match the actual workflow. A Terraform Test lab must run `terraform test`; a state lab must include bootstrap and state verification; a backend lab must show the exact safe init command; a conceptual lab must show the scoring command.

Success criteria must name lab-specific behavior. Generic requirements for validation, preconditions, and checks are forbidden unless those constructs are the stated learning objective.

## 7. Starter contract

A starter must:

- pass `terraform fmt -check`;
- normally pass `terraform init -backend=false` and `terraform validate`, unless initialization or syntax is the topic;
- fail exactly one documented plan, test, state, or scoring gate for a deterministic reason tied to the objective;
- preserve enough scaffold and old configuration for the learner to reason about the change;
- contain no globally unique placeholder dependency when a deterministic value or mock can be used;
- contain no complete answer in comments, TODO text, outputs, tests, fixtures, or disabled blocks.

A failing starter is not proven by missing credentials, unavailable networking, missing provider packages, invalid placeholder names, or unrelated syntax errors.

## 8. Canonical solution contract

The canonical solution must be reconstructed from Terraform semantics and the declared scenario, not copied uncritically from the current repository. It must:

- satisfy every task and success criterion;
- use stable resource identities and maintainable expressions;
- preserve state identity for refactors;
- avoid credentials, account identifiers, and secret-bearing outputs;
- avoid accidental provider behavior and external infrastructure assumptions;
- pass every applicable gate after reset and on a second run.

Tests may expose required behavior but must not prescribe the complete HCL expression.

## 9. Validation contract

Each migrated lab has two separate gates.

### Starter gate

Record the exact command, expected stage, expected diagnostic category, and failing test/rule. The command must fail for the intended reason.

### Solution gate

Run and inspect, as applicable:

```text
terraform fmt -check -recursive
terraform init -backend=false
terraform validate
terraform test
terraform plan -out=plan.tfplan
terraform show -json plan.tfplan
terraform state list
terraform workspace show
```

State/refactor solutions must additionally prove expected old and new addresses, absence of unintended delete/create actions, and final no-op behavior. Backend and conceptual labs use type-appropriate static or scoring checks rather than a meaningless plan.

No command may be reported as passing unless it was executed and its output inspected. Unavailable checks are recorded as `NOT VERIFIED` with the exact reason.

## 10. Test quality contract

Tests must verify behavior rather than presence. Assertions should cover the applicable subset of:

- exact resource count and addresses;
- stable `for_each` keys and filtering;
- map/list shape and exact selected values;
- merged tag precedence;
- lifecycle replacement or drift behavior;
- provider alias wiring into child modules;
- expected validation, precondition, and check outcomes;
- sensitive output metadata;
- state address movement and absence of destroy/create;
- normal, boundary, and failure scenarios.

Assertions such as `value != null`, `can(output.value)`, or output existence are insufficient on their own. Planned values that are legitimately unknown must not be asserted as known. Tests that use AWS resources must use supported mocking or an explicitly optional live path.

## 11. Cloud-safety contract

The default check path must have:

- `requires_cloud_credentials: false`;
- `creates_billable_resources: false`;
- no real backend initialization;
- no live data-source dependency;
- no account-specific IDs or globally unique manual placeholders.

An optional `aws-live` path must document prerequisites, region, resources created, maximum expected cost, cleanup command, failure cleanup, and explicit opt-in. Normal CI must never run it.

Unused AWS provider declarations are prohibited in local and conceptual labs because they add unnecessary registry/network dependency.

## 12. State and refactor contract

State labs must own all state under their lab directory or an explicitly isolated temporary directory. They require:

- an old configuration or bootstrap fixture;
- deterministic state seeding;
- documented old addresses;
- a genuine refactor starter;
- expected target addresses;
- state and plan inspection;
- a safe reset that removes only lab-owned artifacts;
- a full second run proving repeatability.

Deleting state to hide replacement is forbidden. Import labs must create or emulate the import target reproducibly.

## 13. Backend, remote-state, and workspace contract

Backend labs must separate backend configuration, provider configuration, input variables, producer state, and consumer code. Terraform expressions and input variables must not be used inside backend blocks.

Example backend files contain placeholders only, no credentials or real resource names, and use an `.example` suffix where secrets or environment-specific values may be supplied. Default validation uses a local backend or static checker. Reset removes only lab-owned backend metadata and workspaces.

## 14. Conceptual and constraint lab contract

Conceptual labs use `SCENARIO.md`, `QUESTIONS.md`, `student-answer.md`, and `rubric.yaml`. Scoring evaluates decisions and reasoning without exact prose matching. Canonical answers remain off the starter branch.

Constraint labs must exercise both `required_version` and `required_providers`. Validation must evaluate operator semantics and allowed/disallowed versions; `terraform validate` alone is insufficient.

## 15. Repository tooling contract

The repository must eventually provide portable commands:

```text
python tools/labctl.py list
python tools/labctl.py status <lab-id>
python tools/labctl.py reset <lab-id>
python tools/labctl.py check <lab-id>
python tools/labctl.py check --all
```

Tooling must work on Windows and Linux, use explicit exit codes, avoid shell injection, and delete only lab-owned artifacts. CI must distinguish local/mock checks from manually authorized live-cloud checks.

## 16. Reset and repeatability contract

Reset must remove only generated artifacts such as `.terraform/`, lab-owned state, plans, generated fixtures, backend metadata, and lab-created workspaces. It must preserve source files, user answers where documented, global Terraform configuration, and unrelated state.

For every migrated lab, execute: reset; starter gate; apply the canonical implementation only in an
isolated temporary copy; solution gate; reset; repeat the solution gate; delete the temporary copy.
Record both runs without retaining the answer in the repository.

## 17. Migration acceptance checklist

A lab is migrated only when all are true:

- README, manifest, starter, tests, fixtures, and scripts agree;
- starter has no solution leakage;
- starter fails at the intended gate;
- canonical solution passes all applicable gates;
- reset and a second run pass;
- no unapproved live cloud operation is required;
- no test was weakened to obtain a pass;
- verification evidence and any `NOT VERIFIED` items are in the migration report.
