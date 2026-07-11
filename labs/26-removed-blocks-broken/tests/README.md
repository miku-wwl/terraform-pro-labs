# Protected verification contract

The seed retains both old resources in real isolated state. Plan JSON must show the service rename
as one no-op move with `previous_address`, while the attachment must have the exact `forget` action
caused by `removed` with `destroy = false`. Create and delete actions are rejected.
