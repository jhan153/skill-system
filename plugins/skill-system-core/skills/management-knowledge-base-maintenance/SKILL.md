---
name: management-knowledge-base-maintenance
description: Integrity-check, reindex, inspect typed relations and semantic history, classify overlap, derive recurrence profiles, compact, and explicitly reconcile an existing Markdown Knowledge Base. Use for store-wide or cross-record maintenance; never auto-merge similarity, compute scores, auto-repair read-only findings, or mutate Memory and LLM Wikis.
---

# Management Knowledge Base Maintenance

## Routing Card
- role: knowledge_operation
- intent_signature: Knowledge Base integrity-check, reindex, relation/history check, overlap/conflict reconciliation, recurrence report
- use_when: the user explicitly requests maintenance of an exact or manifest-declared store
- do_not_use_when: task context read, one known record update, new category authoring, plan sync, Memory, or Wiki work is primary
- expected_inputs: declared store, `report|integrity-check|reindex|link-check|relation-check|history-check|overlap-check|conflict-check|recurrence-report|compact` operation, and affected IDs when bounded
- expected_outputs: structural findings and only explicitly requested store/index changes with readback
- context_targets:
  must_read: manifest, index, affected records, `references/project_context_manifest.md`, and `references/knowledge_record_contract.md`
  read_if_needed: direct canonical/evidence refs or superseded records needed for one finding
  do_not_load_by_default: full external sources, unrelated Memory/Wikis/plans, raw transcripts
- risk_profile:
  reads: one declared Knowledge Base
  writes: only explicit reindex/reconcile/compact changes
  tools: targeted local search/edit/readback
  sensitive_resources: private refs require explicit scoped access
- entry_scene: PREPARE

## Operations
- `report`: summarize layout, categories, statuses, navigation coverage, and unresolved structural issues; byte-read-only.
- `integrity-check`: check required envelope fields, stable IDs, category/path match, index/record agreement, typed field shape, and reciprocal supersession links; byte-read-only. Treat unadopted legacy envelopes as readable legacy records, not fabricated history.
- `link-check`: inspect declared repo/design/component/verifier targets without broad external retrieval; byte-read-only.
- `relation-check`: check relation vocabulary, target existence, basis refs, and invalid lifecycle cycles; byte-read-only. Reverse edges are derived and need not be duplicated.
- `history-check`: compare current snapshot, `updated_at`, semantic revisions, and supersession state without reconstructing missing legacy history; byte-read-only.
- `overlap-check`: classify exact identity, dependent duplication, stable-identity amendment, replacement, scope overlap, and contradiction. Similarity proposes candidates but never authorizes merge; byte-read-only.
- `conflict-check`: identify duplicate active rules, contradictory scope, or competing canonical refs; byte-read-only.
- `recurrence-report`: derive observation count, distinct verified provenance roots, first/last dates, scopes, unresolved roots, and counterexamples. Treat source existence separately from verification of the asserted relationship to the record. Keep dimensions separate and return no rank or score; byte-read-only.
- `reindex`: rebuild only catalog rows from records, never rewrite records from the index.
- `compact`: remove duplicated prose/index detail while preserving current snapshots, stable IDs, typed relations, observations, semantic revisions, and lifecycle links.

Read-only findings never authorize repair. Reconciliation writes require explicit affected-record approval and use `management-knowledge-base-update` semantics.

## Workflow
1. Bind `knowledge_root` and `knowledge_index` from the exact or nearest manifest-declared store; missing is `unavailable`, not auto-init. Reuse those variables for every selected record and index operation; never substitute a default path.
2. Scope the requested operation and select index/records before following refs.
3. Separate structural validity, semantic identity/overlap, source existence, verification of the asserted relationship, current truth, and recurrence. Preserve counterexamples and unresolved provenance.
4. Stop after findings for read-only operations.
5. For approved writes, use `management-knowledge-base-update` semantics, stage affected records and index rows together, and read back current snapshots, relations, observations, revisions, and lifecycle links. Use an independent read-only semantic review when a merge/replacement can change a widely consumed rule.

## Output
Lead with operation status, affected IDs/files, structural findings, overlap/relation/history findings, source dependence or recurrence dimensions, mutation/readback when applicable, and one next decision only if required. Never collapse the result into importance, confidence, maturity, or frequency scores.
