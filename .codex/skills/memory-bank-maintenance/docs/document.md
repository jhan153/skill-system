# memory-bank-maintenance Design Document

```mermaid
sequenceDiagram
  autonumber
  participant P as Parser
  participant C as ConsistencyChecker
  participant M as Maintainer
  participant S as MemoryStore
  participant V as Validator

  P->>C: Parse files and load snapshot
  C->>M: Classify report, validate, or consolidate
  M->>S: Write only if consolidation or explicit repair
  S->>V: Validate post-run integrity
  V-->>S: validation_state
```

## Overview
This workflow keeps an existing memory bank healthy and inspectable without conflating read-only checks and write-producing consolidation.

## Runtime Rules
- Read-only requests stay read-only.
- Consolidation writes a `system` event and increments `snapshot_version`.
- Conflict reporting must identify the exact mismatched fields or item IDs.

## Failure Paths
- Missing files: stop with `blocked`.
- Invalid JSON or schema drift: stop and surface the exact mismatch.
- Ambiguous consolidation candidate: return `unverified` without writing.

## Validation
- File parseability
- Cross-file consistency
- Snapshot monotonicity
- Read-only/write boundary integrity
