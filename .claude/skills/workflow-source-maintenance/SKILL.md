---
name: workflow-source-maintenance
description: Post-development source maintenance workflow for behavior-preserving dead-code pruning, source diet, stale scaffold removal, and unused import/export cleanup. Use when the user asks to delete or prune source proven obsolete after implementation without adding features or changing intended behavior. Do not use for live-code restructuring or wrapper collapse, feature implementation, concrete bug fixes, broad architecture redesign, dependency upgrades, documentation-only edits, or comment-only maintenance.
disable-model-invocation: true
---

# Workflow Source Maintenance

## Routing Card
- role: primary
- intent_signature:
  - source maintenance
  - code maintenance
  - source cleanup
  - code cleanup
  - source diet
  - dead code removal
  - dead-code pruning
  - unused code
  - unused exports
  - stale scaffold
  - post-development cleanup
  - 유지보수
  - 소스 정리
  - 코드 다이어트
  - 죽은 코드 제거
  - 불필요한 코드 제거
  - 1차 개발 후 정리
- use_when:
  - the user asks to clean up or slim down source code after implementation.
  - the task is mostly deletion or pruning of obsolete source, stale scaffolding, unused imports/exports, obsolete branches, or temporary implementation leftovers.
  - the requested maintenance must preserve intended behavior.
- do_not_use_when:
  - the user asks to add or change product behavior; use `workflow-implementation`.
  - the user asks for behavior-preserving structural refactor such as rename, move, extract, split, or broad restructure as the main task; use `workflow-refactor-safely`.
  - the user asks to inline or collapse a still-reachable wrapper, simplify live control flow, or update callers for a structural change; use `workflow-refactor-safely` regardless of change size.
  - the user asks to fix a concrete failing test, build error, runtime exception, or regression; use `workflow-bug-fix`.
  - the user asks for architecture candidate discovery or design judgment only; use `analysis-architecture-deepening` or `analysis-codebase-design`.
  - the user asks only to update comments or docstrings; use `workflow-comment-maintenance`.
  - the user asks to upgrade packages, SDKs, frameworks, or lockfiles; use `workflow-dependency-upgrade`.
- expected_inputs:
  - maintenance scope and behavior-preservation boundary
  - target source files, tests, callers, public exports, and build/typecheck/lint commands when available
  - evidence for obsolete code when user already has candidates
- expected_outputs:
  - maintenance scope, candidate inventory, delete plan, changed artifacts, deleted/pruned code, simplified code, preserved candidates with reasons, validation, behavior-preservation evidence, and remaining risks
- context_targets:
  must_read:
    - current maintenance request
    - target source files and local callers
    - relevant tests, public exports, package entrypoints, routing tables, or generated-source policy when deletion risk exists
  read_if_needed:
    - build/typecheck/lint configuration
    - framework conventions, plugin discovery, dynamic import, reflection, CLI/API entrypoint registration, or feature flag definitions
    - prior implementation plan only when the user references it
  do_not_load_by_default:
    - full repo
    - broad architecture reports
    - unrelated docs or memory
    - package manager state unless dependency cleanup is in scope
- risk_profile:
  reads:
    - targeted source, callers, tests, exports, and validation configuration
  writes:
    - WRITE_CODEBASE for behavior-preserving source/test/config cleanup only
  tools:
    - focused search, diff, build/typecheck/lint/test, and public-entrypoint checks tied to the cleanup scope
  sensitive_resources:
    - credentials default deny; source maintenance should not require secrets or production data
- entry_scene:
  - PREPARE

## Contract
- Remove only code proven obsolete while preserving intended user-visible behavior. “No static references” is a lead, not proof.
- Establish one canonical owner before editing. Generated/runtime projections are never a second source: change the owner, regenerate, and read back the affected projection.
- Keep source maintenance to proven-obsolete deletion and the smallest import/export/caller repair caused by that deletion. Route live-code simplification, wrapper collapse, feature work, structural redesign, or concrete failures to their owners.

## Workflow
1. Lock the maintenance slice, behavior-preservation boundary, cleanup type, canonical source, and generated or external projections. If ownership is ambiguous, stop before mutation.
2. Trace production reachability through callers, exports, package/CLI entrypoints, route tables, plugin discovery, framework conventions, dynamic imports, string lookup, reflection, feature flags, migrations, compatibility paths, and source-generation markers as relevant.
3. When source selection, migration, transforms, adapters, or external boundaries are involved, inspect the actual selected path or readback. Static, mock, or agent-authored-test success cannot override a conflicting production or user-path observation.
4. Classify candidates as `safe_delete`, `needs_confirmation`, `keep_public_contract`, `keep_dynamic_entrypoint`, `keep_migration_or_compat`, `keep_fixture`, `keep_generated_or_external_source`, or `unclear`.
5. Apply one coherent batch: delete first, repair imports/exports/callers, regenerate owned projections, and make only deletion-required local simplifications. Defer every uncertain candidate.
6. Validate the behavior boundary with the narrowest discriminating evidence: affected production/readback path when material, then relevant build/typecheck/lint, public-entry smoke, or existing focused regression checks. Review the diff before expanding.

If cleanup exposes a concrete failing path, preserve the evidence and route repair to `workflow-bug-fix`; do not delete the path or relabel the batch behavior-preserving.

## Delete Gate
Delete only when canonical ownership is known, production reachability and contract checks support obsolescence, and no material public, dynamic, migration, compatibility, fixture, or external-source role remains. Valid cases include:
- an internal symbol with no static or dynamic reachability;
- call sites removed or updated in the same batch without changing the behavior boundary;
- an unreachable wrapper with no callers or dynamic/public entrypoint role; collapsing a still-reachable wrapper belongs to `workflow-refactor-safely`;
- an explicitly obsolete branch/scaffold supported by current code, contract, or user decision;
- a mechanically unused import/export confirmed by the language toolchain.

Builds, linters, and tests validate only what they cover; they do not independently prove semantic obsolescence. Mocks prove the mock boundary. Do not delete when reachability is ambiguous, a generated file's owner lies elsewhere, or stale comments/docs are the only evidence.

## Output
Return only applicable sections: `maintenance_scope`, `candidate_inventory`, `delete_plan`, `changed_artifacts`, `deleted_or_pruned`, `simplified`, `preserved_with_reason`, `validation`, `behavior_preservation_evidence`, and `remaining_risks`.

Keep feature implementation with `workflow-implementation`, concrete repair with `workflow-bug-fix`, live-code rename/move/extract/split/inline/collapse with `workflow-refactor-safely`, and comment-only or dependency work with their dedicated workflows.
