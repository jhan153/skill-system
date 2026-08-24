---
name: management-project-context
description: Manage an explicitly requested project-context.yaml through minimal initialization, read-only diagnosis, selected-key updates, or bounded bootstrap. Preserve unrelated manifest sections, require exact approval for every write target, and never auto-create undeclared stores during ordinary work.
disable-model-invocation: true
---

# Management Project Context

## Routing Card
- role: project_context_operation
- intent_signature: explicit project-context manifest init, doctor, update, or bootstrap
- use_when: the user explicitly requests `manifest-init`, `doctor`, `update`, or guided `bootstrap` for project context locations
- do_not_use_when: ordinary context lookup/task work, inferred cleanup, store-content mutation, or automatic setup after a missing declaration
- expected_inputs: selected mode, exact repository root/manifest, requested keys or capabilities, resolved targets, and exact transaction approval for writes
- expected_outputs: minimal manifest/readback, read-only diagnosis, selected-key update, or approved delegated store bootstrap
- context_targets:
  must_read: exact manifest/root state, nearest repository instructions, and `references/project_context_manifest.md`
  read_if_needed: `references/manifest-modes.md`, exact approved targets, and the owning store initializer for an approved `create-store` action
  do_not_load_by_default: full repo, store contents, transcripts, home/global context, adjacent repositories, or undeclared Wikis
- risk_profile:
  reads: one repository boundary, one manifest, and exact selected targets
  writes: no writes in `doctor`; one minimal manifest or selected keys; delegated stores only in an approved bootstrap transaction
  tools: targeted local inspection/edit/readback and `skill-system-harness context resolve` when available
  sensitive_resources: credentials and discovery of home/adjacent stores denied; an external target requires an exact user-supplied path and approval
- entry_scene: PREPARE

## Mode Contract

Choose exactly one mode and read [Manifest Modes](references/manifest-modes.md):

- `manifest-init`: create only `schema_version: 1` and `project_id`, plus an exact location supplied or approved in the same request.
- `doctor`: validate declarations and resolved existence without mutation, normalization, discovery, or repair.
- `update`: change only explicitly named keys in an existing manifest while preserving unrelated and unknown sections.
- `bootstrap`: inspect and propose bounded action IDs, obtain one exact transaction decision, then delegate only approved store creation.

Initialization and update never create store content. Bootstrap may delegate `create-store` only to `management-memory-bank-init` or `management-knowledge-base-init`; it does not populate knowledge, copy chat, initialize plan trees, or create an LLM Wiki.

## Workflow

1. Resolve the exact user path, otherwise the nearest manifest inside the current repository. Do not scan elsewhere.
2. Select one mode from the requested outcome and apply its existence and authorization gate.
3. Bind every relative path from the manifest directory. For Knowledge, bind and report both `knowledge_root` and `knowledge_index`; an index outside the root is a separate exact target.
4. Before any write, show the exact manifest delta and every other target/action. Apply only approved action IDs and ask again only if scope changes.
5. Read back the complete manifest and every approved target entrypoint. Report declaration, target existence, and content initialization as separate states.

## Output

Return `mode`, manifest/root, findings or exact delta, approval boundary, applied actions, delegated owners, resolver/readback, preserved sections, and unavailable items. A missing declaration or target remains `unavailable`; it is never implicit setup authority.
