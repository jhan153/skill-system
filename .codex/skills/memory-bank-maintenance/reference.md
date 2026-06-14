# memory-bank-maintenance Reference

## Scope
- This pack covers report, validate, conflict-check, and consolidate operations.
- It does not create new projects and does not directly mutate goals or rules on behalf of feature work.

## Canonical Enums
- `entity`: `goal|rule|mistake|system`
- `action`: `validate|consolidate|detect_conflict|resolve_conflict|update|deprecate`
- `status`: `active|candidate|deprecated`
- `verification`: `verified|unverified`
- `confidence`: `low|medium|high`
- `validation_state`: `agent-verified|user-verification-needed|unverified|blocked`

## Read-Only Operations
- `report`: summarize current state, touched files, and validation status
- `validate`: run schema and consistency checks without writes
- `conflict-check`: identify duplicate items, invalid status combinations, or broken references without writes

## Consolidation Rules
- Consolidation is the only maintenance operation that writes by default.
- Candidate mistakes may be merged when item meaning clearly overlaps and evidence families match.
- Promotion from `candidate` to `active` requires sufficient evidence and should set `verification=verified`.
- Stale rules may be deprecated only when a stronger current rule supersedes them.

## Consolidation Event Schema
```json
{
  "event_id": "evt_20260410T123000Z_0004",
  "at": "2026-04-10T12:30:00Z",
  "actor": "agent|automation",
  "workflow": "maintenance",
  "entity": "system",
  "action": "consolidate",
  "item_id": "snapshot_0002",
  "before": {
    "snapshot_version": 1
  },
  "after": {
    "snapshot_version": 2,
    "affected_items": ["mistake_001"]
  },
  "reason": "candidate mistakes consolidated",
  "evidence": "overlapping recurring corrections with sufficient evidence",
  "snapshot_base_version": 1,
  "validation_state": "agent-verified"
}
```

## Conflict Criteria
- Duplicate `item_id`
- Invalid enum value
- `current.md` item pointing to a missing `source_event`
- Deprecated item still marked verified without current justification

## Validation Checklist
- JSON parseability
- Enum consistency
- Cross-file reference consistency
- Snapshot version monotonicity


## Memory Card Routing Contract
Memory entries should be routable before they are loaded into context. Do not load the full memory bank by default; load active memory cards matching the repo, topic, and request. Superseded or archived entries are excluded unless conflict/history is specifically needed. One-turn preferences should not become memory cards.

```yaml
memory_card:
  memory_id:
  project:
  repo:
  topic:
  status: active | superseded | archived
  applies_when:
  do_not_apply_when:
  related_skills:
  related_files:
  last_verified:
```
