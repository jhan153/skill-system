---
name: knowledge-base-update
description: Update, supersede, deprecate, or relink an existing project Knowledge record and its index entry. Use when an accepted domain, design, algorithm, architecture, code-review, or decision fact changed; do not create speculative records, rewrite Memory, or synchronize an LLM Wiki.
---

# Knowledge Base Update

## Routing Card
- role: knowledge_operation
- intent_signature: update or supersede durable project knowledge
- use_when: the user explicitly requests a known record change, or an approved checkpoint supplies a specific accepted change
- do_not_use_when: the store/record is missing, new category authoring is primary, a plan is still tentative, or broad maintenance is requested
- expected_inputs: declared store, exact record ID/path, `update|supersede|deprecate|relink`, accepted change, and source anchors
- expected_outputs: target record and index change with preserved history links and readback
- context_targets:
  must_read: manifest, target record/index row, current canonical refs, and `.codex/docs/knowledge_record_contract.md`
  read_if_needed: directly superseded records or accepted decision/plan slice
  do_not_load_by_default: full store, unrelated categories, Memory, Wiki, raw chat
- risk_profile:
  reads: one target record and direct refs
  writes: target/superseding record and index row only
  tools: local edit and readback
  sensitive_resources: private evidence summarized or excluded
- entry_scene: PREPARE

## Workflow
1. Resolve the exact or manifest-declared store and stable record ID.
2. Confirm the change is accepted and belongs to Knowledge rather than Memory or current implementation only.
3. Compare current canonical refs and identify affected consumers.
4. Update in place when identity is stable; otherwise create the replacement and set reciprocal supersession/status links. Never silently fork.
5. Update the index in the same operation and read back record, index, anchors, status, and consumer impact.

## Output
Report record IDs, operation, accepted source, changed links, index/readback result, affected consumers, and unresolved stale anchors. Do not report a structural edit as proof the knowledge itself is true.
