# Protected dependency replacement behavior

`scripts/verify_dependency_replacement.py` creates temporary local state, plans an upstream release-marker change and a direct service-name change separately, and inspects plan JSON actions plus replacement reason.
