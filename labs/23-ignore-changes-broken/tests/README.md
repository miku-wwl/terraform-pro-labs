# Protected drift behavior

`scripts/verify_drift_boundary.py` creates temporary local state, injects controlled permission-only, content-only, and filename-only state drift, and checks all resulting plan action sets without refreshing away the fixtures.
