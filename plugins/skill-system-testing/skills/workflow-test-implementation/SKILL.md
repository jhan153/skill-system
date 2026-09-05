---
name: workflow-test-implementation
description: Implement and execute a complete test contract as test-only code, fixtures, generators, baselines, capture/replay tooling, runners, and diagnostic artifacts. Consume `test_design_result` when design was material, or admit a direct authoritative contract for simple tests. Never invent or weaken the oracle, change production code, or equate Workflow completion with product Pass.
---

# Workflow Test Implementation

## Routing Card

- role: execution_primary
- family: testing
- intent_signature: implement tests, add unit/integration/system tests, implement replay or screenshot test, 테스트 구현
- use_when:
  - the user requests test-only implementation or execution and the complete test contract is already authoritative
  - an accepted Plan assigns a Test Implementation node with a Core `test_design_result` or complete inline contract
- do_not_use_when:
  - a material SUT, basis, scenario, oracle, tolerance, baseline, environment, or horizon choice remains open
  - production behavior or testability code must be changed, a concrete failure must be repaired, or Human Test is primary
  - the request is only to review existing test evidence
- expected_inputs:
  - target snapshot and representative actual path
  - Core `test_design_result` or complete inline authoritative test contract
  - test-only write scope, existing framework/runner, environment authority, and available diagnostics
- expected_outputs:
  - implemented test assets and honest condition-scoped execution evidence
  - Core `test_implementation_result` in graph mode
  - explicit design/testability/environment gaps without weakened assertions or fabricated success
- context_targets:
  must_read:
    - target snapshot, test contract, actual production path, and test-only write boundary
    - `references/testing_stage_contract.md`
    - `references/testing_strategy_contract.md`
  read_if_needed:
    - existing nearby test conventions, runner/config, fixtures, baselines, and diagnostics
    - `references/execution_item_view.md` in graph mode or when the result crosses another Workflow/plugin
    - `test-replay-corpus`, `test-visual-regression` in explicit `evidence` mode, or another Plan-selected testing specialist only when the contract names that evidence surface
    - `references/runtime_debugging_contract.md` when the accepted contract requires a debugger stop, crash/core/minidump, build/symbol manifest, dynamic diagnostic, concurrency trace, graphics capture, or device-loss artifact
    - `references/execution_assurance_contract.md` when test implementation or evidence consumption has material maker/checker separation or standard/strict assurance requirements
  do_not_load_by_default:
    - full repo, unrelated tests, broad design reports, open human decisions, raw production data, or credentials
- risk_profile:
  reads: target production path, accepted test contract, nearby tests/config, and observed output
  writes: test-only source, fixtures, corpus metadata, approved baselines, test config/runners, and diagnostic artifacts within explicit scope
  tools: focused build/test/capture/replay/measurement commands required by the accepted contract
  sensitive_resources: external services, devices, private captures, destructive state, and credentials require explicit authority
- entry_scene: PREPARE

## Core Cards

- produces: `references/core-execution-items-v1/cards/test_implementation_result.md`
- consumes: `references/core-execution-items-v1/cards/test_design_result.md`, `references/core-execution-items-v1/cards/known_bug_record.md`

## Stage Boundary

Apply `references/testing_stage_contract.md`. This Workflow owns test-only implementation and the
assigned scoped execution. It never changes production code, repairs a discovered production
failure, edits Plan/Handoff, selects a successor, or performs Human Test. A test condition's
verdict and this Workflow's completion are separate.

## Direct Admission Gate

Test Design may be skipped only when all applicable fields are already authoritative:

- SUT/test boundary and representative actual path;
- test basis and condition IDs;
- positive plus material negative/edge cases;
- inputs/data provenance and production validation path;
- expected result, property, relation, distribution, approved baseline, or human judgment owner;
- tolerance/decision rule and proof ceiling;
- environment, instrumentation, sequence, and horizon; and
- existing implementation surface or explicit permission for the bounded test-only assets.

If any field needs a substantive choice, return `design_required` with the exact missing owner.
Do not perform hidden Test Design inside this Workflow.

## Workflow

1. Pin the target snapshot, accepted Test Design or inline contract, condition IDs, actual path,
   allowed test-only files, forbidden production paths, runner/environment, and expected
   diagnostics. Observe current-run Known Bug exclusions without reopening them.
2. Inspect the nearest existing test patterns and choose the smallest implementation that realizes
   the contract. Do not add a framework, mock family, fixture system, corpus, baseline registry, or
   dependency unless the accepted contract requires it.
3. Implement the prescribed inputs, scenarios, oracle, environment/horizon controls, and
   diagnostics. Reuse production loaders, validators, canonicalizers, composition roots, or public
   boundaries named by the design; a test-only semantic model or bypass is a contract violation.
   When visual evidence is assigned, invoke `test-visual-regression` only in frozen `evidence` mode;
   a missing visual contract is `design_required`, never permission for hidden redesign.
4. Run the smallest condition-matched command or observation. Preserve expected/actual values,
   seed/state history, screenshots/diffs, traces/profiles/dumps, build identity, and selected-source
   readback required by the contract. For an accepted runtime-debugging capture, also preserve exact
   binary/module/symbol/device/tool identity, included and missing state, capture filters, and
   debugger/instrumentation perturbation under `references/runtime_debugging_contract.md`. Execute
   only the accepted trigger, probe/location/range, commands, and capture scope mechanically. If the
   observation requires a new watchpoint, breakpoint, step, replay query, shader invocation, or
   capture range, stop and return the bounded evidence/handoff through `execution_summary` and
   artifact/evidence refs. Capture does not authorize target-state mutation or a root-cause verdict.
5. Challenge the test with its named falsifier or semantic mutant when safe and authorized. A
   passing happy path without the required falsifier remains incomplete test implementation.
6. Review design conformance: no weakened assertion, widened tolerance, reduced horizon, silently
   replaced baseline, masked meaningful variability, mock-substituted SUT, or implementation-derived
   expected result. Return a test-contract conflict instead of manufacturing Green.
7. Apply the completion gate before reporting. A material design/authority/testability/environment
   conflict, missing required test asset, or required falsifier that was not implemented and
   attempted returns lifecycle `not_produced` with the exact gap and emits no Core card. When the
   assigned implementation contract is complete, report condition results within their actual
   path/environment/horizon and emit Core `test_implementation_result` in graph mode. A completed
   test may honestly observe `fail|inconclusive|unavailable`; those condition verdicts are evidence
   for the Coordinator or direct owner and never start repair automatically.

## Completion Gate

Core `test_implementation_result` means the assigned test-only implementation contract and required
falsifier are complete, not that every condition passed. Non-material unresolved or optional
conditions may remain explicit in the payload. A required missing oracle, target path, testability
hook, environment, baseline authority, or falsifier makes the result `not_produced`; do not emit a
partial card, weaken the contract, or relabel the missing obligation as a product failure.

## Evidence Rules

- A replay proves repeatable stimulation and observed output, not correctness without an oracle.
- A screenshot proves visible pixels/framing for its state and viewport, not interaction,
  semantics, accessibility, responsiveness, or business correctness.
- A statistical result proves the declared metric under its recorded ensemble and decision rule,
  not other seeds, workloads, horizons, or populations.
- A mock, fake, fixture, or agent-authored expected value proves only its encoded boundary.
- `coverage` shows execution of counted structure, not assertion quality or semantic correctness.
- A debugger stop, dump, dynamic report, trace/replay, or graphics capture proves only its recorded
  state/events under verified identity and capture scope. Testing preserves the artifact and a
  bounded handoff; it does not infer the unique cause.

## Output Contract

Return only applicable fields:

- `implementation_scope`
- `test_design_result_ref`
- `inline_contract_refs`
- `target_snapshot`
- `test_asset_snapshot`
- `changed_test_artifacts`
- `condition_results`
- `execution_summary`
- `falsifier_result`
- `design_conformance`
- `proof_ceiling`
- `known_bug_exclusions`
- `review_slice`
- `unresolved_design_testability_or_environment_gaps`
- `artifact_refs` and `evidence_refs` for diagnostics and run artifacts
- Core `test_implementation_result` when graph-mode identity is supplied
