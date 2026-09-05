# Execution Workflow Routing

> Generated from canonical skill-local Routing Cards. Read only the matching section.

## `workflow-bug-fix`

- role: primary
- family: workflow
- intent_signature:
  - bug/failing-test/build/runtime/regression fix; broken behavior repair
- use_when:
  - the user requests a bounded repair of an observed or reproducible defect in an already-implemented accepted production contract and expects verification afterward, whether the cause is known or still needs proportional diagnosis.
  - a Plan/Coordinator dispatches an explicit `BF1` or `BF2` node with `node_id`, `round`, `source_review_item_ref`, concrete source findings, and an accepted repair contract that the intervention preserves.
  - a direct standalone repair under the same accepted repair contract resumes after one locally reviewed attempt and still has one bounded round available.
- do_not_use_when:
  - diagnosis-only with no repair request, full static code review/disposition, Plan or Handoff mutation, successor selection, a Known Bug already excluded for the current run, first implementation or explicit production-mechanism replacement, an unresolved algorithm/model/behavior decision, ordinary feature work, or validation-only work.
- expected_inputs:
  - observed symptom/original signal, already-implemented accepted repair contract, material expected condition, available oracle or canonical source, reproduction context, genuine same-contract attempt history, and, in DAG mode, assigned node/round/source-review identity plus concrete findings
- expected_outputs:
  - after semantic admission, one `bug_fix_result` containing attempt history, changed snapshot/review anchor or an explicit no-change result, original-signal observation, actual-path readback, visible attempt status, and an optional non-final Known Bug candidate; on owner-kind mismatch, lifecycle `not_produced` with no card or attempt
- context_targets:
  must_read:
    - original failure, material expected condition, implicated production owner/path, and repository instructions
  read_if_needed:
    - canonical input/source, caller/state flow, boundary readback, existing tests, config/manifests, and validation contract
    - `references/database_persistence_transparency_contract.md` when the bounded repair changes database schema, ORM/ODM mapping, query, migration, transaction, or data-access-boundary behavior
    - `references/identifier_readability_principle.md` when the assigned failure or review finding is an identifier-readability defect, or the bounded intervention must rename a related identifier set
    - `workflow-implementation` paradigm references as non-owning shape context only after semantic admission confirms that the accepted production contract stays unchanged
    - `references/execution_item_contract.md` in DAG mode or whenever a repair result/candidate crosses a Workflow, Coordinator, Plan/Handoff, or plugin boundary
    - `references/runtime_debugging_contract.md` when a supplied `debugging_result` must be consumed or the repair diagnosis uses a debugger, crash/core/minidump, symbols/unwind, dynamic diagnostics, concurrency trace, graphics capture, or device-loss artifact
    - select only the matching detailed runtime lane: `references/runtime-debugging/debugging-signal-and-causal-loop.md`, `references/runtime-debugging/live-debugger-operation.md`, `references/runtime-debugging/crash-dump-symbols-and-unwind.md`, `references/runtime-debugging/dynamic-temporal-and-concurrency-debugging.md`, or `references/runtime-debugging/graphics-debugging.md`
    - `references/causal-diagnosis.md` when the cause is unclear, recurring, intermittent, high-risk, or needs a discriminator before repair
    - `references/attempt-and-known-bug.md` whenever a prior repair attempt exists or the bug sits inside a graph/handoff
    - `references/execution_assurance_contract.md` when a repair has material maker/checker separation or destructive, auth/security, schema/data, infrastructure, external-write, or broad-refactor risk
  do_not_load_by_default:
    - full repo/memory, broad reports, unrelated history, raw production data, or credentials
- risk_profile:
  reads: failure output, production source/callers/state, tests/config, and validation/readback evidence
  writes: DAG mode exactly one semantically admitted contract-preserving intervention; standalone mode at most two locally reviewed interventions for the same problem and accepted repair contract
  tools: reproduction, focused diagnostics, diff inspection, one original-signal observation after an intervention, and actual-path readback
  sensitive_resources: deny credentials; external or destructive reproduction needs explicit boundary review
- entry_scene:
  - PREPARE

## `workflow-code-review`

- role: review_gate
- family: workflow
- intent_signature: static code review, state/flow/reachability review, dynamic diagrams, optional design conformance, 정적 코드 리뷰
- use_when: review bound production or test code before PR/integration through source-derived models, with or without an authoritative design baseline.
- do_not_use_when: mapping-only (`analysis-codebase-map`), lightweight style/naming feedback, repair, runtime validation, production test-oracle/evidence review, or Plan/Handoff editing is primary.
- expected_inputs: exact snapshot/diff identity, change intent and material changed effects, review slice, code contracts/invariants, optional accepted architecture/UI/Test Design baseline, Known Bug exclusions, and optional node/round identity
- expected_outputs: risk-selected Mermaid evidence, review coverage and ceiling, blocking findings, advisories, deferred items, and a standalone or Core static disposition
- context_targets:
  must_read:
    - exact implementation slice, repository instructions, and `references/static_code_review_contract.md`
    - one representative path plus the material edge/failure/cancel/compensation paths selected by the activated risk axes; these are a minimum, not a coverage ceiling
    - supplied node/round and Known Bug exclusions; never full Plan/Handoff
  read_if_needed:
    - only callers, registrations, state owners, configuration, or decisions that can change a material finding; read tests only when the reviewed artifact is test implementation or an existing test is necessary direct contract/caller evidence
    - `references/architecture_design_contract.md` when an accepted architecture design is supplied
      as a conformance baseline or the bound review explicitly includes architecture-delta
      conformance
    - `references/programming_paradigm_contract.md` when an accepted architecture or atomic
      boundary baseline contains a target-relevant programming-paradigm or adjacent-model
      application, or the bound Implementation result supplies a task-local application and
      `paradigm_conformance`; after that base contract, load only its selected files under
      `references/programming-paradigms/`
    - `references/maintainable_code_principles.md` when maintainability is a material review criterion or the diff materially changes ownership, abstraction, invariant/effect boundaries, conventions, or verification
    - `references/database_persistence_transparency_contract.md` when the bound diff changes database schema, mapping, query, migration, transaction, or data-access ownership
    - `references/identifier_readability_principle.md` when related identifiers materially obstruct state, flow, ownership, or effect tracing, or identifier-readability conformance is explicitly in the bound review scope; never activate this Workflow for lightweight naming feedback alone
    - `references/runtime_debugging_contract.md` when the diff changes crash/dump capture, symbol/build manifests, debugger hooks, dynamic-diagnostic integration, trace/replay capture, graphics validation/markers, or device-loss diagnostics
    - `references/execution_item_contract.md` when node/round identity is supplied or the compact result will cross a Workflow, Coordinator, Plan/Handoff, or plugin boundary
    - `references/testing_stage_contract.md` and `references/testing_strategy_contract.md` when reviewing a Core `test_implementation_result` against a `test_design_result`
    - load only applicable baseline and references: `references/model-comparison.md` for Mermaid mechanics; `references/finding-handoff.md` for standalone/Core presentation
  do_not_load_by_default:
    - unrelated source/design artifacts or runtime evidence
- risk_profile:
  reads: targeted code and directly relevant contract, baseline, ownership, or rationale evidence
  writes: none; the Coordinator alone records results in Handoff
  tools: focused static inspection and risk-selected Mermaid construction/rendering
  sensitive_resources: credentials denied; tests/runtime and code/Plan mutation require another owner
- entry_scene: PREPARE

## `workflow-dependency-upgrade`

- role: primary
- family: workflow
- intent_signature:
  - dependency/package/framework/SDK/runtime/lockfile upgrade; 의존성 업그레이드; 패키지 업데이트
- use_when:
  - the requested implementation centers on upgrading, pinning, replacing, or migrating dependency state and only the compatibility changes it requires.
- do_not_use_when:
  - ordinary feature work, choice analysis without edits, comments/docs-only work, validation-only planning, or security/release verdicts is primary.
- expected_inputs:
  - target and desired version/policy, package manager, canonical manifests/lockfiles, affected integrations, and allowed process/network boundary
- expected_outputs:
  - bounded dependency-state and migration changes, selected-version/path evidence, scoped validation, unresolved conditions, and rollback
- context_targets:
  must_read:
    - request, canonical manifests/lockfiles, current resolution, and affected production config/call sites
  read_if_needed:
    - authoritative release/migration contract, dependency graph, build/CI output, generated code, or actual integration readback
    - `references/execution_item_contract.md` when a concrete compatibility failure is delegated to Bug Fix and the upgrade owner must consume repair/review/Known Bug items
    - `references/execution_assurance_contract.md` when the upgrade has material maker/checker separation or auth/security, schema/data, infrastructure, external-write, destructive, or broad-migration risk
    - `workflow-implementation` paradigm references as non-owning shape context when the requested/required migration names a paradigm or implementation model; `workflow-dependency-upgrade` remains the migration owner
  do_not_load_by_default:
    - full repo/memory, unrelated dependency trees/reports, credentials, or raw production data
- risk_profile:
  reads: dependency state, integration path, authoritative contract, and validation output
  writes: scoped manifests/lockfiles plus only required config and production migration
  tools: package-manager resolution/update and condition-matched build/runtime checks
  sensitive_resources: deny credentials; network, private registries, lifecycle scripts, and destructive cleanup require their governing boundary
- entry_scene:
  - PREPARE

## `workflow-implementation`

- role: primary
- family: workflow
- intent_signature:
  - direct implementation
  - code change
  - add production-coupled regression tests
  - implement feature
  - 구현
- use_when:
  - the user asks for a concrete production code, script, API, config, or build change, including bounded regression tests that are part of that production slice.
  - the positive output first implements or explicitly replaces an accepted production algorithm, model, backend, canonical data/ownership flow, or implementation contract, even when an observed failure or review finding motivated the change.
  - requirements are sufficient for a current-turn implementation slice.
  - the task is ordinary development work not already owned by a narrower specialist.
- do_not_use_when:
  - the request is to coordinate or advance an approved Plan rather than implement one bounded node; the Orchestrator follows the copied Plan/Handoff contract.
  - the requested intervention is a semantically admitted bounded repair of a concrete defect in an already-implemented accepted production contract; use `workflow-bug-fix`. A failure signal alone does not exclude this Workflow.
  - the user asks for behavior-preserving rename, move, extract, collapse, simplify, or restructure work; use `workflow-refactor-safely`.
  - the task is now primarily a first or repeated bounded repair under the same accepted repair contract; use `workflow-bug-fix` with its preserved genuine attempt history. A newly accepted production-mechanism replacement is not another repair round.
  - the user wants a causal source/runtime explanation of existing code; use `report-implementation-explainer`.
  - an existing capability's product-facing behavior is still undecided and the user asks to resolve it; use `plan-behavior-discovery`.
  - the request is pure analysis, planning, review, validation-only, or other report generation.
  - the requested outcome is standalone Test Design or test-only implementation/execution; use `workflow-test-design` or `workflow-test-implementation`.
- expected_inputs:
  - requested behavior or change
  - relevant repository files and existing local patterns
  - explicit programming-paradigm, data-layout, execution-model, or compile-time/runtime choices when available
  - explicit constraints, non-goals, and validation expectations when available
- expected_outputs:
  - scoped production-path change, condition-bound evidence, remaining gaps, and user-verification needs
- context_targets:
  must_read:
    - current implementation request
    - repository instructions such as `AGENTS.md`
    - target files or nearest existing patterns for the requested behavior
  read_if_needed:
    - adjacent callers, canonical data/source owner, package manifest, or validation contract
    - active plan only when explicitly referenced as task input
    - `references/architecture_design_contract.md` when an accepted architecture design is input or
      the implementation slice crosses several module, data/state, runtime/failure, integration,
      deployment, or trust boundaries governed by one design
    - `references/boundary_decision_contract.md` when an accepted boundary decision is input or the implementation materially creates, moves, merges, or splits an owner/module/API/adapter/state boundary
    - `references/maintainable_code_principles.md` when maintainability is explicit or the change materially affects ownership, abstraction, invariants, effects, conventions, or verification
    - `references/database_persistence_transparency_contract.md` when adding or changing database schema, ORM/ODM mapping, query, migration, transaction, or data-access-boundary behavior
    - `references/identifier_readability_principle.md` when implementation introduces or renames a related identifier set in repository-owned code and repository conventions or domain terms do not already decide a clearly distinguishable shape
    - `references/runtime_debugging_contract.md` when implementing crash/dump capture, build/symbol publication, debugger hooks, dynamic-diagnostic or trace/replay integration, graphics validation/markers, or device-loss diagnostics
    - `references/execution_item_view.md` when a delegated node result will cross into Code Review, a Coordinator, Plan/Handoff, or another plugin
    - `references/programming_paradigm_contract.md` when an accepted architecture contains a
      programming-paradigm or adjacent-model pattern application, an accepted atomic boundary has
      `paradigm_constraints`, the user names/supplies a paradigm/model, asks to combine approaches,
      or a local choice may change state/effect ownership, data layout, compile/runtime extension,
      dispatch, or execution architecture
    - after that base contract, only the selected files under
      `references/programming-paradigms/`, followed by the matching local method files when concrete
      realization needs them
    - `references/paradigm-composition.md` only after the shared paradigm contract selects the
      relevant axis/application and concrete implementation needs one or more detailed method
      profiles; then load only the files routed by that index
    - `references/delivery_slice_contract.md` when any requested change needs multiple executable batches, including a wide migration or non-feature decomposition
    - `references/execution_assurance_contract.md` when maker/checker separation, standard/strict assurance, or high-risk rollback/readback is material
  do_not_load_by_default:
    - full repo
    - full memory bank
    - broad architecture reports
    - unrelated plans or transcripts
- risk_profile:
  reads:
    - targeted source, callers, tests, configs, manifests, and observed output
  writes:
    - WRITE_CODEBASE for the requested implementation scope
  tools:
    - CALL_PROCESS for focused build, test, lint, typecheck, smoke, or static validation commands
  sensitive_resources:
    - credentials default deny; destructive, network, data, or external-side-effect work requires explicit boundary review
- entry_scene:
  - PREPARE

## `workflow-prototype`

- role: primary
- family: workflow
- intent_signature: one bounded product or engineering question answered by a runnable disposable artifact
- use_when:
  - the user explicitly requests a prototype or spike and can name, or safely delegate, the decision it must inform.
  - observing UI variants or exercising a small state/logic model is cheaper and more discriminating than more discussion.
- do_not_use_when:
  - the task is open-ended ideation, requirements discovery, ordinary production implementation, bug work, validation-only work, or a behavior-preserving refactor.
  - the desired claim requires representative load, production data, security review, accessibility audit, concurrency evidence, or real integration behavior.
- expected_inputs: one question, decision owner, discriminating observation, target project/runtime, budget/stop, write boundary, retention boundary, and excluded claims
- expected_outputs: isolated runnable prototype, one exact launch instruction, observation guide, bounded verdict or pending-decision state, proof ceiling, retention status, and production handoff
- context_targets:
  must_read:
    - current question and target decision
    - repository instructions and the smallest relevant route/module/runtime path
    - local run command, components/tooling, and data/state shape needed for a representative observation
  read_if_needed:
    - accepted behavior decisions, safe fixtures, nearby prototypes, or the exact external boundary being stubbed
  do_not_load_by_default:
    - full repository, broad plans, unrelated design system internals, production data, credentials, or live mutation paths
- risk_profile:
  reads: scoped target context and representative safe data/state shapes
  writes: isolated prototype files within the authorized boundary; optional branch/worktree only when repository policy permits it; no cleanup or deletion without explicit authorization
  tools: host runtime plus the narrowest build, preview, browser, terminal, file-open, or smoke operation needed to observe the question
  sensitive_resources: deny credentials and production data; stub external writes unless that boundary is the explicit question and separately authorized
- entry_scene: PREPARE

## `workflow-refactor-safely`

- role: primary
- family: workflow
- intent_signature:
  - safe/behavior-preserving refactor; rename/move/extract/collapse; 안전한 리팩터링
- use_when:
  - the user requests a production-code rename, move, extraction, collapse, simplification, or restructure with behavior preserved.
- do_not_use_when:
  - behavior/feature change, concrete bug repair, design-only judgment, validation-only work, comments/docs-only change, repeated same-signature failure, or deletion of unreachable/obsolete code without live structural changes is primary.
- expected_inputs:
  - structural goal, material preservation conditions and authority, target production owner/path, callers, and available observations
- expected_outputs:
  - scoped contract, one production batch, changed artifacts/callers, actual-path evidence, unresolved conditions, and rollback
- context_targets:
  must_read:
    - refactor request, target production source/callers, and public/canonical/observed behavior contract
  read_if_needed:
    - relevant tests, actual readback, design decision, config/manifests, source selection, or prior failure output
    - `references/boundary_decision_contract.md` when an accepted boundary decision is input or the refactor materially moves, extracts, merges, splits, or collapses a boundary
    - `references/maintainable_code_principles.md` when maintainability is an explicit goal or the batch materially changes intent locality, ownership, abstraction, invariant/effect boundaries, conventions, or verification
    - `references/identifier_readability_principle.md` when the refactor renames a related production identifier set or identifier similarity is the stated structural problem
    - `references/execution_item_contract.md` when a concrete failure is delegated and repair/review/Known Bug items return to the refactor owner
    - `references/execution_assurance_contract.md` when maker/checker separation or destructive, auth/security, schema/data, infrastructure, external-write, or broad-refactor risk requires standard/strict assurance
    - `workflow-implementation` paradigm references as non-owning shape context when the user/preservation contract names a paradigm, data layout, execution model, construction rule, or other target shape; `workflow-refactor-safely` remains the preservation owner
  do_not_load_by_default:
    - full repo/memory, unrelated reports/plans, raw production data, or credentials
- risk_profile:
  reads: target/callers, contract/oracle, tests/config, and actual-path evidence
  writes: one behavior-preserving production-code batch at a time
  tools: targeted inspection, mechanical edits, and condition-matched validation
  sensitive_resources: deny credentials and raw production data
- entry_scene:
  - PREPARE

## `workflow-source-maintenance`

- role: primary
- family: workflow
- intent_signature: behavior-preserving dead-code/source diet or comment/docstring synchronization
- use_when: the user explicitly requests obsolete-source pruning or comment/docstring/TODO maintenance without intended behavior change
- do_not_use_when: feature implementation, concrete failure repair, reachable-code rename/move/extract/inline/restructure, dependency upgrade, README/wiki writing, or architecture analysis is primary
- expected_inputs: selected mode, target files/symbols, behavior-preservation boundary, relevant callers/contracts, and available focused checks
- expected_outputs: classified candidates, bounded edits, preserved items with reasons, behavior-preservation evidence, and remaining risk
- context_targets:
  must_read: current request, targeted source, and the code/callers/contracts needed to establish current meaning or reachability
  read_if_needed:
    - `references/comment-sync.md` in `comment_sync`; public exports, dynamic entrypoints, generated-source policy, build/lint/doc checks, or framework conventions
    - `references/execution_assurance_contract.md` when source pruning has material maker/checker separation or destructive, external-write, or broad-refactor risk
  do_not_load_by_default: full repo, broad reports, unrelated docs/memory, or package-manager state
- risk_profile:
  reads: targeted source, callers/contracts, comments, tests, exports, and validation configuration
  writes: behavior-preserving source/comment/test/config cleanup inside the requested slice
  tools: focused search, diff, build/typecheck/lint/test/doc checks, and public-entrypoint checks
  sensitive_resources: credentials and production data denied
- entry_scene: PREPARE
