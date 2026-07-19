# memory-bank-correction-capture Reference

## Semantic Gate

All conditions must hold:

1. The correction changes future project interaction or execution behavior.
2. It is expected to matter across sessions.
3. It names a specific failure pattern rather than a general dissatisfaction.
4. Persistence is explicitly authorized by the user or an approved checkpoint.

Do not record wording-only issues, one-time preferences, raw chats, or a correction that belongs as a goal/rule update.

## Canonical Shape

- Entity: `mistake`
- Action: `create|update`
- Status: `candidate|active|deprecated`
- Verification: `unverified|verified`
- Validation state: `agent-verified|user-verification-needed|unverified|blocked`

```json
{
  "event_id": "evt_20260410T122000Z_0003",
  "at": "2026-04-10T12:20:00Z",
  "actor": "user|agent",
  "workflow": "correction-capture|project-context-checkpoint",
  "entity": "mistake",
  "action": "create|update",
  "item_id": "mistake_001",
  "before": {},
  "after": {
    "status": "candidate",
    "verification": "unverified"
  },
  "reason": "persistent correction pattern",
  "evidence": "minimal masked summary or source pointer",
  "snapshot_base_version": 1,
  "validation_state": "agent-verified"
}
```

The compact current item includes `id`, `status`, `verification`, `updated_at`, `source_event`, one operational summary, and optional `applies_when`/`do_not_apply_when` anchors. Do not store confidence, recurrence, maturity, usage, or satisfaction scores.

## Evidence And Duplicate Rules

- Never store raw names, emails, account IDs, tokens, or pasted private content.
- Prefer a source pointer or the minimum masked summary needed to recognize the future pattern.
- Update only an obvious same-pattern item; uncertain matches stay separate for explicit maintenance.
- Capture cannot activate a candidate. Explicit maintenance with accepted evidence or user decision owns activation.
