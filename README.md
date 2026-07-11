# Terraform Professional Practice Labs

This repository contains 32 deterministic, resettable Terraform Professional practice labs. Every
lab is a learner-facing starter with a manifest, an expected-failure gate, protected verification,
and a credential-free default workflow. Canonical answers are intentionally kept off this branch.

From the repository root:

```text
python tools/labctl.py list
python tools/repo_check.py
python tools/labctl.py check --all
```

Use each lab README for the scenario, editable files, expected initial failure, success criteria,
and reset workflow. The aggregate check treats each documented starter failure as a passing gate.
Default validation requires no cloud credentials and creates no billable resources; AWS-focused
labs use provider mocks or offline fixtures.

The source project is attributed to
[`lance0821/tfpro-labs`](https://github.com/lance0821/tfpro-labs). The existing Apache License 2.0
is preserved in `LICENSE`; provenance and any applicable NOTICE obligations should still be
confirmed before redistribution.
