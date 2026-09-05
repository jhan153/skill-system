# Job System Implementation

Cross-stage selection authority lives in `references/programming-paradigms/job-system.md`. This file owns
concrete realization and actual-path verification; it may narrow implementation admission from
production evidence but never broadens the accepted trigger or scope.

A Job System is an execution architecture, not a replacement for procedural, object-oriented, functional, or data-oriented design. Use it when CPU work decomposition also needs explicit dependencies, scheduling, completion, cancellation/error propagation, or resource-access coordination.

## Classification

| Model | Primary concern |
| --- | --- |
| Thread pool | execute independent callbacks on worker threads |
| Job System | schedule small CPU tasks with dependencies, completion, and load balancing |
| `async`/`await` | express asynchronous continuation, often for latency/I/O |
| Actor system | isolate state behind message-addressed owners |
| ECS scheduler | derive system ordering from component access, often using a Job System |
| GPU task graph | order GPU commands, queues, barriers, and resource transitions |

A queue plus `enqueue(lambda)` is not yet a Job System. The architecture becomes job-oriented when dependency and completion semantics, safe data access, and dynamic execution are first-class.

## Ownership Principle

> Domain modules decide how work is decomposed; the Job System decides where ready work executes.

The scheduler must not invent domain grain, fallback policy, numerical order, or resource meaning. A mesh module knows what a face-normal range means. The scheduler knows only that a runnable body, dependencies, and access declaration exist.

## Three Levels Of Work

Do not equate domain items with scheduler nodes.

```text
Domain operation
  RecomputeNormals for one mesh

Logical parallel items
  faces or vertices that can be processed independently

Scheduler jobs
  contiguous chunks of many faces/vertices
```

One million vertices should not automatically produce one million Job nodes. Chunking balances scheduling overhead, cache behavior, and load imbalance.

## Cost And Grain Model

```text
T1 = serial useful work
T∞ = longest dependency chain / span
P  = available workers

ideal floor >= max(T1 / P, T∞)

observed time
  ~= ideal floor
   + job creation and queueing
   + dependency and synchronization cost
   + cache/memory movement
   + load imbalance
   + blocking or preemption delay
```

The scheduler can redistribute ready work, but it cannot remove `T∞`. Record total work and span
separately; high aggregate utilization can still miss a deadline when the critical chain is long.

Smaller chunks improve balance but increase allocation, queue operations, atomics, dependency counters, cache traffic, wakeups, and tracing. Larger chunks reduce overhead but may leave workers idle.

Choose grain from a representative workload:

| Work shape | Initial policy |
| --- | --- |
| uniform item cost | contiguous static chunks |
| highly variable item cost | smaller chunks plus work stealing |
| recursive divide-and-conquer | serial cutoff below a measured size |
| memory-bandwidth-bound loop | larger cache-friendly ranges |
| tiny operation | fuse operations or avoid scheduling |
| frame-budgeted work | bounded slices that avoid long monopolizing jobs |
| deterministic reduction | fixed partition and fixed reduction tree |

Measure empty-job schedule/complete overhead, then keep useful chunk work comfortably above it.

## Kernel And Orchestration Separation

```cpp
void computeFaceNormals(
    MeshView mesh,
    std::span<Vec3> output,
    IndexRange range);

JobHandle scheduleFaceNormals(
    JobSystem& jobs,
    MeshView mesh,
    std::span<Vec3> output,
    GrainPolicy grain);
```

The kernel remains sequentially callable and testable. The scheduling function owns chunking and dependencies. This enables serial fallback, deterministic tests, profiling, and changing the scheduler without rewriting the numerical code.

## Dependency And Completion Model

Distinguish two relationships:

```text
Execution dependency
  A must finish before B may start
  A -> B

Completion dependency
  A's body returned, but A is complete only after nested child B
  A contains B
```

Represent prerequisites with counters/edges and represent nested completion with an existing scope
or structured task group when it supplies the required guarantees. Do not add a parallel counter or
completion owner merely to restate that contract, and do not overload blocking `wait()` to represent
both relationships.

For the simplest safe graph lifecycle:

1. create nodes;
2. attach dependency edges;
3. validate cycles or invalid handles;
4. seal/publish the graph;
5. enqueue roots whose prerequisite count is zero.

Attaching successors after a predecessor is concurrently completing requires a separate synchronization contract. Avoid that complexity unless dynamic graph mutation is required.

When implementing custom scope/completion bookkeeping, close these obligations explicitly:

- Register a child's completion obligation before publishing it as runnable, including submissions
  that may execute inline before `schedule` returns.
- Every accepted child reaches exactly one accounted terminal outcome: success, failure, or
  cancellation. A cancellation request alone does not retire work that can still access the scope's
  state or resources.
- Distinguish rejected admission from an accepted job whose enqueue fails. Undo an unaccepted
  reservation, or complete accepted work through its failure path, exactly once; enqueue rejection,
  cancellation, and body completion must not leak or double-release the obligation.
- Coordinate close with admission. Define when external and already-owned nested submissions may
  still be accepted, and do not publish scope completion while a legal admission can still race
  with the final outstanding-work check. Account for the parent's own body before completing its
  nested scope.
- Publish terminal scope completion only after its admitted work and required cleanup are finished,
  with the matching visibility and lifetime guarantees. Reuse existing task-group semantics when
  they already supply this protocol; these obligations do not mandate a new counter or framework.
- External submission cannot reopen an already terminal scope generation. If the existing primitive
  supports reuse, follow its explicit new-scope/generation protocol; do not make an observed completed
  operation pending again by incrementing the old count or reusing its completion identity.

## Minimal Semantic API

The API shape varies, but it should express:

- schedule a body with prerequisite handles;
- `parallel_for` or range decomposition with grain policy;
- continuation or `when_all` composition;
- task group/scope for nested completion;
- cancellation and error propagation;
- completion observation without blocking all workers;
- optional resource read/write declarations;
- names/tracing IDs for diagnostics.

The API must also define handle lifetime, generation/reuse, submission from external threads, shutdown behavior, and what waiting from a worker does.

The scheduler must also define whether a suspended or resumed task may continue on another worker.
Serialization prevents concurrent execution; it does not guarantee the same OS thread. A dependency
on TLS continuity, a thread-owned lock/allocator, or a thread-affine API must satisfy that resource's
actual thread requirement at every use and release. Returning to the same executor or serial lane
is insufficient when it may migrate. Keep movable computation state task-local, but do not assume
that moving a lock guard into task-local storage transfers an OS-thread-owned lock.

## Scheduling Strategy

Begin with the simplest scheduler that proves the API and dependency model:

```text
external submission
     -> central ready queue
     -> worker pool
```

Move to per-worker deques and work stealing only when contention or imbalance is observed. A typical owner pushes/pops locally while thieves steal older work. Implementing a lock-free Chase-Lev-style deque also requires correct last-item races, resize, index overflow, weak memory ordering, shutdown, and memory reclamation; it is not a casual optimization.

## Waiting And Blocking

Do not make nested blocking wait the central composition primitive:

```cpp
jobs.schedule([&] {
    JobHandle child = jobs.schedule(...);
    jobs.wait(child); // may block a scarce worker
});
```

Prefer, in order:

1. explicit dependencies and continuations;
2. nested completion/task scopes;
3. worker-helping waits when carefully specified;
4. fibers only when synchronous-looking suspend/resume behavior justifies stack and tooling complexity.

A helping wait or suspension may run unrelated jobs or re-enter the same owner before the waiting
operation resumes. Identify the permitted re-entry set, held locks, and temporarily broken
invariants. Restore externally observable invariants and release incompatible locks before yielding
or helping, or use a documented isolation/async-aware synchronization contract that preserves
ownership, cancellation cleanup, and forward progress. A pinned OS thread or serial executor alone
does not prevent same-thread re-entry, self-deadlock, or another task observing intermediate state.
Do not help work that needs a resource the waiter retains unless the accepted protocol closes that
dependency; asynchronous-aware mutexes are not prohibited when their actual contract does so.

File/network/database waits, long mutex waits, process waits, and GPU fence waits should usually use an I/O/event executor or dedicated integration path rather than occupy CPU compute workers.

## Data Access Model

Scheduling does not remove data races. Make safe parallelism visible through one or more of:

- immutable snapshots and views;
- disjoint output ranges;
- explicit resource read/write sets;
- versioned handles;
- thread-local/Job-local partial results followed by reduction;
- per-identity serial queues when order matters only within each object.

Non-overlapping writes do not establish visibility to a later consumer on another thread. Bind
the actual completion/publication edge and last-consumer lifetime; reuse the selected runtime's
documented synchronization and ownership guarantees when they close those obligations. A dependency
arrow or method named `complete` alone is not that evidence, and an already sufficient completion
contract does not require an extra mutex or a new profile.

```cpp
JobDesc job {
    .reads = {Positions, Indices},
    .writes = {FaceNormals},
    .body = ...
};
```

Read/read can run together. Any overlapping write needs ordering, partitioning, atomics/locks with an accepted cost, or a different algorithm.

Prefer partial accumulation and reduction over many workers contending on shared vertices or hash entries. Specify floating-point reduction order when reproducibility matters.

Keep four claims separate: data-race freedom, deterministic dependency/order, numerical reduction
determinism, and cross-platform bitwise reproducibility. A dependency edge proves only its required
ordering. Floating-point reproducibility additionally needs a fixed partition/reduction tree and a
compatible execution environment, or an explicit tolerance contract.

## Staged Result Publication

A Job handle or task scope represents an in-progress operation; it must not make a partially initialized final domain object publicly usable.

Reuse the existing scheduler handle, task group, future, fence, and result/storage primitives when they already express the required progress and lifetime. Add `UploadTicket`, `BuildRequest`, or another public staged type only for a real additional invariant, state set, cancellation/cleanup rule, or publication boundary; do not wrap a Job handle only to rename it.

```text
JobScope / UploadTicket / BuildRequest
  Pending -> Running
               |- Completed
               |- Failed
               `- Cancelled

completed builder/patch
  -> validate coverage/version/invariants
  -> commit/freeze
  -> final canonical value
```

Workers may fill disjoint ranges in builder storage, produce local partials, or create a versioned patch. Only the completion/commit boundary may publish the final buffer, mesh, connection result, or uploaded resource state. Failure and cancellation must prevent publication and leave ownership/cleanup defined.

Do not use a public final object with a mutable `ready_` flag, let background work silently change which methods are legal, or treat a completion handle as proof that every range and invariant was validated. For file/network progress, coordinate with the I/O/event executor rather than blocking compute workers; for GPU/DMA, use an explicit upload ticket/fence state and publish readiness after the required synchronization.

## Snapshot, Compute, Commit

For editors, CAD, scene systems, and other mutable domains:

```text
owner thread
  snapshot data + version
          |
          v
Job graph
  compute local result/patch
          |
          v
commit boundary
  compare source version
  apply, merge, discard, or reschedule
```

This prevents background workers from mutating a live identity graph without conflict policy. The domain owner decides how a stale result is handled.

## Accepted Pipelines And Frames In Flight

When an accepted domain or rendering owner overlaps distinct items or frames, the Job System only
carries ready work; it does not select the pipeline policy. Each in-flight item needs a versioned
snapshot or token, a maximum count and backpressure rule, last-consumer reclamation, and measured
memory plus end-to-end latency. A throughput gain does not prove lower input-to-visible latency.

## Suitable And Unsuitable Work

Strong candidates:

- vertex/face/particle/instance range kernels;
- BVH construction and recursive spatial work with cutoffs;
- culling, animation evaluation, draw-packet preparation;
- independent residual/Jacobian evaluation and deterministic reduction;
- simulation stages with explicit dependencies;
- asset transforms after I/O is complete.

Conditional candidates:

- shared-topology mutation requiring partition/merge;
- Gauss-Seidel-like algorithms with order dependencies;
- nested solvers already using their own thread pool;
- tiny work whose scheduler overhead dominates.

Poor candidates for the general CPU pool:

- blocking I/O and external waits;
- one isolated background callback with no graph semantics;
- highly sequential critical paths;
- work whose mutable aliasing cannot be partitioned or ordered safely.

## Composition Rules

- **Functional** kernels reduce hidden dependencies and support safe retries or reductions.
- **Data-oriented** layouts provide chunkable ranges and visible read/write sets.
- **Procedural** orchestration can define domain stages while Job orchestration maps them to a DAG.
- **Object-oriented** owners manage scheduler lifetime, task scopes, resources, and domain commit, but workers should receive handles/views rather than deep shared graphs.
- **Structured Async** owns file/network/device waits, request lifetime, cancellation, and
  backpressure before ready CPU work enters the Job System.
- **Shared-Memory Concurrency** addresses material invariant, visibility, synchronization,
  reclamation, or progress obligations left open by the existing owner/runtime contract, including
  cross-thread publication of owner-exclusive ranges. Reuse sufficient runtime completion and
  last-consumer guarantees before adding a profile or coordination mechanism.
- **TMP** may specialize a bounded kernel, not replace runtime dependency scheduling.

## Discriminating Task Cases

- **Serial is not pinned:** a continuation moves from thread A to B inside one serial executor.
  Reject using serialization as evidence that B may release A's thread-owned mutex or reuse A's
  TLS state. Check actual thread identity requirements or remove that cross-suspension dependency.
- **Custom completion:** a child can execute inline, enqueue can reject, and close can race with
  submission. Admit/register before execution and account every accepted terminal outcome exactly
  once; neither an early zero count nor a cancellation request alone means the scope is complete.
- **Existing scope:** the selected task group already guarantees admission, terminal accounting,
  closure, and cleanup. Bind those guarantees on the actual path; add no mirror counter.
- **Helping re-entry:** a parent retains a mutex or exposes a temporary invariant while its wait
  helps another task that touches the same owner. Same-thread execution does not make that safe.
  Release/restore before helping, or establish a documented isolation and progress contract.

## Implementation Verification

- The requirement needs graph/dependency/completion semantics beyond one asynchronous callback.
- Total work and the longest dependency chain are observed separately; job count and worker
  utilization are not used as proxies for either.
- Domain, logical-item, and scheduler-grain levels are distinct.
- Sequential kernels remain independently callable.
- Dependencies, admission/close, completion, cancellation, error, and shutdown semantics are defined;
  custom bookkeeping covers inline execution, enqueue rejection, and exactly-once terminal accounting,
  while existing sufficient task-group contracts are reused.
- Worker waiting cannot deadlock or starve ready child work under the stated policy; helping and
  suspension account for unrelated re-entry, held resources, and temporarily broken invariants.
- Read/write overlap and shared accumulation have an explicit algorithm.
- In-progress Job/bulk/GPU work reuses existing scheduler/runtime primitives when sufficient; any new request/builder/ticket owns a real additional invariant and cannot publish a partially initialized final object.
- Blocking I/O and nested parallel runtimes are separated or coordinated.
- Migrating tasks meet each resource's actual OS-thread requirement; serialization or the same
  executor is not used as thread-affinity proof, and affinity alone is not re-entry safety.
- Grain and scheduler sophistication are justified by a representative workload.
- Determinism requirements pin partition and reduction order where necessary.
- Snapshot/commit version conflicts have a domain-owned outcome.
- Accepted pipelined work has an owner-provided in-flight bound, reclamation point, and latency
  contract.
