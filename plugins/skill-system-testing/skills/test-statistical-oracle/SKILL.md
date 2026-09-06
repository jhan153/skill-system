---
name: test-statistical-oracle
description: Design ensemble/distributional test oracles for stochastic, chaotic, or numerically variable software, including simulations and optimization. Separate accepted normative external contracts from empirical choices requiring representative observations; one replay is not population evidence.
---

# Test Statistical Oracle

## Routing Card

- role: test_design_specialist
- family: testing
- intent_signature: statistical test oracle, nondeterministic test, chaotic simulation test, seed ensemble, distributional regression
- use_when: a named software condition is inherently stochastic/chaotic or requires repeated-run distributional judgment, with an accepted normative external contract or the representative observations needed for the selected decision
- do_not_use_when: an exact/invariant oracle is sufficient, scientific inference about a population is primary, neither authoritative contract nor required observations can frame the decision, or test implementation is requested
- expected_inputs: condition/failure, accepted basis or external-contract boundary/revision, observable metric, run/seed/workload unit, environment/horizon, candidate threshold authority, and representative observations when the selected choice is empirical
- expected_outputs: estimand and ensemble contract, decision rule or human-decision request candidate, uncertainty/error controls, diagnostics, and proof ceiling
- context_targets:
  must_read:
    - condition, SUT/path or accepted external-contract boundary/revision, observable, variability basis, environment/horizon, authority, and `references/testing_strategy_contract.md`
  read_if_needed:
    - representative run data, seed policy, workload distribution, reference solver/version, performance constraints, or `test-oracle-design`
  do_not_load_by_default:
    - full research corpus, unrelated benchmarks, raw private datasets, or credentials
- risk_profile:
  reads: accepted normative contract evidence and bounded run summaries when an empirical choice requires them
  writes: none
  tools: bounded reproducible computation from accepted contract assumptions or supplied/authorized observations when needed to compare candidate rules
  sensitive_resources: preserve data governance and never expose raw private captures
- entry_scene: PREPARE

## Admission And Evidence Basis

An accepted normative external contract may define the intended observable, distribution or
property, and decision authority before an executable SUT exists. Design against that exact
boundary/revision, keep contract-derived expectations distinct from measurements, and record the
missing runtime path as a later Test Implementation prerequisite rather than fabricating a run.

An empirical choice about current variance, tail behavior, performance, baseline, or threshold
requires representative observations. A normative distribution or approved error rule does not
prove the implementation's actual variability. If required observations or normative fields are
missing, return the exact gap; do not invent variance, sample results, thresholds, or statistics to
complete the design.

## Workflow

1. Bind the actual SUT path or accepted external-contract boundary/revision and define the estimand:
   metric/property, run/seed/workload unit, target distribution or relation, environment, horizon,
   and material correctness constraints. Separate normative assumptions from observed variability,
   and chaotic trajectory divergence from a failure in the macroscopic property being judged.
2. Identify variability sources and which are controlled, sampled, stratified, or intentionally
   preserved. An observed fixed-seed run covers that trajectory only; it cannot replace ensemble evidence when
   seed variability is the risk.
3. Choose repetitions/seed set/workloads from the required error sensitivity, tail behavior,
   runtime cost, and recurrence using the accepted contract or required representative observations.
   Record the derivation and its assumptions; do not optimize the selection against the current
   output until the test passes.
4. Define aggregation and uncertainty: mean/median, quantile/tail probability, interval, failure
   rate, distribution distance, trend/drift, or reference-relative rule. Include missing/timeout,
   outlier, warmup, multiple-comparison, and flaky-environment handling when material.
5. Bind the threshold or comparison rule to canonical authority. If the acceptable tail risk,
   tolerance, or false-positive/negative tradeoff belongs to a human, return a complete
   `plan-test-discovery` request candidate with options grounded in the accepted contract and, for
   empirical choices, the required representative observations.
6. Name a falsifier such as sign reversal, disabled constraint, zero iterations, excessive drift,
   or distribution shift that the rule must detect. Bound observation-based claims to the ensemble
   actually observed.

## Output Contract

Return condition, estimand, analysis/run unit, variability model, seed/workload/repetition policy,
environment/horizon, aggregation/uncertainty, decision rule/authority, false-positive/negative
tradeoff, missing/outlier handling, diagnostics, falsifier, proof ceiling, discovery request
candidate, and unresolved data/authority gaps, including later runtime prerequisites for contract-only
design. Identify which conclusions are contract-derived and which are supported by actual observations.
