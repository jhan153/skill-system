# memory-bank-update Design Document

```mermaid
sequenceDiagram
  autonumber
  participant P as PreflightChecker
  participant L as LedgerWriter
  participant C as CurrentSnapshot
  participant A as ArchiveWriter
  participant V as Validator

  P->>L: Validate target entity and load snapshot
  L->>L: Append update event
  L->>C: Apply latest state
  C->>A: Append history block
  A->>V: Validate consistency
  V-->>A: validation_state
```

## Overview
This workflow handles persistent goal and rule mutations for an existing project memory bank.

## Runtime Rules
- `events.jsonl` is written first.
- `current.md` reflects only the latest visible state.
- `archive.md` receives the matching compact change block.
- `meta.json.updated_at` moves forward on every successful mutation.

## Failure Paths
- Missing memory-bank files: stop and route to init.
- Entity outside `goal|rule`: stop with `blocked`.
- Missing target item for update or deprecate: return `user-verification-needed`.

## Validation
- Event/order integrity
- Snapshot integrity
- Archive integrity
