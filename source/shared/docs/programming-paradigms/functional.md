# Functional Selection Profile

- **Trigger:** deterministic value transformation, reducer/state transition, replay, undo,
  memoization, scheduling, or effect isolation is the governing property.
- **Non-trigger:** long-lived identity, resource lifetime, event addressing, or unavoidable effect
  ownership is the whole problem.
- **Minimum closure:** explicit semantic inputs/outputs/errors, named state transition, isolated
  effects, and no hidden semantic mutable input; bounded internal mutation may remain private.
- **Maximum scope:** the observable value/effect boundary; resource, UI, storage, plugin, and commit
  ownership stay in an imperative/object shell.
- **Interactions:** procedural loops, data-oriented arrays, Job scheduling, object shells, and TMP
  static facts may implement distinct properties.
- **Proof ceiling:** a pure-looking signature or immutable syntax does not prove absence of hidden
  effects, determinism, allocation cost, or reduction-order stability.

Implementation details and actual-path verification remain with the matching
`workflow-implementation` method profile.
