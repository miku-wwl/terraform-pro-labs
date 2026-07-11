# Protected lifecycle behavior

`scripts/verify_replacement.py` creates temporary local state at release `v1`, plans release `v2`, and inspects the JSON action order for `terraform_data.service`.
