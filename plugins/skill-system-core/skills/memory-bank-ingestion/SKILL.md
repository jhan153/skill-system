---
name: memory-bank-ingestion
description: Promote an explicitly approved closeout packet or proposal into durable memory with append-only ingestion events and source-artifact archive links. Use only when promotion approval and a concrete packet exist; never ingest raw plans, transcripts, or secrets directly.
---

# Memory Bank Ingestion

## Routing Card
- role: memory_operation
- intent_signature:
  - memory ingestion, closeout promotion, archive into memory, 기억 승격
- use_when:
  - an approved closeout packet contains durable candidates that must enter long-term memory.
- do_not_use_when:
  - approval/packet is missing or the task is init, direct update, correction capture, or read-only maintenance.
- expected_inputs:
  - approved packet, source artifact pointer, target bank, and explicit mutation approval
- expected_outputs:
  - classified candidates, append-only ingestion event, accepted entries, archive pointers, and validation status
- context_targets:
  must_read:
    - approved packet and target current/archive/meta state
    - `.codex/docs/memory_mutation_contract.md` before admission or write
  read_if_needed:
    - only the source artifact slices needed to verify a candidate or archive pointer
  do_not_load_by_default:
    - full plan history, full repo, unrelated memory, or raw transcripts
- risk_profile:
  reads:
    - approved packet, target bank, and selected source evidence
  writes:
    - append-only memory changes after explicit approval
  tools:
    - safe file and schema validation
  sensitive_resources:
    - redact secrets, PII, and raw private content before admission
- entry_scene:
  - PREPARE

## Admission Gate
All are required:

1. explicit approval for persistent mutation;
2. a packet identifying source artifact, durable candidates, transient exclusions, sensitivity check, and target bank;
3. source-grounded candidates with operational value beyond the closed task;
4. no unresolved conflict that requires `memory-bank-maintenance` first.

The packet proposes; it does not self-authorize. Raw artifact text is archived by pointer, not copied wholesale into current memory.

## Workflow
1. Validate approval, packet shape, target bank, and sensitivity screening.
2. Reclassify each candidate as durable, transient, conflicting, or insufficiently supported.
3. Map every admitted candidate to a canonical entity/item ID; any unresolved mapping or conflict makes the whole batch a no-write outcome.
4. Apply accepted entries, the canonical ingestion event, archive pointers, and metadata through the shared stable-operation transaction.
5. Post-validate the new ledger state before handing later consolidation work to `memory-bank-maintenance`.

## Compact Packet Contract
```yaml
closeout_packet:
  source_artifact:
  approval_evidence:
  durable_candidates: []
  transient_excluded: []
  sensitivity_check:
  target_memory_path:
```

## Output
Report admitted and excluded candidate IDs with reasons, archive/event pointers, validation status, and remaining maintenance needs. Omit empty categories.

## Behavior Cases
- Positive: “이 승인된 closeout packet의 두 policy를 장기 메모리로 승격해줘.”
- Negative: “이 전체 plan을 알아서 기억해.” → no approved packet, blocked.
- Edge: packet is approved but contains a secret → block admission until redacted.

## Known Limits
- Ingestion validates admission and ledger consistency, not long-term truth or conflict freedom.
- Later consolidation and conflict resolution belong to `memory-bank-maintenance`.
