# Protected verification contract

The verifier creates only the declared dev, staging, and prod workspaces in a runtime copy. It
checks each workspace's exact state address and settings, rejects destroy actions, requires final
no-op plans, and proves both production guardrail branches.
