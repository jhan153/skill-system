---
name: knowledge-base-maintenance
description: Validate, reindex, detect duplicates or broken artifact links, compact, and explicitly reconcile an existing Markdown Knowledge Base. Use for store-wide or cross-record maintenance; never use claim/edge/Wiki projection semantics, compute maturity scores, auto-repair read-only findings, or mutate Memory and LLM Wikis.
disable-model-invocation: true
---

# Knowledge Base Maintenance

## Routing Card
- role: knowledge_operation
- intent_signature: Knowledge Base validate, reindex, link check, duplicate/conflict reconciliation
- use_when: the user explicitly requests maintenance of an exact or manifest-declared store
- do_not_use_when: task context read, one known record update, new category authoring, plan sync, Memory, or Wiki work is primary
- expected_inputs: declared store, `report|validate|reindex|link-check|conflict-check|compact` operation, and affected IDs when bounded
- expected_outputs: structural findings and only explicitly requested store/index changes with readback
- context_targets:
  must_read: manifest, index, affected records, and `.codex/docs/knowledge_record_contract.md`
  read_if_needed: direct canonical/evidence refs or superseded records needed for one finding
  do_not_load_by_default: full external sources, unrelated Memory/Wikis/plans, raw transcripts
- risk_profile:
  reads: one declared Knowledge Base
  writes: only explicit reindex/reconcile/compact changes
  tools: targeted local search/edit/readback; no required Python validator
  sensitive_resources: private refs require explicit scoped access
- entry_scene: PREPARE

## Operations
- `report`: summarize layout, categories, statuses, and unresolved structural issues; byte-read-only.
- `validate`: check required envelope fields, stable IDs, category/path match, index/record agreement, and supersession links; byte-read-only.
- `link-check`: inspect declared repo/design/component/verifier targets without broad external retrieval; byte-read-only.
- `conflict-check`: identify duplicate active rules, contradictory scope, or competing canonical refs; byte-read-only.
- `reindex`: rebuild only catalog rows from records, never rewrite records from the index.
- `compact`: remove duplicated prose/index detail while preserving records, stable IDs, and history links.

Read-only findings never authorize repair. Reconciliation writes require explicit affected-record approval and use `knowledge-base-update` semantics.

## Workflow
1. Resolve the exact or nearest manifest-declared store; missing is `unavailable`, not auto-init.
2. Scope the requested operation and select index/records before following refs.
3. Separate structural validity from semantic truth and current-source verification.
4. Stop after findings for read-only operations.
5. For approved writes, stage affected records and index rows together, preserve stable IDs/supersession, and read back exact changes.

## Output
Lead with operation status, affected IDs/files, structural findings, semantic/source uncertainty, mutation/readback when applicable, and one next decision only if required.
