---
name: test-statistical-oracle
description: Design a reproducible ensemble or distributional test oracle for stochastic, chaotic, simulation, optimization, and numerically variable software. Define the estimand, run/seed unit, workload, repetitions, uncertainty, decision rule, false-positive/negative tradeoff, diagnostics, and proof ceiling without inventing thresholds or treating one deterministic replay as population evidence.
---

# Test Statistical Oracle

## Routing Card

- role: test_design_specialist
- intent_signature: statistical test oracle, nondeterministic test, chaotic simulation test, seed ensemble, distributional regression
- use_when: a named software condition is inherently stochastic/chaotic or requires repeated-run distributional judgment
- do_not_use_when: an exact/invariant oracle is sufficient, scientific inference about a population is primary, no executable observation exists, or test implementation is requested
- expected_inputs: condition/failure, accepted basis, observable metric, run/seed/workload unit, representative environment/horizon, candidate threshold authority, and available observations
- expected_outputs: estimand and ensemble contract, decision rule or human-decision request candidate, uncertainty/error controls, diagnostics, and proof ceiling
- context_targets:
  must_read:
    - condition, SUT/path, observable, variability source, environment/horizon, authority, and `references/testing_strategy_contract.md`
  read_if_needed:
    - representative run data, seed policy, workload distribution, reference solver/version, performance constraints, or `test-oracle-design`
  do_not_load_by_default:
    - full research corpus, unrelated benchmarks, raw private datasets, or credentials
- risk_profile:
  reads: bounded run summaries and test-contract evidence
  writes: none
  tools: reproducible computation on supplied/authorized observations when needed to compare candidate rules
  sensitive_resources: preserve data governance and never expose raw private captures
- entry_scene: PREPARE

## Workflow

1. Define the estimand: metric/property, run/seed/workload unit, target distribution or relation,
   environment, horizon, and material correctness constraints. Separate chaotic trajectory
   divergence from a failure in the macroscopic property being judged.
2. Identify variability sources and which are controlled, sampled, stratified, or intentionally
   preserved. A fixed seed proves that trajectory only; it cannot replace ensemble evidence when
   seed variability is the risk.
3. Choose repetitions/seed set/workloads from the required error sensitivity, tail behavior,
   runtime cost, and recurrence. Record how the selection was obtained; do not optimize it against
   the current output until the test passes.
4. Define aggregation and uncertainty: mean/median, quantile/tail probability, interval, failure
   rate, distribution distance, trend/drift, or reference-relative rule. Include missing/timeout,
   outlier, warmup, multiple-comparison, and flaky-environment handling when material.
5. Bind the threshold or comparison rule to canonical authority. If the acceptable tail risk,
   tolerance, or false-positive/negative tradeoff belongs to a human, return a complete
   `plan-test-discovery` request candidate with observed options; never choose it silently.
6. Name a falsifier such as sign reversal, disabled constraint, zero iterations, excessive drift,
   or distribution shift that the rule must detect. Limit claims to the observed ensemble,
   workload, environment, and horizon.

## Output Contract

Return condition, estimand, analysis/run unit, variability model, seed/workload/repetition policy,
environment/horizon, aggregation/uncertainty, decision rule/authority, false-positive/negative
tradeoff, missing/outlier handling, diagnostics, falsifier, proof ceiling, discovery request
candidate, and unresolved data/authority gaps.
