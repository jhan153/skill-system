---
name: knowledge-algorithm-record
description: Record one accepted project algorithm choice with problem constraints, invariants, complexity, rejected alternatives, implementation anchors, and verification evidence. Use explicitly for durable algorithm knowledge; do not store speculative proposals, benchmark noise, or generic textbook summaries.
---

# Knowledge Algorithm Record

## Routing Card
- role: knowledge_operation
- intent_signature: durable selected algorithm and implementation constraints
- use_when: the user explicitly requests recording an accepted project algorithm decision or invariant
- do_not_use_when: selection is unresolved, evidence is only a transient benchmark, the content is generic theory, or an existing record should be updated
- expected_inputs: problem, constraints, selected method, aliases/search terms, invariants/complexity, alternatives, implementation/verifier refs, overlap candidates, and declared store
- expected_outputs: one algorithm record plus index row and readback
- context_targets:
  must_read: manifest/index, matching algorithm/decision records, implementation/verifier refs, and `.codex/docs/knowledge_record_contract.md`
  read_if_needed: exact benchmark or design decision that materially supports selection
  do_not_load_by_default: full benchmark history, unrelated algorithms, Memory, Wiki, papers not selected as evidence
- risk_profile:
  reads: matching records and exact code/evidence refs
  writes: one algorithm record and index row
  tools: targeted local read/edit/readback
  sensitive_resources: private datasets/results require scoped summaries
- entry_scene: PREPARE

## Record Body
Capture problem and constraints, selected algorithm, correctness invariants, time/space behavior, implementation anchors, verifier/benchmark conditions, and rejected or superseded alternatives with reasons.

## Workflow
1. Bind `knowledge_root` and `knowledge_index` from the exact approved path or nearest manifest declaration, reuse them for every record/index path, and confirm selection is accepted and durable. Missing is `unavailable`; never guess or scan for a store.
2. Verify implementation/evidence anchors, separate measured facts from rationale, and search existing algorithms/decisions by constraint, scope, alias, and implementation anchor.
3. Classify same identity, amendment, replacement, specialization/generalization, conflict, or new selection. Use `knowledge-base-update` for an existing identity; do not treat another benchmark run as a new algorithm record.
4. Create one `category=algorithm` record only for a new identity, with the full current envelope, one `created` revision, and typed relation/observation links when applicable.
5. Add its navigable index row and read back constraints, code refs, verifier refs, relations/history, and supersession links.

Use `knowledge-base-update` when changing an existing selection. Do not turn a proposal or unrepresentative measurement into current project knowledge.
