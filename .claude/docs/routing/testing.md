# Testing Routing

> Generated from canonical skill-local Routing Cards. Read only the matching section.

## `plan-test-discovery`

- role: support
- family: testing
- intent_signature: human-in-loop test decision, oracle discussion, tolerance approval, baseline approval, test discovery
- use_when:
  - `workflow-test-design` identifies one named condition that needs a human-owned judgment before a test contract can be completed
  - the user explicitly asks to decide how an executable or accepted externally contracted behavior should be judged or what uncertainty is acceptable
- do_not_use_when:
  - a canonical requirement, mathematical property, accepted interface contract, or observation already accepted by a named authority decides the field
  - the open question is product requirements, user behavior, algorithm choice, test implementation, production repair, or Human Test
- expected_inputs:
  - target snapshot and representative actual path, or an accepted external-contract boundary and revision
  - blocked Test Design condition IDs
  - admitted evidence, unresolved judgment, options, consequences, and recommendation
  - authority owner and optional Execution Handoff package/plan identity
- expected_outputs:
  - decision ledger with authority and accepted uncertainty
  - inline result or package-local `inputs/test-decisions.md`
  - `decision_ready` or explicit open status plus the required continuation boundary
- context_targets:
  must_read:
    - discovery request, target/condition IDs, evidence, options, and decision owner
    - `references/testing_stage_contract.md`
    - `references/testing_strategy_contract.md`
  read_if_needed:
    - `references/execution_handoff_input_contract.md` when a package or graph-mode node is bound
    - `references/test-decision-record.md` when persisting the result
    - `references/runtime_debugging_contract.md` when the human-owned decision changes debugger/dump/dynamic/graphics collection scope or cost, perturbation acceptance, sensitive-data handling, or the deliberately lowered proof ceiling; exact target/build/module/load-address/symbol identity match remains an evidence-validity rule and cannot be waived into a match
    - the smallest source, measurement, screenshot, recording, or artifact slice that distinguishes the options
  do_not_load_by_default:
    - full repository, full Plan/Handoff, unrelated requirements, raw production data, or credentials
- risk_profile:
  reads: bounded test basis, current observations, and decision-relevant artifacts
  writes: none by default; with explicit persistence or a bound package, only `inputs/test-decisions.md`
  tools: focused read-only observation and one human question at a time when decisions are dependent
  sensitive_resources: private data and external systems require their governing access and redaction boundary
- entry_scene: PREPARE

## `test-evidence-review`

- role: testing_evidence_gate
- family: testing
- intent_signature: review tests, false green, test quality, oracle audit, mutation adequacy, test evidence review
- use_when: a named test design/implementation/result needs a bounded credibility review before its evidence is consumed
- do_not_use_when: test design or implementation is requested, a concrete failing test must be repaired, broad code review is primary, or no bounded artifact/condition exists
- expected_inputs: test design/contract, test assets/result, target snapshot/path, authority refs, diagnostics, falsifier, and claimed proof ceiling
- expected_outputs: prioritized evidence-linked findings, condition-level credibility/limits, and exact design/implementation/authority handoff
- context_targets:
  must_read:
    - bounded test contract/assets/result, claimed condition, authority, actual path, and `references/testing_strategy_contract.md`
  read_if_needed:
    - target production owner/path, expected-value computation, fixture/generator, baseline history, run artifacts, or semantic-mutant observation
    - `references/runtime_debugging_contract.md` when the evidence includes a debugger stop, crash/core/minidump, symbols, dynamic diagnostic, concurrency trace, graphics capture, or device-loss artifact
  do_not_load_by_default:
    - full repo/test suite/history, unrelated product conditions, raw production data, or credentials
- risk_profile:
  reads: bounded test and target path plus decisive artifacts
  writes: none
  tools: focused static inspection and one safe non-debugger falsifier/readback when already authorized; runtime-debugging evidence review uses existing artifacts/session metadata only
  sensitive_resources: deny credentials and minimize production data
- entry_scene: PREPARE

## `test-oracle-design`

- role: test_design_specialist
- family: testing
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

## `test-replay-corpus`

- role: test_design_specialist
- family: testing
- intent_signature: replay test, recording test, captured fixtures, reality corpus, deterministic reproduction
- use_when: a named failure or regression needs production-path capture/replay or a versioned representative corpus
- do_not_use_when: synthetic data is sufficient and authoritative, exact oracle selection is primary, raw production capture is unauthorized, or implementation alone is requested
- expected_inputs: failure/condition, production capture point, loader/validator path, state history, privacy boundary, oracle ref, schema/build identity, and recurrence
- expected_outputs: capture/replay/corpus contract, provenance schema, sanitization/minimization rules, representativeness limits, and proof ceiling
- context_targets:
  must_read:
    - named condition, actual capture-to-replay path, data authority/privacy, oracle ref, and `references/testing_strategy_contract.md`
  read_if_needed:
    - production schemas/loaders/validators, representative failures, build/version metadata, storage limits, or existing fixture conventions
  do_not_load_by_default:
    - raw production datasets, credentials, full telemetry history, or unrelated corpus files
- risk_profile:
  reads: authorized schema/path metadata and minimum representative samples
  writes: none; `workflow-test-implementation` owns requested capture/replay/corpus assets
  tools: safe metadata/readback inspection only
  sensitive_resources: default deny raw private data; require minimization, sanitization, retention, and access ownership
- entry_scene: PREPARE

## `test-scenario-design`

- role: test_design_specialist
- family: testing
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

## `test-scope-selection`

- role: test_design_specialist
- family: testing
- intent_signature: test boundary, test level, SUT selection, unit versus integration versus system
- use_when: a named condition has materially competing SUT boundaries, observation boundaries, or test-level/profile classifications
- do_not_use_when: the boundary is already accepted, production module design is open, test scenarios/oracles are primary, or implementation is requested
- expected_inputs: material failure, accepted basis, current production path, candidate SUT boundaries, observable signal, and constraints
- expected_outputs: selected SUT/observation boundary, multi-axis test profile, preserved production boundary, and one falsifier
- context_targets:
  must_read:
    - named failure/condition, accepted basis, actual production path, and candidate observation points
    - `references/testing_strategy_contract.md`
  read_if_needed:
    - targeted callers, interface contracts, state/data flow, existing tests, and environment boundary
  do_not_load_by_default:
    - full repo, broad architecture maps, unrelated test inventory, or credentials
- risk_profile:
  reads: targeted owner/path/callers and existing test evidence
  writes: none
  tools: focused source/runtime inspection only
  sensitive_resources: production data and credentials denied without governing authority
- entry_scene: PREPARE

## `test-statistical-oracle`

- role: test_design_specialist
- family: testing
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

## `test-visual-regression`

- role: testing_design_or_evidence_specialist
- family: testing
- intent_signature: visual regression design, screenshot regression evidence, rendered golden test, pixel diff, visual replay
- use_when:
  - the caller or assigned node explicitly selects `design` to author a visual-regression contract for named states/viewports
  - the caller or assigned node explicitly selects `evidence` to capture/compare an accepted visual-regression contract
- do_not_use_when:
  - neither `design` nor `evidence` is explicitly selected
  - visual direction, exact design-target fidelity, or product-family coherence is primary; use `design-visual-regression`
  - accessibility, interaction semantics, responsive completeness, or subjective acceptance is the only condition
  - `evidence` lacks a rendered target, accepted contract, or accepted baseline identity
- expected_inputs:
  - selected mode and condition ID
  - for `design`: target snapshot or accepted external rendered-state contract, baseline authority/version, named states/viewports, and environment constraints
  - for `evidence`: accepted visual-regression contract ref, rendered target/current snapshot, and matching baseline identity
- expected_outputs:
  - `design`: visual-regression contract and implementation handoff, with no capture/diff/verdict
  - `evidence`: condition-scoped screenshot/diff evidence and verdict, with no redesign
  - explicit baseline, environment, and proof-ceiling gaps
- context_targets:
  must_read:
    - selected mode, condition, baseline/contract authority, state/viewports, and `references/testing_strategy_contract.md`
  read_if_needed:
    - font/assets/theme/renderer identity, animation/randomness controls, nearby capture tooling, or test-design handoff
  do_not_load_by_default:
    - unrelated routes/screens, mutable design sources, full visual history, private sessions, or credentials
- risk_profile:
  reads: rendered target or accepted external rendered-state contract, accepted baselines, and named capture state
  writes: `design` none; `evidence` screenshots and scoped diff artifacts only when explicitly requested; test code/baseline updates belong to `workflow-test-implementation`
  tools: `design` bounded read-only contract inspection; `evidence` browser/simulator/native capture and image comparison when available
  sensitive_resources: authenticated/private surfaces require explicit authority
- entry_scene: PREPARE

## `workflow-test-design`

- role: execution_primary
- family: testing
- intent_signature: test design node, test plan for executable behavior, oracle and scenario synthesis, 테스트 설계
- use_when:
  - the user requests a concrete test design artifact for an executable SUT or accepted external contract
  - an accepted Plan assigns a Test Design node after a minimum implementation, prototype, or external contract exists
  - multiple scenario, oracle, data, environment, or horizon decisions must be made before test code can be implemented
- do_not_use_when:
  - an authoritative implementation-ready test contract already exists; use `workflow-test-implementation`
  - the SUT is not executable and no accepted external contract exposes the required behavior
  - the open question is product requirements, algorithm selection, production repair, test-only implementation, or Human Test
- expected_inputs:
  - target snapshot and executable SUT/representative actual path, or accepted external-contract boundary/revision and intended observable signals
  - accepted requirements, invariants, behavior decisions, external contracts, or explicitly accepted characterization
  - known failures, representative data, environment constraints, and optional graph identity
- expected_outputs:
  - implementation-ready test contract and handoff
  - Core `test_design_result` when graph-mode identity is supplied
  - explicit human decision, testability, or authority gaps without fabricated defaults
- context_targets:
  must_read:
    - target snapshot, executable SUT/actual path or accepted external-contract path, accepted basis, and material failure risk
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
    - `test-visual-regression` in explicit `design` mode only when a rendered regression condition and accepted baseline/external contract exist
    - `references/runtime_debugging_contract.md` when a condition requires a debugger stop, crash/core/minidump, exact build and symbols, dynamic diagnostic, concurrency trace, graphics capture, or device-loss artifact
    - `references/execution_assurance_contract.md` when validation work itself has material maker/checker separation or standard/strict assurance requirements
  do_not_load_by_default:
    - full repo, all test methods, unrelated plans, raw production data, credentials, or every existing test
- risk_profile:
  reads: target code/path, accepted contracts, representative data/evidence, existing test conventions, and diagnostics
  writes: explicitly requested test-design artifact only; never test or production code
  tools: bounded read-only observation needed to distinguish design choices
  sensitive_resources: production captures and private data require governing access, minimization, and redaction
- entry_scene: PREPARE

## `workflow-test-implementation`

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
