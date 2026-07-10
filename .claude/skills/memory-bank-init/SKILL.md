---
name: memory-bank-init
description: Initialize project-scoped persistent memory by creating the canonical baseline files, project identity metadata, and first append-only event. Use only on an explicit init or reinit request; do not overwrite an existing bank as if it were a normal update.
---

# Memory Bank Init

## Routing Card
- role: memory_operation
- intent_signature:
  - initialize memory bank, start persistent project memory, 메모리뱅크 초기화
- use_when:
  - the user explicitly asks to create project memory or explicitly approves reinitialization.
- do_not_use_when:
  - the request is an update, correction capture, maintenance operation, or design discussion.
- expected_inputs:
  - project root, target path, and explicit init/reinit intent
- expected_outputs:
  - baseline files, project identity, first event, and validation result
- context_targets:
  must_read:
    - project identity and existing target-path state
    - `.codex/docs/memory_mutation_contract.md` before creating files
  read_if_needed:
    - `reference.md` for the canonical schema and project-id rule
    - `docs/document.md` only for an exceptional failure path
  do_not_load_by_default:
    - full repo, other projects' memory, or unrelated history
- risk_profile:
  reads:
    - project identity and target memory path
  writes:
    - canonical baseline files only after explicit init/reinit intent
  tools:
    - safe filesystem and schema checks
  sensitive_resources:
    - credentials default deny
- entry_scene:
  - PREPARE

## Preflight
1. Resolve the project root and derive `project_id` by the rule in `reference.md`.
2. Inspect the target path without loading unrelated memory.
3. If a bank exists, stop unless the user explicitly requested reinitialization.
4. Treat reinitialization as a migration/backup-sensitive operation: never delete or overwrite accepted history silently.
5. Confirm the target is writable.

## Workflow
1. Stage `current.md`, `archive.md`, `events.jsonl`, and `meta.json` for a fresh target under the shared mutation contract.
2. Append the first `entity=project`, `action=create` event.
3. Write the baseline current/archive sections and project metadata.
4. Commit the fresh bank as one unit where possible, then validate all files and stable project identity.

If explicit reinitialization is requested, preserve or archive the existing bank according to repository policy before creating a replacement. If no safe preservation policy exists, report `blocked` instead of deleting it.

## Validation
- All four files exist and parse.
- A fresh bank has exactly one init event.
- `current.md` contains the required baseline sections.
- `meta.json` records schema/snapshot version and the derived project identity.
- Existing accepted history was not silently destroyed.

## Output
Report created/preserved paths, the project/event IDs, validation status, and any identity or reinit uncertainty.

## Behavior Cases
- Positive: “이 저장소에 프로젝트 메모리뱅크를 처음 만들어줘.”
- Negative: “기존 goal 하나 수정해줘.” → `memory-bank-update`.
- Edge: a bank exists and the user only says “초기화해줘” ambiguously → ask/mark blocked before destructive replacement.

## Known Limits
- Initialization creates storage, not the substantive long-term memory policy.
- Path-hash identity is less portable than an explicit or repository-derived identity.
