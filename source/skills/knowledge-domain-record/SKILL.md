---
name: knowledge-domain-record
description: Record one accepted project-specific domain term, invariant, state rule, or operational consequence in an existing declared Knowledge Base. Use explicitly for durable domain knowledge; do not record generic background, tentative interpretations, interaction mistakes, or implementation chronology.
---

# Knowledge Domain Record

## Routing Card
- role: knowledge_operation
- intent_signature: durable domain vocabulary, invariant, state or business rule
- use_when: the user explicitly requests recording one accepted project-specific domain fact
- do_not_use_when: the fact is generic, tentative, task-local, already an existing-record update, or belongs to Memory/design/algorithm/architecture/review
- expected_inputs: precise statement, aliases/search terms, scope, canonical/evidence refs, consumers, overlap candidates, and declared store
- expected_outputs: one domain record plus index row and readback
- context_targets:
  must_read: manifest/index, matching domain records, canonical refs, and `.codex/docs/knowledge_record_contract.md`
  read_if_needed: source slice needed to disambiguate vocabulary or invariant
  do_not_load_by_default: full store/domain corpus, Memory, Wiki, transcripts
- risk_profile:
  reads: matching domain records and refs
  writes: one domain record and index row
  tools: local edit/readback
  sensitive_resources: private domain sources require explicit scope
- entry_scene: PREPARE

## Record Body
Capture vocabulary/meaning, invariant or allowed/forbidden states, operational consequence, scope/exceptions, and direct consumers. Prefer canonical code/schema/spec refs over an explanatory paraphrase alone.

## Workflow
1. Bind `knowledge_root` and `knowledge_index` from the exact approved path or nearest manifest declaration, reuse them for every record/index path, and confirm the statement is accepted, project-specific, and durable. Missing is `unavailable`; never guess or scan for a store.
2. Search matching titles, aliases, terms, scopes, relation targets, and canonical refs. Classify same identity, shared-provenance recurrence, amendment, replacement, partial scope overlap, conflict, or genuinely new knowledge.
3. If an existing record owns the identity, use `knowledge-base-update` to observe/amend/relink it. For partial overlap, keep distinct identities and add the typed scope relation; never merge from wording similarity.
4. Create one stable `category=domain` record only for a new identity, using the full current envelope, one `created` semantic revision, direct anchors, and any source-traced relation/observation.
5. Add its compact navigable index row and read back record, index, refs, relations, history, and consumers.

If an existing record owns the identity, use `knowledge-base-update` instead. Do not write a record merely because the model can explain the domain.
