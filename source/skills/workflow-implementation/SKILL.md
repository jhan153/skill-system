---
name: workflow-implementation
description: Primary workflow for direct or DAG-assigned production software implementation nodes, including first implementation or explicit replacement of an accepted algorithm, model, backend, canonical data/ownership flow, or other production mechanism even when a current failure motivated it. Do not use for standalone test design/test-only implementation owned by the Testing plugin, Plan coordination, behavior-preserving refactors, semantically admitted bounded repairs of already-implemented accepted contracts, or analysis/validation-only work.
---

# Workflow Implementation

## Routing Card
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

### Resource Closure

```json
[
  {
    "source": "shared/docs/architecture_design_contract.md",
    "target": "references/architecture_design_contract.md",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "selected skill's matching read_if_needed condition applies"
  },
  {
    "source": "shared/docs/boundary_decision_contract.md",
    "target": "references/boundary_decision_contract.md",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "selected skill's matching read_if_needed condition applies"
  },
  {
    "source": "shared/contracts/core-execution-items-v1/cards/bug_fix_result.md",
    "target": "references/core-execution-items-v1/cards/bug_fix_result.md",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "matching Core result crosses the declared workflow boundary"
  },
  {
    "source": "shared/contracts/core-execution-items-v1/cards/code_review_result.md",
    "target": "references/core-execution-items-v1/cards/code_review_result.md",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "matching Core result crosses the declared workflow boundary"
  },
  {
    "source": "shared/contracts/core-execution-items-v1/cards/implementation_result.md",
    "target": "references/core-execution-items-v1/cards/implementation_result.md",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "matching Core result crosses the declared workflow boundary"
  },
  {
    "source": "shared/contracts/core-execution-items-v1/cards/known_bug_record.md",
    "target": "references/core-execution-items-v1/cards/known_bug_record.md",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "matching Core result crosses the declared workflow boundary"
  },
  {
    "source": "shared/docs/database_persistence_transparency_contract.md",
    "target": "references/database_persistence_transparency_contract.md",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "selected skill's matching read_if_needed condition applies"
  },
  {
    "source": "shared/docs/delivery_slice_contract.md",
    "target": "references/delivery_slice_contract.md",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "selected skill's matching read_if_needed condition applies"
  },
  {
    "source": "shared/schemas/execution/execution-item.schema.json",
    "target": "references/execution-item.schema.json",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "matching Core result crosses the declared workflow boundary"
  },
  {
    "source": "shared/docs/execution_assurance_contract.md",
    "target": "references/execution_assurance_contract.md",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "selected skill's matching read_if_needed condition applies"
  },
  {
    "source": "shared/docs/execution_item_contract.md",
    "target": "references/execution_item_view.md",
    "projection": "execution-item-view",
    "load": "read_if_needed",
    "condition": "selected skill's matching read_if_needed condition applies"
  },
  {
    "source": "shared/docs/identifier_readability_principle.md",
    "target": "references/identifier_readability_principle.md",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "selected skill's matching read_if_needed condition applies"
  },
  {
    "source": "shared/docs/maintainable_code_principles.md",
    "target": "references/maintainable_code_principles.md",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "selected skill's matching read_if_needed condition applies"
  },
  {
    "source": "shared/docs/programming-paradigms",
    "target": "references/programming-paradigms",
    "projection": "tree",
    "load": "read_if_needed",
    "condition": "selected skill's matching read_if_needed condition applies"
  },
  {
    "source": "shared/docs/programming_paradigm_contract.md",
    "target": "references/programming_paradigm_contract.md",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "selected skill's matching read_if_needed condition applies"
  },
  {
    "source": "shared/docs/runtime_debugging_contract.md",
    "target": "references/runtime_debugging_contract.md",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "selected skill's matching read_if_needed condition applies"
  }
]
```

## Core Cards

- produces: `references/core-execution-items-v1/cards/implementation_result.md`
- consumes: `references/core-execution-items-v1/cards/code_review_result.md`, `references/core-execution-items-v1/cards/bug_fix_result.md`, `references/core-execution-items-v1/cards/known_bug_record.md`

## Contract
- **C0 — Positive-output precedence.** Classify the requested production output before its motivating symptom, failing condition, review disposition, attempt history, or node label. First implementation or explicit replacement of an accepted production mechanism remains Implementation work. An unresolved mechanism choice returns to its decision owner; only a bounded defect repair that preserves an already-implemented accepted contract belongs to Bug Fix.
- **C1 — Work boundary.** Own ordinary coding from the active user work contract through the production-path change and its evidence. Preserve deliverables, allowed/excluded actions, verification owner, interaction/continuation behavior, and stop terms; never reactivate excluded test, validation, or meta work. Implementation is the requested source, runtime config/build, or executable behavior. Plans, docs, mocks, interfaces, or tests alone complete only when they are the requested deliverable.
- **C2 — Complete canonical behavior.** Close the whole required behavior with the least conceptual machinery, not the fewest changed lines. Give each internal concept one contract, representation, state machine, and policy owner; update every in-scope producer, consumer, and caller. Missing or mismatched canonical input fails or remains an explicit user decision, never a placeholder, warning, fallback, or success-looking partial result. A material regression, contradicted completion claim, repeated correction, or ownership/architecture drift invalidates the frame; reconstruct the positive objective, canonical artifacts/owners, actual paths, affected consumers, and one disconfirming case before dependent work.
- **C3 — Direct boundaries.** Converge internal disagreement instead of preserving it through adapters, bridges, proxies, shims, or dual models. Translate only at an unmodifiable external ABI, protocol, SDK, device, or bounded-version boundary; keep translation thin, stateless, total, validation-first, and free of defaults, fallback, retry, caching, lifecycle, domain policy, or hidden state. Prefer functions, values, concrete types, direct calls, existing primitives, and composition. Add an interface, inheritance hierarchy, registry, factory, generic framework, or other indirection only for a present semantic responsibility that direct dispatch or composition cannot satisfy. Treat class-per-noun, interface-per-implementation, one-line forwarding functions, blanket DRY across different meanings, factory/manager/service/repository/wrapper layers, mock-created seams, and speculative extension frameworks as explicit implementation anti-patterns—not harmless style alternatives.
- **C4 — Valid construction.** A successful public domain/resource value is immediately valid; no partially initialized final object, setter assembly, zombie handle, or hidden readiness state may escape. Staged construction is limited to intrinsic external, asynchronous/streaming, bulk/parallel-fill, or GPU/DMA progress. Reuse an existing future/task/result/request/span/builder when it owns the states. A new staged operation requires a distinct invariant, state set, or lifetime and must represent `pending`, `completed`, `failed`, and `cancelled` as explicit valid states; failure and cancellation are not optional afterthoughts. Only its successful `finish`/`commit`/`freeze` boundary may publish the final value.
- **C5 — Authoritative shape.** Treat an explicit user-selected paradigm/model, accepted
  `architecture_design` and its paradigm/model pattern applications, and accepted
  `boundary_decision` and its optional `paradigm_constraints` as implementation constraints.
  Compose approaches only at the module,
  data/state, runtime/failure, integration, deployment/trust, compile-time, or execution boundary
  they govern. Preserve each accepted paradigm axis, owner, minimum closure, maximum scope,
  interactions, forbidden drift, architecture delta, and proof ceiling. Preserve compatible local
  patterns when no approach is selected; do not reproduce conflicting speculative architecture.
  Expose any hard safety, security, language, ABI, framework, canonical-data, compatibility, or
  measured-production conflict instead of silently reinterpreting the request. A proposed
  architecture is not implementation authority. Every new or changed material paradigm/model
  choice passes the shared impact/decision-owner gate. Implementation retains only
  `decision_owner: implementation`; `atomic_boundary` returns to `analysis-boundary-design` and
  `coupled_architecture` returns to `workflow-architecture-design`. Independent implementation may
  continue only where it does not depend on them.

## Systems Preflight

For every non-trivial implementation, answer these questions internally before selecting code
shape. Persist or report the answers only when they materially affect scope, ownership, routing, or
evidence:

1. Does a representative bulk or hot path make data movement, layout, batching, or tail latency
   material? Apply the Data-Oriented profile only when the actual access pattern can change the
   decision.
2. Does work wait, suspend, or depend on file/network/device/timer/process completion? Apply the
   Structured Async profile when operation lifetime, cancellation, queueing, or publication is
   material.
3. Do several execution contexts share a mutable invariant, publication edge, or reclamation
   protocol? Apply the Shared-Memory Concurrency profile; immutable or owner-exclusive state keeps
   the simpler local contract.
4. Does ready CPU work require graph-shaped dependencies, completion scope, load balancing, or
   resource-access coordination? Apply the Job System profile; one callback or external wait is not
   a Job graph.
5. Does data or resource lifetime cross a callback, task, queue, frame, version, or shutdown
   boundary? Name its owner, valid states, sole publication/commit point, and reclamation rule.
6. Is a performance optimization requested without a verified bottleneck and comparable baseline?
   Return the unresolved diagnosis to `analysis-performance` instead of selecting a speculative
   optimization.
7. What representative actual path and realistic negative or edge case could falsify the selected
   shape or its claimed property?

A negative answer preserves the coherent local model and loads no specialist profile. This
preflight is a routing gate, not permission to introduce concurrency, abstraction, or optimization.

Apply conditional references without transferring workflow ownership:

| Reference | This Workflow consumes and owns |
| --- | --- |
| `architecture_design_contract.md` | Preserve accepted drivers, pattern stop boundaries, canonical owners, architecture delta, transition constraints, and fitness handoff; implement only the assigned slice and record its design reference in artifact/evidence refs when crossing owners. |
| `boundary_decision_contract.md` | Preserve accepted pressure, invariant, outside contract, dependency direction, and optional atomic paradigm profile/axis/property owner/scope/proof constraints; implement and read back only the smallest enforcement. |
| `maintainable_code_principles.md` | Apply the six principles after the behavior boundary; own only the in-scope implementation and changed-path evidence. |
| `database_persistence_transparency_contract.md` | Preserve accepted source/domain/boundary meaning; own the concrete model, read/write effects, consistency/transaction, lifecycle, cost visibility, and matching readback. |
| `identifier_readability_principle.md` | Own introduced/changed related identifiers and required callers; preserve higher naming authority and leave static findings to Code Review. |
| `runtime_debugging_contract.md` | Implement only the requested diagnostic infrastructure; preserve exact target/build/symbol/capture identity, crash-context safety, partial-artifact reporting, perturbation, trust/privacy controls, and the runtime proof ceiling without claiming a current root cause. |
| `programming_paradigm_contract.md` | Preserve shared paradigm axes, authority, scope/interactions, impact/decision-owner gate, thin-profile proof ceilings, and immutable accepted applications; own local decisions and downstream `paradigm_conformance` only. |
| `paradigm-composition.md` | Route an already selected application to only the detailed method profiles needed for concrete code realization and actual-path readback. |
| `delivery_slice_contract.md` | Select a multi-batch delivery shape only when more than one executable batch is required. |
| `execution_item_view.md` | Use the role-scoped Core envelope and items only when a result crosses Workflow, Coordinator, Plan/Handoff, or plugin boundaries. |

## Workflow
1. Compile scope into the active work contract; apply C0 before repair history or Plan labels, then classify core work, required prerequisites, optional validation/quality, and meta work. State observable success and one material negative or edge case.
2. Treat the change as local only when one owner and representative path cover the outcome with no material consumer, invariant, canonical-source, or ownership decision. Otherwise establish the positive objective, canonical artifacts/owners, actual paths, affected consumers, invariants/dependencies, and one disconfirming case before selecting a diff.
3. When shape is explicit or material, map the selected approach, canonical owner, in-scope
   producers/consumers, construction/state/data/effect/dispatch/execution rules, and one forbidden
   drift. Load only applicable references. Preserve accepted architecture applications and atomic
   boundary paradigm constraints, including paradigm axes/interactions, pattern maximum scope,
   architecture delta, transition constraints, and proof ceilings. Apply the shared
   impact/decision-owner gate to every new or changed material paradigm/model choice, whether
   user-explicit or agent-selected, before loading detailed method profiles. Keep
   `local_implementation`; hand `atomic_boundary` to `analysis-boundary-design` and
   `coupled_architecture` to `workflow-architecture-design`, leaving only the dependent shape
   unresolved. Name any C4 staged-operation exception, reused primitive or justifying invariant/state
   set, and sole publication boundary. Omit this step for a trivial already-shaped change.
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
| crash/debug/dynamic/graphics diagnostic infrastructure | Source and configuration readback for identity, lifetime/reentrancy, partial-capture, trust/privacy, and marker/correlation paths plus one safe condition-matched capture/readback when available; ordinary tests or static shape do not prove behavior in a real corrupted or device-loss context. |
| implementation shape | Changed boundaries realize the selected state, data, effect, dispatch/specialization, or execution rules and keep the non-applicable boundary out. |
| paradigm/model application conformance | Changed-path source readback establishes only observable code shape; attach matching runtime/test/trace/benchmark evidence for determinism, lifecycle, memory/performance, compile-cost, or scheduling claims without mutating the accepted application. |
| construction or simplicity | No partial final value escapes; staged work exposes `pending/completed/failed/cancelled`, and each abstract type has a current invariant/responsibility that reduces total conceptual machinery. |

- `Line count`, file count, smaller diff size, and a passing mock are never evidence of simplicity. A passing happy path does not prove the absence of hidden readiness, failure, cancellation, or partial-publication states. These are explicit anti-fake-signal rules, not optional review advice.
- A required `fail`, `needs_review`, `unverified`, or `blocked` condition stays open until evidence from that same condition resolves it.
- If direct observation needs unavailable GUI, credentials, or external state, return task state `user-verification-needed` or `unverified`; do not add a surrogate path and call it complete.
- If an optional verifier or permission is unavailable, defer that semantic intent and continue independent required implementation. Do not retry it as another command, GUI path, wrapper, probe, or new test; use `blocked` only when no required runnable work remains.
- If no suitable verifier exists, keep the implementation scope complete but lower its evidence label. Do not create validation-only work or repeat an unchanged check to promote the label.
- If a material semantic completion claim otherwise depends mainly on code and checks produced by the same agent, apply `references/execution_assurance_contract.md` in `standard` mode. Its independent pass does not replace direct condition evidence, own Core cards, or become a second implementation owner.
- When review returns `repair_required`, classify the required positive work against the accepted implementation/method contract before dispatch. Consume an assigned `workflow-bug-fix` round only for a semantically admitted bounded repair. First implementation or explicit production-mechanism replacement stays with an existing Implementation node or requires Plan correction; an unresolved mechanism returns to its decision owner. Another repair round requires a concrete review disposition under the same accepted repair contract and its owning execution context. Plan/Handoff records a final `known_bug_record` in graph mode; standalone Bug Fix may record it only after its bounded final review. This Workflow consumes the record and never produces it.
- When node/Coordinator identity is supplied, return the Core `implementation_result` item from `references/execution_item_view.md`: changed snapshot/artifacts, implemented conditions, bounded review slice, and unresolved conditions. Never choose the review or successor node.

## Output Contract
Return only the sections needed:
- `implementation_scope`
- `implementation_shape` when the user selected an approach or the shape materially determined the diff
- `architecture_design` conformance when that contract was consumed
- `paradigm_conformance` when an accepted application was consumed, or one task-local application
  plus its conformance when Implementation owned `local_implementation`
- `boundary_decision` conformance when the contract was consumed
- `database_persistence_transparency` conformance when the contract was consumed
- `changed_artifacts`
- `validation`
- `review_notes`
- `user_verification_needed`
- `unverified_gaps`
- `next_step`
