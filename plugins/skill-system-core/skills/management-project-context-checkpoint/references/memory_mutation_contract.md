# Memory Bank Contract

This contract defines the readable project Memory Bank format and every Memory read/write boundary.
It is not permission to create, read, or mutate a store.

## Location And Authority

Bind these values once per operation:

```text
memory_root := exact approved directory, otherwise memory_bank.root from the nearest project-context.yaml
memory_file := memory_root/memory.md
```

- An exact user path wins. Otherwise use the nearest manifest declaration according to
  `project_context_manifest.md`.
- Missing declarations or files are `unavailable`; readers and writers never scan, guess, or
  initialize a fallback.
- Only explicit initialization may propose `docs/memory-bank/` when no path is supplied. Approval
  binds the proposal before writing.
- Current user instructions, current repository evidence, and an accepted active Plan outrank
  Memory. Memory admission never changes the current task owner or grants write authority.

## Canonical Single-File Format

`memory.md` is the only canonical Memory state. Keep it compact and directly readable:

```markdown
# Project Memory

- Schema: memory-bank-v1
- Project: <project_id>
- Updated: <YYYY-MM-DD>

## MEM-RULE-001 — Short title

- Type: goal | rule | mistake
- Kind: constraint | practice | none
- Status: active | candidate | deprecated
- Verification: verified | unverified
- Summary: <one current operational statement>
- Applies when: <anchors or none>
- Do not apply when: <anchors or none>
- Related skills: <IDs or none>
- Related files: <paths/symbols or none>
- Source refs: <stable refs>
- Updated: <YYYY-MM-DD>

### Revisions

- <date> | created | <short semantic reason> | <source refs>
```

Use stable IDs such as `MEM-GOAL-*`, `MEM-RULE-*`, and `MEM-MISTAKE-*`. Keep deprecated records
addressable in the same file. Do not create event ledgers, archive mirrors, metadata databases,
scores, confidence fields, or a second current-state projection.

## Admission Rules

- `goal`: an explicitly persistent project outcome that matters across sessions.
- `rule`: an explicitly persistent constraint or a proven reusable practice.
- `mistake`: an explicitly authorized recurring interaction/execution failure pattern. New mistake
  records are always `candidate` and `unverified`.
- Temporary instructions, one-turn preferences/corrections, generic dissatisfaction, raw chat,
  implementation chronology, completed-task narrative, and facts better owned by Knowledge do not
  enter Memory.
- Only `verified active` records may govern work. An `unverified active` record is advisory, a
  `candidate` is non-authoritative, and a `deprecated` record is history-only unless requested.

## Mutation Contract

1. Resolve `memory_root`, `memory_file`, project identity, target ID, and the current file snapshot.
2. Confirm explicit persistence authority or one approved project-context checkpoint item.
3. Classify the target-record operation as `create`, `update`, `activate`, or `deprecate`.
4. Change one target record and append one concise semantic revision under that record. A batch
   with an unresolved identity or conflict performs no writes.
5. Update the document-level date only when a record changed. Preserve unrelated records and their
   order where practical.
6. Read back the target record, revision, project identity, source refs, and unchanged unrelated
   content before reporting success.

Never hard-delete history, activate a candidate from recurrence/count alone, auto-merge similar
wording, or use a report/source's existence as proof of its asserted relationship.

## Initialization

Initialization creates only `memory.md` with the document header and no inferred records, then
updates only `memory_bank.root` and `memory_bank.storage` in `project-context.yaml`. Existing content
is never reinitialized in place; use explicit legacy migration or a separately approved new target.

## Maintenance And Legacy Migration

- `report`, `integrity-check`, and `conflict-check` are read-only.
- `consolidate` merges only directly equivalent identities and preserves a revision/source trail.
- `compact` shortens duplicated prose while preserving current meaning, stable IDs, source refs,
  status, and semantic revisions.
- `migrate-legacy` is the only path from the former `current.md`/`archive.md`/`events.jsonl`/
  `meta.json` layout. It requires explicit scope and mapping approval, writes a new `memory.md`,
  reads it back, and leaves the legacy files untouched until the user separately decides disposal.
- Unknown or malformed legacy state is reported; never infer missing events, verification, or item
  identity.

## Operation Owners

- `management-memory-bank-harness`: minimum relevant read only.
- `management-memory-bank-init`: explicit empty store and manifest binding.
- `management-memory-bank-update`: one record mutation and revision.
- `management-memory-bank-maintenance`: explicit read-only checks, consolidation, compaction, or
  legacy migration.
- `management-project-context-checkpoint`: classifies explicitly authorized current-task material
  and delegates each mutation; it owns no alternate packet or Memory format.

A semantic no-op is a valid no-write result. A failed readback leaves the operation unresolved with
the exact target and mismatch; it never starts unrelated repair automatically.
