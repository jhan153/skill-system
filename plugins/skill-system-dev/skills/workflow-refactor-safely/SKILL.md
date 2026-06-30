---
name: workflow-refactor-safely
description: Behavior-preserving refactoring workflow. Use when Codex must rename, move, extract, collapse, simplify, or restructure code while preserving observable behavior, with characterization checks, small batches, and validation before any feature or bug-fix changes.
---

# Workflow Refactor Safely

## Routing Card
- role: primary
- intent_signature:
  - safe refactor
  - behavior-preserving refactor
  - rename move extract
  - restructure code
  - refactor safely
  - 안전한 리팩터링
  - 동작 보존 리팩터링
- use_when:
  - the user asks to refactor while preserving behavior.
  - the change is mostly rename, move, extract, collapse, simplify, or restructure.
  - the work needs characterization checks before or during code movement.
- do_not_use_when:
  - the task intentionally changes behavior or adds a feature; use `workflow-implementation`.
  - the task fixes a concrete failure; use `workflow-bug-fix`.
  - the user asks for design judgment only; use `analysis-codebase-design`.
  - the same validation failure repeats after a refactor attempt; use `workflow-recovery`.
- expected_inputs:
  - refactor goal and behavior-preservation boundary
  - relevant source files, tests, callers, and existing patterns
  - validation expectations or current test command when available
- expected_outputs:
  - behavior contract, refactor scope, batch plan, changed artifacts, validation result, behavior-preservation evidence, and rollback/fallback
- context_targets:
  must_read:
    - current refactor request
    - target source files and callers
    - tests or observable behavior contract
  read_if_needed:
    - module design notes or `analysis-codebase-design` output
    - package manifests or build config when moves affect imports
    - previous validation output
  do_not_load_by_default:
    - full repo
    - full memory bank
    - unrelated architecture reports
    - unrelated plans
- risk_profile:
  reads:
    - targeted source, callers, tests, build config, and validation output
  writes:
    - WRITE_CODEBASE for behavior-preserving refactor scope only
  tools:
    - CALL_PROCESS for characterization tests, typecheck, build, lint, and focused validation
  sensitive_resources:
    - credentials default deny; refactors should not need secrets or production data
- entry_scene:
  - PREPARE

## Purpose
- Preserve observable behavior while improving structure.
- Split refactors into small reversible batches.
- Keep refactor work separate from feature changes and bug fixes unless the user explicitly accepts the mixed scope.

## Workflow
1. Define the behavior contract:
   - public API
   - data shape
   - side effects
   - errors/logs when user-visible
   - performance expectations when relevant
2. Identify characterization evidence:
   - existing tests
   - focused smoke command
   - typecheck/build
   - snapshot/fixture/manual check when no tests exist
3. Choose one refactor batch:
   - rename
   - move
   - extract
   - inline/collapse
   - split module
   - narrow interface
4. Apply one coherent batch.
5. Validate before broadening.
6. Inspect diff for behavior drift, unrelated cleanup, dead compatibility paths, and missed callers.
7. Continue only when validation preserves the original contract.

## Refactor Rules
- Do not mix behavior changes with refactor unless the user explicitly asks and validation separates both.
- Prefer mechanical moves/renames before semantic rewrites.
- Keep old compatibility shims only when callers cannot be updated safely in the same scope.
- Delete shallow wrappers only when callers and tests confirm behavior preservation.
- If a refactor reveals a bug, stop and route the bug through `workflow-bug-fix` instead of quietly changing behavior.

## Output Contract
Return only the sections needed:
- `behavior_contract`
- `refactor_scope`
- `batch_plan`
- `changed_artifacts`
- `validation`
- `behavior_preservation_evidence`
- `rollback_or_fallback`
- `remaining_risks`

## Cross-Skill Boundaries
- `analysis-codebase-design` owns the design decision for module boundaries and seams before refactor.
- `workflow-implementation` owns feature or behavior-changing implementation.
- `workflow-bug-fix` owns concrete failure repair.
- `workflow-minimal-implementation` can challenge speculative abstractions introduced by the refactor.
- `workflow-recovery` owns repeated validation failure after attempted refactor fixes.

## Invocation Examples
Positive:
- "이 서비스 파일을 동작 보존하면서 작게 나눠줘."
- "이 이름들을 도메인 모델에 맞게 안전하게 rename해줘."
- "이 shallow wrapper를 제거하되 기존 테스트로 검증해줘."

Negative:
- "새 기능 추가하면서 구조도 바꿔줘." -> `workflow-implementation` with refactor as scoped substep
- "이 버그 고쳐줘." -> `workflow-bug-fix`
- "어디에 seam을 둘지 설계만 해줘." -> `analysis-codebase-design`
