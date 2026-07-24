---
name: memory-bank-maintenance
description: Report, validate, conflict-check, or explicitly consolidate an existing declared project Memory Bank while preserving append-only history. Read-only operations never repair; consolidation never uses maturity or confidence scoring.
disable-model-invocation: true
---

# Memory Bank Maintenance

## Routing Card
- role: memory_operation
- intent_signature: Memory status, validate, conflict-check, consolidate, compact current snapshot
- use_when: the user explicitly requests maintenance of an exact or manifest-declared bank
- do_not_use_when: ordinary task context, initialization, direct goal/rule update, or new correction capture is primary
- expected_inputs: exact bank and `report|validate|conflict-check|consolidate|compact-current` operation
- expected_outputs: evidence-backed findings and only the explicitly requested append-only changes
- context_targets:
  must_read: manifest/exact target, meta, current, targeted events, `.claude/docs/memory_mutation_contract.md`, and `reference.md`
  read_if_needed: matching archive blocks
  do_not_load_by_default: unrelated banks, raw transcripts, full archive, full event ledger
- risk_profile:
  reads: one declared bank
  writes: only explicit consolidate or compact-current operations
  tools: targeted parsing/mutation/readback
  sensitive_resources: credentials and raw private evidence denied
- entry_scene: PREPARE

## Maintenance Contract
- `report`, `validate`, and `conflict-check` are byte-read-only and never auto-repair.
- `consolidate` writes only when identity/equivalence or supersession is directly evidenced. It does not compute maturity, confidence, usage, recurrence, or quality scores.
- `compact-current` removes chronology and deprecated detail from the operational snapshot while preserving stable pointers and append-only history in events/archive.
- Candidate activation requires explicit user acceptance or current verified project policy; repeated appearance or a numerical threshold is insufficient.
- Missing/mismatched paths and legacy enum mismatch are reported, never replaced or migrated as fallback.

## Workflow
1. Resolve the exact or nearest manifest-declared bank and requested operation.
2. Parse meta/current and only events/archive records required by affected item IDs.
3. Check stable IDs, canonical enums, event/current/archive agreement, conflicts, stale pointers, and snapshot monotonicity.
4. Stop after findings for read-only operations.
5. For a write operation, stage one event and all current/archive/meta reflections under the shared stable operation; never hard-delete history.
6. Read back every affected artifact. Partial writes remain failed/blocked.

## Output
Lead with the requested operation result, exact affected IDs/files, latest decisive structural evidence, and remaining semantic uncertainty. Structural consistency does not prove every active Memory item is still correct.
