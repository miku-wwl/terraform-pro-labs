# Protected verification contract

The verifier creates independent dev and prod producer states, points a copied consumer at each
state, and inspects exact outputs, state addresses, plan actions, and the final no-op plan. It also
checks that consumer backend initialization fields stay outside the static backend block.
