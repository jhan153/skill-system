# memory-bank-update Reference

## Scope
- This pack mutates existing `goal` and `rule` items only.
- It never initializes a project and never promotes or consolidates mistakes.

## Canonical Enums
- `entity`: `goal|rule`
- `action`: `create|update|deprecate`
- `status`: `active|deprecated`
- `verification`: `verified|unverified`
- `confidence`: `low|medium|high`
- `validation_state`: `agent-verified|user-verification-needed|unverified|blocked`

## Event Record Schema
```json
{
  "event_id": "evt_20260410T121000Z_0002",
  "at": "2026-04-10T12:10:00Z",
  "actor": "user|agent|automation",
  "workflow": "update",
  "entity": "goal|rule",
  "action": "create|update|deprecate",
  "item_id": "goal_001",
  "before": {},
  "after": {
    "status": "active",
    "verification": "verified",
    "confidence": "high"
  },
  "reason": "변경 사유 요약",
  "evidence": "근거 요약(PII 제거)",
  "snapshot_base_version": 1,
  "validation_state": "agent-verified"
}
```

## `current.md` Item Contract
Every goal or rule item must include:
- `id`
- `status`
- `verification`
- `confidence`
- `updated_at`
- `source_event`

## Update Rules
- Create: new item with stable `item_id`
- Update: preserve `item_id`, overwrite current visible fields, append history
- Deprecate: set `status=deprecated`, keep item in current view or clearly mark it as deprecated
- Never use hard delete

## `archive.md` Block Template
```markdown
## 2026-04-10T12:10:00Z | evt_20260410T121000Z_0002
- workflow: update
- entity: goal
- action: update
- item_id: goal_001
- reason: deployment priority changed
- evidence: user explicitly updated the persistent project goal
- before: {"summary":"기존 목표"}
- after: {"summary":"새 목표","status":"active"}
```

## Validation Checklist
- `events.jsonl` append succeeded before snapshot mutation.
- `current.md` and `archive.md` reference the same `event_id`.
- Deprecated items remain addressable by `item_id`.
