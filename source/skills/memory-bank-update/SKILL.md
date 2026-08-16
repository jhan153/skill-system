---
name: memory-bank-update
description: Add, change, or deprecate an explicitly persistent project goal, cross-session rule, proven working practice, or recurring-mistake candidate in an existing declared Memory Bank. Use append-only events and compact current/archive/meta reflection; never infer persistence, activate a mistake candidate automatically, or initialize a bank.
---

# Memory Bank Update

## Routing Card
- role: memory_operation
- intent_signature: persistent goal/rule/practice mutation or recurring-mistake candidate capture
- use_when: the user explicitly requests persistence, or an approved `workflow-project-context-checkpoint` supplies one identified durable item
- do_not_use_when: the bank is undeclared/absent, the item is temporary/inferred, or init/maintenance is primary
- expected_inputs: mode, exact item or failure pattern, operation, declared bank, persistence authorization, and masked evidence when applicable
- expected_outputs: one append-only event plus compact current/archive/meta reflection and readback
- context_targets:
  must_read: manifest declaration, targeted current item, latest meta/event state, `.codex/docs/memory_mutation_contract.md`, and `reference.md`
  read_if_needed: matching archive block for supersession or directly matching mistake candidates for duplicate identity
  do_not_load_by_default: full bank, unrelated items, raw chat, implementation history
- risk_profile:
  reads: one declared bank and target item
  writes: one goal/rule/practice item or one candidate mistake across the four-file operation
  tools: targeted local mutation/readback
  sensitive_resources: private evidence is summarized
- entry_scene: PREPARE

## Modes And Mutation Gate
The exact existing bank must come from a user path or nearest `project-context.yaml`.

- `durable_item`: one identifiable `goal` or `rule`; a successful recurring workflow is `entity=rule` with `kind=practice`.
- `candidate_mistake`: one explicitly persistent, cross-session interaction or execution failure pattern. New items are always `entity=mistake`, `status=candidate`, and `verification=unverified`; capture never activates or scores them.

Temporary instructions, one-turn preferences/corrections, generic dissatisfaction, raw chat, and inferred preferences never become Memory. Mask mistake evidence and update only an obvious same-pattern candidate; uncertain matches stay separate for explicit maintenance.

Deprecation sets `status=deprecated` and preserves history. A candidate is never promoted by a score; activation requires explicit acceptance or directly verified project policy.

## Workflow
1. Resolve the declared target item and latest snapshot version.
2. Select `durable_item` or `candidate_mistake` and confirm update ownership rather than init, Knowledge, or maintenance.
3. Build one event and the expected compact current/archive/meta result under one stable operation ID.
4. Apply the shared mutation contract and read back all four artifacts, snapshot advancement, history preservation, and target-only change.

Partial reflection, manifest mismatch, or unrelated snapshot churn remains failed/blocked.

## Output
Report mode, gate decision, item/event IDs, masked-evidence status when applicable, final status/verification, cross-file readback, and unresolved conflict. Do not emit the full bank or raw conversation.
