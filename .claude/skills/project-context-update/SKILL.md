---
name: project-context-update
description: Update explicitly selected locations in an existing project-context.yaml while preserving every unrelated and unknown section. Use only on an explicit manifest update request; do not create stores, read their content, or normalize the whole file.
disable-model-invocation: true
---

# Project Context Update

## Routing Card
- role: project_context_operation
- intent_signature: update project-context.yaml paths, 프로젝트 컨텍스트 경로 수정
- use_when: the user explicitly requests a location, project ID, skill root, plan, or named Wiki declaration change
- do_not_use_when: initialization, ordinary context lookup, store content mutation, or inferred cleanup is primary
- expected_inputs: exact or nearest declared manifest, selected keys and values, and explicit update intent
- expected_outputs: section-preserving manifest update and direct readback
- context_targets:
  must_read: the complete target manifest and `.codex/docs/project_context_manifest.md`
  read_if_needed: only the exact resolved paths named by the requested update
  do_not_load_by_default: store contents, other manifests, home context, adjacent repositories, Wiki pages
- risk_profile:
  reads: one exact manifest and selected path existence only
  writes: requested keys in one repository-local manifest
  tools: local file edit and `skill-system-harness context resolve` readback when available
  sensitive_resources: undeclared stores and global/common Memory denied; an external target requires an exact user-supplied value
- entry_scene: PREPARE

## Preservation Contract
- Preserve comments, ordering where practical, and every unknown or unrelated top-level section.
- Change only keys named by the request. A store initializer may update only its owned section; this skill does not broaden that ownership.
- Treat `llm_wikis` entries as independent named sources. Update one named Wiki without replacing siblings unless full replacement is explicit.
- Resolve relative paths from the manifest directory. Preserve an approved relative representation; accept an absolute value only when the user supplied or approved that exact resolved target.
- A missing target is reported as `unavailable`; never create a Memory Bank, Knowledge Base, plan tree, Wiki, or skill root from this workflow.

## Workflow
1. Resolve the exact user path, otherwise the nearest manifest within the current repository boundary. If none exists, stop and route an explicit initialization request to `project-context-init`.
2. Read the entire manifest once and validate `schema_version: 1` plus a non-empty `project_id`.
3. Apply the smallest requested key edit. For Knowledge location changes, bind and report the resulting `knowledge_root` and `knowledge_index`; if the index resolves outside the root, report that exact second target separately. Do not move or rewrite store content. Preserve all other nodes byte-for-byte where the editing mechanism permits.
4. Read back the full manifest and use the common harness resolver when available to confirm resolved paths and existence flags.

## Output
Report the manifest path, exact keys changed, preserved sibling/unknown sections, and resolver readback. Separate location declaration from target existence and write authorization.
