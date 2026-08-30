# Systems Bottleneck Map

Use this reference only after the user-visible metric, representative workload, target environment,
correctness constraints, baseline, and actual path are bound. It is a causal routing aid for
competing CPU, memory, scheduler, synchronization, and I/O hypotheses. It does not select an
optimization, prescribe a counter threshold, or turn a microbenchmark into production evidence.

## Resource Lanes

| Lane | Candidate mechanism | Discriminating evidence | Material falsifier |
| --- | --- | --- | --- |
| CPU frontend/control | instruction-cache pressure, branch misprediction, decode or dispatch limits | on-CPU stacks, instruction/branch counters, representative disassembly, controlled branch/code-shape perturbation | wall time is dominated off-CPU or unchanged when the suspected control path is removed |
| CPU execution/ILP | dependency chain, expensive instruction mix, scalar work, spills | cycles/instructions, backend execution evidence, compiler output, algorithm-preserving kernel comparison | memory, queue, or wait evidence explains the same interval and CPU work is not limiting |
| cache/TLB/locality | working-set cliff, pointer chasing, poor stride, cache/TLB misses | data layout and access stream, cache/TLB counters, size sweep, traversal-order perturbation | same workload stays flat across working-set/layout changes or another resource saturates first |
| memory bandwidth/NUMA | bandwidth ceiling, remote access, migration, shared interconnect pressure | bandwidth and locality counters, CPU/memory placement, thread migration, node-aware comparison | local placement or reduced traffic does not change the bound path under comparable load |
| allocation/virtual memory | allocation churn, fragmentation, page faults, reclaim, copy-on-write | allocation profile, resident/working-set history, fault/reclaim trace, allocator slow-path stacks | preallocation or stable residency leaves the symptom unchanged |
| scheduler/oversubscription | runnable delay, context switches, priority inversion, too many carriers | on/off-CPU stacks, run-queue delay, wakeup and context-switch trace, physical versus logical worker sweep | the critical thread is continuously on-CPU and scheduling delay is negligible |
| synchronization/coherence | lock wait, spinning, atomic retry, false sharing, reclamation stalls | owner/hold/wait time, retry count, cache-to-cache evidence, data layout, thread-count sweep | wait and coherence traffic are absent or do not align with the latency interval |
| I/O/system call | device, filesystem, network, durability, or kernel wait | syscall and I/O trace, issuer attribution, queue depth/age, bytes and operation size, cache/flush state | the request is on-CPU or completion arrives before the observed delay |
| async queue/backpressure | readiness/completion delay, event-loop blocking, blocking adapter saturation, head-of-line blocking | operation lifecycle, callback duration, queue depth/age, admission/rejection, completion latency, worker-pool state | queue age is low, callbacks are bounded, and downstream service time owns the delay |

Do not read one high counter as a cause. Align the observation with the same request, frame, batch,
or interval and reject at least one plausible competing lane.

## CPU And Memory Questions

For an on-CPU hot path, ask in this order:

1. Is the algorithm doing avoidable work or using the wrong complexity class?
2. Is useful execution limited by control/instruction flow, dependency chains, or scalar code?
3. Is the CPU instead waiting for cache, TLB, DRAM, or remote NUMA data?
4. Does the representative access stream match the chosen layout and working set?
5. Does parallel execution add atomic, coherence, bandwidth, or migration cost faster than useful
   work is divided?

Data-oriented changes are candidates only after the access stream and constrained resource are
identified. AoS, SoA, padding, prefetch, pinning, and huge pages are hypotheses with costs, not
defaults.

## Scheduler And Synchronization Questions

Separate these states:

- running on a CPU;
- runnable but not scheduled;
- sleeping on I/O or a synchronization predicate;
- spinning or retrying while consuming CPU;
- waiting for a lock owner that is itself descheduled or blocked; and
- migrated to a CPU or NUMA node that lost useful locality.

High CPU utilization can be useful work, spin, retry, kernel work, or observer overhead. Low
utilization can reflect a long serial dependency, blocked owner, insufficient ready work, or an
external queue. Worker count and utilization do not measure critical-path length.

For shared-memory cost, inspect both logical ownership and hardware sharing granularity. Distinct
fields or per-worker counters may share one coherence line. Padding or pinning can reduce one cost
while increasing footprint, TLB pressure, imbalance, or loss of work conservation.

## I/O And Asynchronous Questions

Determine where the wait actually lives:

- inside a blocking system or library call;
- in a readiness loop that will retry partial progress;
- in a submitted completion operation;
- in a bounded blocking adapter or worker pool;
- in a downstream device/network/storage queue; or
- in application queueing, serialization, backpressure, or head-of-line blocking.

Changing blocking syntax to `async` improves performance only when useful work overlaps the wait or
the new model reduces carrier/resource cost. It may instead add queueing, state-machine,
cancellation, buffer-lifetime, and scheduling overhead. Preserve durability and correctness
semantics when comparing I/O models.

## Scaling And Latency Traps

- Fixed-size speedup and scaled-workload throughput answer different questions. Record whether load,
  problem size, worker count, or hardware changed.
- More workers cannot remove the longest serial/dependency chain and may add scheduling,
  synchronization, coherence, bandwidth, and context-switch cost.
- Batching amortizes fixed overhead but can increase maximum queue age and tail/deadline misses.
  Measure batch size and maximum age, not only average throughput.
- Pipelining distinct requests or frames can increase throughput while increasing end-to-end
  latency, in-flight memory, and reclamation distance.
- Affinity can improve locality while reducing load balancing. Pin only after migration or remote
  access is observed on the bound path.
- Microbenchmark improvement proves only its kernel and environment. Re-read the end-to-end result
  and material side effects under the original workload.

## Evidence Sequence

1. Preserve the original latency, throughput, frame, memory, or capacity symptom and its timeline.
2. Classify on-CPU, runnable, blocked, queued, or external-completion time before choosing a lower
   layer.
3. Select the smallest profile, trace, counter set, or perturbation that distinguishes the leading
   lanes.
4. Change one material variable while holding workload, environment, correctness, and metric
   meaning constant.
5. Re-measure the same user-visible path; report a moved bottleneck separately from a closed one.

## Task Cases

- **Positive:** a frame misses its tail budget with CPU idle holes. Compare critical-path tasks,
  ready-queue delay, blocking waits, and memory stalls before adding jobs.
- **Positive:** throughput falls as workers increase. Compare lock/atomic wait, cache-to-cache
  traffic, bandwidth, migration, and serial span under one thread-count sweep.
- **Negative:** one helper microbenchmark is faster after an SoA rewrite, but the production path is
  I/O-bound. Do not claim a production improvement or select broader DOD work.
- **Edge:** batching raises throughput while queue age and P99 latency cross the requirement. Treat
  the change as invalid for that contract even if average service time improves.
- **Edge:** pinning reduces remote memory access but leaves workers idle. Preserve the locality versus
  work-conservation tradeoff instead of calling either configuration universally superior.

## Stop Rule

Stop using this map once one primary bottleneck is discriminated for the bound workload or the exact
missing observation is named. If the user also requested a fix and the bottleneck is verified, hand
only the smallest selected optimization and same-condition validation target to Implementation.
Otherwise return the diagnosis and unresolved evidence without expanding into implementation. Do
not carry the whole taxonomy into default context.
