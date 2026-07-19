---
name: knowledge-design-record
description: Record one accepted project-specific product or visual design rule with design-system, component, token, state, accessibility, and implementation anchors. Use explicitly for durable local design knowledge; never substitute generic UI patterns or record a one-off visual preference.
---

# Knowledge Design Record

## Routing Card
- role: knowledge_operation
- intent_signature: durable product/design-system rule and implementation linkage
- use_when: the user explicitly requests recording an accepted recurring local design rule
- do_not_use_when: the input is a one-off preference, generic UI advice, unaccepted concept, screenshot critique, or existing-record update
- expected_inputs: product intent, accepted aliases/search terms, affected surfaces/states, design refs, tokens/components, implementation refs, verifier, overlap candidates, and declared store
- expected_outputs: one design record plus index row and readback
- context_targets:
  must_read: manifest/index, matching design records, actual design/design-system/code refs, and `.codex/docs/knowledge_record_contract.md`
  read_if_needed: accessibility or visual verification evidence directly tied to the rule
  do_not_load_by_default: full design library, unrelated code, Memory, Wiki, generic pattern catalogs
- risk_profile:
  reads: matching records and exact design/code anchors
  writes: one design record and index row
  tools: local or explicitly authorized design-source readback
  sensitive_resources: private design systems remain scoped
- entry_scene: PREPARE

## Record Body
Capture product intent, affected surface and states/variants, approved component/token/control, layout/interaction rule, accessibility constraint, implementation symbols, and validation expectation. A local approved control outranks a common model-generated UI pattern.

## Workflow
1. Bind `knowledge_root` and `knowledge_index` from the exact approved path or nearest manifest declaration, reuse them for every record/index path, and verify the rule is accepted, durable, and project-specific. Missing is `unavailable`; never guess or scan for a store.
2. Read the exact design/design-system/code anchors; do not invent missing tokens or component names.
3. Classify matching records as same identity/recurrence, amendment, replacement, partial scope overlap, conflict, or new. Use `knowledge-base-update` for an existing identity and preserve source dependence.
4. Create one `category=design` record only for a new identity, with the full current envelope, a `created` revision, direct consumers, and typed overlap/conflict links when applicable.
5. Add its navigable index row and read back record, design/code anchors, relations/history, and verifier links.

Use `knowledge-base-update` for an existing identity. Do not record broad aesthetics without an operational consequence.
