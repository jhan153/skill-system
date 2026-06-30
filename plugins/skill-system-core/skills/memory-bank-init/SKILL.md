---
name: memory-bank-init
description: Initializes a project-scoped memory bank by creating baseline files, project identity metadata, and the first append-only event. Use when the user explicitly asks to start, initialize, or reinitialize persistent project memory.
---

# Memory Bank Init

## Routing Card
- role: memory_operation
- intent_signature:
  - initialize memory bank, start persistent project memory, 메모리뱅크 초기화
- use_when:
  - the user explicitly asks to create or reinitialize a project memory bank.
  - no project-scoped memory bank exists and persistent memory is requested.
- do_not_use_when:
  - the request is a goal/rule update, recurring correction capture, maintenance report, or memory design discussion.
- expected_inputs:
  - project root
  - explicit init or reinit request
  - existing memory-bank state when present
- expected_outputs:
  - baseline memory-bank files, first event, validation status
- context_targets:
  must_read:
    - project root identity
    - existing memory-bank target path if present
  read_if_needed:
    - `reference.md` for canonical schema
    - `docs/document.md` for failure-path detail
  do_not_load_by_default:
    - full memory bank
    - unrelated project memory
    - full repo
- risk_profile:
  reads:
    - target memory path and project identity
  writes:
    - creates baseline memory files only
  tools:
    - safe filesystem checks
  sensitive_resources:
    - credentials default deny
- entry_scene:
  - PREPARE

Initialize a project-scoped memory bank once per project lifecycle or when the user explicitly requests reinitialization.

Read `reference.md` for the canonical init schema and `docs/document.md` only when you need execution flow or failure-path detail.

## Related Skills
- `memory-bank-update`: 초기화 이후 goal/rule 추가·수정·폐기를 담당합니다.
- `memory-bank-correction-capture`: 초기화 이후 반복 정정이나 persistent mistake 후보 캡처를 담당합니다.
- `memory-bank-maintenance`: 초기화 이후 상태 점검, 검증, 통합, 충돌 점검을 담당합니다.

## Cross-Skill Routing
- 메모리뱅크가 아직 없으면 다른 memory-bank 스킬보다 이 스킬이 우선합니다.
- 초기화가 끝난 뒤 goal/rule 변경 요청은 `memory-bank-update`, 반복 실수 캡처는 `memory-bank-correction-capture`, 상태 점검/통합은 `memory-bank-maintenance`로 넘깁니다.

## What This Skill Does
- Creates the memory-bank storage root and baseline files.
- Derives a stable `project_id` and records project identity metadata.
- Appends the first append-only event before writing the initial current snapshot.

## When to Use
- The user explicitly asks to initialize or start a memory bank.
- The project does not have `docs/memory-bank/projects/{project_id}/` yet.
- The user explicitly approves reinitializing an existing memory bank.

## When Not to Use
- The request is only to change a goal or rule.
- The request is only to capture a correction-based mistake.
- The request is only to validate, consolidate, or report state.
- The user is only discussing memory-bank design without asking for initialization.

## Required Inputs
- Project root or repository context.
- An explicit user request to initialize or reinitialize memory storage.
- Existing memory-bank files if they already exist.

## Preflight Checks
1. Resolve the project root.
2. Derive `project_id` using the rule in `reference.md`.
3. Check whether target files already exist.
4. If files exist, confirm the request is a true reinitialization rather than an update.
5. Confirm the target path is writable.

## Workflow
1. Create `current.md`, `archive.md`, `events.jsonl`, and `meta.json`.
2. Append the first event with `entity=project` and `action=create`.
3. Write baseline sections to `current.md`.
4. Append the matching init block to `archive.md`.
5. Write `meta.json` with `schema_version`, `snapshot_version`, and project locator data.

## Validation Checks
- All four files exist.
- `events.jsonl` contains exactly one init event after a fresh initialization.
- `current.md` contains the three required baseline sections.
- `meta.json` is valid JSON and records the derived `project_id`.

## Failure Handling
- If an existing memory bank is present and the user did not ask to reinitialize, stop and report `blocked`.
- If `project_id` cannot be derived from slug or git remote, fall back to the path-hash rule and mark that choice in `meta.json`.
- If any required file cannot be written, stop and report which file failed.

## Resource and Risk Boundary
- Reads: project identity and existing memory-bank target files only.
- Writes: `current.md`, `archive.md`, `events.jsonl`, and `meta.json` for the target project.
- Tool/process calls: safe path/file validation only.
- Network access: none.
- Credential access: default deny.
- Generated artifacts: new memory-bank baseline files.
- Destructive actions: do not delete existing memory; reinitialization requires explicit user request.
- Required checkpoints: project root, target path, existing-bank status, and reinit intent if files exist.

## Recovery and Context Expansion
- If project identity is unclear, resolve repo root or path hash before reading broader context.
- If files already exist, stop and distinguish update, maintenance, or explicit reinit.
- If schema detail is unclear, read `reference.md` first, then `docs/document.md` only if needed.
- If the request belongs to update, correction, or maintenance, return to scheduling.
- Never recover by loading all memory banks, all repo docs, or all skills at once.

## Output Format
- Report created paths.
- Report appended event IDs.
- Report validation status using one of `agent-verified`, `user-verification-needed`, `unverified`, `blocked`.

## Examples
- "프로젝트 메모리뱅크를 초기화해 주세요."
- "이 저장소에 persistent memory를 새로 시작해 주세요."
- "기존 memory bank를 지우고 다시 초기화해 주세요."

## Known Limits
- Initialization creates structure; it does not decide long-term memory relevance.
- Path-hash project identity is less portable than explicit or repo-derived identity.
- Ambiguous project identity requires user verification before persistent writes.
- Do not load or create full memory content beyond the initialization scope.
