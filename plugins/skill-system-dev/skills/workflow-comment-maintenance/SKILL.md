---
name: workflow-comment-maintenance
description: Behavior-preserving comment and docstring maintenance workflow for synchronizing comments, docstrings, inline rationale, and TODO/FIXME markers with current code meaning. Use when the user asks to update, fix, prune, or sync comments or docstrings without changing code behavior. Do not use for feature implementation, concrete bug fixes, structural refactors, source/code cleanup, dependency upgrades, or README/wiki/general documentation writing.
---

# Workflow Comment Maintenance

## Routing Card
- role: primary
- intent_signature:
  - comment maintenance
  - comment sync
  - docstring update
  - docstring sync
  - stale comment
  - outdated comment
  - comment cleanup
  - inline rationale
  - TODO cleanup
  - FIXME cleanup
  - 주석 최신화
  - 주석 동기화
  - 주석 정리
  - 불필요한 주석 제거
  - docstring 수정
  - TODO 정리
  - FIXME 정리
- use_when:
  - the user asks to update, fix, or sync comments or docstrings to match current code.
  - the task is comment-only or docstring-only maintenance with no intended code-behavior change.
  - stale, misleading, redundant, or noise comments and outdated TODO/FIXME markers should be corrected or pruned.
  - inline rationale must be preserved, compressed, or made accurate.
- do_not_use_when:
  - the user asks to add or change product behavior; use `workflow-implementation`.
  - the user asks for a behavior-preserving structural refactor as the main task; use `workflow-refactor-safely`.
  - the user asks to fix a concrete failing test, build error, runtime exception, or regression; use `workflow-bug-fix`.
  - the user asks to remove dead code, unused imports/exports, or run a source diet; use `workflow-source-maintenance`.
  - the user asks to clarify domain concepts, entities, invariants, or business rules first; use `analysis-domain-modeling`.
  - the user asks to write or revise README, wiki, or general project documentation; that is documentation writing, not in-code comment maintenance.
- expected_inputs:
  - comment maintenance scope and the behavior-preservation boundary
  - target source files, the comments/docstrings in question, and current code meaning
  - public API / framework / generated-doc context when docstrings may be user-facing
- expected_outputs:
  - comment maintenance scope, comment inventory, sync plan, changed artifacts, updated/pruned comments, preserved high-context comments with reasons, public-contract impact notes, validation, and remaining risks
- context_targets:
  must_read:
    - current comment maintenance request
    - target source files and the comments/docstrings being synced
    - the code the comments describe (signatures, control flow, invariants)
  read_if_needed:
    - public API surface, framework docstring consumption (CLI/OpenAPI/schema/help text), or generated-documentation policy when docstrings may be user-facing
    - linter/doc-build/typecheck configuration when comments are validated by tooling
    - prior implementation plan only when the user references it
  do_not_load_by_default:
    - full repo
    - broad architecture reports
    - unrelated docs or memory
- risk_profile:
  reads:
    - targeted source files and the comments/docstrings in scope
  writes:
    - WRITE_CODEBASE for comment, docstring, and inline-rationale text only
  tools:
    - focused search, diff, and doc/lint/typecheck checks tied to the comment scope
  sensitive_resources:
    - credentials default deny; comment maintenance should not require secrets or production data
- entry_scene:
  - PREPARE

## Purpose
- Synchronize comments, docstrings, inline rationale, and TODO/FIXME markers with what the code actually does.
- Preserve high-context knowledge that code alone cannot recover, while removing stale, misleading, or noise comments.
- Keep comment maintenance separate from feature work, bug fixes, structural refactors, source cleanup, and documentation writing.
- Never change code behavior; hand off to the owning execution skill when a comment exposes a real code problem.

## Workflow
1. Lock scope:
   - name the files or comment areas being maintained.
   - state that intended code behavior is preserved by default (comments/docstrings/markers only).
   - classify each item: stale (contradicts code), misleading, redundant/noise, missing rationale, outdated TODO/FIXME, or public-contract docstring.
2. Read the code the comment describes:
   - confirm current signatures, control flow, invariants, and external contracts before rewriting a comment.
   - do not trust the existing comment as evidence of behavior; trust the code.
3. Classify each comment:
   - `sync_to_code` (update to match current behavior)
   - `prune_noise` (remove redundant, obvious, or dead comment)
   - `preserve_high_context` (keep, compress, or clarify a design reason, invariant, contract, past-bug guard, or concurrency/cache/security/performance constraint)
   - `resolve_or_keep_marker` (close an obsolete TODO/FIXME or keep it with a reason)
   - `public_contract_docstring` (docstring consumed as user-facing metadata)
   - `unclear` (insufficient evidence; ask or leave it)
4. Plan a small comment batch:
   - sync and prune in coherent units per file or symbol.
   - never edit executable code in this workflow; if code must change, stop and hand off.
5. Apply one coherent batch (comments/docstrings/markers only).
6. Validate:
   - prefer doc-build, docstring linter, doctest, or typecheck when comments are tool-consumed; otherwise diff review.
   - confirm no executable line changed (comment/docstring-only diff).
7. Review the diff:
   - check that no behavior or code token outside comments changed.
   - check that high-context rationale was preserved, not deleted.
   - flag any docstring change that alters public API, CLI, schema, or help text as a user-facing metadata change.

## Behavior & Context Gate
Preserve, do not remove, when a comment is the only carrier of:
- design rationale or rejected-alternative reasoning
- an invariant, precondition, or postcondition not enforced in code
- an external contract, protocol, or compatibility note
- a guard explaining a past bug, race, deadlock, or security fix
- a concurrency, caching, ordering, security, or performance constraint

Prune only when:
- the comment merely restates the adjacent code with no added meaning
- the comment is dead (refers to removed code) or contradicts current behavior and carries no preservable rationale
- the TODO/FIXME is demonstrably resolved by current code, tests, or user statement

Stop and hand off (do not fix here) when:
- a comment reveals a real code defect; route to `workflow-bug-fix`
- correcting the comment requires changing behavior or structure; route to `workflow-implementation` or `workflow-refactor-safely`
- a docstring is consumed as public API, CLI, OpenAPI, schema, or generated-doc metadata; report the user-facing impact before changing it

## Output Contract
Return only the sections needed:
- `comment_scope`
- `comment_inventory`
- `sync_plan`
- `changed_artifacts`
- `updated_or_pruned`
- `preserved_with_reason`
- `public_contract_impact`
- `validation`
- `behavior_preservation_evidence`
- `remaining_risks`

## Cross-Skill Boundaries
- `workflow-implementation` owns feature or behavior-changing implementation; comment sync is a substep only when implementation is primary.
- `workflow-refactor-safely` owns behavior-preserving structural changes; comment sync rides along but does not own a refactor.
- `workflow-bug-fix` owns concrete failure repair when a comment exposes a real defect.
- `workflow-source-maintenance` owns dead-code and unused-import pruning and source diet; comment-only maintenance routes here instead.
- `analysis-domain-modeling` owns clarifying domain concepts and invariants before comment language is settled.
- `workflow-validation` owns validation-only matrices when installed or explicitly requested.

## Invocation Examples
Positive:
- "주석이 코드랑 안 맞아. 최신화해줘."
- "불필요하고 뻔한 주석 정리하고, 설계 이유 적힌 주석은 남겨줘."
- "docstring이 현재 함수 시그니처랑 동작에 맞는지 고쳐줘."
- "오래된 TODO/FIXME 정리해줘. 끝난 건 지우고 남길 건 이유 달아줘."

Negative:
- "기능 구현하고 주석도 맞춰줘." -> `workflow-implementation` primary, comment maintenance as a support phase.
- "리팩터링하면서 주석도 같이 맞춰줘." -> `workflow-refactor-safely` primary, comment maintenance as a support phase.
- "안 쓰는 코드랑 import 지워줘." -> `workflow-source-maintenance`
- "도메인 규칙부터 정리해줘." -> `analysis-domain-modeling`
- "README에 사용법 문서 써줘." -> documentation writing, not in-code comment maintenance.
