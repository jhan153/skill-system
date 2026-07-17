---
name: knowledge-plan-sync
description: Synchronize only accepted durable decisions or changed domain/design/architecture rules from an approved plan into an existing project Knowledge Base. Use on an explicit sync or approved project checkpoint; never promote an entire plan, tentative language, implementation chronology, or rejected alternatives as current facts.
---

# Knowledge Plan Sync

## Routing Card
- role: knowledge_operation
- intent_signature: accepted plan decision to Knowledge sync
- use_when: the user explicitly requests sync, or an approved commit/closeout checkpoint identifies accepted durable plan changes
- do_not_use_when: the plan is draft/unapproved, no declared Knowledge Base exists, or ordinary implementation status is the only change
- expected_inputs: accepted plan slice, exact decisions/rules, declared store, canonical refs, and affected record IDs/categories
- expected_outputs: minimal create/update/supersede operations plus index and source-plan links
- context_targets:
  must_read: accepted plan decision slice, manifest/index, matching records, and `.codex/docs/knowledge_record_contract.md`
  read_if_needed: canonical source/design refs needed to verify current state
  do_not_load_by_default: full plan history, unrelated plans/store categories, Memory, Wiki, transcripts
- risk_profile:
  reads: accepted slice and matching records
  writes: only durable affected records/index rows
  tools: local edit and readback
  sensitive_resources: private plan material requires explicit scoped handling
- entry_scene: PREPARE

## Workflow
1. Identify statements whose lifecycle is accepted/current and whose value survives the task: domain invariant, design rule, algorithm choice, architecture boundary, recurring review rule, or decision.
2. Exclude TODOs, implementation chronology, speculative future state, temporary failures, and rejected alternatives except as bounded decision history.
3. Map each admitted statement to one category and existing record or stable new ID.
4. Delegate category-specific new authoring or use `knowledge-base-update` for an existing record; keep source plan and canonical artifact refs.
5. Update index rows and read back only affected records. Do not write Memory or an LLM Wiki.

## Output
Report admitted/excluded plan statements with reasons, delegated record operations, affected IDs, plan/canonical refs, and readback status.
