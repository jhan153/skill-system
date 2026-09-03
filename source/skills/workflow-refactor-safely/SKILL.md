---
name: workflow-refactor-safely
description: Restructure production code in small reversible batches while preserving an established observable contract and verifying the same actual path after each batch.
---

# Workflow Refactor Safely

## Routing Card
- role: primary
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

## Core Cards

- consumes after delegated repair or review: `references/core-execution-items-v1/cards/code_review_result.md`, `references/core-execution-items-v1/cards/deferred_item.md`, `references/core-execution-items-v1/cards/bug_fix_result.md`, `references/core-execution-items-v1/cards/known_bug_candidate.md`, `references/core-execution-items-v1/cards/known_bug_record.md`

## Workflow
1. Bind each material preservation condition to its authority and current observation: public/user/canonical contract, actual behavior, API/data shape, side effects, user-visible errors/logs, and relevant performance bounds. If authority is missing or conflicting, mark it unresolved before editing.
2. Trace the actual production owner/path and representative callers, including canonical source, every internal representation/state machine, unavoidable external translation, side effects, and selected output when relevant. Existing tests can expose coverage; an agent-authored characterization test records an established contract but does not create one. When an accepted `boundary_decision` exists or the requested refactor materially changes a boundary, load `references/boundary_decision_contract.md` and preserve its design pressure, owned invariant, outside contract, and dependency direction.
3. Choose one reversible production batch: rename, move, extract, inline/collapse, split, or narrow an already-evidenced interface. Update its callers; interface/mock/test-only work is not refactor progress. The batch may change enforcement, but it cannot silently change domain meaning, ownership, or the accepted boundary decision. If materially different boundary choices remain, keep them unresolved, avoid the dependent edit, and continue only independent in-scope work. `analysis-boundary-design` owns the decision only when explicitly selected. When `references/identifier_readability_principle.md` is active, this refactor owns the behavior-preserving rename and caller convergence only; preserve higher-priority naming authorities and hand material static ambiguity to `workflow-code-review`.
4. Apply the batch, then rerun the same behavior path and read back its material output/side effects. Structural, build, test, and mock passes remain scoped to their own contracts.
5. Apply `references/execution_assurance_contract.md` only when its trigger is material; preserve this refactor as the sole mutation owner and reuse equivalent characterization/review/readback evidence.
6. Inspect for drift, missed callers, unrelated cleanup, duplicate source paths, compatibility shims, and ownership leakage. Continue only when every stated preservation condition is directly passed or explicitly unresolved.

When `references/maintainable_code_principles.md` is active, this workflow owns the before/after
application of its six principles to one behavior-preserving structural batch. Apply them after
binding preservation conditions and before selecting the batch; own rollback and same-path
readback. Behavior changes hand off to `workflow-implementation`, and static disposition remains
with `workflow-code-review`.

## Refactor Rules
- Keep feature and bug changes separate; prefer mechanical moves before semantic rewrites. If the refactor reveals a defect, preserve the signal and route only a semantically admitted bounded same-contract repair to `workflow-bug-fix`; first implementation or accepted production-mechanism replacement belongs to `workflow-implementation`.
- Give each internal concept one canonical contract, representation, state machine, and policy owner. Update every in-scope caller/producer/consumer directly; do not retain an adapter, bridge, proxy, shim, dual model, or fallback merely to keep the batch small. A temporary compatibility boundary is allowed only for an actually unmodifiable external/versioned consumer, must be thin/stateless/fail-closed, and needs a named removal trigger.
- Preserve the complete behavior with the least conceptual machinery, not the smallest total diff. Prefer plain functions, values, concrete types, direct calls, existing primitives, and composition; reject Clean Code-style class/interface/function fragmentation, mock-created seams, forwarding layers, and speculative factories/registries/frameworks.
- Preserve explicit user/canonical paradigm and implementation-shape conditions. Use `workflow-implementation` references only as non-owning shape context; a label without observable state/data/effect/dispatch/construction rules remains unresolved before structural edits.
- Treat an accepted `boundary_decision` as part of the preservation contract. If actual-path evidence falsifies it, preserve the contradiction and stop only the dependent batch; do not rewrite the decision inside the refactor or invoke an analysis chain automatically.
- Delete shallow wrappers only with representative caller and actual-path evidence. A required `fail`, `needs_review`, `unverified`, or `blocked` condition stays open until same-condition resolution evidence exists.

## Output Contract
Return only applicable fields: condition/authority mapping, applicable `boundary_decision` conformance, maintainability-principle evidence when consumed, production batch and changed callers, actual-path preservation evidence, scoped validation, rollback, unresolved conditions, and next action. Do not claim progress from scaffolding or completion from a narrower pass.

## Cross-Skill Boundaries
- `workflow-refactor-safely` owns a still-reachable wrapper collapse or other behavior-preserving live-code restructuring even when the diff is small. `workflow-source-maintenance` owns deletion of unreachable or otherwise proven-obsolete code when no live structural change is required.
- `analysis-boundary-design` owns an unresolved boundary; `workflow-implementation` owns feature changes and accepted production-mechanism replacement; `workflow-bug-fix` owns one semantically admitted contract-preserving intervention/result at a time; `workflow-source-maintenance` owns comments-only work in `comment_sync`; the current task owner or named domain verifier owns validation-only matrices; this workflow applies directness without a second minimality owner. This refactor owner consumes review evidence and carries any final Known Bug without rewriting the preservation verdict.
- `workflow-implementation` paradigm references may constrain the target structure without transferring primary ownership.
