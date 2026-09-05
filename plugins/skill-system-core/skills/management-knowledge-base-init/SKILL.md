---
name: management-knowledge-base-init
description: Initialize a minimal navigable project Knowledge Base of Markdown records and register only its location in project-context.yaml. Use only on an explicit init/reinit request or an explicitly approved project bootstrap handoff; never infer knowledge or create a separate graph, score, Wiki, runtime projection, or derived context store.
---

# Management Knowledge Base Init

## Routing Card
- role: knowledge_operation
- family: management
- intent_signature: initialize project Knowledge Base, 빈 지식저장소 생성
- use_when: the user explicitly requests a new project Knowledge Base, approves it in project bootstrap, or authorizes reinitialization
- do_not_use_when: reading, recording, updating, plan sync, Wiki access, or automatic project setup is primary
- expected_inputs: verified project root/ID, exact target or manifest state, persistence intent, and exact init/reinit/bootstrap approval
- expected_outputs: one navigable compact index, manifest section update, and readback
- context_targets:
  must_read: exact target/manifest state, `references/project_context_manifest.md`, and `references/knowledge_record_contract.md`
  read_if_needed: repository documentation/persistence convention
  do_not_load_by_default: other stores, Memory, Wikis, plans, transcripts, generated projections
- risk_profile:
  reads: exact bound root/index targets and manifest only
  writes: one exact approved root, an explicitly separate index target when configured, and only the manifest `knowledge_base` section
  tools: local file operations and readback
  sensitive_resources: private sources and credentials denied; external/home paths require exact resolved-path approval
- entry_scene: PREPARE

## Workflow
1. Bind `knowledge_root` from the exact approved path or existing manifest declaration. Only when initialization was explicitly requested with neither may you propose `docs/knowledge-base/` as a default; approval binds that proposal before any write. Resolve relative paths from the manifest directory and show the resolved absolute target before any external/home write.
2. Bind `knowledge_index` from the approved/declared `knowledge_base.index`, otherwise `${knowledge_root}/index.md`. Reuse these two variables for every subsequent path; do not substitute a repository convention. If `knowledge_index` resolves outside `knowledge_root`, show and approve that exact second write target before creation. A new initialization materializes the bound index value as an explicit manifest `knowledge_base.index`; the fallback remains for reading compatible existing manifests that omit it.
3. Stop if `knowledge_root` already contains a store unless reinitialization and preservation/migration are explicit.
4. Create only `knowledge_index` with `ID | Category | Title / summary | Search anchors | Related | Path | Status`. Category directories are created lazily by the first admitted record; never add placeholders merely to materialize an empty layout.
5. Add or update only `knowledge_base.root`, `knowledge_base.index`, and `knowledge_base.storage` in `project-context.yaml`, preserving all other sections and the exact approved location representation. For a new store, register both bound location variables even when the index uses the default `${knowledge_root}/index.md` value.
6. Read back `knowledge_root`, `knowledge_index`, the empty catalog, and the manifest. Do not populate inferred records.

Keep typed relations, observation events, and semantic revisions embedded in their owning Markdown record. Initialization never creates claim/edge/event databases or a derived graph cache.

## Output
Report created/preserved paths, manifest readback, and any reinit or persistence uncertainty. Initialization is storage setup, not knowledge creation.
