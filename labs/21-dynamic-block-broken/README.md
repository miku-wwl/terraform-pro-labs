# Lab 21 - Dynamic Nested Ingress Blocks

## Scenario

A security group currently repeats two static ingress blocks even though ingress policy is supplied as structured input. Replace the duplication with input-driven nested blocks that work for any valid rule list.

## Skills tested

- `dynamic` nested blocks and iterator scope
- The distinction between resource `for_each` and nested-block repetition
- Preserving object content in provider schema blocks
- Terraform mock-provider tests

## Difficulty and estimated time

- Difficulty: medium
- Estimated time: 20 minutes

## Execution mode

AWS provider schema planning through Terraform's mock provider. No AWS API call is made.

## Cloud credentials required

No.

## Cost risk

None. Tests only create mocked plans.

## Starting state

The input type and validation are present, but the resource contains two hardcoded ingress blocks and therefore ignores alternate rule collections.

## Files allowed to edit

- `starter/main.tf`

## Files not allowed to edit

- `starter/versions.tf`
- `tests/`
- `scripts/`
- `lab.yaml`

## Tasks

1. Replace the repeated static ingress blocks with one dynamic nested-block construct.
2. Drive its repetition from `var.ingress_rules`.
3. Preserve each rule's description, port, and CIDR in the generated provider block.
4. Keep the fixed outbound rule and port validation intact.

## Constraints

- Do not create multiple security-group resources.
- Do not retain static ingress blocks.
- Do not hardcode the protected alternate test values.
- Do not remove or edit lifecycle-independent protected tests.

## Expected initial failure

`python tools/labctl.py check 21` reports `EXPECTED_DYNAMIC_BLOCK_INCOMPLETE` because an alternate three-rule input still renders the two hardcoded blocks.

## Validation commands

```text
python tools/labctl.py check 21
python tools/labctl.py status 21
```

## Success criteria

- Default input renders exactly two matching ingress blocks.
- Alternate input renders exactly three blocks with exact descriptions, ports, and CIDRs.
- The fixed outbound boundary remains exactly one all-protocol egress rule to `0.0.0.0/0`.
- Invalid ports are rejected.
- The source uses a dynamic ingress construct and contains no static ingress duplication.
- Validation performs no AWS authentication or API operation.

## Reset instructions

```text
python tools/labctl.py reset 21
```

## Limited hints

- A dynamic block has a collection expression, an iterator, and a content body.
- Values inside the content body come from the current iterator element.
