# Structured Async Selection Profile

- **Trigger:** file, network, device, timer, process, or external-operation latency must not block
  its caller; many pending operations need readiness/completion multiplexing; or child-task
  lifetime across asynchronous suspension or an external operation must keep cancellation,
  deadline, error, and cleanup propagation inside one scope.
- **Non-trigger:** CPU speedup or bulk parallelism is primary, one bounded callback is sufficient,
  CPU Job dependency/completion already owns the task tree, the caller may safely wait, or `async`
  syntax merely wraps synchronous work without changing the actual wait owner.
- **Minimum closure:** actual execution domains and wait carriers, structured owner/scope, explicit
  pending/succeeded/failed/cancelled states, deadline/cancellation/shutdown, executor/thread
  affinity, and validated result publication including stale-completion handling; external request
  paths also close request/buffer lifetime, readiness or streaming paths distinguish readiness from
  completion and close partial progress plus registration lifetime, while a queue or pending set
  that can grow also closes capacity, overload/backpressure, maximum useful age, and forward
  progress.
- **Maximum scope:** asynchronous progress, operation lifetime, and completion publication. The
  profile does not acquire protocol meaning, durability, domain retry/fallback policy, CPU Job
  scheduling, shared-memory synchronization, or GPU queue semantics.
- **Interactions:** object/resource owners supply lifetime and canonical commit; Job Systems may
  receive CPU kernels only after I/O progress is ready; shared-memory access uses its own profile;
  snapshot/version owners decide whether a late result commits, merges, is discarded, or retries.
- **Proof ceiling:** an `async` API, coroutine, callback, event loop, or non-blocking call proves
  only representational shape. It does not prove that no thread blocks, cancellation cleans up,
  queues remain bounded, callbacks meet their budget, forward progress holds, or latency/capacity
  improves without actual-path trace and workload evidence.

Implementation details and actual-path verification remain with the matching
`workflow-implementation` method profile.
