# Lab 25 - HCP Terraform Operations Decisions

## Scenario

Northstar runs production infrastructure through HCP Terraform. Read `starter/SCENARIO.md`, then choose an operating model for source-driven runs, exceptional automation, pull-request plans, workspace dependencies, governance, permissions, and production approvals.

This is a conceptual decision lab. It contains no Terraform configuration and does not contact HCP Terraform.

## Skills tested

- Distinguishing VCS-driven and API-driven runs
- Using speculative plans for pull-request feedback
- Directing run triggers between dependent workspaces
- Selecting production policy enforcement and interpreting cost estimates
- Separating plan, apply, and administrative permissions
- Defining auto-apply and production approval boundaries

## Difficulty and estimated time

- Difficulty: hard
- Estimated time: 30 minutes

## Execution mode

- Mode: local conceptual scoring
- Terraform CLI: not used

## Cloud credentials required

No. The lab does not require HCP Terraform, AWS, or other cloud credentials.

## Cost risk

None. Validation reads local Markdown and rubric files only.

## Starting state

`starter/student-answer.md` contains eight `undecided` choices and placeholder rationale prompts. The public rubric describes what is scored but contains no canonical choices.

## Files allowed to edit

- `starter/student-answer.md`

## Files not allowed to edit

- `starter/SCENARIO.md`
- `starter/QUESTIONS.md`
- `rubric.yaml`
- `scripts/score_answer.py`
- `lab.yaml`

## Tasks

1. Read the scenario and all option definitions.
2. Replace every `undecided` value with exactly one option ID from the corresponding question.
3. Write a concise rationale under every matching decision heading.
4. Keep all decision IDs and Markdown headings unchanged so the scorer can locate them.

## Constraints

- Make one decision for every question; do not combine multiple option IDs.
- Base the design on least privilege and an explicit production approval boundary.
- Treat cost estimation as operational evidence, not as a complete billing guarantee.
- Do not add Terraform, provider, token, organization, or workspace credentials.

## Expected initial failure

From the repository root, the unmodified starter fails the scoring stage with `EXPECTED_CONCEPTUAL_RESPONSE_INCOMPLETE` because decisions and rationales are intentionally blank.

## Validation commands

Run the repository gate from the repository root:

```bash
python tools/labctl.py check 25
```

To invoke the scorer directly:

```bash
python labs/25-hcp-terraform-ops-broken/scripts/score_answer.py --rubric labs/25-hcp-terraform-ops-broken/rubric.yaml --answer labs/25-hcp-terraform-ops-broken/starter/student-answer.md
```

## Success criteria

- All eight operating decisions use valid option IDs.
- The choices correctly distinguish routine VCS runs from exceptional API automation.
- Pull requests use a non-applicable plan path.
- Workspace dependency direction follows producer-to-consumer apply success.
- Production policy, permissions, and auto-apply choices preserve an approval boundary.
- Cost-estimation limitations are acknowledged.
- Every decision has a substantive rationale and the score meets the published threshold.

## Reset instructions

```bash
python tools/labctl.py reset 25
```

Reset removes only recorded validation results. It deliberately preserves `student-answer.md`. To discard your own answer, use your version-control workflow explicitly.

## Limited hints

- A plan that cannot apply is useful before merge.
- A dependency trigger points from the workspace that successfully applied to the workspace that consumes its results.
- Permission to propose a run does not have to imply permission to apply it.

## Official references

- [Run modes and options](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/run/modes-and-options)
- [Run triggers](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/settings/run-triggers)
- [Workspace permissions](https://developer.hashicorp.com/terraform/cloud-docs/users-teams-organizations/permissions/workspace)
- [Workspace settings](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/settings)
