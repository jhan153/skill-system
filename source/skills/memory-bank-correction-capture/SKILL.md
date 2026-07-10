---
name: memory-bank-correction-capture
description: Capture an explicit project-level recurring correction as a candidate mistake with masked evidence and append-only history. Use only when the correction should affect future sessions; do not persist one-turn disagreement, wording changes, or ordinary goal/rule updates.
---

# Memory Bank Correction Capture

## Routing Card
- role: memory_operation
- intent_signature:
  - recurring correction, repeated mistake capture, persistent correction memory
- use_when:
  - the user explicitly says a repeated mistake or corrected belief should be remembered across sessions.
  - previously stored project memory is being corrected.
- do_not_use_when:
  - the issue is turn-local, a wording preference, or an unapproved inference.
  - the request changes a persistent goal/rule (`memory-bank-update`) or validates/consolidates memory (`memory-bank-maintenance`).
- expected_inputs:
  - target memory item or repeated failure pattern, recurrence evidence, and masked evidence summary
- expected_outputs:
  - candidate mistake item, append-only event, affected IDs, and validation status
- context_targets:
  must_read:
    - target item and only enough existing mistake candidates to detect duplicates
    - `.codex/docs/memory_mutation_contract.md` before a write
  read_if_needed:
    - `reference.md` for the semantic gate and canonical schema
    - `docs/document.md` only for an exceptional failure path
  do_not_load_by_default:
    - full memory bank, unrelated history, raw transcripts, or goal/rule history
- risk_profile:
  reads:
    - targeted accepted memory and correction evidence
  writes:
    - candidate mistake event plus current/archive/meta reflection after the gate passes
  tools:
    - safe file parsing and validation
  sensitive_resources:
    - mask PII, secrets, and raw private evidence
- entry_scene:
  - PREPARE

## Semantic Gate
Write only when all are true:

1. The user expresses persistent-memory intent or explicitly identifies recurrence.
2. The correction changes project-scoped behavior or stored knowledge, not only this answer's wording.
3. The target or repeated pattern is identifiable.
4. Evidence can be summarized without raw private content.

Otherwise stop without mutation. A negative phrase alone is never sufficient evidence of a recurring mistake.

## Workflow
1. Confirm the target memory bank exists; otherwise route to `memory-bank-init` only if initialization is requested.
2. Apply the detailed gate in `reference.md` and check for an equivalent candidate.
3. Mask the evidence summary.
4. Apply the shared stable-operation, staging/replay, and post-validation contract.
5. Append the mistake event and reflect the candidate in current/archive/meta state.

New entries remain `status=candidate` and `verification=unverified`; capture does not promote or consolidate them.

## Output
Report the gate decision, affected item/event IDs, validation status, and any user verification needed. Do not reproduce raw correction evidence.

## Validation
- Event, current item, and archive block share stable IDs.
- Stored evidence is a masked summary.
- A duplicate was refreshed or linked rather than blindly duplicated.
- No accepted-memory promotion occurred.
- A partial multi-file update was not reported as success.

## Behavior Cases
- Positive: “같은 잘못을 여러 세션에서 반복했으니 실수 후보로 기억해줘.”
- Negative: “방금 문장 표현만 고쳐줘. 메모리에는 넣지 마.” → no write.
- Edge: recurrence is claimed but the target item is ambiguous → `user-verification-needed`, no write.

## Known Limits
- A candidate may still be false-positive until recurrence or validation is established.
- `memory-bank-maintenance` owns later conflict resolution, consolidation, and promotion decisions.
