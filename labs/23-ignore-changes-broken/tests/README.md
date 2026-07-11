# Protected drift behavior

`scripts/verify_drift_boundary.py` creates temporary local state, injects controlled permission-only and content-only state drift, and checks both resulting plan action sets without refreshing away the fixtures.
