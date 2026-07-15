---
name: memory-bank-correction-capture
description: Capture an explicit project-level recurring correction as a candidate mistake with masked evidence and append-only history. Use only when the correction should affect future sessions; do not persist one-turn disagreement, wording changes, or ordinary goal/rule updates.
---

# Memory Bank Correction Capture

## Routing Card
- role: memory_operation
- intent_signature: recurring correction, repeated mistake capture, persistent correction memory
- use_when: the user explicitly wants an identifiable recurring project-level correction or corrected stored belief remembered across sessions
- do_not_use_when: the issue is turn-local, wording-only, inferred, a goal/rule update, or maintenance/consolidation
- expected_inputs: target item or recurring pattern, recurrence evidence, and a maskable evidence summary
- expected_outputs: candidate mistake event/current reflection, affected IDs, and validation status
- context_targets: read the target and only nearby candidates; before writing load `.codex/docs/memory_mutation_contract.md` and `reference.md`; use `docs/document.md` only for an exceptional failure path
- risk_profile: targeted append-only mutation after the gate; mask PII, secrets, identifiers, and raw private evidence
- entry_scene: PREPARE

## Capture Contract
Write only when persistent-memory intent or explicit recurrence, project-scoped behavioral/knowledge impact, an identifiable target/pattern, and safely summarized evidence are all present. A negative phrase, one disagreement, or an agent inference is not recurrence evidence. Ambiguity or unsafe evidence yields no write and the appropriate user check/block.

## Workflow
1. Confirm the target memory bank exists; otherwise route to `memory-bank-init` only if initialization is requested.
2. Apply `reference.md`, check only relevant candidates, and update an obvious duplicate; uncertain matches remain separate candidates for maintenance.
3. Mask the evidence, then stage the event and current/archive/meta reflections under one stable operation.
4. Read back and validate every affected file before reporting success; partial reflection remains failed or blocked.

New entries remain `status=candidate`, `verification=unverified`, and evidence-bounded recurrence counts. Capture never promotes, consolidates, or silently initializes a bank.

## Output
Report the gate decision, affected item/event IDs, masked-evidence status, readback validation, and any user verification needed. Do not reproduce raw evidence or imply that a captured candidate is true; `memory-bank-maintenance` owns later conflict resolution, consolidation, and promotion.
