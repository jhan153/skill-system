# Memory Bank Update Reference

## Scope And Enums

- Entities: `goal|rule|mistake`
- Actions: `create|update|deprecate`
- Status: `active|candidate|deprecated`
- Verification: `verified|unverified`
- Validation state: `agent-verified|user-verification-needed|unverified|blocked`
- Optional rule kind: `constraint|practice`

Do not add confidence, maturity, recurrence, usage, or satisfaction scores.

## Event Record

```json
{
  "event_id": "evt_20260410T121000Z_0002",
  "at": "2026-04-10T12:10:00Z",
  "actor": "user|agent",
  "workflow": "update|candidate-mistake|management-project-context-checkpoint",
  "entity": "goal|rule|mistake",
  "action": "create|update|deprecate",
  "item_id": "rule_001",
  "before": {},
  "after": {
    "kind": "constraint|practice",
    "status": "active",
    "verification": "verified"
  },
  "reason": "durable change summary",
  "evidence": "source pointer or masked user decision",
  "snapshot_base_version": 1,
  "validation_state": "agent-verified"
}
```

## Compact Current Item

Every item includes `id`, `status`, `verification`, `updated_at`, and `source_event`. Rules may include `kind`. Keep one concise operational summary plus `applies_when`, `do_not_apply_when`, and stable plan/Knowledge/source pointers when useful.

- Create: assign one stable item ID.
- Update: preserve the ID and replace only current operational fields.
- Deprecate: preserve the item as deprecated or move its detail to archive while keeping an addressable current pointer.
- Never hard-delete history or append implementation chronology to `current.md`.

## Candidate Mistake Gate

All conditions must hold: the correction changes future project interaction or execution behavior, is expected to matter across sessions, names a specific failure pattern, and has explicit persistence authorization. Do not record wording-only issues, one-time preferences, raw chats, or material that belongs as a goal/rule update.

For `entity=mistake`, allow `create|update`; new items use `status=candidate` and `verification=unverified`. Store only a source pointer or minimal masked summary. Update only an obvious same-pattern item, and never activate a candidate from capture alone.

## Validation

- One semantic event was appended once.
- `current.md`, `archive.md`, and `meta.json` reference its ID and final state.
- Only the target item changed and deprecated history remains addressable.
