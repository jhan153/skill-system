---
name: memory-bank-maintenance
description: Validate, report, conflict-check, or consolidate an existing project memory bank while preserving append-only history. Use only for explicit maintenance work; use narrower memory skills for initialization, direct goal/rule mutation, or new correction capture.
---

# Memory Bank Maintenance

## Routing Card
- role: memory_operation
- intent_signature: memory-bank status, validate, consolidate, conflict-check, stale-entry review
- use_when: the user or authorized automation explicitly requests maintenance of an existing target bank
- do_not_use_when: initialization, goal/rule mutation, or new correction capture is primary
- expected_inputs: exact bank and `report`, `validate`, `conflict-check`, or `consolidate` operation
- expected_outputs: evidence-backed status/conflicts and only requested append-only consolidation changes
- context_targets: read targeted meta/events/current state and only matching archive evidence; before consolidation load `.codex/docs/memory_mutation_contract.md` and `reference.md`
- risk_profile: report/validate/conflict-check are byte-read-only; consolidate writes append-only after explicit request; credentials denied
- entry_scene: PREPARE

## Maintenance Contract
- `report` summarizes, `validate` checks schema/cross-file integrity, and `conflict-check` inspects affected evidence; all remain byte-read-only and never auto-repair.
- `consolidate` writes only when evidence establishes equivalence or valid supersession; uncertainty preserves distinct items and returns `unverified`.
- A missing/mismatched bank or invalid schema is surfaced, never initialized or replaced as fallback. Route goal/rule mutations to `memory-bank-update` and new recurring corrections to `memory-bank-correction-capture`.

## Workflow
1. Confirm the bank and requested operation.
2. Parse `meta.json`, `events.jsonl`, and affected current items.
3. Check stable IDs, schema, event/current/archive consistency, conflicts, and stale/superseded state.
4. In read-only modes, stop after evidence-backed findings.
5. In `consolidate`, stage discovery, decision, one event, and current/archive/meta reflections under the shared stable operation; never hard-delete or rewrite history.
6. Read back every affected file. Advance snapshot/timestamps only after successful validation; partial writes remain failed/blocked.

## Output
Lead with the requested operation result and include exact affected IDs, conflict/consolidation decisions, byte/readback evidence, and remaining uncertainty. A consistency pass proves ledger structure and references only, not that every accepted memory claim remains true.
