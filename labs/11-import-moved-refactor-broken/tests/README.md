# Protected state verification

The executable verifier is `../scripts/verify_refactor.py`. It runs the import and refactor configurations in order against one isolated learner state, inspects Terraform plan JSON and state addresses, and proves the final plan is a no-op.
