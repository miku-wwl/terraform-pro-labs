# Protected lifecycle behavior

`scripts/verify_replacement.py` creates temporary local state at release `v1`, proves unchanged
inputs are no-op, proves a name-only change remains an update, and then inspects exact create-delete
ordering for a release-only replacement. It also verifies the trigger remains scoped to `release`.
