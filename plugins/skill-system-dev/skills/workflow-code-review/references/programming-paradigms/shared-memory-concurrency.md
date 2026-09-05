# Shared-Memory Concurrency Selection Profile

- **Trigger:** multiple execution contexts leave a material shared-invariant, cross-thread
  publication/visibility, lifetime/reclamation, or synchronization/coherence-sensitive scaling
  obligation unresolved by the existing owner and language/runtime contract. Non-overlapping writes
  and immutable values do not by themselves close transfer visibility or last-reader lifetime.
- **Non-trigger:** single-threaded work, or immutable snapshots, disjoint owner-exclusive ranges,
  and message-addressed state whose actual transfer, visibility, and last-consumer reclamation are
  already closed by the existing owner/runtime contract with no other material invariant,
  progress, or coherence obligation remaining. Reuse a documented completion, join,
  future, or equivalent guarantee when it covers the actual edge; add no profile or lock merely
  because another thread consumes the result.
- **Minimum closure:** authoritative state owner and invariant, read/write and alias sets,
  synchronization plus language-level happens-before/visibility, atomicity versus ordering, lock
  scope and wait policy, publication and reclamation including stale handles/ABA where applicable,
  failure/cancellation/shutdown cleanup, progress/fairness requirement, deterministic reduction
  order when required, and cache-line ownership when multicore performance is claimed.
- **Maximum scope:** shared-memory coordination and visibility. It does not acquire domain meaning,
  CPU task scheduling, async operation lifetime, data-layout selection, or platform-specific memory
  model rules beyond the selected language/runtime authority.
- **Interactions:** DOD supplies partitions and locality-sensitive ranges; Job Systems schedule
  ready CPU work; Structured Async owns suspended operation lifetime; object/resource owners supply
  canonical lifetime and commit; the language memory model remains normative for ordering.
- **Proof ceiling:** locks, atomics, concurrent containers, annotations, and type shape prove only
  their local mechanism. They do not prove whole-invariant race freedom, deadlock/starvation
  freedom, linearizability, safe reclamation, determinism, fairness, or scaling. A source-permitted
  bad interleaving can disprove correctness; progress and performance require matching runtime
  evidence.

Implementation details and actual-path verification remain with the matching
`workflow-implementation` method profile.
