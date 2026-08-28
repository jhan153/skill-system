---
name: test-scenario-design
description: Derive the smallest discriminating positive, negative, edge, state, sequence, data, load, and horizon scenario set for accepted test conditions and an actual SUT path. Preserve authority and data provenance; do not invent semantic expectations, choose an open oracle, or implement the tests.
---

# Test Scenario Design

## Routing Card

- role: test_design_specialist
- intent_signature: test cases, scenario matrix, boundary cases, state transitions, sequence and horizon coverage
- use_when: accepted conditions need nontrivial scenario/data/state/sequence/horizon derivation
- do_not_use_when: test basis or oracle authority is open, one obvious case suffices, a corpus/replay system is primary, or implementation is requested
- expected_inputs: accepted condition IDs, SUT/path, input/state domains, oracle contract, representative usage/failures, environment, and evidence budget
- expected_outputs: minimal traceable scenario set, coverage rationale, data provenance, horizon, diagnostics, and excluded combinations
- context_targets:
  must_read:
    - accepted conditions/oracle, actual path, input/state domains, and `references/testing_strategy_contract.md`
  read_if_needed:
    - interface/state contracts, real failure cases, boundary partitions, workload model, or existing nearby scenarios
  do_not_load_by_default:
    - full test suite, unrelated requirements, broad production history, or credentials
- risk_profile:
  reads: conditions, targeted path/state/data, and representative failures
  writes: none
  tools: bounded enumeration or safe observation only
  sensitive_resources: real data must retain provenance and governing minimization/redaction
- entry_scene: PREPARE

## Workflow

1. Trace every condition to authority, SUT boundary, observable, oracle, and proof ceiling. Stop if
   any semantic field is materially open.
2. Partition only meaningful input, state, sequence, configuration, workload, and time dimensions.
   Use equivalence and boundaries, decision rules, state transitions, pairwise/combinatorial
   selection, error/fault propagation, history accumulation, or experience-based cases as their
   risk requires.
3. Include at least one positive and one material negative, edge, or disconfirming scenario.
   Prefer captured real failures and production-valid inputs over test-only semantic data.
4. Record preconditions, stimulus/action, data provenance, environment, sequence/horizon,
   expected observation/oracle ref, diagnostics, and cleanup/side-effect boundary per scenario.
5. Remove redundant cases only when they exercise the same material partition, path, oracle, and
   horizon. Coverage counts and pairwise breadth never replace semantic discrimination.
6. Return excluded combinations with risk/cost justification and one scenario that would expose a
   shallow happy-path suite.

## Output Contract

Return condition-to-scenario matrix, partitions/boundaries, positive/negative/edge cases,
state/sequence/horizon cases, data provenance, environment, oracle refs, diagnostics, excluded
combinations, coverage rationale, falsifier scenario, and unresolved gaps.
