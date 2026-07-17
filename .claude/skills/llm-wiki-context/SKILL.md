---
name: llm-wiki-context
description: Build minimum task-oriented read-only context from one explicitly selected LLM Wiki by first following that Wiki's own guide, index, search, graph, or backlink conventions. Use only when the user explicitly names a Wiki, supplies its exact path, or invokes this skill; never auto-select among multiple Wikis, assume Book-specific structure, mutate Wiki/Memory/Knowledge, or load the whole Wiki.
---

# LLM Wiki Context

## Routing Card
- role: support
- intent_signature: explicit named LLM Wiki exploration and task context construction
- use_when: the user invokes this skill, supplies an exact Wiki path, or explicitly selects a named `llm_wikis` entry
- do_not_use_when: no Wiki is selected, several candidates remain, project Knowledge Base is the intended source, Wiki mutation/composition is requested, or ordinary repo evidence is sufficient
- expected_inputs: current task/owner, exact Wiki path or name, manifest declaration when used, and task anchors
- expected_outputs: compact role-organized context with source page refs returned to the current task owner
- context_targets:
  must_read: current task, selected Wiki declaration/path, and that Wiki's own guide/entrypoint
  read_if_needed: native index/search/graph/backlinks and only pages selected from them
  do_not_load_by_default: full Wiki, other named Wikis, Memory, Knowledge, raw transcripts, Book-specific assumptions
- risk_profile:
  reads: one explicitly selected Wiki
  writes: none
  tools: Wiki-native read/search/navigation only
  sensitive_resources: private Wiki access stays within the selected path/session
- entry_scene: PREPARE

## Resolution
1. Use an exact Wiki path from the user.
2. Otherwise resolve the explicitly selected name in the nearest `project-context.yaml`.
3. Require its declared `guide` or identify the Wiki's own entrypoint from the exact root without broad scanning.
4. If the name is absent, the path is missing, or several Wikis remain possible, return `unavailable`/the one required selection. Do not guess or merge.

## Workflow
1. Read the Wiki's own guide/entrypoint and learn its native navigation and source-link conventions.
2. Decompose the task into objective, entities, operation, invariants, decisions, and code/design/artifact anchors.
3. Use only the Wiki-native index, search, graph, backlinks, or curated paths that match those anchors.
4. Compose context by role: vocabulary, current architecture/state, invariants, accepted decisions, rejected/superseded approaches, artifact anchors, consumers, validation expectations, conflicts/unresolved questions, and source pages.
5. Check freshness/conflicts against current user instructions and accessible canonical project evidence when material.
6. Stop at minimum sufficient context and return it to the current task owner.

Read `references/context-composition.md` only when the Wiki's guide leaves selection or composition ambiguous.

## Boundary
- Read-only: no Wiki edits, page creation, tagging, backlink changes, or automatic Context Pack persistence.
- No Memory or Knowledge writes and no Knowledge-to-Wiki composition.
- Format-independent: do not require claim/source/edge schemas, Runtime Projection, page IDs, folder names, or a particular query language.
- Book is one possible field instance, not a template or special case.

## Output
Return selected Wiki/name/root, navigation method used, task anchors, compact role-organized context, source page refs, conflicts/freshness limits, and no-hit reason when applicable. Omit empty roles.
