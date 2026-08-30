# Procedural Selection Profile

- **Trigger:** an ordered transformation, pipeline, state machine, C ABI/FFI/callback, or bounded
  one-shot operation is the governing property and no long-lived identity dominates.
- **Non-trigger:** shared invariants, identity, resource lifetime, or runtime substitution dominate.
- **Minimum closure:** explicit semantic inputs/outputs/failure, visible order, owned context or
  workspace, and visible mutation/effect/publication boundary.
- **Maximum scope:** the selected operation or pipeline; no ambient global state or absorption of
  identity-rich lifecycle owners.
- **Interactions:** functional public contract, data-oriented kernel, object/resource shell, or Job
  scheduling may own different axes.
- **Proof ceiling:** a flow contract proves intended order and ownership, not runtime correctness,
  allocation cost, or timing until the implementation path is observed.

Implementation details and actual-path verification remain with the matching
`workflow-implementation` method profile.
