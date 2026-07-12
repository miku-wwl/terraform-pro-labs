# Protected dependency replacement behavior

`scripts/verify_dependency_replacement.py` creates temporary local state, plans an upstream release-marker change and a direct service-name change separately, and inspects plan JSON actions, replacement reason, and the exact before/after service input ownership boundary.
