# Protected sensitive-value checks

`scripts/verify_sensitive.py` injects a clearly synthetic runtime probe only inside a temporary directory. It checks that the password has no default, verifies exact applied secret-bearing values without printing them, validates sensitivity metadata and safe diagnostics, rejects unsafe extra outputs, and confirms plan/apply CLI redaction.
