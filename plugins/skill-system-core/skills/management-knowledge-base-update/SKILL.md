---
name: management-knowledge-base-update
description: Amend, observe, reverify, supersede, deprecate, or relink an existing project Knowledge record and its index entry while preserving semantic history and provenance. Use when accepted knowledge changed or recurred, including an approved-plan sync targeting an existing identity; do not promote tentative plan text, create duplicates, compute scores, rewrite Memory, or synchronize an LLM Wiki.
---

# Management Knowledge Base Update

## Routing Card
- role: knowledge_operation
- intent_signature: amend, observe recurrence, reverify, supersede, deprecate, or relink durable project knowledge
- use_when: the user explicitly requests a known record change or approved-plan sync, or an approved checkpoint supplies a specific accepted change
- do_not_use_when: the store/record is missing, new category authoring is primary, a plan is still tentative, or broad maintenance is requested
- expected_inputs: declared store, exact record ID/path, `amend|observe|reverify|supersede|deprecate|relink`, accepted change/event, source/provenance anchors, and affected relation targets
- expected_outputs: target record and index change with current snapshot, semantic revision or observation event, preserved lifecycle links, and readback
- context_targets:
  must_read: manifest, target record/index row, current canonical refs, `references/project_context_manifest.md`, and `references/knowledge_record_contract.md`
  read_if_needed: directly superseded records or accepted decision/plan slice
  do_not_load_by_default: full store, unrelated categories, Memory, Wiki, raw chat
- risk_profile:
  reads: one target record and direct refs
  writes: target/superseding record and index row only
  tools: local edit and readback
  sensitive_resources: private evidence summarized or excluded
- entry_scene: PREPARE

## Workflow
1. Bind `knowledge_root` and `knowledge_index` from the exact or manifest-declared store, then resolve the stable record ID from that index. Reuse the bound variables for every read/write; never substitute a default path.
2. Confirm the change/event is accepted or source-traced, belongs to Knowledge rather than Memory/task status, and is not the same occurrence already recorded. From a plan, admit only accepted/current durable decisions or rules; exclude TODOs, estimates, chronology, rejected alternatives except bounded decision history, and speculative future state.
3. Compare the current record, nearest overlap candidates, canonical refs, provenance roots, relations, and affected consumers. Classify exact identity, dependent duplicate, amendment, replacement, scope overlap, or conflict before writing.
4. For `observe`, append one bounded support/recurrence/application/counterexample event with its `source_ref`, `provenance_root`, date, scope, and verification. Verification checks the event's asserted relationship to the record, not merely that its source exists; an explicit report alone remains unverified behavioral evidence. Shared provenance roots remain dependent and counterexamples never become support.
5. Before the first mutation of an unadopted legacy record, append `adopted_snapshot` and state that earlier semantic history was not reconstructed. For stable-identity meaning changes, update the current snapshot and append one semantic revision. For a new identity, create the replacement and set reciprocal supersession/status links. Never silently fork or auto-merge from similarity.
6. For `relink`, use only the typed relation vocabulary with a stable target and basis refs. Preserve unresolved or conflicting links instead of using vague `related_to` edges.
7. Update `updated_at` and the compact index search/related anchors in the same operation; do not promote terms found only in unverified observations into accepted current search anchors. Read back record, index, observations/revisions, relations, status, and consumer impact. Use independent semantic review when a merge or replacement changes a widely consumed rule.

## Output
Report admitted/excluded plan statements when applicable, record IDs, operation/classification, accepted source and provenance root, plan/work/canonical links, changed relation/history/observation links, index/readback result, affected consumers, and unresolved stale anchors. Recurrence dimensions remain transparent and separate; do not report a structural edit or repeated occurrence as proof the knowledge itself is true.
