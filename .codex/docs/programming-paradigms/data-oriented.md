# Data-Oriented Selection Profile

- **Trigger:** a representative bulk path makes data movement, access order, branching, batching,
  SIMD/GPU transfer, memory traffic, or tail latency material.
- **Non-trigger:** small/irregular/identity-heavy work, a different dominant algorithm/I/O/lock
  bottleneck, layout translation or structural churn that dominates the representative traversal,
  or aesthetics alone; do not infer SoA or ECS from the label.
- **Minimum closure:** representative count/frequency/transformation/read-write evidence, selected
  layout and traversal, canonical data/identity owner, explicit views/ranges, and complete
  publication/commit; parallel shared writes also need partition/reduction semantics and, when
  multicore scaling is claimed, an explicit cache-line/coherence-sharing assumption.
- **Maximum scope:** the measured or intrinsically constrained hot compute snapshot/path; DOD does
  not acquire document identity, domain policy, or scheduler ownership.
- **Interactions:** identity-rich authoring/object/session owners supply snapshot, translation,
  version, and commit semantics; functional/procedural kernels supply transformations, Job Systems
  consume access ranges, Shared-Memory Concurrency owns visibility/coherence constraints, and
  bounded TMP may specialize layouts.
- **Proof ceiling:** layout structure proves representation only. Disjoint logical ranges do not
  prove absence of false sharing, and race freedom does not prove reduction-order or floating-point
  determinism. Performance requires the same representative workload and metric before/after.

Implementation details and actual-path verification remain with the matching
`workflow-implementation` method profile.
