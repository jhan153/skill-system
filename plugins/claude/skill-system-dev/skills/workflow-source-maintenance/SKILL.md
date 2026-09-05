---
name: workflow-source-maintenance
description: "Perform behavior-preserving source maintenance in one of two modes: prune code proven obsolete, or synchronize comments/docstrings/TODO markers with current code meaning. Use for explicit source cleanup after implementation; do not use for feature work, concrete bug repair, live-code restructuring, dependency upgrades, or general documentation."
---

# Workflow Source Maintenance

## Routing Card
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

## Modes

- `source_prune`: remove source proven obsolete, plus only deletion-required import/export/caller repair.
- `comment_sync`: update or prune comments, docstrings, inline rationale, and TODO/FIXME markers only. Read [Comment Sync](references/comment-sync.md).

Feature work and accepted production-mechanism replacement remain with `workflow-implementation`;
only semantically admitted bounded same-contract repair belongs to `workflow-bug-fix`; reachable-code
restructuring belongs to `workflow-refactor-safely`. Apply YAGNI/directness pressure inside those
owners rather than attaching another skill. If maintenance exposes one of those needs, preserve the
evidence and hand off rather than broadening this workflow.

## Common Workflow

1. Lock the mode, target slice, canonical owner, behavior boundary, and generated/external projections.
2. Establish current production meaning. In `source_prune`, trace static and dynamic reachability; in `comment_sync`, inspect the exact code and public/tool-consumed metadata the text describes.
3. Classify candidates and defer uncertainty. Absence of static references or a stale comment is a lead, not proof.
4. Apply one coherent batch. Change the canonical owner, regenerate owned projections, and make no unrelated structural or behavior change.
5. Run the narrowest discriminating existing check and review the diff. Actual-path evidence outranks static, mock, or agent-authored checks when source selection or a production boundary is material.
6. Apply `references/execution_assurance_contract.md` only when its trigger is material; preserve this maintenance workflow as the sole mutation owner and reuse equivalent reachability/review/readback evidence.

## Source-Prune Gate

Delete only when canonical ownership is known, production reachability and contract checks support obsolescence, and no material public, dynamic, migration, compatibility, fixture, generated, or external-source role remains. Classify candidates as `safe_delete`, `needs_confirmation`, `keep_public_contract`, `keep_dynamic_entrypoint`, `keep_migration_or_compat`, `keep_fixture`, `keep_generated_or_external_source`, or `unclear`.

Valid removals include an unreachable internal symbol, an explicitly obsolete branch/scaffold, or an unused import/export confirmed by the language toolchain. A still-reachable wrapper collapse or live-flow simplification is a refactor, not pruning.

## Output

Return only applicable fields: `mode`, `maintenance_scope`, `candidate_inventory`, `change_plan`, `changed_artifacts`, `deleted_or_pruned`, `updated_comments`, `preserved_with_reason`, `public_contract_impact`, `validation`, `behavior_preservation_evidence`, and `remaining_risks`.
