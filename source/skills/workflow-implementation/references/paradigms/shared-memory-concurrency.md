# Shared-Memory Concurrency Implementation

Cross-stage selection authority lives in
`references/programming-paradigms/shared-memory-concurrency.md`. This file owns concrete
realization and actual-path verification; it may narrow implementation admission from production
evidence but never broadens the accepted trigger or scope.

Shared-memory concurrency begins with one mutable invariant observed or changed by several
execution contexts. Select the smallest coordination mechanism that preserves ownership,
visibility, lifetime, and required progress. Do not start from a preferred lock, atomic primitive,
or lock-free container.

## Distinguish The Properties

| Property | Question |
| --- | --- |
| ownership | who alone may mutate or publish the state now? |
| atomicity | which transition must not be observed partially? |
| ordering/visibility | which writes must another participant observe before which reads? |
| lifetime/reclamation | when can an address, handle, or version no longer be observed? |
| progress/fairness | can ready work eventually proceed without deadlock, livelock, or starvation? |
| determinism | must schedule, logical order, numerical result, or bits be reproducible? |
| performance | is cost caused by waiting, spinning, retry, coherence traffic, bandwidth, or migration? |

One atomic read-modify-write can close one-location atomicity without closing a multi-field
invariant, publication order, reclamation, progress, or determinism.

## Ownership Before Synchronization

Prefer these shapes in order of conceptual sufficiency, not as a universal performance ranking:

1. immutable snapshot or value passed to readers;
2. owner-exclusive or disjoint writable ranges followed by one commit;
3. one serialized state owner addressed by messages or a pipe;
4. a mutex/monitor around one named invariant;
5. bounded atomics for an independently meaningful location or protocol state; and
6. a lock-free algorithm only when its progress property and reclamation cost are required and
   evidenced.

Do not split one invariant across several locks merely to make locks smaller. Do not combine
unrelated state under one lock merely to simplify a call site. Record the canonical owner, fields,
allowed transitions, and every caller that may observe or mutate them.

## Memory-Model Contract

The selected language and runtime memory model is authoritative. Platform or kernel examples can
inform hypotheses but cannot replace language-level rules.

For each cross-thread publication:

```text
producer writes state
  -> release/synchronized publication edge
  -> acquire/synchronized observation edge
  -> consumer may read the published invariant
```

Name the matching edges; a fence on one participant alone may be insufficient. Distinguish compiler
ordering, CPU ordering, cache coherence, and device/DMA visibility when more than one layer is
actually involved. Avoid stronger ordering only after the weaker contract is proved correct and a
matching cost matters.

## Locks, Atomics, And Waiting

Use a mutex or monitor when several fields form one invariant or the critical section may block.
Keep lock ordering and reentrancy explicit, and never hold a lock across an external wait, callback,
unknown user code, or cancellation boundary unless that behavior is the accepted contract.

Spinning is appropriate only for a measured, bounded critical section when the owner can run on a
different physical execution resource and oversubscription or priority inversion cannot make the
wait unbounded. Otherwise park/block or redesign ownership.

Condition notification is not the predicate. Wait in a loop that rechecks authoritative state and
handles timeout, cancellation, spurious wakeup, and shutdown. Prefer an elapsed-time/monotonic
deadline where clock changes must not alter the wait budget.

Lock-free is not a synonym for wait-free, starvation-free, simple, or fast. A selected algorithm
must name its progress guarantee, retry/contended path, ABA treatment, memory ordering, and
reclamation protocol.

## Publication, Handles, And Reclamation

An object may be unreachable from the canonical registry while another thread still holds an
address or stale handle. Close both logical lifetime and physical reclamation:

- use generation/version checks for reusable IDs and handles;
- remove or mark state before reclamation according to the algorithm contract;
- define which readers may still hold references and how their completion becomes visible;
- use the existing ownership, reference-count, epoch, hazard, RCU, or task-scope primitive when it
  already supplies the required guarantee; and
- never invent a lock-free reclamation scheme as an incidental optimization.

Cancellation and shutdown must also prevent new publication, release waiters, and leave no owner
that can access reclaimed state.

## Cache-Line And Locality Boundary

Logical independence does not imply hardware independence. Concurrent writers to different fields
or array elements can still transfer one coherence line between CPUs.

When multicore scaling is material:

- observe write frequency, cache-to-cache/coherence traffic, worker placement, and thread-count
  scaling before diagnosing false sharing;
- consider per-worker/per-CPU accumulation, sharding, hot read/write separation, or less frequent
  global publication before padding every type;
- verify actual allocation and array stride after alignment or padding; and
- account for increased footprint, cache/TLB pressure, NUMA placement, and the possibility that the
  bottleneck moves elsewhere.

Affinity and pinning trade locality against load balancing and work conservation. Treat thread,
memory, and queue placement as one locality domain only after representative evidence makes remote
access or migration a primary constraint.

## Reductions And Determinism

Prefer thread/task-local partials plus an explicit reduction over many workers contending on one
global accumulator. Keep these claims separate:

- data-race freedom;
- deterministic dependency or commit order;
- deterministic numerical reduction; and
- cross-platform bitwise reproducibility.

Floating-point addition is not generally associative. Reproducibility needs a fixed partition and
reduction tree plus a compatible execution environment, or a domain-owned tolerance contract.

## Evidence And Diagnostics

Static source inspection can disprove safety when a permitted interleaving violates ownership,
visibility, lifetime, or cleanup. It cannot prove that a rare interleaving will occur in production
or that progress/performance meets a runtime bound.

Useful runtime evidence includes lock owner/hold/wait time, runnable and blocked state, wakeup path,
atomic retry count, queue depth, task/thread identity, cache-to-cache events, memory layout, thread
affinity, and a same-workload thread-count sweep. Sanitizers and stress tests prove only their
observed schedules and configured instrumentation.

## Composition Rules

- Use **DOD** to create disjoint ranges and locality-aware storage; this profile owns visibility and
  reclamation when ranges or phases still share state.
- Use a **Job System** to schedule ready CPU work; dependency edges do not replace memory ordering
  or reclamation.
- Use **Structured Async** for suspended operation lifetime and cancellation; callbacks that share
  mutable state still need this profile.
- Use **object-oriented** owners for resource lifetime and one invariant; use **functional** or
  **procedural** kernels to reduce hidden sharing.

## Task Cases

- **Positive:** several workers update one cache and publish a new version. Record the cache owner,
  invariant, visibility edge, handle generation, reclamation, wait/progress policy, and evidence.
- **Negative:** workers receive immutable snapshots and write disjoint owner-exclusive buffers that
  are committed once. Keep the simpler partition/commit contract; do not add shared locks.
- **Edge:** per-worker counters are logically distinct but share a coherence line. Diagnose the
  cache-line layout and scaling curve before selecting padding or per-CPU aggregation.
- **Edge:** a lock-free queue passes stress tests but reuses nodes without a reclamation contract.
  The implementation remains unsafe regardless of queue throughput.
- **Edge:** a parallel reduction is race-free but changes floating-point order. Report numerical
  determinism separately instead of claiming deterministic execution.

## Implementation Verification

- The shared invariant, canonical owner, readers, writers, and alias sets are explicit.
- Every publication has matching language-level visibility/order and a single-location atomic is
  not used as evidence for a wider invariant.
- Lock scope/order, wait predicate, timeout/cancellation, and shutdown behavior are complete.
- Handles, ABA exposure, reader lifetime, and physical reclamation close one consistent protocol.
- The selected progress/fairness property is named; lock-free is not treated as wait-free.
- Parallel writes were checked for cache-line interference when scaling motivated the design.
- Affinity/NUMA changes are evidence-driven and retain an acceptable load-balancing policy.
- Reduction order and numerical tolerance are owned explicitly when reproducibility matters.
- Static, sanitizer, stress, and performance evidence retain their distinct proof ceilings.
