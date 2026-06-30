---
name: memory-bank-correction-capture
description: Captures project-level corrections as candidate recurring mistakes with masked evidence and append-only history. Use when the user explicitly corrects previously stored project memory or identifies a persistent repeated mistake across sessions.
---

# Memory Bank Correction Capture

## Routing Card
- role: memory_operation
- intent_signature:
  - recurring correction, repeated mistake capture, persistent correction memory
- use_when:
  - the user explicitly identifies a repeated mistake or correction that should change long-lived project behavior.
- do_not_use_when:
  - the request is a one-turn disagreement, wording fix, goal/rule mutation, or maintenance operation.
- expected_inputs:
  - existing memory-bank files
  - corrected memory or repeated failure pattern
  - masked evidence summary
- expected_outputs:
  - candidate mistake record, append-only event, validation status
- context_targets:
  must_read:
    - target memory item or current mistake section
    - existing candidate mistakes enough to avoid duplicates
  read_if_needed:
    - `reference.md` semantic gate
    - `docs/document.md` failure-path detail
  do_not_load_by_default:
    - full memory bank
    - unrelated project memory
    - goal/rule mutation history
- risk_profile:
  reads:
    - targeted correction evidence and existing mistake candidates
  writes:
    - append candidate mistake event and update current/archive/meta
  tools:
    - safe file validation
  sensitive_resources:
    - PII must be masked; credentials default deny
- entry_scene:
  - PREPARE

Capture recurring project-level corrections as mistake records. This skill is semantic-gated: do not trigger on every negative phrase or local wording fix.

Read `reference.md` for the correction gate and mistake schema and `docs/document.md` only when you need flow or failure-path detail.

## Related Skills
- `memory-bank-init`: 메모리뱅크가 없으면 먼저 실행되어야 합니다.
- `memory-bank-update`: 정정 대상이 recurring mistake가 아니라 project goal/rule 변경이면 이 스킬 대신 사용합니다.
- `memory-bank-maintenance`: 누적된 candidate mistake의 통합, 승격, 충돌 해소는 후행 유지보수 단계에서 담당합니다.

## Cross-Skill Routing
- 메모리뱅크가 없으면 `memory-bank-init`이 선행되어야 합니다.
- 요청이 persistent rule/goal 변경이면 `memory-bank-update`로 넘깁니다.
- 캡처된 candidate mistake의 통합이나 상태 점검은 `memory-bank-maintenance`로 넘깁니다.
- 이 스킬은 semantic gate를 통과한 recurring correction만 기록합니다.

## What This Skill Does
- Detects whether a correction changes persistent project memory.
- Records or refreshes candidate mistake items with masked evidence.
- Preserves uncertainty instead of promoting the mistake immediately.

## When to Use
- The user corrects previously stored project memory.
- The user points out a recurring mistake that should be remembered across sessions.
- The correction should change long-lived project behavior or guidance.

## When Not to Use
- The user is only disagreeing with a one-turn response.
- The user is only fixing wording, translation, or formatting in the current turn.
- The request is actually a goal or rule change.
- The request is to validate, consolidate, or report the memory bank.

## Required Inputs
- Existing memory-bank files.
- The corrected target memory or repeated failure pattern.
- A concise evidence summary with PII removed.
- Enough context to decide whether the issue is recurring and project-scoped.

## Preflight Checks
1. Confirm the memory bank exists.
2. Confirm the correction changes persistent project memory rather than turn-local phrasing.
3. Identify the target entity, related item, or corrected memory gap.
4. Mask PII from the evidence summary.
5. Load existing mistake items to avoid creating an obvious duplicate.

## Workflow
1. Apply the semantic gate from `reference.md`.
2. If the correction is out of scope, stop without writing.
3. Append a mistake event to `events.jsonl`.
4. Reflect the candidate mistake in `current.md`.
5. Append the matching block to `archive.md`.
6. Update `meta.json.updated_at`.

## Validation Checks
- The correction passed the semantic gate.
- The resulting mistake item uses `status=candidate`.
- The resulting mistake item uses `verification=unverified`.
- `evidence` stores only a masked summary.

## Failure Handling
- If the memory bank does not exist, stop and report that `memory-bank-init` is required.
- If the correction is one-off or turn-local, stop without writing and report `blocked`.
- If the target memory cannot be identified confidently, return `user-verification-needed`.

## Resource and Risk Boundary
- Reads: targeted memory state, existing mistake candidates, and masked correction evidence.
- Writes: candidate mistake event and current/archive/meta updates only after semantic gate passes.
- Tool/process calls: safe file parsing and validation only.
- Network access: none.
- Credential access: default deny; mask PII and secrets from evidence.
- Generated artifacts: updated memory ledger files.
- Destructive actions: out of scope.
- Required checkpoints: recurring/project-scoped semantic gate, duplicate check, PII masking.

## Recovery and Context Expansion
- If memory bank is missing, route to `memory-bank-init`.
- If correction is turn-local, stop without writing.
- If target is a persistent goal/rule, route to `memory-bank-update`.
- If duplicate status is unclear, read only existing mistake candidates before expanding.
- If consolidation is needed, route to `memory-bank-maintenance`.
- Never recover by loading all memory banks, unrelated project memory, or all skills at once.

## Output Format
- Report whether the semantic gate passed.
- Report appended event IDs and affected mistake item IDs.
- Report validation status using one of `agent-verified`, `user-verification-needed`, `unverified`, `blocked`.

## Examples
- "이건 프로젝트 룰이 아니라 예외 케이스였어요. 다음부터 헷갈리지 않게 기록해 주세요."
- "같은 종류의 정정이 반복되니 실수 항목으로 남겨 주세요."
- "방금 표현만 고친 거라 메모리엔 넣지 마세요."

## Known Limits
- Candidate mistake memory can be false-positive until recurrence or validation evidence exists.
- Raw private evidence must not be stored; keep only masked summaries.
- One-time preferences or wording fixes should not become memory cards.
- Maintenance owns later consolidation or acceptance into long-term memory.
