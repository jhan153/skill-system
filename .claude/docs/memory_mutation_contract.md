# Memory Mutation Contract

Use this contract for every write-producing Memory Bank operation. It is a consistency boundary, not permission to mutate memory.

## Before Write

1. Confirm explicit persistent-memory intent and the owning operation.
2. Resolve the target bank, canonical entity (`project`, `goal`, `rule`, or `mistake`), stable item IDs, and base `snapshot_version`.
3. Assign one stable operation/event ID before changing files; retries reuse that ID.
4. Scan the ledger mechanically and admit only target records into model context.
5. Preflight duplicates, conflicts, sensitivity/redaction, and every candidate in a batch. A batch with an unresolved candidate performs no writes.
6. Build the expected event, current snapshot, archive block, and metadata result before committing.

## Commit And Replay

- Prefer staging complete replacement content in a private temporary directory and atomically replacing files or the fresh bank directory where the filesystem permits it.
- When the repository cannot atomically replace the whole multi-file state, persist a transaction marker containing operation ID, base version, intended file digests, and phase before the first ledger mutation.
- Append or stage the canonical event once. A retry with the same operation ID must resume/verify the same intended state, never append a second semantic event.
- Detect a changed base version before commit and stop for conflict resolution.
- Never report success from a partial event/current/archive/meta update.
- Fresh initialization commits all baseline files as one unit. Reinitialization is not fresh init and must preserve existing accepted history or stop.

## Post-Write Validation

Verify all of the following before reporting `agent-verified`:

- event ID, entity, item ID, action, actor/workflow, and before/after state use the canonical schema;
- `events.jsonl`, `current.md`, and `archive.md` agree on stable IDs and final state;
- `meta.json` records the expected snapshot version and timestamp;
- deprecation/consolidation preserved append-only history;
- the operation changed only its owned entities and target items;
- sensitive raw evidence was not persisted;
- the transaction marker is completed/cleared according to repository policy.

A failed post-check is `blocked` with the operation ID and inconsistent files. Do not start an unrelated repair or append a compensating event without an explicit recovery decision.

## Operation Boundaries

- `memory-bank-update` owns canonical `goal`/`rule` create, update, and deprecate mutations.
- `memory-bank-correction-capture` owns new recurring `mistake` candidates; correcting a stored goal/rule routes to update.
- `memory-bank-maintenance` may consolidate mistake candidates. Goal/rule conflicts produce a proposal for update rather than an implicit policy mutation.
- `memory-bank-ingestion` is a thin approved-packet adapter: every admitted candidate must map to a canonical entity/item ID and use the same transaction path.
- A semantic-gate no-op is a valid no-write outcome, not a failure.
