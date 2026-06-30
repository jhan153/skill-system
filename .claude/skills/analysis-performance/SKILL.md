---
name: analysis-performance
description: Performance analysis for software systems. Use when Codex must diagnose latency, throughput, memory, CPU, query, bundle, rendering, startup, or algorithmic bottlenecks with measurements or scoped evidence before recommending or applying optimizations.
---

# Analysis Performance

## Routing Card
- role: primary
- intent_signature:
  - performance analysis
  - latency
  - throughput
  - memory usage
  - CPU bottleneck
  - slow query
  - 성능 분석
  - 병목
- use_when:
  - the user asks why something is slow, heavy, memory-hungry, or inefficient.
  - optimization requires identifying a measured or evidence-backed bottleneck first.
  - the task involves latency, throughput, CPU, memory, query count, rendering cost, startup time, bundle size, or algorithmic complexity.
- do_not_use_when:
  - the task is a correctness bug with failing behavior; use `analysis-bug` or `workflow-bug-fix`.
  - the user already selected a simple implementation change with no performance uncertainty; use `workflow-implementation`.
  - the request is broad repo-wide reporting; use `analysis-codebase`.
  - the user asks for research benchmarking or scientific experiment design.
- expected_inputs:
  - performance symptom, metric, workload, route, query, function, UI path, or resource concern
  - baseline numbers, profiler output, logs, traces, tests, or an explicit `Unverified` gap
  - target environment and acceptable performance goal when available
- expected_outputs:
  - performance target, baseline evidence, bottleneck hypothesis, measurement plan/result, optimization options, recommended next change, and validation criteria
- context_targets:
  must_read:
    - current performance symptom and desired metric
    - relevant code path, query, component, or workload
    - existing measurement/log/profile evidence or explicit `Unverified` gap
  read_if_needed:
    - benchmark scripts, test fixtures, logs, traces, package manifests, or observability docs
    - algorithm/data-size assumptions
    - recent diffs if the slowdown is a regression
  do_not_load_by_default:
    - full repo
    - full memory bank
    - unrelated logs
    - broad architecture reports
- risk_profile:
  reads:
    - targeted source, logs, traces, profiler output, tests, configs, and metrics
  writes:
    - none by default; WRITE_CODEBASE only after a bottleneck is selected and implementation is requested
  tools:
    - CALL_PROCESS for focused benchmarks, profilers, tests, static checks, and measurement scripts
  sensitive_resources:
    - credentials default deny; production traces/data require explicit boundary review and redaction
- entry_scene:
  - PREPARE

## Purpose
- Avoid optimizing guesses.
- Separate measurement, bottleneck selection, optimization choice, and validation.
- Recommend the smallest change that moves the target metric without sacrificing correctness.

## Workflow
1. Define the performance target:
   - metric
   - workload/input size
   - environment
   - acceptable threshold
2. Establish a baseline from existing evidence or a focused measurement.
3. Map the hot path or resource path.
4. Hold 2-3 bottleneck hypotheses only long enough to discriminate them.
5. Choose one primary bottleneck with evidence.
6. Compare optimization options:
   - algorithm/data structure
   - caching or batching
   - query/index/IO reduction
   - concurrency or backpressure
   - rendering/bundle/startup reduction
   - configuration/runtime tuning
7. Recommend or hand off the smallest optimization and its validation.

## Measurement Rules
- Prefer direct measurements over static intuition.
- Mark missing baseline or environment mismatch as `Unverified`.
- Do not report percentage improvements unless both before and after measurements are comparable.
- Do not trade correctness, data freshness, security, or accessibility for speed without explicit user acceptance.
- When measurements cannot run locally, provide the exact command, expected signal, and user-verification gap.

## Output Contract
Return only the sections needed:
- `performance_target`
- `baseline_evidence`
- `hot_path`
- `bottleneck_hypotheses`
- `primary_bottleneck`
- `optimization_options`
- `recommended_next_change`
- `validation_plan`
- `unverified_gaps`

## Cross-Skill Boundaries
- `workflow-implementation` owns applying the selected optimization in code.
- `workflow-refactor-safely` owns behavior-preserving refactors that prepare a performance change.
- `analysis-algorithm` owns pure algorithm/approach selection when no current performance symptom exists.
- `analysis-bug` owns correctness failures.
- `analysis-codebase` owns repo-wide performance/security/architecture report artifacts.

## Invocation Examples
Positive:
- "이 API가 느린 이유를 병목 중심으로 분석해줘."
- "메모리 사용량이 커졌는데 어디서 늘어나는지 봐줘."
- "렌더가 느린데 측정 가능한 개선 옵션을 비교해줘."

Negative:
- "이 failing test 고쳐줘." -> `workflow-bug-fix`
- "이 알고리즘 중 뭘 쓸지 비교해줘." -> `analysis-algorithm`
- "이 최적화 코드를 바로 적용해줘." -> `workflow-implementation` after bottleneck is selected
