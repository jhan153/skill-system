# Structured Async Implementation

Cross-stage selection authority lives in
`references/programming-paradigms/structured-async.md`. This file owns concrete realization and
actual-path verification; it may narrow implementation admission from production evidence but
never broadens the accepted trigger or scope.

Structured async is an operation-lifetime and progress model. It lets a caller continue before an
operation finishes while keeping completion, failure, cancellation, cleanup, and result ownership
inside an explicit scope. It is not a synonym for CPU parallelism or a promise that no OS thread
will block.

## Distinguish The Models

| Model | Wait/progress owner |
| --- | --- |
| blocking call | the calling thread waits inside the operation |
| non-blocking readiness | the call reports retry-later; an event loop or readiness source decides when to retry |
| asynchronous completion | a submitted operation later reports result/error through a completion channel |
| coroutine/task | language/runtime state machine that may suspend; its executor and underlying operation still decide where work runs |
| blocking adapter | a dedicated bounded worker performs an unavoidable blocking API and reports completion |
| CPU Job System | workers execute ready CPU kernels with dependencies; it does not own external I/O progress |

Record the actual model at every boundary. An `async` function may execute synchronously until its
first suspension, an event-loop callback may block the whole loop, and an apparently asynchronous
file API may use a blocking worker pool internally.

## Ownership Principle

> The scope that starts an asynchronous operation owns its lifetime until one terminal result has
> been observed and every resource used by the operation can be reclaimed.

Prefer structured parent/child scopes, task groups, request scopes, connection owners, or another
existing lifetime primitive. Do not detach work merely to avoid waiting. A genuinely detached task
needs an application-lifetime owner, error sink, cancellation/shutdown path, and bounded resource
policy.

## Operation State And Publication

Use one explicit state machine appropriate to the runtime:

```text
created -> queued -> running/suspended
                     |- succeeded(result)
                     |- failed(error)
                     `- cancelled(reason)
```

- A cancellation request is not proof that the operation has stopped or released its resources.
- Completion is terminal exactly once; duplicate callback/resume paths must be rejected or made
  idempotent by the owning primitive.
- Request, descriptor, callback context, and input/output buffers outlive every pending kernel or
  OS operation that can still access them.
- A future, task handle, or readiness flag does not itself validate final-domain invariants.
- Publish a final value only after completion, coverage, version, and owner invariants succeed.

For mutable documents, scenes, sessions, or caches, carry a source version or generation with the
operation and let the canonical owner decide whether a late result commits, merges, is discarded,
or is rescheduled.

## Readiness, Completion, And Partial Progress

Readiness means an operation is expected to make progress without blocking; it is not proof that a
requested transfer is complete. Completion means a previously submitted operation reached a
terminal result under the platform contract.

Non-blocking and completion loops must preserve:

- partial reads/writes and the unconsumed buffer suffix;
- retry-later as normal state, without a busy retry loop;
- EOF, timeout, cancellation, and typed failure as distinct outcomes;
- one owner for registration, deregistration, and descriptor/handle close; and
- callback or continuation work small enough for its execution domain, with CPU-heavy work handed
  to the selected Job System or another bounded CPU executor.

## Queue, Backpressure, And Forward Progress

Every queue or pending-operation set that can grow under load defines:

- producer, consumer, capacity or concurrency limit, and the resource being protected;
- admission and overload behavior such as reject, shed, coalesce, defer, or apply upstream
  backpressure;
- maximum useful age, deadline, or stale-work rule when latency matters;
- cancellation and shutdown treatment for queued and already-running operations; and
- the forward-progress exception needed by work that releases capacity or satisfies a dependency.

An unbounded queue can turn overload into memory growth and tail latency. A bound that is too low
can deadlock mutually dependent work or prevent cleanup from running. Choose the bound from the
resource and dependency model, then observe queue depth, age, rejection, completion, and wait time
under a representative load.

## Cancellation, Deadline, And Shutdown

Cancellation is cooperative unless the selected platform contract proves otherwise. Each stage
must either stop before its next effect, complete the effect and suppress publication, or perform a
declared compensation. Do not report cancellation while a buffer, callback, child task, or external
operation can still mutate owned state.

Use an owner-controlled monotonic deadline when elapsed-time behavior matters. Recheck the
authoritative predicate after wakeup or completion; a signal is a reason to inspect state, not the
state itself.

A safe shutdown normally follows this ownership order:

1. stop or bound new admission;
2. signal cancellation/closure to owned scopes;
3. continue servicing completions needed for cleanup and forward progress;
4. drain or join according to the declared policy; and
5. close executors, descriptors, buffers, and owners after no completion can reference them.

## Executor And Affinity Boundary

Document where callbacks and continuations may run: inline on the completing thread, on an event
loop, on a CPU pool, on a pinned lane, or on a caller-selected executor. Thread-local state,
thread-affine APIs, and OS-thread-owned locks or allocators are invalid across suspension unless the
contract guarantees resumption on that same lane.

Place unavoidable blocking APIs behind a dedicated bounded adapter rather than a CPU Job worker or
event-loop callback. The adapter makes the blocking carrier, capacity, cancellation limitation, and
shutdown behavior visible; it does not convert the underlying operation into native non-blocking
I/O.

## Suitable And Unsuitable Work

Strong candidates:

- many concurrent socket, file, device, timer, or process operations;
- responsive UI/editor/server flows that must not hold the owner thread while waiting;
- staged resource loading with explicit cancellation and versioned publication;
- request trees whose child results, errors, and cleanup must finish within one scope.

Poor candidates:

- CPU-bound loops that need data partitioning and parallel speedup;
- one bounded background callback with no structured child lifetime or queue pressure;
- fire-and-forget effects with no owner, error sink, or shutdown path;
- operations whose buffers or domain objects cannot outlive pending completion safely.

## Composition Rules

- Use a **Job System** for ready CPU work, not for blocking external waits.
- Use **Shared-Memory Concurrency** only when callbacks or tasks truly share mutable state; prefer
  immutable messages, snapshots, or one-owner serialization first.
- Use **object-oriented** owners for connection, request, resource, executor, and task-scope
  lifetime.
- Use **procedural** state machines or **functional** transformations for individual continuation
  steps where they keep effects and retries visible.
- Use **data-oriented** buffers when completed input feeds representative bulk kernels; the async
  layer owns progress, not the kernel layout.

## Task Cases

- **Positive:** thousands of connections need readiness/completion multiplexing, bounded output
  queues, deadlines, cancellation, and one owner for partial buffers. Select Structured Async.
- **Negative:** a fixed array update is CPU-bound and all data is ready. Select DOD/Job System as
  evidenced; do not add coroutines or an event loop.
- **Edge:** an `async` file wrapper uses a blocking pool. Preserve its structured scope but expose
  pool capacity, blocking carrier, cancellation limit, queue age, and shutdown behavior.
- **Edge:** cancellation races with a late success callback. The versioned owner accepts exactly one
  terminal outcome and prevents stale result publication while still completing cleanup.

## Implementation Verification

- The actual execution domain and wait carrier are identified for every stage.
- Readiness, completion, partial progress, retry-later, EOF, timeout, failure, and cancellation are
  not collapsed into one boolean state.
- Parent/child lifetime, result/error propagation, and detached-task ownership are explicit.
- Buffers, handles, callback contexts, and domain owners outlive all pending access.
- Queue capacity, overload/backpressure, deadline/staleness, and forward progress are defined.
- Event-loop and completion callbacks do not perform unbounded CPU or blocking work.
- Cancellation and shutdown drain or suppress late completion without leaking or publishing stale
  state.
- Executor/thread affinity is explicit; suspension does not silently invalidate TLS or
  thread-affine state.
- A matching trace or workload observation, not `async` syntax, supports latency, capacity, and
  non-blocking claims.
