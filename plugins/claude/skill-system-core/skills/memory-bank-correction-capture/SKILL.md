---
name: memory-bank-correction-capture
description: Capture an explicitly persistent project-level interaction or execution mistake as a candidate in an existing declared Memory Bank. Use only on a direct memory request or approved project-context checkpoint; never collect complaints, chats, or one-turn corrections automatically.
disable-model-invocation: true
---

# Memory Bank Correction Capture

## Routing Card
- role: memory_operation
- intent_signature: remember recurring mistake, persistent correction capture
- use_when: the user explicitly asks to remember a recurring mistake, or an approved checkpoint identifies one durable cross-session correction
- do_not_use_when: the issue is one-turn, wording-only, inferred, already represented as a goal/rule, or the bank is undeclared/absent
- expected_inputs: exact mistake pattern, persistence authorization, masked evidence summary, and declared bank
- expected_outputs: one candidate mistake event with compact four-file reflection and readback
- context_targets:
  must_read: manifest declaration, matching current candidates, `.claude/docs/memory_mutation_contract.md`, and `reference.md`
  read_if_needed: matching event/archive record for duplicate identity
  do_not_load_by_default: full bank, raw conversation, unrelated corrections, private identifiers
- risk_profile:
  reads: one declared bank and nearby candidates
  writes: one candidate mistake operation
  tools: targeted local mutation/readback
  sensitive_resources: raw private evidence denied
- entry_scene: PREPARE

## Capture Contract
The correction must describe future project behavior, have an identifiable failure pattern, and be explicitly authorized for persistence. A complaint or negative phrase alone is not authorization or recurrence evidence. Do not infer a count, confidence, maturity, or severity score.

New items are always `status=candidate` and `verification=unverified`. Capture does not promote, consolidate, initialize a bank, or create a field-feedback dataset.

## Workflow
1. Resolve the exact or manifest-declared bank; otherwise no-write.
2. Compare only directly matching candidates. Update an obvious duplicate; leave uncertain matches separate.
3. Mask the evidence and stage one event plus compact current/archive/meta reflections under one operation ID.
4. Read back every affected file and confirm target-only change and history preservation.

## Output
Report the gate, item/event IDs, masked-evidence status, four-file readback, and any explicit maintenance need. Never reproduce raw evidence or imply a candidate is an active instruction.
