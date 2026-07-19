---
name: knowledge-code-review-record
description: Record one recurring repository-specific code-review rule with detection cues, correct pattern, exceptions, and source examples by pointer. Use explicitly after a rule proves durable across reviews; never archive every review comment, one-off bug, personal style preference, or generic lint advice.
disable-model-invocation: true
---

# Knowledge Code Review Record

## Routing Card
- role: knowledge_operation
- intent_signature: recurring repository-specific review rule
- use_when: the user explicitly requests recording a durable review rule that should guide future changes
- do_not_use_when: the comment is one-off, already enforced by an obvious tool without project nuance, generic style advice, a personal preference, or an existing-record update
- expected_inputs: rule, affected scope, detection cues, correct pattern, exceptions, example/canonical refs, and declared store
- expected_outputs: one code-review record plus index row and readback
- context_targets:
  must_read: manifest/index, matching review records, representative correct/incorrect source refs, and `.codex/docs/knowledge_record_contract.md`
  read_if_needed: linter/test/config or prior accepted decision owning the rule
  do_not_load_by_default: full review history, PR comments, unrelated code, Memory, Wiki
- risk_profile:
  reads: matching records and representative source refs
  writes: one code-review record and index row
  tools: targeted local read/edit/readback
  sensitive_resources: private review identities/comments are not copied
- entry_scene: PREPARE

## Record Body
Capture the repository-specific rule, why it matters here, detection cues, correct pattern, exceptions, affected files/symbols, tool support, and representative examples by stable pointer.

## Workflow
1. Resolve the declared store and confirm the rule recurs or is an explicit repository policy.
2. Separate durable rule from the one-off symptom and remove reviewer identity or conversational text.
3. Create one `category=code-review` record using the common envelope.
4. Add its index row and read back scope, examples, exceptions, and verifier/tool links.

Use `knowledge-base-update` for an existing rule. Do not convert every review comment into Knowledge.
