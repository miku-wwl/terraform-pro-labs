# Protected verification

The executable lifecycle verifier is in `../scripts/verify_prevent_destroy.py`. It creates isolated temporary state, requests a destroy plan, and checks the resulting lifecycle diagnostic. This directory is protected so future public Terraform tests can be added without changing the learner's working directory.
