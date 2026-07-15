---
name: memory-bank-ingestion
description: Promote an explicitly approved closeout packet or proposal into durable memory with append-only ingestion events and source-artifact archive links. Use only when promotion approval and a concrete packet exist; never ingest raw plans, transcripts, or secrets directly.
---

# Memory Bank Ingestion

## Routing Card
- role: memory_operation
- intent_signature: memory ingestion, closeout promotion, archive into memory, 기억 승격
- use_when: an explicitly approved closeout packet proposes durable candidates for an existing target bank
- do_not_use_when: approval or packet is missing, or init/direct update/correction capture/read-only maintenance is primary
- expected_inputs: approved packet, approval evidence, source-artifact pointer, target bank, and sensitivity result
- expected_outputs: classified candidates, append-only ingestion event/reflections, archive pointers, and readback status
- context_targets: read the packet and targeted bank; load `.codex/docs/memory_mutation_contract.md` plus only source slices needed to verify candidates; exclude full plans/repos, unrelated memory, and transcripts
- risk_profile: approved append-only mutation only; redact secrets, PII, identifiers, and raw private content before admission
- entry_scene: PREPARE

## Admission Contract
Require explicit persistent-mutation approval, the packet shape in `references/ingestion-packet-schema.md`, source-grounded candidates with post-task operational value, a valid target bank, and no unresolved conflict. Approval does not replace a packet and a packet never self-authorizes. Archive raw artifacts by pointer rather than copying them into current memory.

## Workflow
1. Validate approval, packet shape, target bank, and sensitivity screening.
2. Reclassify each candidate as durable, transient, conflicting, or insufficiently supported.
3. Map every admitted candidate to a canonical entity/item ID. Any unsafe content, unresolved mapping/conflict, missing source, or target mismatch makes the whole batch no-write; route conflicts to `memory-bank-maintenance` before retry and never substitute a stale packet or bank.
4. Stage accepted entries, one ingestion event, archive pointers, and current/archive/meta reflections under the shared stable operation.
5. Read back and validate all affected files before reporting success; partial application remains failed/blocked, then hand later consolidation to `memory-bank-maintenance`.

## Output
Report admitted/excluded IDs with reasons, archive/event pointers, source and mutation readback, and remaining maintenance needs. Omit empty categories. Ingestion proves approved admission and ledger consistency, not long-term truth or conflict freedom.
