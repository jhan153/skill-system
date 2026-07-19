---
name: memory-bank-update
description: Add, change, or deprecate an explicitly persistent project goal, cross-session rule, or proven working practice in an existing declared Memory Bank. Use append-only events and compact current/archive/meta reflection; never infer persistence or initialize a bank.
disable-model-invocation: true
---

# Memory Bank Update

## Routing Card
- role: memory_operation
- intent_signature: persistent goal, rule, or working-practice mutation
- use_when: the user explicitly requests persistence, or an approved `project-context-checkpoint` supplies one identified durable item
- do_not_use_when: the bank is undeclared/absent, the item is a recurring correction, or init/maintenance is primary
- expected_inputs: exact item, `create|update|deprecate`, declared bank, and persistence authorization
- expected_outputs: one append-only event plus compact current/archive/meta reflection and readback
- context_targets:
  must_read: manifest declaration, targeted current item, latest meta/event state, `.codex/docs/memory_mutation_contract.md`, and `reference.md`
  read_if_needed: matching archive block for supersession
  do_not_load_by_default: full bank, unrelated items, raw chat, implementation history
- risk_profile:
  reads: one declared bank and target item
  writes: one goal/rule item across the four-file operation
  tools: targeted local mutation/readback
  sensitive_resources: private evidence is summarized
- entry_scene: PREPARE

## Mutation Gate
The exact existing bank must come from a user path or nearest `project-context.yaml`. The target is one identifiable `goal` or `rule`; a successful recurring workflow is `entity=rule` with `kind=practice`. Temporary instructions, one-turn preferences, and inferred preferences never become Memory.

Deprecation sets `status=deprecated` and preserves history. A candidate is never promoted by a score; activation requires explicit acceptance or directly verified project policy.

## Workflow
1. Resolve the declared target item and latest snapshot version.
2. Confirm update ownership rather than init, correction capture, Knowledge, or maintenance.
3. Build one event and the expected compact current/archive/meta result under one stable operation ID.
4. Apply the shared mutation contract and read back all four artifacts, snapshot advancement, history preservation, and target-only change.

Partial reflection, manifest mismatch, or unrelated snapshot churn remains failed/blocked.

## Output
Report the gate decision, item/event IDs, final status/verification, cross-file readback, and unresolved conflict. Do not emit the full bank or raw conversation.
