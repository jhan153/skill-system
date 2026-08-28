---
name: test-oracle-design
description: Select and bound an authoritative test oracle for one named condition using exact results, invariants, metamorphic relations, differential references, approved golden baselines, statistical rules, or explicit human judgment. Preserve circularity, independence, tolerance, and proof-ceiling limits; never derive correctness from the implementation under test.
---

# Test Oracle Design

## Routing Card

- role: test_design_specialist
- intent_signature: test oracle, expected result, invariant, metamorphic, differential, golden baseline, oracle problem
- use_when: one test condition has materially competing oracle regimes, authority sources, tolerances, or independence limits
- do_not_use_when: the oracle is already authoritative, scenario coverage is primary, statistical design alone is primary, or test code is requested
- expected_inputs: named condition, SUT/path, accepted basis, candidate observations/references, tolerance needs, and failure consequence
- expected_outputs: oracle contract, authority/provenance, comparison rule, independence limits, falsifier, proof ceiling, and human-decision candidate when required
- context_targets:
  must_read:
    - condition, authority candidates, actual path, observed signal, and `references/testing_strategy_contract.md`
  read_if_needed:
    - mathematical/domain specification, reference implementation, accepted baseline, representative outputs, or `test-statistical-oracle`
  do_not_load_by_default:
    - full repo, unrelated outputs, broad research, mutable baselines, or credentials
- risk_profile:
  reads: bounded contracts, reference outputs, and representative observations
  writes: none
  tools: safe comparisons needed to discriminate oracle candidates
  sensitive_resources: private/reference data requires declared access and redaction
- entry_scene: PREPARE

## Oracle Regimes

Choose from the condition, not repository fashion:

- exact authoritative expected value;
- invariant or constraint/property;
- metamorphic relation across transformed inputs/runs;
- differential comparison to an independent implementation/version/platform;
- approved golden or snapshot with explicit provenance and update authority;
- statistical/distributional decision rule;
- scoped human judgment unit; or
- observation only when no defensible verdict exists.

## Workflow

1. State the positive condition, material falsifier, actual observable, and authority hierarchy.
2. Reject circular candidates: expected values computed by the same semantic implementation,
   implementation output promoted without approval, mocks that replace the behavior under test, or
   a production validator treated as proof of real-world representativeness.
3. Compare at most three oracle regimes by defect discrimination, independence, false-positive and
   false-negative consequence, reproducibility, diagnostic value, execution cost, and proof ceiling.
4. Define equivalence, tolerance, masking, aggregation, baseline update, and unavailable-result
   rules. Use `test-statistical-oracle` when repeated/ensemble inference is material.
5. If a human-owned choice changes verdict or accepted uncertainty and evidence cannot settle it,
   return a complete `plan-test-discovery` request candidate. Do not ask the human directly from
   this specialist or invent the answer.
6. Return one oracle contract and one defect/falsifier it must detect. If no oracle is defensible,
   classify the surface as observation/diagnostic capture rather than a Pass/Fail test.

## Output Contract

Return condition, selected oracle regime, authority/source, comparison rule, tolerance/decision
rule, independence analysis, accepted variability, diagnostic artifacts, falsifier, proof ceiling,
rejected candidates, discovery request candidate, and unresolved authority gaps.
