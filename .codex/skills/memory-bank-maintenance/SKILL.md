---
name: memory-bank-maintenance
description: Validates, consolidates, and reports project-scoped memory-bank state while preserving append-only history. Use when the user explicitly asks to inspect state, run validation, resolve conflicts, or consolidate recurring memory items.
---

# Memory Bank Maintenance

## Routing Card
- role: memory_operation
- intent_signature:
  - memory-bank status, validate, consolidate, conflict-check, stale entry review
- use_when:
  - the user or automation explicitly asks to inspect, validate, consolidate, report, or resolve conflicts in an existing memory bank.
- do_not_use_when:
  - the request is initialization, direct goal/rule mutation, new correction capture, or design brainstorming.
- expected_inputs:
  - existing memory-bank files
  - requested operation: `report`, `validate`, `consolidate`, or `conflict-check`
- expected_outputs:
  - validation/report results, conflict list, optional consolidation event, status
- context_targets:
  must_read:
    - relevant `meta.json`, `events.jsonl`, and affected sections of `current.md`
  read_if_needed:
    - `archive.md` for conflict or consolidation evidence
    - `reference.md` for schema or consolidation rules
  do_not_load_by_default:
    - unrelated project memory
    - full repo
    - all memory banks
- risk_profile:
  reads:
    - targeted memory bank files
  writes:
    - none for report/validate; consolidation writes only when requested
  tools:
    - safe schema/file validation
  sensitive_resources:
    - credentials default deny
- entry_scene:
  - PREPARE

Maintain the health of an existing memory bank. This skill owns validation, reporting, conflict handling, and consolidation.

Read `reference.md` for the maintenance schema and consolidation rules and `docs/document.md` when you need detailed flow or failure-path detail.

## Related Skills
- `memory-bank-init`: 메모리뱅크가 없으면 먼저 실행되어야 합니다.
- `memory-bank-update`: 유지보수 중 드러난 goal/rule 변경 요청은 이 스킬이 아니라 update 단계로 넘깁니다.
- `memory-bank-correction-capture`: 새 recurring correction을 기록하는 일은 유지보수 자체가 아니라 correction-capture 단계가 담당합니다.
- `strict-response-quality`: 사용자가 형식적 상태 보고를 원할 때 채팅 응답을 정리할 수 있지만, 메모리뱅크 상태 머신은 이 스킬이 소유합니다.

## Cross-Skill Routing
- 메모리뱅크가 없으면 `memory-bank-init`으로 되돌립니다.
- goal/rule의 생성·변경·폐기는 `memory-bank-update`로 넘깁니다.
- 새로운 recurring correction 기록은 `memory-bank-correction-capture`로 넘기고, 이 스킬은 이미 존재하는 ledger의 validate/report/consolidate만 담당합니다.
- `strict-response-quality`가 함께 활성화되어도 유지보수 연산과 상태 판정은 이 스킬의 Output Format과 Validation Checks를 우선합니다.

## What This Skill Does
- Reports current memory-bank state without unnecessary writes.
- Validates schema, file integrity, and cross-file consistency.
- Consolidates duplicate or stale items and records the consolidation event.

## When to Use
- The user asks for memory-bank status or validation.
- The user asks to consolidate recurring mistakes or stale rules.
- Automation runs a scheduled maintenance pass.
- The user asks to inspect conflicts or repair inconsistencies.

## When Not to Use
- The request is to initialize a new memory bank.
- The request is to create or update a goal or rule directly.
- The request is to capture a new correction-based mistake.
- The user is only brainstorming the design without asking for state inspection or maintenance.

## Required Inputs
- Existing memory-bank files.
- Requested operation: `report`, `validate`, `consolidate`, or `conflict-check`.
- Optional schedule or automation context for consolidation.

## Preflight Checks
1. Confirm the memory bank exists.
2. Parse `meta.json` and `events.jsonl`.
3. Check that `current.md` sections and item contracts are intact.
4. Identify whether the request is read-only or write-producing.
5. If consolidation is requested, load candidate mistakes and deprecated-rule candidates.

## Workflow
1. Run schema and file integrity checks.
2. If the request is `report` or `validate`, do not write unless the user explicitly asked for repair.
3. If the request is `consolidate`, deduplicate candidate mistakes, resolve conflicts, and append a `system` consolidation event.
4. Update `meta.json.snapshot_version`, `updated_at`, and `last_consolidated_at` only for successful write-producing maintenance.
5. Report results with explicit validation status.

## Validation Checks
- `events.jsonl` and `meta.json` are parseable.
- `current.md` item fields match the canonical contract.
- Consolidation increments `snapshot_version`.
- Read-only maintenance leaves the ledger unchanged.

## Failure Handling
- If files are missing, stop and report `blocked`.
- If the schema is inconsistent, report the exact mismatch and return `user-verification-needed` unless repair was explicitly requested.
- If consolidation inputs are too ambiguous, stop before writing and report `unverified`.

## Resource and Risk Boundary
- Reads: relevant memory-bank ledger files and schema references.
- Writes: none for report/validate; consolidation writes append-only events and metadata only when requested.
- Tool/process calls: safe parsing and validation only.
- Network access: none.
- Credential access: default deny.
- Generated artifacts: status report or updated memory ledger files.
- Destructive actions: hard deletion forbidden; consolidate or deprecate through ledger events.
- Required checkpoints: operation type, read-only vs write-producing mode, schema mismatch evidence.

## Recovery and Context Expansion
- If files are missing, stop and route to `memory-bank-init` only when initialization is requested.
- If schema is unclear, read `reference.md` before archive history.
- If conflict evidence is missing, read only the affected archive entries.
- If the request is goal/rule mutation, route to `memory-bank-update`.
- If the request is new recurring correction capture, route to `memory-bank-correction-capture`.
- Never recover by loading all memory banks, unrelated project memory, or all skills at once.

## Output Format
- Report the requested operation.
- Report appended event IDs when writes occurred.
- Report conflicts, affected items, and validation status using one of `agent-verified`, `user-verification-needed`, `unverified`, `blocked`.

## Examples
- "메모리뱅크 상태를 점검해 주세요."
- "candidate 실수들을 통합해 주세요."
- "이 메모리뱅크에 스키마 충돌이 있는지 확인해 주세요."

## Known Limits
- Read-only report/validate modes do not repair memory state.
- Consolidation can merge unrelated entries without strong evidence.
- Archived or superseded entries stay excluded unless conflict/history requires them.
- Return to scheduling when mutation scope or persistent intent is unclear.
