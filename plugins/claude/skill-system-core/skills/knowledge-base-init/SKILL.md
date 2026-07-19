---
name: knowledge-base-init
description: Initialize a minimal project Knowledge Base of Markdown records and register only its location in project-context.yaml. Use only on an explicit init or reinit request; never generate a Wiki, claim graph, Runtime Projection, Context Pack, validator, or inferred knowledge.
disable-model-invocation: true
---

# Knowledge Base Init

## Routing Card
- role: knowledge_operation
- intent_signature: initialize project Knowledge Base, 빈 지식저장소 생성
- use_when: the user explicitly requests a new project Knowledge Base or approved reinitialization
- do_not_use_when: reading, recording, updating, plan sync, Wiki access, or automatic project setup is primary
- expected_inputs: verified project root/ID, exact target or manifest state, persistence intent, and init/reinit authorization
- expected_outputs: minimal category layout, compact index, manifest section update, and readback
- context_targets:
  must_read: exact target/manifest state, `.codex/docs/project_context_manifest.md`, and `.codex/docs/knowledge_record_contract.md`
  read_if_needed: repository documentation/persistence convention
  do_not_load_by_default: other stores, Memory, Wikis, plans, transcripts, generated projections
- risk_profile:
  reads: exact target and manifest only
  writes: one project-local store and only the manifest `knowledge_base` section
  tools: local file operations and readback
  sensitive_resources: private sources and credentials denied
- entry_scene: PREPARE

## Workflow
1. Resolve the exact user path, declared root, or default `docs/knowledge-base/` only because init was explicitly requested.
2. Stop if a store exists unless reinitialization and preservation/migration are explicit.
3. Create `index.md` and empty `domain`, `design`, `algorithm`, `architecture`, `code-review`, and `decisions` category roots using repository-compatible placeholders only when empty directories cannot persist.
4. Add or update only `knowledge_base.root`, `knowledge_base.index`, and `knowledge_base.storage` in `project-context.yaml`, preserving all other sections.
5. Read back the layout, index, and manifest. Do not populate inferred records.

## Output
Report created/preserved paths, manifest readback, and any reinit or persistence uncertainty. Initialization is storage setup, not knowledge creation.
