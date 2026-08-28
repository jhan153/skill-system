---
name: workflow-test-design
description: Design an implementation-ready software test contract after a minimum executable SUT or accepted external contract exposes a representative path. Bind test basis, conditions, scenarios, data, oracle, environment, horizon, diagnostics, and proof ceiling; invoke `plan-test-discovery` only for a named human-owned judgment. Do not write test or production code.
---

# Workflow Test Design

## Routing Card

- role: execution_primary
- intent_signature: test design node, test plan for executable behavior, oracle and scenario synthesis, 테스트 설계
- use_when:
  - the user requests a concrete test design artifact for an executable SUT
  - an accepted Plan assigns a Test Design node after a minimum implementation, prototype, or external contract exists
  - multiple scenario, oracle, data, environment, or horizon decisions must be made before test code can be implemented
- do_not_use_when:
  - an authoritative implementation-ready test contract already exists; use `workflow-test-implementation`
  - the SUT is not executable and no accepted external contract exposes the required behavior
  - the open question is product requirements, algorithm selection, production repair, test-only implementation, or Human Test
- expected_inputs:
  - target snapshot, SUT, representative actual path, and observable signals
  - accepted requirements, invariants, behavior decisions, external contracts, or explicitly accepted characterization
  - known failures, representative data, environment constraints, and optional graph identity
- expected_outputs:
  - implementation-ready test contract and handoff
  - Core `test_design_result` when graph-mode identity is supplied
  - explicit human decision, testability, or authority gaps without fabricated defaults
- context_targets:
  must_read:
    - target snapshot, SUT/actual path, accepted basis, and material failure risk
    - `references/testing_stage_contract.md`
    - `references/testing_strategy_contract.md`
  read_if_needed:
    - applicable `inputs/test-decisions.md` decided rows and their pinned Plan scope
    - `references/execution_item_view.md` in graph mode or when the result crosses another Workflow/plugin
    - `test-scope-selection` for a material level/boundary/profile choice
    - `test-scenario-design` for nontrivial scenario, state, sequence, data, or horizon coverage
    - `test-oracle-design` for competing oracle regimes or independence questions
    - `test-statistical-oracle` for stochastic, chaotic, ensemble, or distributional behavior
    - `test-replay-corpus` for capture, recording, replay, or corpus provenance
    - `test-visual-regression` only when a rendered regression condition and accepted baseline exist
  do_not_load_by_default:
    - full repo, all test methods, unrelated plans, raw production data, credentials, or every existing test
- risk_profile:
  reads: target code/path, accepted contracts, representative data/evidence, existing test conventions, and diagnostics
  writes: explicitly requested test-design artifact only; never test or production code
  tools: bounded read-only observation needed to distinguish design choices
  sensitive_resources: production captures and private data require governing access, minimization, and redaction
- entry_scene: PREPARE

## Core Cards

- produces: `references/core-execution-items-v1/cards/test_design_result.md`
- consumes: `references/core-execution-items-v1/cards/implementation_result.md`

## Stage Boundary

Apply `references/testing_stage_contract.md`. This Workflow owns one Test Design node or direct
design artifact. It may use narrow testing specialists for already identified subquestions, but it
does not automatically run a skill chain, start Test Implementation, edit Plan/Handoff, select a
successor, or wait for Human Test.

Test Design begins after a minimum executable SUT or accepted external contract exists. It does
not require an exact output oracle: authoritative invariants, metamorphic relations, differential
references, statistical decision rules, or explicitly accepted human judgment may define bounded
conditions. Current implementation output remains observation unless accepted by a named owner.

## Workflow

1. Bind the target snapshot, test object and largest real boundary, accepted basis, failure risk,
   representative path, observable signal, and non-goals. State one positive plus one material
   negative, edge, or falsifying condition.
2. Build a multi-axis test profile instead of assigning one overloaded test label: execution
   mode, level, purpose, design technique, change relation, data/oracle strategy, environment, and
   horizon. Use `test-scope-selection` only when this boundary/profile is materially open.
3. Derive the smallest scenario set that discriminates the conditions. Preserve real input/data
   provenance and production validation/canonicalization. Use `test-scenario-design` or
   `test-replay-corpus` only for a distinct scenario or corpus problem.
4. Bind each condition to an oracle authority and proof ceiling. Prefer exact or invariant
   authority where valid; use metamorphic, differential, statistical, golden, or direct human
   judgment only under their actual contracts. Use `test-oracle-design` or
   `test-statistical-oracle` when those choices are material.
5. If one named condition requires a human-owned judgment that admitted evidence cannot resolve,
   prepare the complete Discovery request required by `references/testing_stage_contract.md` and
   invoke `plan-test-discovery`. Send one question and yield without polling. In an approved graph,
   resume only after `plan-execution-handoff` pins the decided IDs through an explicit Plan revision,
   synchronizes Handoff, and delivers the resume follow-up. Direct or still-proposed work may resume
   from a decided record within its unchanged accepted envelope. Never reinterpret an open/assumed
   row as authority.
6. Specify testability prerequisites: inputs, clock/seed, viewport/assets, workload, repetitions,
   duration/state history, instrumentation, diagnostic artifacts, and accepted variability. A
   missing production hook or representative path is a testability gap, not permission to invent a
   test-only semantic model.
7. Produce one bounded implementation handoff naming condition IDs, test-only write scope,
   forbidden design changes, existing framework/runner, required artifacts, and the falsifier that
   must challenge the implemented test.
8. Read back every designed condition against its basis and actual path. Emit Core
   `test_design_result` in graph mode; never claim that the test exists or the product passes.

## Discovery Request Gate

Discovery is not a fallback for low confidence. Invoke it only when a choice belongs to a human or
declared domain authority and changes verdict, proof ceiling, accepted uncertainty, or qualitative
judgment. Supply blocked condition IDs, target snapshot, current evidence, 2–4 exclusive options,
their detection/miss tradeoffs, recommendation, and independent work remaining.

If the answer changes the positive outcome, production owner/boundary, DAG, or completion oracle,
stop the current design and require a sibling Plan through Scope Admission. A tolerance, baseline,
or judgment choice within the already accepted test envelope may resume the same node after the
required Plan revision.

## Output Contract

Return only applicable fields:

- `test_design_scope`
- `test_design_snapshot`
- `target_snapshot`
- `test_profile`
- `test_basis_refs`
- `condition_ids`
- `actual_path`
- `oracle_contracts`
- `environment_and_horizon`
- `diagnostic_and_falsifier_contract`
- `implementation_handoff`
- `proof_ceiling`
- `human_decision_refs`
- `unresolved_decisions_or_testability_gaps`
- `artifact_refs` and `evidence_refs` for the full scenario/data design and decisive observations
- Core `test_design_result` when graph-mode identity is supplied
