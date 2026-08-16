# Memory Mutation Contract

Use this contract for every write-producing Memory Bank operation. It is a consistency boundary, not permission to mutate Memory.

## Before Write

1. Confirm an explicit Memory request or approved project commit/closeout checkpoint.
2. Resolve an exact user path or the nearest `project-context.yaml`; never select a fallback bank.
3. Resolve the canonical entity (`project|goal|rule|mistake`), stable item IDs, and base `snapshot_version`.
4. Assign one operation/event ID before changing files; retries reuse it.
5. Read only the target current items and event/archive records needed for duplicate, conflict, sensitivity, and supersession checks.
6. Build the expected event, compact current snapshot, archive block, and metadata result before committing. A batch with an unresolved item performs no writes.

Canonical item state is `active|candidate|deprecated` with `verified|unverified`. Do not add confidence, maturity, recurrence, usage, or satisfaction scores.

## Commit And Replay

- Stage `events.jsonl`, `current.md`, `archive.md`, and `meta.json` as one operation. Prefer atomic replacement where repository policy permits it.
- If whole-state atomic replacement is unavailable, use a transaction marker with operation ID, base version, intended digests, and phase before the first mutation.
- Append or stage the semantic event once. A retry resumes or verifies the same intended state and never appends a duplicate event.
- Detect a changed base version before commit and stop for explicit conflict resolution.
- Never report success from a partial four-file update.
- Fresh initialization also updates only the `memory_bank` section of `project-context.yaml` and preserves all other manifest sections.

## Compact Snapshot Rule

`current.md` contains only current goals, rules, recurring mistake summaries, successful working practices, routing anchors, and stable pointers. It does not accumulate raw conversations, logs, implementation chronology, completed task narratives, or full plan/Knowledge bodies. Move historical detail to events/archive and keep a pointer.

## Post-Write Validation

Before reporting success, verify:

- canonical event ID, entity, item ID, action, actor/workflow, and before/after state;
- event/current/archive agreement on stable IDs and final state;
- expected `meta.json` snapshot version and timestamp;
- append-only preservation for deprecation/consolidation;
- target-only changes and no raw sensitive evidence;
- completed/cleared transaction marker according to repository policy;
- unchanged unrelated `project-context.yaml` sections when initialization touched the manifest.

A failed post-check is `blocked` with the operation ID and inconsistent files. Do not start unrelated repair or append a compensating event without an explicit recovery decision.

## Operation Boundaries

- `management-memory-bank-init`: explicit fresh store and manifest-section registration.
- `management-memory-bank-update`: goal/rule/practice create, update, or deprecate, plus explicitly authorized recurring-mistake candidate capture.
- `management-memory-bank-maintenance`: read-only report/validation/conflict check plus explicitly requested consolidate/compact operations.
- `management-project-context-checkpoint`: classifies an approved commit/closeout and delegates each Memory mutation to the narrow owner; it does not invent a separate packet format.

A semantic-gate no-op is a valid no-write result.
