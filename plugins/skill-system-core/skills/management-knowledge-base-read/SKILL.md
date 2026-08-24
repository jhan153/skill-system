---
name: management-knowledge-base-read
description: Read a minimum task-relevant slice of a declared Knowledge Base, including bounded why/history, scope, conflict, and recurrence paths when requested. Use for project knowledge or concrete artifact/decision anchors; never scan undeclared stores, load the full graph, or substitute generic patterns for matching local knowledge.
---

# Management Knowledge Base Read

## Routing Card
- role: support
- intent_signature: local knowledge lookup, why/history path, related decision, recurring ticket or observation trace
- use_when: the user explicitly asks for project knowledge, or a declared store and concrete task anchor indicate a matching durable rule may exist
- do_not_use_when: no exact/declared store exists, the task has no concrete anchor, mutation is requested, or an LLM Wiki was selected
- expected_inputs: current task, exact path or nearest manifest, and file/symbol/component/topic/decision anchors
- expected_outputs: small source-traced current summaries plus only the typed relation/revision/observation path needed by the task owner
- context_targets:
  must_read: current request, manifest declaration, `references/project_context_manifest.md`, `references/knowledge_record_contract.md`, Knowledge index, and matching active records
  read_if_needed: canonical/evidence refs needed to resolve one conflict or verify freshness
  do_not_load_by_default: full store, unrelated categories, Memory, Wikis, raw sources, transcripts
- risk_profile:
  reads: one declared store and matching records
  writes: none
  tools: targeted local read/search only
  sensitive_resources: private refs require explicit scoped access
- entry_scene: PREPARE

## Workflow
1. Bind `knowledge_root` and `knowledge_index` from the exact path or nearest manifest declaration according to `references/project_context_manifest.md`. Missing means `unavailable`; do not scan, initialize, or substitute a default.
2. Derive task anchors and search `knowledge_index` first. Resolve every selected record path under the bound `knowledge_root` unless the index contains an explicit approved external record path.
3. Select matching current records by title, accepted aliases, search terms, `applies_to`, consumers, relation targets, and canonical anchors. Surface matching unverified records; admit superseded/deprecated records only for a material history path.
4. Choose the edge family that answers the question: causal/decision links for why, semantic/scope links for overlap or applicability, lifecycle/revisions for change history, and observations/provenance roots for recurrence.
5. Expand one typed edge at a time, record the visited targets, and stop on cycles or as soon as the question is answered. Reverse traversal uses targeted ID/ref search; never load the whole store as a graph dump.
6. For recurrence, return separate observation count, distinct verified provenance roots, first/last dates, scopes, unresolved roots, and counterexamples. Do not infer truth, importance, cause, or confidence from frequency.
7. Compare admitted records with current instructions and canonical repository/design evidence. Current verified source wins on conflict; preserve the losing record/path as stale or unresolved context when material.
8. Follow direct `canonical_refs`, `evidence_refs`, or `verified_by` only as needed, then return vocabulary/rules/invariants/decisions/anchors/validation expectations by role rather than page-by-page summaries.

Local Knowledge outranks generic model patterns within its verified scope. It does not override current user instructions or canonical source and does not replace the execution owner.

## Output
Return selected IDs, concise current statements, the traversed `source --relation--> target` path when used, canonical artifact anchors, recurrence dimensions when requested, conflicts/unverified items, and source record paths. Do not persist a context artifact unless explicitly requested.
