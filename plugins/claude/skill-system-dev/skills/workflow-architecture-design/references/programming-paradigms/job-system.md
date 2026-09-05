# Job System Selection Profile

- **Trigger:** CPU work genuinely needs graph-shaped dependencies, completion scope,
  cancellation/error propagation, load balancing, or resource-access coordination beyond one
  asynchronous callback.
- **Non-trigger:** one background callback, blocking I/O/external waits, tiny/sequential work, or
  mutable aliasing that cannot be safely partitioned or ordered.
- **Minimum closure:** representative total-work/span and critical-path pressure,
  domain/logical/grain separation, sequentially callable kernels, distinct dependency/completion
  semantics, admission-before-execution, exactly-once terminal accounting and close/admission
  coordination supplied by an existing sufficient scope or an explicit custom protocol,
  lifecycle/shutdown, safe read/write or reduction rules, and validated result publication/commit.
  Completion and external/worker wait policy must preserve forward progress and account for helping
  or suspension re-entry, held resources, and temporary invariants. When tasks may migrate, TLS or
  thread-owned resources require their actual OS-thread guarantee; a serial lane is not that
  guarantee, and affinity alone does not close re-entry safety.
- **Maximum scope:** ready-work scheduling. Domain grain, fallback/numerical policy, resource
  meaning, data layout, I/O runtime, and GPU/actor semantics stay with their owners.
- **Interactions:** DOD supplies ranges/access sets. Check cross-thread visibility and last-consumer
  reclamation even for disjoint ranges; reuse documented runtime completion guarantees and apply
  Shared-Memory Concurrency only for material coordination obligations that remain. Structured Async
  owns external waits and suspended-operation lifetime,
  functional/procedural code supplies kernels, object/session owners supply lifetime and commit,
  pipeline owners supply bounded in-flight/version/reclamation and end-to-end latency policy, and
  TMP may specialize only bounded kernels.
- **Proof ceiling:** DAG/API shape or high worker utilization proves representability only, not a
  critical-path deadline, end-to-end latency, deadlock freedom, starvation, cancellation behavior,
  determinism, scaling, or scheduler cost without operational observation.

Implementation details and actual-path verification remain with the matching
`workflow-implementation` method profile.
