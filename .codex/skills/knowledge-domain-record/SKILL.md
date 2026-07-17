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
- expected_inputs: precise statement, scope, canonical/evidence refs, consumers, and declared store
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
1. Resolve the declared store and confirm the statement is accepted, project-specific, durable, and not a duplicate.
2. Check current canonical refs and conflicts.
3. Create one stable `category=domain` record using the common envelope and category body.
4. Add its compact index row and read back record, index, refs, and consumers.

If an existing record owns the identity, use `knowledge-base-update` instead. Do not write a record merely because the model can explain the domain.
