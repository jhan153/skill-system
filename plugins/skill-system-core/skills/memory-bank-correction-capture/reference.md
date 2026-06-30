# memory-bank-correction-capture Reference

## Scope
- This pack records project-level corrections as mistake memory.
- It does not initialize the memory bank and does not consolidate candidates into active items.

## Semantic Gate
Record a mistake only when all conditions below hold:
1. The correction affects persistent project behavior, goals, rules, or repeated execution quality.
2. The correction is expected to matter across future sessions.
3. The correction is specific enough to describe a recurring failure pattern.

Do not record a mistake when any condition below holds:
1. The issue is only wording or formatting in the current turn.
2. The issue is a one-time preference change.
3. The issue is better represented as a goal or rule update.

## Canonical Enums
- `entity`: `mistake`
- `action`: `create|update`
- `status`: `candidate|active|deprecated`
- `verification`: `unverified|verified`
- `confidence`: `low|medium|high`
- `validation_state`: `agent-verified|user-verification-needed|unverified|blocked`

## Mistake Event Schema
```json
{
  "event_id": "evt_20260410T122000Z_0003",
  "at": "2026-04-10T12:20:00Z",
  "actor": "user|agent",
  "workflow": "correction-capture",
  "entity": "mistake",
  "action": "create|update",
  "item_id": "mistake_001",
  "before": {},
  "after": {
    "status": "candidate",
    "verification": "unverified",
    "confidence": "low",
    "recurrence_count": 1
  },
  "reason": "반복 정정 패턴 포착",
  "evidence": "PII 제거된 정정 요약",
  "snapshot_base_version": 1,
  "validation_state": "agent-verified"
}
```

## `current.md` Mistake Item Contract
Every mistake item must include:
- `id`
- `status`
- `verification`
- `confidence`
- `recurrence_count`
- `updated_at`
- `source_event`

## Evidence Rules
- Never store raw names, emails, IDs, tokens, or pasted private content.
- Keep `evidence` to the minimum summary needed to explain the recurring issue.
- If the evidence is incomplete, keep the item candidate and lower confidence.

## Duplicate Handling
- If an obvious same-item match already exists, prefer `action=update`.
- If the match is uncertain, create a new candidate and let maintenance consolidate later.

## Validation Checklist
- Semantic gate result is explicit.
- Candidate items remain `verification=unverified` unless separately validated.
- `recurrence_count` is never inferred upward without evidence.
