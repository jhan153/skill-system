---
name: memory-bank-maintenance
description: Validate, report, conflict-check, or consolidate an existing project memory bank while preserving append-only history. Use only for explicit maintenance work; use narrower memory skills for initialization, direct goal/rule mutation, or new correction capture.
---

# Memory Bank Maintenance

## Routing Card
- role: memory_operation
- intent_signature:
  - memory-bank status, validate, consolidate, conflict-check, stale-entry review
- use_when:
  - the user or an authorized automation explicitly asks to inspect or maintain existing memory state.
- do_not_use_when:
  - initialization, goal/rule mutation, or capture of a new recurring correction is the actual task.
- expected_inputs:
  - target bank and operation: `report`, `validate`, `conflict-check`, or `consolidate`
- expected_outputs:
  - evidence-backed status/conflicts and, only when requested, append-only consolidation changes
- context_targets:
  must_read:
    - relevant `meta.json`, `events.jsonl`, and affected `current.md` sections
    - `.codex/docs/memory_mutation_contract.md` before `consolidate`
  read_if_needed:
    - matching `archive.md` history and `reference.md` schema/consolidation rules
  do_not_load_by_default:
    - all memory banks, unrelated project memory, or full repository context
- risk_profile:
  reads:
    - targeted ledger files and affected history
  writes:
    - none for report/validate; append-only consolidation changes only when explicitly requested
  tools:
    - safe schema, consistency, and file validation
  sensitive_resources:
    - credentials default deny
- entry_scene:
  - PREPARE

## Operation Gate
- `report`: summarize current state; no writes.
- `validate`: check schema and cross-file integrity; no repair unless separately requested.
- `conflict-check`: inspect only the affected current/archive evidence; no mutation by default.
- `consolidate`: merge only evidence-backed duplicates or superseded candidates and append a consolidation event.

If the bank is missing, report `blocked`; do not silently initialize it. Goal/rule changes route to `memory-bank-update`, and new repeated corrections route to `memory-bank-correction-capture`.

## Workflow
1. Confirm the bank and requested operation.
2. Parse `meta.json`, `events.jsonl`, and affected current items.
3. Check stable IDs, schema, event/current/archive consistency, conflicts, and stale/superseded state.
4. In read-only modes, stop after evidence-backed findings.
5. In `consolidate`, preserve distinct items unless evidence establishes equivalence; apply the shared stable-operation transaction to event/current/archive/meta state.
6. Revalidate and report exact affected IDs.

## Validation
- Read-only operations leave files byte-unchanged.
- Consolidation has discovery, decision, and post-change verification evidence.
- `snapshot_version` and timestamps change only after a successful write.
- No hard deletion or history rewrite occurs.
- Goal/rule conflicts produce an update proposal rather than an implicit policy mutation.

## Output
Lead with the requested operation's result. Include affected IDs, conflicts or consolidation decisions, validation evidence, and remaining uncertainty; omit empty maintenance categories.

## Behavior Cases
- Positive: “candidate 실수 두 개가 같은 항목인지 검증하고 통합해줘.”
- Negative: “새 persistent rule을 추가해줘.” → `memory-bank-update`.
- Edge: two similar candidates lack shared evidence → keep separate and report `unverified`.

## Known Limits
- Consolidation can erase meaningful distinctions when evidence is weak; uncertainty blocks the merge.
- Validation proves ledger consistency, not that every accepted memory claim is currently true.
