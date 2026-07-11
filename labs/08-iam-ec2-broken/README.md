# Lab 08 - IAM Role-to-EC2 Dependency Chain

## Scenario

An application instance needs an EC2 trust policy, managed permissions policy, role attachment, instance profile, and EC2 profile reference. The starter creates every object but breaks two links in that chain.

## Skills tested

- IAM trust and permission policy structure
- Managed policy attachment to a role
- IAM role to instance-profile wiring
- EC2 instance-profile integration
- AWS mock-provider graph testing

## Difficulty and estimated time

- Difficulty: medium
- Estimated time: 20 minutes

## Execution mode

`aws-mock`. The configuration uses a deterministic plan-only AMI ID and never queries or applies to AWS.

## Cloud credentials required

No.

## Cost risk

None; no real EC2 or IAM object is created.

## Starting state

Trust and permission documents are deterministic. The policy attachment targets a different role name, and the EC2 instance does not reference the instance profile.

## Files allowed to edit

- `starter/main.tf`

## Files not allowed to edit

- `starter/versions.tf`
- `tests/`
- `scripts/`
- `lab.yaml`

## Tasks

1. Preserve the EC2 trust relationship and scoped S3 permission document.
2. Attach the managed policy to the declared application role.
3. Preserve the role-to-instance-profile reference.
4. Connect the EC2 instance to that instance profile.
5. Keep all names driven by `name_prefix`.

## Constraints

- Do not introduce an AMI, VPC, subnet, or account data lookup.
- Do not replace references with repeated hardcoded names.
- Do not add credentials or perform a real apply.
- Do not edit protected tests.

## Expected initial failure

`python tools/labctl.py check 08` reports `EXPECTED_IAM_EC2_CHAIN_INCOMPLETE` because the attachment and instance-profile links do not form a complete dependency chain.

## Validation commands

```text
python tools/labctl.py check 08
python tools/labctl.py status 08
```

## Success criteria

- The trust policy permits `ec2.amazonaws.com` to call `sts:AssumeRole`.
- The managed policy has the exact S3 actions and two resource scopes.
- Policy attachment, role, profile, and EC2 use direct Terraform references.
- Alternate prefixes flow through every named object.
- No AWS credentials, lookup, or API call is used.

## Reset instructions

```text
python tools/labctl.py reset 08
```

## Limited hints

- The instance profile is the bridge between an IAM role and EC2.
- Referencing an upstream resource attribute also creates the graph dependency.
