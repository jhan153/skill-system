# memory-bank-correction-capture Design Document

```mermaid
sequenceDiagram
  autonumber
  participant G as SemanticGate
  participant L as LedgerWriter
  participant C as CurrentSnapshot
  participant A as ArchiveWriter
  participant V as Validator

  G->>G: Evaluate correction scope
  G->>L: Pass recurring project-level correction
  L->>L: Append mistake event
  L->>C: Reflect candidate mistake
  C->>A: Append history block
  A->>V: Validate masking and status
  V-->>A: validation_state
```

## Overview
This workflow captures recurring correction patterns without overfitting on every disagreement or wording fix.

## Runtime Rules
- Semantic gating happens before any write.
- New mistake items start as `candidate` and `unverified`.
- Promotion to `active` belongs to maintenance, not correction capture.

## Failure Paths
- Gate fails because the correction is turn-local: no writes.
- Duplicate match is ambiguous: return `user-verification-needed`.
- Evidence contains raw PII: redact before any write.

## Validation
- Scope gate integrity
- PII masking integrity
- Candidate-state integrity
