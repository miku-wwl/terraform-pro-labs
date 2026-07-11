# Lab 15 - Conditional S3 Versioning, Lifecycle, Tags, and Outputs

## Scenario

An application portfolio defines S3 buckets by logical name. The current configuration creates optional resources for every bucket, gives common tags the wrong precedence, and returns positional outputs. Correct the model without contacting AWS.

## Skills tested

- Stable resource identity with `for_each`
- Conditional versioning and lifecycle resources
- Layered tag merging and override precedence
- Map-shaped outputs
- AWS mock-provider tests

## Difficulty and estimated time

- Difficulty: medium
- Estimated time: 25 minutes

## Execution mode

AWS provider schema planning through Terraform's mock provider.

## Cloud credentials required

No. Tests do not authenticate or call AWS APIs.

## Cost risk

None. The workflow creates mocked plans only.

## Starting state

All buckets have versioning and lifecycle resources, missing retention is replaced by seven days, common tags overwrite bucket tags, and outputs are lists.

## Files allowed to edit

- `starter/main.tf`

## Files not allowed to edit

- `starter/versions.tf`
- `tests/`
- `scripts/`
- `lab.yaml`

## Tasks

1. Keep ordinary buckets keyed by every input map key.
2. Create versioning only where `versioning` is true.
3. Create lifecycle configuration only where `lifecycle_days` is set and retain the matching day value.
4. Merge common and bucket-specific tags so the bucket layer wins collisions.
5. Return exact keyed maps for bucket names, versioned buckets, and lifecycle retention.

## Constraints

- Preserve resource and output addresses.
- Do not hardcode the protected scenario keys.
- Do not introduce a real AWS plan or apply.
- Do not edit or weaken protected tests.

## Expected initial failure

`python tools/labctl.py check 15` reports `EXPECTED_S3_CONDITIONAL_CONFIGURATION_INCOMPLETE` after format, init, and validation pass.

## Validation commands

```text
python tools/labctl.py check 15
python tools/labctl.py status 15
```

## Success criteria

- Bucket keys exactly follow the input map.
- Only selected buckets receive enabled versioning and lifecycle resources.
- Lifecycle days remain paired with logical bucket keys.
- Bucket tags override common tags.
- All three outputs are exact maps, including empty conditional maps.
- Invalid non-positive retention is rejected without cloud access.

## Reset instructions

```text
python tools/labctl.py reset 15
```

## Limited hints

- Build separate collections for each optional behavior.
- Merge order determines which map wins a duplicate key.
