---
name: knowledge-plan-sync
description: Synchronize only accepted durable decisions or changed project rules from an approved plan into an existing Knowledge Base, preserving why, work-item links, overlap classification, and semantic history. Use on explicit sync or approved checkpoint; never promote an entire plan, tentative chronology, or repeated wording as new knowledge.
disable-model-invocation: true
---

# Knowledge Plan Sync

## Routing Card
- role: knowledge_operation
- intent_signature: accepted plan decision to Knowledge sync
- use_when: the user explicitly requests sync, or an approved commit/closeout checkpoint identifies accepted durable plan changes
- do_not_use_when: the plan is draft/unapproved, no declared Knowledge Base exists, or ordinary implementation status is the only change
- expected_inputs: accepted plan slice, exact decisions/rules, declared store, canonical refs, source work-item/ticket refs and provenance roots, and affected record IDs/categories
- expected_outputs: minimal create/observe/amend/relink/supersede operations plus index, semantic history, and source-plan/work links
- context_targets:
  must_read: accepted plan decision slice, manifest/index, matching records, and `.claude/docs/knowledge_record_contract.md`
  read_if_needed: canonical source/design refs needed to verify current state
  do_not_load_by_default: full plan history, unrelated plans/store categories, Memory, Wiki, transcripts
- risk_profile:
  reads: accepted slice and matching records
  writes: only durable affected records/index rows
  tools: local edit and readback
  sensitive_resources: private plan material requires explicit scoped handling
- entry_scene: PREPARE

## Workflow
1. Bind `knowledge_root` and `knowledge_index` from the exact approved path or nearest manifest declaration and reuse them for every record/index path. Missing is `unavailable`; never guess or scan for a store.
2. Identify statements whose lifecycle is accepted/current and whose value survives the task: domain invariant, design rule, algorithm choice, architecture boundary, recurring review rule, or decision.
3. Exclude TODOs, implementation chronology, speculative future state, temporary failures, and rejected alternatives except as bounded decision history.
4. Map each admitted statement to one category and search aliases, scopes, canonical anchors, relation targets, and existing observations before assigning an identity.
5. Classify exact identity/dependent recurrence, stable-identity amendment, replacement, scope overlap, conflict, or new knowledge. Preserve why with `motivated_by`/`raised_by`/`resulted_in` and stable plan/work-item pointers; do not infer a causal edge merely from proximity in a plan.
6. Delegate category-specific new authoring only for a new identity. Use `knowledge-base-update` to observe, amend, relink, reverify, or supersede an existing record, retaining provenance roots and semantic revisions.
7. Update navigable index rows and read back only affected records, relation paths, observations/revisions, and lifecycle links. Do not write Memory or an LLM Wiki.

## Output
Report admitted/excluded plan statements with reasons, overlap classification, delegated record operations, affected IDs, plan/work/canonical refs, relation/history/observation changes, and readback status.
