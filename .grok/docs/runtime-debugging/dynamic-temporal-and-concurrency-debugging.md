# Dynamic, Temporal, And Concurrency Debugging

Use this reference when a snapshot cannot expose the first invalid transition, when timing or
schedule matters, or when corruption, races, deadlocks, lifetime errors, or intermittent failures
compete.

## Select One Dynamic Lane

| Unresolved question | Preferred lane | Direct support | Proof ceiling |
| --- | --- | --- | --- |
| who first wrote this location incorrectly | narrow watchpoint or recorded memory history | observed write instruction/thread/value under that run | other executions and writes outside watched scope |
| which prior event led here | bounded trace or record/replay | recorded event/instruction order and captured state | unrecorded data/events; replay environment differences |
| whether an instrumentable memory/undefined/thread violation occurred | targeted dynamic detector | reported violation in the instrumented execution | unexecuted paths, uninstrumented modules, changed timing/layout |
| why work stopped progressing | thread/task/queue snapshots plus wait-for/progress evidence | observed waits, owners, held resources, progress markers | missing async/device owners or history |
| which schedule triggers an intermittent failure | reproducible schedule/seed or lower-perturbation tracing | named schedule/history under recorded condition | general absence or frequency outside sampled schedules |

Do not run several heavy lanes simultaneously unless each answers a distinct material question;
combined instrumentation can destroy comparability and hide the original failure.

## Watchpoint And Corruption Workflow

1. Prove the watched address, size, alignment, allocation/object lifetime, and owning field for the
   current run. A stale address from a previous run is invalid evidence.
2. Record the already-invalid value and the expected invariant.
3. Watch the smallest location that can expose the first bad write. Note hardware versus emulated
   behavior, thread coverage, access type, and slot/size limits.
4. On a stop, validate that the write belongs to the watched lifetime and inspect the instruction,
   writer thread, value, source mapping, and caller/owner state.
5. Distinguish the corrupting write from legitimate initialization, reuse, teardown, allocator
   metadata, or a later manifestation.

## Dynamic Diagnostic Reports

- Record exact binary/build, instrumented module coverage, runtime options, allocator, optimization,
  environment, workload, and tool/runtime version.
- A detector failure is direct evidence of the reported violation under that instrumented run when
  identity and report integrity hold.
- A clean run proves only the executed inputs, paths, schedules, instrumented modules, and detector
  configuration. It is not absence proof.
- Instrumentation may change memory layout, allocation, stack use, scheduling, timing, and supported
  address space. Keep original and instrumented manifestations separate.
- Do not combine incompatible detector/runtime modes merely to increase coverage. Use separate runs
  and preserve the condition difference.

## Record, Replay, And Trace

Classify what the lane records: control flow, instructions, branches, memory writes, system events,
thread scheduling, application events, or device work. “Replay available” does not imply every
memory value or external effect is historical.

- Pin target/build and recording configuration.
- Record buffer limits, dropped events, snapshots/checkpoints, external inputs, non-replayed I/O,
  and whether reads can observe current rather than recorded state.
- Navigate backward only within supported recorded semantics. Preserve the exact event/instruction
  that first violates the invariant.
- Treat replay as a changed execution environment when the tool reconstructs, serializes, resets,
  accelerates, or omits work.
- A deterministic replay proves repeatable stimulation of the captured condition, not correctness.

## Race Diagnosis

- Define the shared state, expected synchronization/order invariant, conflicting accesses, and
  lifetime.
- Distinguish data race, higher-level atomicity/order violation, stale publication, ABA/reuse,
  cancellation/lifetime race, and queue ownership error; one detector category does not cover all.
- Preserve thread/task identity, access type, synchronization edges, memory-order semantics when
  relevant, and the observed schedule or trace position.
- A race report is strong evidence for the reported instrumented accesses. A clean report is bounded
  by instrumentation coverage and observed schedules.
- If breakpoints or all-stop attachment remove the symptom, record perturbation and prefer lower-
  intrusion trace, dynamic detection, crash capture, or controlled schedule evidence.

## Deadlock And Progress Diagnosis

Build an observed wait-for view:

```text
waiter -> awaited resource/condition/queue -> observed owner or producer
```

For each edge, record held resources, acquisition/wait site, timeout/cancellation state, task/queue
executor, and last progress marker. A closed cycle with no permitted breaker supports deadlock. A
long wait, starvation, livelock, priority inversion, blocked device submission, exhausted worker
pool, or missing external response requires different evidence.

One all-thread snapshot can expose a stable cycle but cannot reconstruct the temporal order that
created it. If order is causal, add the smallest history lane rather than asserting it from stack
proximity.

## Perturbation Ledger

Record every material difference from the original condition: attach/stop mode, breakpoints,
watchpoints, detector instrumentation, altered optimization, allocator/runtime, environment, seed,
clock, trace buffer, replay, thread affinity, device validation, and capture overhead. When the
failure moves or disappears, treat that as evidence about sensitivity, not resolution.

## Stop And Handoff

Stop when the first invalid transition and its owner are directly observed, when one leading
hypothesis and discriminator remain, or when coverage/perturbation makes the lane insufficient.
Return the original trigger, identity, recorded horizon, observed transition/order, competing causes,
perturbations, causal status, and the exact original-signal verification target for a later repair.
