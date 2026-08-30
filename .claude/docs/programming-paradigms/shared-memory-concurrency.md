# Shared-Memory Concurrency Selection Profile

- **Trigger:** multiple execution contexts access a shared mutable invariant, publish state across
  threads, coordinate lifetime/reclamation, or make a synchronization/coherence-sensitive scaling
  claim that partitioned single-owner data cannot close.
- **Non-trigger:** immutable snapshots, disjoint owner-exclusive ranges with an explicit commit and
  no remaining visibility/reclamation/coherence claim, single-threaded work, or message-addressed
  state whose one owner performs every mutation.
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
