# Protected sensitive-value checks

`scripts/verify_sensitive.py` injects a clearly synthetic runtime probe only inside a temporary directory. It checks variable and output sensitivity metadata, exact safe diagnostics, the absence of unsafe extra outputs, and CLI redaction without printing the probe.
