# Lab 09 - Security Groups with Independent Rule Resources

## Scenario

A security-group shell must manage ingress and egress exclusively through independent AWS rule resources. The starter declares those resource types, but creates no ingress instances and restricts egress to HTTPS instead of all IPv4 traffic.

## Skills tested

- Security-group shell resources without inline rules
- `aws_vpc_security_group_ingress_rule`
- `aws_vpc_security_group_egress_rule`
- Stable `for_each` keys and exact rule content

## Difficulty and estimated time

- Difficulty: easy
- Estimated time: 15 minutes

## Execution mode

`aws-mock`. A deterministic plan-only VPC ID is used; no real VPC lookup or AWS request occurs.

## Cloud credentials required

No.

## Cost risk

None.

## Starting state

The SG has no inline rules. The independent ingress resource iterates an empty map, and the egress resource has the wrong protocol boundary.

## Files allowed to edit

- `starter/main.tf`

## Files not allowed to edit

- `starter/versions.tf`
- `tests/`
- `scripts/`
- `lab.yaml`

## Tasks

1. Create one independent ingress rule per stable input key.
2. Preserve each rule's description, TCP port, CIDR, and SG reference.
3. Correct the independent egress rule to allow all IPv4 protocols.
4. Keep the SG shell free of inline ingress and egress blocks.
5. Support an empty ingress map safely.

## Constraints

- Do not add inline rule blocks to `aws_security_group.web`.
- Do not replace stable input keys with list indexes.
- Do not query a default VPC or use a real account resource.
- Do not edit protected tests.

## Expected initial failure

`python tools/labctl.py check 09` reports `EXPECTED_SEPARATE_SG_RULES_INCOMPLETE` because no ingress rules are created and egress is limited to TCP 443.

## Validation commands

```text
python tools/labctl.py check 09
python tools/labctl.py status 09
```

## Success criteria

- Default ingress resource keys are exactly `admin` and `web`.
- Each rule retains its exact port, CIDR, and security-group reference.
- The independent egress rule uses protocol `-1` and IPv4 CIDR `0.0.0.0/0`.
- Empty ingress creates no ingress resources while preserving egress.
- No inline rules, credentials, VPC lookup, or AWS API request are used.

## Reset instructions

```text
python tools/labctl.py reset 09
```

## Limited hints

- Use the map itself when resource identity already has meaningful keys.
- All-protocol egress does not use TCP port bounds.
