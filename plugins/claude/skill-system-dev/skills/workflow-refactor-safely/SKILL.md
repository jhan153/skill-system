---
name: workflow-refactor-safely
description: Restructure production code in small reversible batches while preserving an established observable contract and verifying the same actual path after each batch.
disable-model-invocation: true
---

# Workflow Refactor Safely

## Routing Card
- role: primary
- intent_signature:
  - safe/behavior-preserving refactor; rename/move/extract/collapse; 안전한 리팩터링
- use_when:
  - the user requests a production-code rename, move, extraction, collapse, simplification, or restructure with behavior preserved.
- do_not_use_when:
  - behavior/feature change, concrete bug repair, design-only judgment, validation-only work, comments/docs-only change, or repeated same-signature failure is primary.
- expected_inputs:
  - structural goal, material preservation conditions and authority, target production owner/path, callers, and available observations
- expected_outputs:
  - scoped contract, one production batch, changed artifacts/callers, actual-path evidence, unresolved conditions, and rollback
- context_targets:
  must_read:
    - refactor request, target production source/callers, and public/canonical/observed behavior contract
  read_if_needed:
    - relevant tests, actual readback, design decision, config/manifests, source selection, or prior failure output
  do_not_load_by_default:
    - full repo/memory, unrelated reports/plans, raw production data, or credentials
- risk_profile:
  reads: target/callers, contract/oracle, tests/config, and actual-path evidence
  writes: one behavior-preserving production-code batch at a time
  tools: targeted inspection, mechanical edits, and condition-matched validation
  sensitive_resources: deny credentials and raw production data
- entry_scene:
  - PREPARE

## Workflow
1. Bind each material preservation condition to its authority and current observation: public/user/canonical contract, actual behavior, API/data shape, side effects, user-visible errors/logs, and relevant performance bounds. If authority is missing or conflicting, mark it unresolved before editing.
2. Trace the actual production owner/path and representative callers, including canonical source, transforms, adapters, side effects, and selected output when relevant. Existing tests can expose coverage; an agent-authored characterization test records an established contract but does not create one.
3. Choose one reversible production batch: rename, move, extract, inline/collapse, split, or narrow an already-evidenced interface. Update its callers; interface/mock/test-only work is not refactor progress.
4. Apply the batch, then rerun the same behavior path and read back its material output/side effects. Structural, build, test, and mock passes remain scoped to their own contracts.
5. Inspect for drift, missed callers, unrelated cleanup, duplicate source paths, compatibility shims, and ownership leakage. Continue only when every stated preservation condition is directly passed or explicitly unresolved.

## Refactor Rules
- Keep feature and bug changes separate; prefer mechanical moves before semantic rewrites. If the refactor reveals a bug, preserve the signal and route it to `workflow-bug-fix` instead of silently changing behavior.
- Keep a compatibility shim only when in-scope callers cannot be updated safely. Canonical source, domain/fallback/failure policy, and migration truth stay at their production owner on one authoritative path; missing or mismatched required input fails closed.
- Delete shallow wrappers only with representative caller and actual-path evidence. A required `fail`, `needs_review`, `unverified`, or `blocked` condition stays open until same-condition resolution evidence exists.

## Output Contract
Return only applicable fields: condition/authority mapping, production batch and changed callers, actual-path preservation evidence, scoped validation, rollback, unresolved conditions, and next action. Do not claim progress from scaffolding or completion from a narrower pass.

## Cross-Skill Boundaries
- `analysis-codebase-design` owns an unresolved boundary; `workflow-implementation` owns feature changes; `workflow-bug-fix` owns repair; `workflow-comment-maintenance` owns comments-only work; `workflow-validation` owns validation-only matrices; `workflow-recovery` owns repeated post-refactor failure.
