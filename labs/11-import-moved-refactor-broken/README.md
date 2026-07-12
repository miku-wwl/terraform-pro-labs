# Lab 11 — Import, Moved Blocks, and Module Refactor

## Scenario

An identifier was created by an old Terraform configuration and then released from its bootstrap state. Adopt that identity into a new learner state at its old root address. After proving the import, refactor the resource into the supplied child module without changing its identity or scheduling replacement.

Import and refactor are deliberately separate stages. This avoids combining an import target and a moved source in one configuration transition.

## Skills tested

- Seeding and inspecting isolated Terraform state
- Declarative import into an exact resource address
- Moving a root resource address into a child module
- Reading plan JSON and state addresses during a refactor
- Proving identity continuity and a final no-op plan

## Difficulty and estimated time

- Difficulty: hard
- Estimated time: 35 minutes

## Execution mode

- Mode: local state-refactor workflow
- Backend: lab-owned local state under `.lab-state/`
- Provider: HashiCorp `random`, a logical provider with no remote service

## Cloud credentials required

No. The workflow does not configure AWS or read any cloud credentials.

## Cost risk

None. The seed and learner workflows operate only on local Terraform state.

## Starting state

Run reset and seed before each attempt. The seed command copies `bootstrap/old-config` into the ignored `.lab-state/` work area, applies it, verifies the old address `random_id.legacy_record`, captures its import identifier, and removes that binding from bootstrap state. The identity is then ready for the learner's isolated import state.

The learner workflow has two ordered configurations:

1. `starter/import-stage` adopts the identity at the old root address.
2. `starter/refactor-stage` changes the configuration shape to the supplied module.

The protected verifier uses one state across both stages.

## Files allowed to edit

- `starter/import-stage/main.tf`
- `starter/refactor-stage/main.tf`

## Files not allowed to edit

- `lab.yaml`
- `bootstrap/old-config/`
- `starter/import-stage/versions.tf`
- `starter/refactor-stage/versions.tf`
- `starter/modules/`
- `scripts/`

## Tasks

1. Reset and seed the lab, then inspect the old resource address printed by the seed workflow.
2. In the import-stage configuration, declaratively adopt the generated identifier at the existing root resource address. Use the supplied `import_id` variable; do not hardcode a generated value.
3. Run the solution-mode check and confirm the imported state contains only the old root address before it proceeds to the refactor gate.
4. In the refactor-stage configuration, preserve that state identity while moving the resource into the supplied child module.
5. Run the complete check and confirm the target module address, zero create/delete actions, unchanged identifier, and final no-op plan.

## Constraints

- Complete the declarative import before the module refactor.
- Use configuration-driven address migration for the refactor; do not substitute an imperative `terraform state mv` command.
- Do not change resource type, byte length, module/resource names, or protected verifier files.
- Do not hardcode the generated identifier or copy state files between stages.
- Do not add AWS or any other cloud provider.

## Expected initial failure

After seeding, `python tools/labctl.py check 11` reaches the behavioral state gate and reports `EXPECTED_STATE_REFACTOR_INCOMPLETE`. Initially the import stage proposes creating a new identity instead of adopting the seeded one. Once import is corrected, the same gate continues into the refactor stage and rejects any root-to-module delete/create plan.

## Validation commands

From the repository root:

```text
python tools/labctl.py reset 11
python tools/labctl.py seed 11
python tools/labctl.py status 11
python tools/labctl.py check 11
python tools/labctl.py check 11 --mode solution
```

The plain check proves the untouched starter fails for the expected reason. After editing both allowed files, use `--mode solution` for the passing gate. Both modes format all Lab 11 Terraform files; the verifier initializes and validates each stage in an isolated work directory, applies only the local logical resource, inspects saved plan JSON, lists state addresses, and runs a final detailed-exitcode plan.

## Success criteria

- Seed establishes and reports `random_id.legacy_record` before releasing its state binding.
- The import plan reports one import and zero add/destroy actions.
- Imported state contains exactly `random_id.legacy_record` and its identifier matches the fixture.
- The refactor plan records an exact move to `module.record.random_id.this` with zero add/destroy actions.
- Final state contains exactly the module address and preserves the imported identifier.
- A subsequent plan reports `0 to add, 0 to change, 0 to destroy`.
- Reset removes `.lab-state/`, including its state, plans, fixture, and nested `.terraform/` data.

## Reset instructions

From the repository root:

```text
python tools/labctl.py reset 11
```

Reset removes only Lab 11 generated artifacts and recorded check results. It preserves both learner-editable configuration files.

## Limited hints

- The first stage is about associating a supplied identifier with an existing configuration address, not generating a replacement.
- The second stage changes only the address. Terraform needs an explicit record of the old and new addresses to distinguish a move from delete/create.
