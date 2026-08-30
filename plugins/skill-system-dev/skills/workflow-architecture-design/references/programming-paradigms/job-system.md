# Job System Selection Profile

- **Trigger:** CPU work genuinely needs graph-shaped dependencies, completion scope,
  cancellation/error propagation, load balancing, or resource-access coordination beyond one
  asynchronous callback.
- **Non-trigger:** one background callback, blocking I/O/external waits, tiny/sequential work, or
  mutable aliasing that cannot be safely partitioned or ordered.
- **Minimum closure:** representative total-work/span and critical-path pressure,
  domain/logical/grain separation, sequentially callable kernels, distinct dependency/completion
  semantics, lifecycle/shutdown, safe read/write or reduction rules, completion composition that
  does not occupy a worker needed for forward progress, an explicit external/worker wait policy,
  and validated result publication/commit; when tasks may migrate, thread-affine or TLS
  dependencies also need an explicit execution-lane contract or task-local alternative.
- **Maximum scope:** ready-work scheduling. Domain grain, fallback/numerical policy, resource
  meaning, data layout, I/O runtime, and GPU/actor semantics stay with their owners.
- **Interactions:** DOD supplies ranges/access sets, Shared-Memory Concurrency supplies visibility
  and reclamation rules, Structured Async owns external waits and suspended-operation lifetime,
  functional/procedural code supplies kernels, object/session owners supply lifetime and commit,
  pipeline owners supply bounded in-flight/version/reclamation and end-to-end latency policy, and
  TMP may specialize only bounded kernels.
- **Proof ceiling:** DAG/API shape or high worker utilization proves representability only, not a
  critical-path deadline, end-to-end latency, deadlock freedom, starvation, cancellation behavior,
  determinism, scaling, or scheduler cost without operational observation.

Implementation details and actual-path verification remain with the matching
`workflow-implementation` method profile.
