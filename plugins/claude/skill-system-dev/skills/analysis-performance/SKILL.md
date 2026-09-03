---
name: analysis-performance
description: Diagnose a current latency, throughput, CPU, memory, query, rendering, startup, bundle, or complexity symptom on its representative actual path before selecting an optimization.
---

# Analysis Performance

## Routing Card
- role: primary
- intent_signature:
  - performance/latency/throughput/CPU/memory/query/render/startup/bundle analysis; 성능 분석; 병목
- use_when:
  - a current software symptom needs measurement-backed bottleneck diagnosis before an optimization is selected.
- do_not_use_when:
  - correctness diagnosis/fix, an already-selected implementation, a still-open algorithm choice, repo-wide reporting, or scientific experiment design is primary.
- expected_inputs:
  - user-relevant metric and symptom, representative workload/path, target environment/threshold, existing measurements, and material correctness constraints
- expected_outputs:
  - scoped target and baseline, actual hot path, discriminated bottleneck, evidence authority/scope, smallest next change or handoff, and unresolved conditions
- context_targets:
  must_read:
    - request, metric/workload/environment, affected actual path, and available baseline/profile/trace
  read_if_needed:
    - targeted code/query/config, benchmark method, recent regression diff, data-size assumptions, or observability contract
    - `references/systems-bottleneck-map.md` only when CPU microarchitecture, memory hierarchy,
      scheduler/synchronization, and I/O/queue hypotheses compete on the same representative path
  do_not_load_by_default:
    - full repo/memory, unrelated logs/reports, raw production data, or credentials
- risk_profile:
  reads: targeted path, comparable measurements, profiles/traces, configs, and correctness evidence
  writes: none; implementation belongs to its workflow after bottleneck selection
  tools: focused profiling and comparable measurement of the relevant path
  sensitive_resources: production data/traces require their governing access and redaction boundary
- entry_scene:
  - PREPARE

## Workflow
1. Bind each material condition: metric, representative workload/input size, environment, acceptable threshold, and correctness, freshness, security, accessibility, or side-effect constraints. Identify when the user condition is itself structural, such as exact emitted bytes.
2. Establish a baseline and trace the actual user/resource path through relevant code, query, cache, adapter, renderer, bundle, process, or IO boundary. Prefer direct observed behavior; an agent-authored benchmark, fixture, test, or mock proves only its exercised scope.
3. Hold only enough bottleneck hypotheses to discriminate them with a profile, trace, counterexample, or comparable measurement. When several systems resource layers remain plausible, use `references/systems-bottleneck-map.md` to choose the next discriminating observation without treating its taxonomy as a diagnosis. Representative actual-path evidence outranks a conflicting helper benchmark; retain any `fail`, `needs_review`, `unverified`, or blocked measurement gap.
4. Select one primary bottleneck only when evidence separates it from alternatives. Report percentage or before/after improvement only for the same material metric under comparable workload and environment, with required result and side-effect readback.
5. If the user requested a fix and the bottleneck is verified, hand the smallest optimization and comparable validation target to `workflow-implementation`. Do not imply the optimization ran; after implementation, verify on the same relevant path before claiming improvement.

## Measurement Rules
- Missing baseline, actual-path coverage, or comparable environment makes the user-level claim `unverified`; mock or microbenchmark success cannot fill that gap.
- A faster result that violates a required material condition is invalid, not an improvement. Change such a condition only through an explicit user decision before evaluating the new contract.
- Static analysis may identify candidates, not measured impact. When local measurement is unavailable, provide the exact evidence-producing action and keep the claim unresolved.
- Deterministic artifact evidence can complete an explicitly structural metric when it directly covers the condition; do not infer latency, CPU, memory, or user experience from it.

## Output Contract
Return only applicable fields: target/conditions, baseline and evidence scope, actual hot path, hypotheses and discriminating evidence, primary bottleneck, verified conclusion, smallest next change or implementation handoff, comparable validation target, and unresolved gaps. Separate bottleneck identification from optimization success.

## Cross-Skill Boundaries
- `workflow-runtime-debugging` owns an explicitly requested execution-ready debugging scope or correctness investigation when a debugger, crash artifact, dynamic diagnostic, or graphics capture is material; simple source/log RCA stays with the current task owner. A progressing target whose dominant question is frame time, latency, utilization, throughput, or resource cost stays here. No-progress under a bound horizon, OOM/allocation failure, watchdog termination, wrong state, invalid ordering/access, corruption, or device loss stays with Runtime Debugging even when resource pressure is a cause candidate. `workflow-bug-fix` repairs a bounded defect under an already-implemented accepted contract. `workflow-implementation` applies a selected optimization or production replacement even when a current symptom motivated it; `analysis-algorithm` owns a still-open approach choice regardless of symptom; `analysis-codebase-map` owns Mermaid architecture maps; `research-experiment-blueprint` owns scientific benchmark design; `workflow-refactor-safely` owns preparatory behavior-preserving structure changes.
