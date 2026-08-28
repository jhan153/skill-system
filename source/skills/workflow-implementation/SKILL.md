---
name: workflow-implementation
description: Primary workflow for direct or DAG-assigned production software implementation nodes. Use when the user or an accepted Plan node requests production code, API, script, config, build, or production-coupled regression test changes. Do not use for standalone test design/test-only implementation owned by the Testing plugin, Plan coordination, behavior-preserving refactors, concrete bug fixes, or analysis/validation-only work; review findings that require repair enter the bounded workflow-bug-fix cycle without blocking unrelated implementation nodes.
---

# Workflow Implementation

## Routing Card
- role: primary
- intent_signature:
  - direct implementation
  - code change
  - add production-coupled regression tests
  - implement feature
  - 구현
- use_when:
  - the user asks for a concrete production code, script, API, config, or build change, including bounded regression tests that are part of that production slice.
  - requirements are sufficient for a current-turn implementation slice.
  - the task is ordinary development work not already owned by a narrower specialist.
- do_not_use_when:
  - the request is to coordinate or advance an approved Plan rather than implement one bounded node; the Orchestrator follows the copied Plan/Handoff contract.
  - the user asks to fix a concrete failure or failing test; use `workflow-bug-fix`.
  - the user asks for behavior-preserving rename, move, extract, collapse, simplify, or restructure work; use `workflow-refactor-safely`.
  - the task is now primarily a concrete first or repeated repair; use `workflow-bug-fix` with its preserved attempt history.
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
    - `references/boundary_decision_contract.md` when an accepted boundary decision is input or the implementation materially creates, moves, merges, or splits an owner/module/API/adapter/state boundary
    - `references/maintainable_code_principles.md` when maintainability is explicit or the change materially affects ownership, abstraction, invariants, effects, conventions, or verification
    - `references/database_persistence_transparency_contract.md` when adding or changing database schema, ORM/ODM mapping, query, migration, transaction, or data-access-boundary behavior
    - `references/identifier_readability_principle.md` when implementation introduces or renames a related identifier set in repository-owned code and repository conventions or domain terms do not already decide a clearly distinguishable shape
    - `references/execution_item_view.md` when a delegated node result will cross into Code Review, a Coordinator, Plan/Handoff, or another plugin
    - `references/paradigm-composition.md` as the paradigm reference index when the user names an implementation paradigm/model, supplies paradigm research, asks to combine approaches, or the choice would materially alter state ownership, data layout, dispatch, effects, or execution boundaries; then load only the paradigm files routed by that index
    - `references/delivery_slice_contract.md` when any requested change needs multiple executable batches, including a wide migration or non-feature decomposition
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

## Core Cards

- produces: `references/core-execution-items-v1/cards/implementation_result.md`
- consumes: `references/core-execution-items-v1/cards/code_review_result.md`, `references/core-execution-items-v1/cards/bug_fix_result.md`, `references/core-execution-items-v1/cards/known_bug_record.md`

## Contract
- **C1 — Work boundary.** Own ordinary coding from the active user work contract through the production-path change and its evidence. Preserve deliverables, allowed/excluded actions, verification owner, interaction/continuation behavior, and stop terms; never reactivate excluded test, validation, or meta work. Implementation is the requested source, runtime config/build, or executable behavior. Plans, docs, mocks, interfaces, or tests alone complete only when they are the requested deliverable.
- **C2 — Complete canonical behavior.** Close the whole required behavior with the least conceptual machinery, not the fewest changed lines. Give each internal concept one contract, representation, state machine, and policy owner; update every in-scope producer, consumer, and caller. Missing or mismatched canonical input fails or remains an explicit user decision, never a placeholder, warning, fallback, or success-looking partial result. A material regression, contradicted completion claim, repeated correction, or ownership/architecture drift invalidates the frame; reconstruct the positive objective, canonical artifacts/owners, actual paths, affected consumers, and one disconfirming case before dependent work.
- **C3 — Direct boundaries.** Converge internal disagreement instead of preserving it through adapters, bridges, proxies, shims, or dual models. Translate only at an unmodifiable external ABI, protocol, SDK, device, or bounded-version boundary; keep translation thin, stateless, total, validation-first, and free of defaults, fallback, retry, caching, lifecycle, domain policy, or hidden state. Prefer functions, values, concrete types, direct calls, existing primitives, and composition. Add an interface, inheritance hierarchy, registry, factory, generic framework, or other indirection only for a present semantic responsibility that direct dispatch or composition cannot satisfy. Treat class-per-noun, interface-per-implementation, one-line forwarding functions, blanket DRY across different meanings, factory/manager/service/repository/wrapper layers, mock-created seams, and speculative extension frameworks as explicit implementation anti-patterns—not harmless style alternatives.
- **C4 — Valid construction.** A successful public domain/resource value is immediately valid; no partially initialized final object, setter assembly, zombie handle, or hidden readiness state may escape. Staged construction is limited to intrinsic external, asynchronous/streaming, bulk/parallel-fill, or GPU/DMA progress. Reuse an existing future/task/result/request/span/builder when it owns the states. A new staged operation requires a distinct invariant, state set, or lifetime and must represent `pending`, `completed`, `failed`, and `cancelled` as explicit valid states; failure and cancellation are not optional afterthoughts. Only its successful `finish`/`commit`/`freeze` boundary may publish the final value.
- **C5 — Authoritative shape.** Treat an explicit user-selected paradigm/model and an accepted `boundary_decision` as implementation constraints. Compose approaches only at the runtime-state, data-layout, compile-time, or execution boundary they govern. Preserve compatible local patterns when no approach is selected; do not reproduce conflicting speculative architecture. Expose any hard safety, security, language, ABI, framework, canonical-data, compatibility, or measured-production conflict instead of silently reinterpreting the request. Materially competing boundary choices remain unresolved; `analysis-boundary-design` owns them only when explicitly selected, while independent implementation may continue.

Apply conditional references without transferring workflow ownership:

| Reference | This Workflow consumes and owns |
| --- | --- |
| `boundary_decision_contract.md` | Preserve accepted pressure, invariant, outside contract, and dependency direction; implement and read back only the smallest enforcement. |
| `maintainable_code_principles.md` | Apply the six principles after the behavior boundary; own only the in-scope implementation and changed-path evidence. |
| `database_persistence_transparency_contract.md` | Preserve accepted source/domain/boundary meaning; own the concrete model, read/write effects, consistency/transaction, lifecycle, cost visibility, and matching readback. |
| `identifier_readability_principle.md` | Own introduced/changed related identifiers and required callers; preserve higher naming authority and leave static findings to Code Review. |
| `paradigm-composition.md` | Load only implicated paradigm files and record where each selected approach applies and stops. |
| `delivery_slice_contract.md` | Select a multi-batch delivery shape only when more than one executable batch is required. |
| `execution_item_view.md` | Use the role-scoped Core envelope and items only when a result crosses Workflow, Coordinator, Plan/Handoff, or plugin boundaries. |

## Workflow
1. Compile scope into the active work contract; classify core work, required prerequisites, optional validation/quality, and meta work. State observable success and one material negative or edge case.
2. Treat the change as local only when one owner and representative path cover the outcome with no material consumer, invariant, canonical-source, or ownership decision. Otherwise establish the positive objective, canonical artifacts/owners, actual paths, affected consumers, invariants/dependencies, and one disconfirming case before selecting a diff.
3. When shape is explicit or material, map the selected approach, canonical owner, in-scope producers/consumers, construction/state/data/effect/dispatch/execution rules, and one forbidden drift. Load only applicable references. Preserve an accepted boundary decision; without one, leave materially competing choices unresolved and avoid dependent edits. Name any C4 staged-operation exception, reused primitive or justifying invariant/state set, and sole publication boundary. Omit this step for a trivial already-shaped change.
4. Implement C2–C4 in the canonical owner and update every required participant. Before adding indirection, name its present semantic responsibility and why a direct value/function/call, existing primitive, variant, or composition cannot close the requirement. For multiple batches, use `vertical_slice`, `migration_sequence`, or `evidence_unit`, and derive order/parallelism from dependencies, overlapping writes, and unresolved decisions; `single_batch` does not activate the delivery contract.
5. When agent verification is owned and allowed, use one existing verifier, direct observation, or focused smoke check that can expose the realistic failure. Include affected-boundary and disconfirming-case readback for material shape. Add a regression test only when requested or when an existing test system covers an anchored regression without new framework, mock, fixture family, or dependency work. Preserve `user-verification-needed` when the user owns verification.
6. Inspect the diff for scope creep, churn, missed participants, duplicate contracts, adapters/shims/proxies, hidden state, stale-frame conclusions, and accepted-boundary drift. Explicitly reject class-per-noun, interface-per-implementation, forwarding-only functions, blanket DRY, manager/service/repository/wrapper layers, mock-created seams, speculative frameworks, and staged operations that hide `failed` or `cancelled` states.
7. Report each material condition as evidenced, user-only, or unresolved.

## Evidence Gate
- Match claims to their actual evidence scope; structural checks prove structure, mocks prove only their boundary, and agent-authored tests are regression/self-check evidence rather than an independent semantic oracle.

| Claim | Required evidence |
| --- | --- |
| requested behavior | Representative production path and a realistic failure/edge observation. |
| canonical convergence | Every in-scope producer/consumer uses one representation/state machine; no adapter, shim, legacy path, or fallback preserves the replaced contract. |
| source selection, migration, transform, adapter, or external boundary | Actual-path readback; external translation yields one canonical valid value or typed failure and owns no policy/hidden state. |
| implementation shape | Changed boundaries realize the selected state, data, effect, dispatch/specialization, or execution rules and keep the non-applicable boundary out. |
| construction or simplicity | No partial final value escapes; staged work exposes `pending/completed/failed/cancelled`, and each abstract type has a current invariant/responsibility that reduces total conceptual machinery. |

- `Line count`, file count, smaller diff size, and a passing mock are never evidence of simplicity. A passing happy path does not prove the absence of hidden readiness, failure, cancellation, or partial-publication states. These are explicit anti-fake-signal rules, not optional review advice.
- A required `fail`, `needs_review`, `unverified`, or `blocked` condition stays open until evidence from that same condition resolves it.
- If direct observation needs unavailable GUI, credentials, or external state, return task state `user-verification-needed` or `unverified`; do not add a surrogate path and call it complete.
- If an optional verifier or permission is unavailable, defer that semantic intent and continue independent required implementation. Do not retry it as another command, GUI path, wrapper, probe, or new test; use `blocked` only when no required runnable work remains.
- If no suitable verifier exists, keep the implementation scope complete but lower its evidence label. Do not create validation-only work or repeat an unchanged check to promote the label.
- If a material semantic completion claim otherwise depends mainly on code and checks produced by the same agent, attach the non-node `workflow-rigor` modifier in `standard` mode when available. Its independent pass does not replace direct condition evidence, own Core cards, or become a second implementation owner.
- When review exposes a concrete failure, dispatch only the assigned `workflow-bug-fix` round and consume its changed snapshot/attempt result. Another round requires a concrete review disposition and its owning execution context. Plan/Handoff records a final `known_bug_record` in graph mode; standalone Bug Fix may record it only after its bounded final review. This Workflow consumes the record and never produces it.
- When node/Coordinator identity is supplied, return the Core `implementation_result` item from `references/execution_item_view.md`: changed snapshot/artifacts, implemented conditions, bounded review slice, and unresolved conditions. Never choose the review or successor node.

## Output Contract
Return only the sections needed:
- `implementation_scope`
- `implementation_shape` when the user selected an approach or the shape materially determined the diff
- `boundary_decision` conformance when the contract was consumed
- `database_persistence_transparency` conformance when the contract was consumed
- `changed_artifacts`
- `validation`
- `review_notes`
- `user_verification_needed`
- `unverified_gaps`
- `next_step`
