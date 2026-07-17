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
- expected_inputs: problem, constraints, selected method, invariants/complexity, alternatives, implementation/verifier refs, and declared store
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
1. Resolve the declared store and confirm selection is accepted and durable.
2. Verify implementation/evidence anchors and separate measured facts from rationale.
3. Create one `category=algorithm` record using the common envelope.
4. Add its index row and read back constraints, code refs, verifier refs, and supersession links.

Use `knowledge-base-update` when changing an existing selection. Do not turn a proposal or unrepresentative measurement into current project knowledge.
