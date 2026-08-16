# management-memory-bank-maintenance Reference

## Canonical Enums

- Entity: `goal|rule|mistake|system`
- Action: `validate|consolidate|detect_conflict|resolve_conflict|update|deprecate`
- Status: `active|candidate|deprecated`
- Verification: `verified|unverified`
- Validation state: `agent-verified|user-verification-needed|unverified|blocked`

Legacy `accepted|proposal|stale|superseded|archived|field_feedback` states are not silently mapped. Report them as migration candidates and wait for an explicit maintenance decision.

## Operations

- `report`: summarize compact current state and schema version.
- `validate`: check parseability, canonical enums, stable references, and snapshot monotonicity.
- `conflict-check`: identify duplicate IDs, contradictory active rules, broken pointers, or candidate overlap.
- `consolidate`: merge directly equivalent items or record explicit supersession with one append-only event.
- `compact-current`: keep only current operational summaries and stable history/source pointers; chronology remains in events/archive or a plan/Knowledge artifact.

## Promotion And Deprecation

- Candidate mistakes may be merged when identity and evidence clearly overlap.
- Candidate activation requires explicit user acceptance or a current verified repository policy.
- An active rule may be deprecated only when a stronger current instruction, source, decision, or plan supersedes it.
- Never use counts, scores, or elapsed time as a promotion condition.

## Routable Current Item

```yaml
memory_item:
  id:
  entity: goal | rule | mistake
  kind: constraint | practice  # rule only
  status: active | candidate | deprecated
  verification: verified | unverified
  summary:
  applies_when: []
  do_not_apply_when: []
  related_skills: []
  related_files: []
  source_event:
  updated_at:
```

Items should be searchable from `current.md` before any event/archive detail is loaded. One-turn preferences and raw session narratives do not become items.

## Validation

- JSON parseability and canonical enum use.
- Every current item points to an existing source event.
- Event/current/archive/meta final state agrees.
- Snapshot versions are monotonic.
- `current.md` contains no long implementation chronology or raw conversation.
