---
name: memory-bank-update
description: Updates stored project goals or rules with append-only events, current-state reflection, and archive tracking. Use when the user explicitly adds, changes, or deprecates persistent project goals or cross-session rules.
---

# Memory Bank Update

## Routing Card
- role: memory_operation
- intent_signature:
  - persistent goal update, persistent rule update, 메모리 goal/rule 수정
- use_when:
  - the user explicitly adds, changes, or deprecates persistent project goals or cross-session rules.
- do_not_use_when:
  - the memory bank is missing, the request is correction capture, maintenance, or one-turn preference.
- expected_inputs:
  - existing memory-bank files
  - target `goal` or `rule`
  - requested mutation and evidence summary
- expected_outputs:
  - append-only event, updated current snapshot, archive entry, validation status
- context_targets:
  must_read:
    - relevant `meta.json`, `events.jsonl`, and current item in `current.md`
  read_if_needed:
    - `reference.md` for canonical enum/schema
    - matching archive block for conflict resolution
  do_not_load_by_default:
    - full memory bank
    - unrelated project memory
    - correction-capture records
- risk_profile:
  reads:
    - targeted memory files and target item
  writes:
    - append event and update current/archive/meta for goal/rule only
  tools:
    - safe file validation
  sensitive_resources:
    - credentials default deny
- entry_scene:
  - PREPARE

Update persistent goals or rules only. Do not use this skill for initialization, correction-based mistake capture, or maintenance tasks.

Read `reference.md` for the canonical update schema and `docs/document.md` only when you need mutation flow or failure-path detail.

## Related Skills
- `memory-bank-init`: 메모리뱅크가 없을 때 선행되어야 합니다.
- `memory-bank-correction-capture`: 정정 사항이 goal/rule 변경이 아니라 recurring mistake 캡처라면 이 스킬 대신 사용합니다.
- `memory-bank-maintenance`: 갱신 후 상태 점검, 충돌 확인, 통합이 필요할 때 후행 유지보수를 담당합니다.

## Cross-Skill Routing
- 메모리뱅크가 없으면 `memory-bank-init`이 선행되어야 합니다.
- 요청이 correction-based mistake capture면 쓰지 말고 `memory-bank-correction-capture`로 넘깁니다.
- 요청이 report/validate/consolidate/conflict-check면 `memory-bank-maintenance`로 넘깁니다.
- 이 스킬은 persistent `goal`/`rule` mutation만 소유합니다.

## What This Skill Does
- Applies goal and rule mutations to an existing memory bank.
- Appends a ledger event before changing the current snapshot.
- Keeps deletions as `status=deprecated` instead of hard deletion.

## When to Use
- The user explicitly adds a new project goal.
- The user explicitly updates a persistent project rule.
- The user explicitly deprecates a goal or rule that should no longer apply across sessions.

## When Not to Use
- The memory bank does not exist yet.
- The user is correcting prior memory and the correction should be captured as a recurring mistake.
- The request is only to validate, consolidate, or inspect the memory-bank state.
- The request is a one-off preference that should not persist across sessions.

## Required Inputs
- Existing memory-bank files.
- A target entity of `goal` or `rule`.
- The requested create, update, or deprecate change.
- The reason or evidence summary for the change.

## Preflight Checks
1. Confirm the memory bank exists.
2. Confirm the target entity is `goal` or `rule`.
3. Load `meta.json` and parse the latest snapshot version.
4. Parse `events.jsonl` and `current.md` enough to locate the target item.
5. Reject the request if it belongs to correction capture or maintenance instead.

## Workflow
1. Build the event with canonical enum names.
2. Append the event to `events.jsonl` first.
3. Reflect the latest item state in `current.md`.
4. Append the matching history block to `archive.md`.
5. Update `meta.json.updated_at`.

## Validation Checks
- The event exists in `events.jsonl`.
- `current.md` reflects the new state and keeps stable item IDs.
- `archive.md` records the same `event_id`.
- A delete request results in `status=deprecated`, not removal.

## Failure Handling
- If the memory bank does not exist, stop and report that `memory-bank-init` is required.
- If the target item cannot be identified for an update or deprecate action, stop and report `user-verification-needed`.
- If the request is actually a correction-based mistake capture, stop without writing and redirect to `memory-bank-correction-capture`.

## Resource and Risk Boundary
- Reads: target memory ledger files and relevant item only.
- Writes: append-only event first, then current/archive/meta reflection for goal/rule mutation.
- Tool/process calls: safe file parsing and validation only.
- Network access: none.
- Credential access: default deny.
- Generated artifacts: updated memory ledger files.
- Destructive actions: hard deletion is forbidden; deprecate instead.
- Required checkpoints: memory exists, target entity is `goal` or `rule`, and request is persistent.

## Recovery and Context Expansion
- If memory bank is missing, route to `memory-bank-init`.
- If target item is ambiguous, ask for the item or mark `user-verification-needed`.
- If the request is recurring correction capture, route to `memory-bank-correction-capture`.
- If the request is validation/consolidation/reporting, route to `memory-bank-maintenance`.
- Never recover by loading all memory banks, unrelated project memory, or all skills at once.

## Output Format
- Report appended event IDs.
- Report affected item IDs and their final status.
- Report validation status using one of `agent-verified`, `user-verification-needed`, `unverified`, `blocked`.

## Examples
- "프로젝트 목표에 배포 안정성 우선을 추가해 주세요."
- "이 룰은 더 이상 유효하지 않으니 폐기 처리해 주세요."
- "기존 rule_003을 새 정책에 맞게 수정해 주세요."

## Known Limits
- This skill mutates goals and rules only; initialization and mistake capture belong elsewhere.
- Persistent memory can overfit one session, so explicit long-term intent is required.
- Missing evidence should keep entries `unverified` or `user-verification-needed`.
- Load matching active memory cards only, not the full memory bank.
