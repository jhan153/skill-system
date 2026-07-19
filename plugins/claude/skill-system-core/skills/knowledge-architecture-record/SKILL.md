---
name: knowledge-architecture-record
description: Record one accepted project architecture boundary, ownership rule, dependency direction, lifecycle, or data-flow invariant with code/design anchors. Use explicitly for durable architecture knowledge; do not record speculative diagrams, generic patterns, or temporary implementation status.
disable-model-invocation: true
---

# Knowledge Architecture Record

## Routing Card
- role: knowledge_operation
- intent_signature: durable architecture boundary, ownership, lifecycle, dependency, data flow
- use_when: the user explicitly requests recording an accepted project architecture rule or decision
- do_not_use_when: architecture is undecided, the content is generic pattern advice, task chronology, or an existing-record update
- expected_inputs: boundary/owners, dependency/data flow, invariants, consequences, canonical refs, consumers, and declared store
- expected_outputs: one architecture record plus index row and readback
- context_targets:
  must_read: manifest/index, matching architecture/decision records, exact module/schema/code refs, and `.codex/docs/knowledge_record_contract.md`
  read_if_needed: migration plan or runtime evidence directly governing the boundary
  do_not_load_by_default: full repo architecture, unrelated diagrams, Memory, Wiki, old plans
- risk_profile:
  reads: matching records and boundary anchors
  writes: one architecture record and index row
  tools: targeted local read/edit/readback
  sensitive_resources: private architecture refs remain scoped
- entry_scene: PREPARE

## Record Body
Capture boundary and owner, dependency direction, lifecycle/data flow, invariants, allowed exceptions, migration/consumer consequences, and direct code/schema/design anchors.

## Workflow
1. Resolve the declared store and verify the boundary is accepted/current.
2. Inspect representative owners/consumers and one material counterexample or exception when relevant.
3. Create one `category=architecture` record using the common envelope.
4. Add its index row and read back ownership, anchors, consumers, and supersession links.

Use `knowledge-base-update` for an existing boundary. Do not save a clean diagram as knowledge when source ownership disagrees.
