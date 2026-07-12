# Protected verification contract

The verifier creates only the declared dev, staging, and prod workspaces in a runtime copy. It
checks each workspace's exact state address and settings, rejects destroy actions, requires final
no-op plans, accepts every approved production size, rejects two undersized sizes and one
unapproved non-small family, and proves the independent auto-approve guardrail.
