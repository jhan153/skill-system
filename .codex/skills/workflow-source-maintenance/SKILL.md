---
name: workflow-source-maintenance
description: Post-development source maintenance workflow for behavior-preserving code cleanup, dead-code pruning, source diet, stale scaffold removal, unused import/export cleanup, shallow wrapper collapse, and small maintainability refactors. Use when the user asks to clean up, slim down, prune, or maintain source code after implementation without adding features or changing intended behavior. Do not use for feature implementation, concrete bug fixes, broad architecture redesign, dependency upgrades, documentation-only edits, or comment-only maintenance.
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
  - the task is mostly deletion, pruning, simplification, or local maintainability cleanup.
  - suspected dead code, stale scaffolding, unused imports/exports, shallow wrappers, obsolete branches, or temporary implementation leftovers should be removed safely.
  - the requested maintenance must preserve intended behavior.
- do_not_use_when:
  - the user asks to add or change product behavior; use `workflow-implementation`.
  - the user asks for behavior-preserving structural refactor such as rename, move, extract, split, or broad restructure as the main task; use `workflow-refactor-safely`.
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

## Purpose
- Remove code that is safe to remove, not code that only looks unused.
- Preserve intended behavior while reducing source surface area, stale scaffolding, speculative branches, and maintenance noise.
- Keep cleanup separate from feature work, bug fixes, broad redesign, and comment-only maintenance.

## Workflow
1. Lock scope:
   - name the source area, files, or recent implementation slice being maintained.
   - state that intended behavior is preserved by default.
   - classify the requested cleanup type: dead code, stale scaffold, unused import/export, shallow wrapper, duplicate helper, speculative abstraction, obsolete branch, debug leftover, or orphaned fixture/example.
2. Discover candidates with evidence:
   - search static references and local callers.
   - inspect exports, package entrypoints, route tables, plugin discovery, framework conventions, dynamic imports, string lookups, reflection, feature flags, migrations, compatibility shims, generated-source markers, fixtures, and examples when relevant.
   - mark weak evidence as `unclear` instead of deleting.
3. Classify each candidate:
   - `safe_delete`
   - `likely_delete_but_needs_confirmation`
   - `keep_public_contract`
   - `keep_dynamic_entrypoint`
   - `keep_migration_or_compat`
   - `keep_test_fixture`
   - `keep_generated_or_external_source`
   - `unclear`
4. Plan a small cleanup batch:
   - delete first.
   - repair imports/exports/call sites in the same batch.
   - apply only narrow local simplification needed after deletion.
   - defer risky candidates.
5. Apply one coherent batch.
6. Validate before expanding:
   - prefer typecheck, build, lint, focused tests, or public-entrypoint smoke checks that can catch missing references.
   - separate validation that was run from behavior that still needs user verification.
7. Review the diff:
   - check for accidental behavior change.
   - check that public API, routing, generated files, migrations, and compatibility paths were not removed without evidence.
   - stop and route to `workflow-bug-fix` if cleanup reveals a concrete failure.

## Delete Gate
Delete only when at least one condition is met:
- Static references are absent and the symbol is not a public export or dynamic entrypoint.
- All call sites are updated or removed in the same batch.
- Build, typecheck, lint, or focused tests confirm removal.
- The code is a shallow wrapper with no independent policy, validation, compatibility, or public API role.
- The branch, scaffold, or fixture is explicitly obsolete by code, tests, docs, or user statement.
- The import/export is mechanically unused and validated by compiler, linter, build, or equivalent evidence.

Do not delete by default when:
- The symbol is public API or package export.
- The code may be loaded by reflection, string lookup, framework convention, plugin discovery, routing, or dynamic import.
- The path is a migration, rollback, compatibility, feature-flag, or deprecation path.
- The file is generated or the source of truth is elsewhere.
- Tests are absent and reachability is ambiguous.
- Comments or stale docs are the only evidence that something is obsolete.

## Output Contract
Return only the sections needed:
- `maintenance_scope`
- `candidate_inventory`
- `delete_plan`
- `changed_artifacts`
- `deleted_or_pruned`
- `simplified`
- `preserved_with_reason`
- `validation`
- `behavior_preservation_evidence`
- `remaining_risks`

## Cross-Skill Boundaries
- `workflow-implementation` owns feature or behavior-changing implementation.
- `workflow-bug-fix` owns concrete failure repair.
- `workflow-refactor-safely` owns behavior-preserving structural changes where rename, move, extract, split, or broad restructure is the main task.
- `workflow-minimal-implementation` attaches as YAGNI pressure but does not own cleanup execution.
- `analysis-architecture-deepening` and `analysis-codebase-design` own candidate discovery or design judgment before cleanup when the safe target is not selected.
- `workflow-validation` owns validation-only matrices when installed or explicitly requested.
- `workflow-dependency-upgrade` owns package, runtime, SDK, framework, and lockfile changes.

## Invocation Examples
Positive:
- "1차 개발 끝났으니 소스코드 정리하고 죽은 코드 지워줘."
- "안 쓰는 export/import와 stale scaffold를 제거해줘."
- "코드 다이어트해줘. 기능 변화는 없어야 해."
- "임시 구현 흔적과 shallow wrapper를 증거 확인해서 걷어내줘."

Negative:
- "새 기능 구현하고 cleanup도 같이 해줘." -> `workflow-implementation` primary, source maintenance as a cleanup substep only if requested.
- "이 버그 고쳐줘." -> `workflow-bug-fix`
- "서비스 레이어를 파일 3개로 나눠줘." -> `workflow-refactor-safely`
- "deep module 후보 찾아줘." -> `analysis-architecture-deepening`
- "주석 최신화해줘." -> `workflow-comment-maintenance`
