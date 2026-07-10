# AGENTS.md

## Project purpose

This repository is being converted into a high-quality Terraform Professional practice lab collection.

The final repository must provide labs that are:

* suitable for blind practice;
* reproducible;
* resettable;
* automatically verifiable;
* safe to run without unintended cloud cost;
* consistent across README, starter code, tests, fixtures, and validation scripts;
* explicit about anything that cannot be verified locally.

This is not a simple cleanup task.

Do not assume the existing README files, Terraform configurations, tests, or success criteria are correct. Treat the current repository as input material that must be audited and improved.

The detailed repository design and migration plan are stored in:

```text
docs/refactor-master-plan.md
```

Read that file before making architectural or lab-structure decisions.

---

## Required context before every task

Before changing any files, inspect:

```text
AGENTS.md
docs/refactor-master-plan.md
docs/audit-report.md
docs/lab-matrix.csv
docs/lab-standard.md
docs/migration-report.md
```

Some of these files may not exist during the earliest phases.

Also inspect:

```bash
git status
git branch --show-current
git log -5 --oneline
```

For every lab included in the current task, read all relevant:

* README files;
* Terraform files;
* modules;
* Terraform test files;
* fixtures;
* backend configuration;
* scripts;
* JSON and CSV input files;
* manifests.

Do not rely on memory from an earlier task or conversation. The repository contents and Git history are the source of truth.

---

## Task scope

The current user prompt defines the active phase and allowed scope.

The current-phase prompt takes priority over broader future work described in the master plan.

Only modify files required for the current phase.

Do not:

* start the next phase automatically;
* modify labs outside the current phase;
* perform unrelated cleanup;
* redesign a frozen standard without a concrete defect;
* extend the task because another issue was noticed.

When an out-of-scope issue is found, record it in the appropriate audit or migration document and leave the code unchanged.

Stop after the current phase is complete.

---

## General working rules

Use this sequence for each phase:

1. Inspect the current repository state.
2. Confirm the exact files and labs in scope.
3. Produce a brief implementation plan.
4. Establish or verify the canonical solution.
5. Create or correct the starter.
6. Implement meaningful validation.
7. Verify the starter fails for the intended reason.
8. Verify the solution passes.
9. Verify reset and repeatability.
10. Update repository documentation.
11. Review the final diff.
12. Stop.

Do not claim a command passed unless it was actually executed and its result was inspected.

When a command cannot be executed, record:

```text
NOT VERIFIED
```

Include the exact reason.

Do not fabricate successful Terraform plans, state transitions, tests, provider behavior, or cloud results.

---

## Starter principles

A starter must be a genuine exercise starting point, not a lightly edited solution.

The starter should preserve enough structure for the learner to understand the scenario while withholding the core implementation.

Appropriate starter techniques include:

* removing a required block;
* leaving a meaningful but incorrect implementation;
* retaining an old configuration that requires refactoring;
* removing part of an expression;
* omitting required behavior;
* providing an incomplete test;
* retaining a stable scaffold around the target skill.

Do not leave the canonical solution in the starter.

Do not leak complete answers through:

* comments;
* TODO text;
* test names;
* fixture names;
* outputs;
* README hints;
* disabled code;
* commented-out solution blocks.

Acceptable:

```hcl
# TODO: Produce a stable map suitable for for_each.
```

Not acceptable:

```hcl
# TODO: Use:
# { for name, cfg in var.items : name => cfg if cfg.enabled }
```

Unless syntax debugging is the topic, prefer starters that pass:

```bash
terraform fmt -check
terraform init -backend=false
terraform validate
```

The starter should then fail at the plan, test, state, or scenario-verification stage because the required behavior has not been implemented.

The failure must be:

* deterministic;
* relevant to the learning objective;
* easy to identify;
* unrelated to missing credentials, random external state, or invalid placeholder names.

---

## Canonical solution principles

Do not automatically treat the current repository code as the correct solution.

Reconstruct and verify the canonical solution from:

* the intended topic;
* Terraform semantics;
* the lab scenario;
* the expected behavior;
* meaningful tests.

A canonical solution must:

* match the README tasks;
* use valid and maintainable Terraform;
* avoid unnecessary complexity;
* avoid hardcoded credentials;
* avoid unknown external dependencies;
* avoid relying on accidental provider behavior;
* pass all applicable validation;
* preserve resource identity in refactor labs;
* avoid secret exposure;
* use correct provider and Terraform version constraints;
* demonstrate the intended exam skill rather than merely satisfy a weak test.

Do not weaken the intended implementation to make validation easier.

---

## Validation rules

Use validation appropriate to the lab type.

Possible commands include:

```bash
terraform fmt -check -recursive
terraform init -backend=false
terraform validate
terraform test
terraform plan
terraform show -json
terraform state list
terraform providers
terraform workspace show
```

Use repository tooling when available:

```bash
python tools/labctl.py list
python tools/labctl.py status <lab-id>
python tools/labctl.py reset <lab-id>
python tools/labctl.py check <lab-id>
python tools/labctl.py check --all
```

Every migrated lab must have two distinct gates.

### Starter gate

The starter must fail:

* at the expected stage;
* for the expected reason;
* on the intended test or rule.

A failure caused only by unavailable networking, missing cloud credentials, or provider installation does not prove the starter is correct.

### Solution gate

The canonical solution must pass every applicable check:

* formatting;
* initialization;
* validation;
* Terraform tests;
* plan inspection;
* state inspection;
* conceptual scoring;
* reset and rerun.

For state and refactor labs, also verify that no unintended destroy/create operation occurs.

---

## Test quality

Tests must verify behavior, not merely file presence or output existence.

Avoid using only weak checks such as:

```hcl
output.value != null
can(output.value)
```

Meaningful tests may verify:

* resource count;
* resource addresses;
* stable `for_each` keys;
* filtering behavior;
* map and list shape;
* exact selected values;
* merged tag precedence;
* lifecycle behavior;
* replacement behavior;
* provider alias mapping;
* module input and output wiring;
* expected validation failures;
* expected precondition failures;
* sensitive metadata;
* state movement;
* absence of unintended destroy/create actions;
* backend configuration rules;
* workspace isolation;
* sequential Terraform test behavior.

Where appropriate, cover:

1. a normal case;
2. a boundary case;
3. a failure case;
4. a state or refactor case.

Do not remove, bypass, or weaken a test merely to make a solution pass.

If an existing test is incorrect, replace it with a stronger test and document the reason.

---

## Cloud safety

Do not execute a real AWS, Azure, HCP Terraform, or other cloud apply unless the current phase explicitly requires it and the user has explicitly authorized it.

Default lab execution must not:

* create billable cloud resources;
* require long-lived credentials;
* depend on resources that happen to exist in an account;
* use real secrets;
* expose account identifiers;
* leave infrastructure running.

Prefer:

* local Terraform behavior;
* `terraform_data`;
* deterministic fixtures;
* local state;
* mock providers;
* plan-only validation;
* static backend checks.

When a live-cloud path is retained, it must be optional and clearly document:

* prerequisites;
* expected cost;
* execution commands;
* cleanup commands;
* known risks.

Do not make live-cloud execution part of normal pull request validation.

---

## State and refactor labs

State-related labs must be reproducible.

Do not rely only on statements such as:

```text
Assume the resource already exists.
```

Use a repeatable structure such as:

```text
bootstrap/
fixtures/
old configuration
starter configuration
canonical solution
reset process
```

A state or refactor lab should verify, where applicable:

* the original resource address;
* the target resource address;
* imported state;
* moved block mapping;
* removed block behavior;
* count-index to `for_each` key mapping;
* module address changes;
* final state contents;
* absence of unintended replacement;
* final no-op plan;
* successful reset and second run.

Do not delete the state merely to make a refactor plan appear clean.

Do not fake a no-op plan.

Use isolated state directories so one lab cannot modify another lab or the user's unrelated Terraform state.

---

## Backend and remote-state labs

Clearly separate:

* backend configuration;
* provider configuration;
* normal input variables;
* producer state;
* consumer configuration;
* environment-specific initialization values.

Do not use Terraform input variables inside backend blocks.

Prefer local fixtures for default validation.

Example backend files must:

* use placeholder values;
* contain no credentials;
* contain no real account resources;
* clearly indicate that they are examples.

Backend initialization metadata must be removed during reset.

---

## HCP Terraform and conceptual labs

Do not represent conceptual decision-making exercises as meaningless Terraform locals and outputs.

Use scenario-oriented files such as:

```text
SCENARIO.md
QUESTIONS.md
student-answer.md
rubric.yaml
```

Keep canonical answers isolated from the starter.

Scoring should evaluate important decisions and reasoning, such as:

* VCS-driven versus API-driven runs;
* speculative plans;
* run triggers;
* policy enforcement modes;
* cost estimation;
* team permissions;
* auto-apply;
* production approval boundaries.

Do not require exact full-text matching when a structured rubric is more appropriate.

---

## Provider and version-constraint labs

Version-constraint labs must genuinely exercise:

```hcl
terraform {
  required_version = "..."

  required_providers {
    provider_name = {
      source  = "..."
      version = "..."
    }
  }
}
```

Do not mix in unrelated copied validation, lifecycle, or environment examples.

Verify the actual meaning of operators such as:

```text
=
!=
>=
<=
~
~>
```

Do not consider `terraform validate` alone sufficient to prove that a constraint strategy is correct.

---

## Documentation rules

Each migrated lab must have documentation consistent with the actual implementation.

A lab README should clearly describe:

* title;
* scenario;
* skills tested;
* difficulty;
* estimated time;
* execution mode;
* cloud requirement;
* cost risk;
* starting state;
* editable files;
* protected files;
* tasks;
* constraints;
* expected initial failure;
* validation commands;
* success criteria;
* reset instructions;
* limited hints.

Success criteria must be specific to the lab.

Do not retain copied criteria about validation, preconditions, checks, or tests unless they are genuinely part of that lab.

Commands in the README must match the real workflow.

For example, a Terraform Test lab must explicitly use:

```bash
terraform test
```

Update these files after each migration phase:

```text
docs/lab-matrix.csv
docs/migration-report.md
```

Update `docs/audit-report.md` when earlier audit findings are proven incorrect or incomplete.

Change `docs/lab-standard.md` only when an actual standard defect is identified. Record:

* the change;
* the reason;
* affected labs;
* required remediation.

---

## Git rules

Do not:

* rewrite upstream history;
* force-push;
* delete user work;
* modify unrelated branches;
* commit credentials;
* commit generated cloud secrets;
* hide large unrelated changes in one commit.

Before editing, inspect the current branch and worktree.

Do not overwrite uncommitted user changes.

If unrelated uncommitted changes exist, preserve them and avoid modifying the same files unless the current task explicitly requires it.

Use focused commits when commits are requested.

Suitable commit scopes include:

```text
chore(audit)
refactor(lab-01)
refactor(labs-02-05)
test(state-labs)
docs(hcp-labs)
ci(terraform-labs)
```

Do not create commits or push unless the current task explicitly requests it.

---

## Repository tools

Prefer portable tooling.

Repository-level commands should work on both:

* Linux;
* Windows.

Do not rely exclusively on Bash when the same operation can be implemented in Python.

Use safe subprocess handling, explicit exit codes, and clear error messages.

Reset commands must remove only lab-owned artifacts such as:

```text
.terraform/
terraform.tfstate
terraform.tfstate.backup
*.tfplan
generated fixtures
temporary backend metadata
temporary workspaces created by the lab
```

Reset must not delete unrelated user files or global Terraform configuration.

---

## Final review for each phase

Before finishing a phase, inspect:

```bash
git status
git diff --stat
git diff
```

Confirm:

* only in-scope files changed;
* no solution leaked into starter;
* no credentials were added;
* no test was weakened without justification;
* documentation matches actual results;
* all PASS claims were executed;
* all unverified items are marked `NOT VERIFIED`;
* the next phase has not been started.

The final response for each phase must include:

* files changed;
* labs changed;
* commands executed;
* starter-gate results;
* solution-gate results;
* reset results;
* items not verified;
* remaining risks.

After reporting the current phase, stop.
