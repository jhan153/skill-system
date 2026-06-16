---
name: memory-bank-ingestion
description: "Promote approved plan/goal/phase-plan closeout packets and proposal candidates into durable long-term memory with append-only ingestion events and archive linkage."
---

# Memory Bank Ingestion

## Routing Card
- role: memory_operation
- intent_signature:
  - `memory ingestion`, `기억 승격`, `closeout promotion`, `archive into memory`
- use_when:
  - an approved closeout packet or memory proposal candidate must be promoted into durable memory.
  - raw plan/goal/phase-plan artifacts must be linked into archive pointers with append-only events.
- do_not_use_when:
  - memory-bank initialization, direct goal/rule update, correction capture, or read-only maintenance.
  - no explicit user approval for persistent memory mutation exists.
- expected_inputs:
  - approved closeout packet
  - source artifact pointer
  - proposal candidates
  - target memory-bank path
  - explicit user approval for memory mutation
- expected_outputs:
  - appended ingestion event, accepted memory entries, archive pointers, validation status
- context_targets:
  must_read:
    - approved closeout packet and proposal candidates
    - target memory-bank current/archive/meta state
  read_if_needed:
    - source plan/goal/phase-plan artifact being archived
  do_not_load_by_default:
    - full repo
    - unrelated memory entries
- risk_profile:
  reads:
    - READ_MEMORY_BANK for current/archive/meta state
  writes:
    - WRITE_MEMORY_BANK only after explicit user approval for persistent mutation
  tools:
    - none beyond memory-bank file operations
  sensitive_resources:
    - mask secrets, credentials, and private content before ingestion
- entry_scene:
  - PREPARE

## Related Skills
- `plan-spec-curator`: produces proposal-only closeout packets; does not mutate memory.
- `memory-bank-update`: direct persistent goal/rule mutation.
- `memory-bank-maintenance`: validate, consolidate, and resolve conflicts after ingestion.
- `memory-bank-correction-capture`: recurring correction candidate capture.

## Trigger
- `memory ingestion`, `closeout를 기억으로 승격`, `archive pointer 반영`

## Trigger Guard (Do Not Trigger)
- Plain memory init/update/maintenance/correction-capture requests.
- Any promotion without an approved packet and explicit mutation approval.

## Goal
- Promote durable items into accepted long-term memory with append-only semantics and archive linkage, never bypassing approval.

## Mandatory Sequence
1. Confirm an approved closeout packet and explicit mutation approval; otherwise stop as `blocked`.
2. Classify proposal candidates into durable vs transient.
3. Append durable items as accepted memory entries with an ingestion event.
4. Link the raw artifact into archive pointers.
5. Hand validation/consolidation to `memory-bank-maintenance`.

## Approved Packet Schema
```yaml
closeout_packet:
  source_artifact:        # plan/goal/phase-plan pointer
  approval_evidence:      # explicit user approval for memory mutation
  durable_candidates: []  # entries proposed for long-term memory
  transient_excluded: []  # entries to drop, with reason
  sensitivity_check:      # secrets/PII screened before ingestion
  target_memory_path:
  maintenance_handoff:    # what memory-bank-maintenance should validate next
```

## Append-only Event Schema
```yaml
ingestion_event:
  timestamp:
  source_artifact:
  accepted_entries: []
  excluded_entries: []
  approval_pointer:
  validation_status: agent-verified | user-verification-needed | unverified | blocked
```
- Events are append-only; never rewrite or delete prior entries.

## Blocked Cases
Report `blocked` (do not mutate memory) when any holds:
- no explicit user approval for persistent memory mutation
- no approved closeout packet
- raw secrets/credentials/PII present and not yet redacted
- target memory path unknown
- a conflict requires `memory-bank-maintenance` to resolve first

## Reference
- Read `references/ingestion-packet-schema.md` for a closeout-packet example, an ingestion-event example, and a blocked-output example.

## Output Contract
1. Approval and packet check
2. Accepted memory entries
3. Archive pointers
4. Appended ingestion event
5. Validation status / remaining checks

## Resource and Risk Boundary
- Reads: memory-bank state and the approved packet only.
- Writes: memory-bank only after explicit approval; append-only, never destructive rewrite.
- Network/credentials: none; mask sensitive content before ingestion.
- Destructive actions: never; ingestion is additive.

## Anti-Patterns
- Promoting without approval or without a closeout packet.
- Overwriting or deleting existing memory instead of appending.
- Ingesting raw secrets, credentials, or private transcripts.

## Known Limits
- Ingestion does not validate long-term consistency; `memory-bank-maintenance` does.
- Without an approved packet, this skill reports `blocked` rather than guessing.
