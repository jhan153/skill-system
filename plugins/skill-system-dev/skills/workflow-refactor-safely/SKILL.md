---
name: workflow-refactor-safely
description: Restructure production code in small reversible batches while preserving an established observable contract and verifying the same actual path after each batch.
---

# Workflow Refactor Safely

## Routing Card
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
    - `workflow-implementation` method index and only its matching paradigm references when the user/preservation contract names a target shape or the transformation affects construction, aliasing, execution order, resource lifetime, cancellation, or publication; apply them to preserve the accepted behavior
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

## Transformation Method

Start from a concrete burden in reading or changing the existing path. An owner is the place that
decides a policy, mutates state, or controls a resource lifetime; it need not be a new class.
First consider keeping the behavior local, collapsing forwarding, or moving/merging responsibility
into an existing owner. Extract a boundary when it removes an evidenced independent responsibility
or protects a required invariant. Select the applicable transformation, not every row:

| Observed problem | Transformation and order |
| --- | --- |
| A layer only forwards calls or values | Check for hidden validation, synchronization, transaction, lifetime, or external-contract duties. When no separate duty remains, inline/collapse at the caller, preserving evaluation order/count, aliasing, errors, and effects; update callers and remove the redundant layer. |
| One policy is repeated across callers | Establish the authoritative rule, move it to its existing semantic owner, and update affected callers before removing equivalent copies. Surface conflicting behavior instead of choosing a convenient copy. |
| State and the rules that maintain it are scattered | Bring the required state, mutations, and lifetime operations together. Transfer responsibility explicitly rather than introducing a second state holder or manager between the old participants. |
| Independently changing work is entangled | Identify inputs, results, mutations, captures, and failure effects; extract the cohesive operation with the smallest contract, then reconnect callers. Prefer values and functions; introduce a new owner type when it materially contains an invariant, mutation, or lifetime. |
| The same internal meaning has competing representations or state machines | Select the accepted contract and update its producers/consumers coherently. Do not retain an internal adapter to hide disagreement; genuinely different meanings keep their explicit value conversion. |
| Related names obscure their differences | Follow domain/API conventions, rename declarations and uses together, and check registrations, reflection, and serialized/public names as applicable. Preserve external spellings that the contract fixes. |

For stateful or asynchronous moves, establish the destination's invariant and lifetime before
redirecting users. Preserve buffer/capture validity, cancellation versus actual completion,
publication, and cleanup order throughout the change; use the matching Implementation method
guidance when needed. A moved callback must not leave its data owned by a shorter-lived scope.

## Workflow
1. State the structural burden to remove and the expected improvement in responsibility, state, or call flow. Bind each material preservation condition to its authority and current observation: public/user/canonical contract, actual behavior, API/data shape, side effects, user-visible errors/logs, and relevant performance bounds. Keep missing or conflicting authority explicit.
2. Trace the actual production owner/path and representative callers, including canonical source, every internal representation/state machine, unavoidable external translation, side effects, and selected output when relevant. Existing tests can expose coverage; an agent-authored characterization test records an established contract but does not create one. When an accepted `boundary_decision` exists or the requested refactor materially changes a boundary, load `references/boundary_decision_contract.md` and preserve its design pressure, owned invariant, outside contract, and dependency direction.
3. Use the Transformation Method to choose one reversible batch and its migration order. Preserve domain meaning and accepted policy/state/lifetime authority, including any explicitly accepted ownership move. Leave unresolved boundary choices outside the batch and continue independent work. Apply the identifier-readability reference when its condition holds.
4. Apply the batch, then rerun the same behavior path and read back its material output/side effects.
5. Apply `references/execution_assurance_contract.md` when its trigger is material, reusing equivalent characterization/review/readback evidence.
6. Compare the original burden with the changed path: where decisions and mutations now live, what callers must know, and which forwarding or duplicate state disappeared. Reconsider a batch that only relocates complexity or explains it with new comments. Inspect for missed callers and drift; keep every preservation condition passed or explicitly unresolved.

When `references/maintainable_code_principles.md` is active, apply its six principles after binding
preservation conditions and before selecting the batch; compare the before/after code.

## Refactor Rules
- Keep feature and bug changes separate; prefer mechanical moves before semantic rewrites. If the refactor reveals a defect, preserve the signal and route only a semantically admitted bounded same-contract repair to `workflow-bug-fix`; first implementation or accepted production-mechanism replacement belongs to `workflow-implementation`.
- Preserve the complete behavior with the least conceptual machinery. Prefer values, direct functions/calls, existing primitives, and concrete owners. Similar names or data shapes do not make independently governed policies or states the same responsibility.
- Introduce an interface only for a present substitution need, including compile-time polymorphism, or an imposed language/framework/public contract that direct values/functions/calls or existing primitives cannot satisfy. Preserve a justified existing interface even with one implementation; hypothetical reuse and mock convenience are insufficient reasons to add one.
- Keep translation adapters at genuine external or accepted fixed compatibility boundaries. Translate narrowly and without hidden state to one valid internal value or explicit failure; keep domain policy, fallback, and state/lifetime authority in their actual owners. A temporary compatibility adapter needs a named removal trigger.
- Short RAII, lock, transaction, validation, and resource wrappers may carry real behavior. Preserve that behavior on failure, cancellation, and early return when considering collapse. Comments may explain domain reasons, ordering, or compatibility constraints; declarations, calls, mutations, and cleanup must show the ownership mechanics.
- Preserve explicit user/canonical paradigm and implementation-shape conditions. Use `workflow-implementation` references only as non-owning shape context; a label without observable state/data/effect/dispatch/construction rules remains unresolved before structural edits.
- Treat an accepted `boundary_decision` as part of the preservation contract. If actual-path evidence falsifies it, preserve the contradiction and stop only the dependent batch; do not rewrite the decision inside the refactor or invoke an analysis chain automatically.

## Output Contract
Return only applicable fields: condition/authority mapping, applicable `boundary_decision` conformance, maintainability-principle evidence when consumed, production batch and changed callers, before/after structural improvement, actual-path preservation evidence, scoped validation, rollback, unresolved conditions, and next action. Carry any final Known Bug from delegated repair alongside the preservation verdict without rewriting it.
