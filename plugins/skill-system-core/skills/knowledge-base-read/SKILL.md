---
name: knowledge-base-read
description: Read a minimum task-relevant slice of an existing Knowledge Base declared by project-context.yaml. Use when the user requests project knowledge or a concrete file, symbol, component, design, algorithm, architecture, review, or decision anchor may be governed by a local record; never scan undeclared stores or substitute generic patterns for matching local knowledge.
---

# Knowledge Base Read

## Routing Card
- role: support
- intent_signature: local domain/design/algorithm/architecture/review knowledge lookup
- use_when: the user explicitly asks for project knowledge, or a declared store and concrete task anchor indicate a matching durable rule may exist
- do_not_use_when: no exact/declared store exists, the task has no concrete anchor, mutation is requested, or an LLM Wiki was selected
- expected_inputs: current task, exact path or nearest manifest, and file/symbol/component/topic/decision anchors
- expected_outputs: small source-traced record summaries returned to the current task owner
- context_targets:
  must_read: current request, manifest declaration, Knowledge index, and matching active records
  read_if_needed: canonical/evidence refs needed to resolve one conflict or verify freshness
  do_not_load_by_default: full store, unrelated categories, Memory, Wikis, raw sources, transcripts
- risk_profile:
  reads: one declared store and matching records
  writes: none
  tools: targeted local read/search only
  sensitive_resources: private refs require explicit scoped access
- entry_scene: PREPARE

## Workflow
1. Resolve an exact path, otherwise the nearest manifest declaration. Missing means `unavailable`; do not scan or initialize.
2. Derive task anchors and search the compact index first.
3. Select only matching `active` records. Surface a matching unverified record with its status; exclude superseded/deprecated records unless history is material.
4. Compare the record with current instructions and canonical repository/design evidence. Current verified source wins on conflict.
5. Follow direct `canonical_refs` or `verified_by` only as needed for the task, then stop at minimum sufficient context.
6. Return vocabulary/rules/invariants/decisions/anchors/validation expectations by role, not page-by-page summaries.

Local Knowledge outranks generic model patterns within its verified scope. It does not override current user instructions or canonical source and does not replace the execution owner.

## Output
Return selected IDs, concise applicable statements, canonical artifact anchors, conflicts/unverified items, and source record paths. Do not persist a context artifact unless explicitly requested.
