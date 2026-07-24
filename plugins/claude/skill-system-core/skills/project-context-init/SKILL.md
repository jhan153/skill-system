---
name: project-context-init
description: Initialize, explicitly bootstrap, or diagnose project-declared context locations. Use only when the user asks to create project-context.yaml, set up project context stores, or run a context doctor; inspect and propose before bootstrap writes, and never create an unapproved store or auto-run during ordinary tasks.
disable-model-invocation: true
---

# Project Context Init

## Routing Card
- role: project_context_operation
- intent_signature: initialize project-context.yaml, project context bootstrap/setup, context doctor, 프로젝트 컨텍스트 셋업/진단
- use_when: the user explicitly requests `manifest-init`, guided `bootstrap`, or read-only `doctor` behavior
- do_not_use_when: ordinary context resolution, an undeclared store is merely missing during another task, store content mutation, or generic project setup is primary
- expected_inputs: selected mode, exact repository root/manifest, stable project ID when known, desired context capabilities, and one exact transaction approval that enumerates every write target
- expected_outputs: manifest readback, a read-only diagnosis, or one approved bootstrap transaction delegated to existing store owners
- context_targets:
  must_read: exact root/manifest state, nearest repository instructions, and `.claude/docs/project_context_manifest.md`
  read_if_needed: bounded project-local paths that support one proposed declaration; owning init contract for each approved store
  do_not_load_by_default: full repo, store contents, transcripts, home/global context, adjacent repositories, undeclared Wikis
- risk_profile:
  reads: exact repository boundary, manifest, bounded project-local setup signals, and only an explicitly supplied external target itself
  writes: none in doctor; one manifest in manifest-init; only explicitly approved manifest keys and delegated stores in bootstrap
  tools: targeted local inspection/edit/readback and `skill-system-harness context resolve` when available
  sensitive_resources: home/global discovery, private sources, and credentials denied; an exact external/home target is allowed only when explicitly supplied and approved
- entry_scene: PREPARE

## Modes

### `manifest-init`

Create only a minimal project-owned manifest. Stop if it exists unless replacement is explicit; otherwise use `project-context-update` for selected keys.

```yaml
schema_version: 1
project_id: <project-id>
```

Add an optional location section only when the same request supplied or approved that exact location. A declaration does not create its target.

### `doctor`

Read only. Validate the manifest schema/project ID, resolve every declared relative path from the manifest directory, distinguish `declared-existing`, `declared-missing`, and `undeclared`, and inspect only the declared index/guide entrypoints needed to confirm usability. Report stale or conflicting declarations; do not normalize paths, create targets, infer desired stores, or repair findings.

### `bootstrap`

Provide one bounded guided setup for users who would otherwise need to invoke several context skills manually:

1. Inspect the repository root, current manifest, nearest instructions, and obvious project-local context conventions. Never discover or scan home/adjacent repositories; when the user supplied an exact external target, inspect only that resolved target and not its parent or neighbors.
2. Present what already exists and a minimal proposal. For each proposed action state the manifest value, resolved absolute path, `storage`, action (`register-existing | declare-only | create-store | leave-unavailable`), owning skill, and why the project appears to need it. A Knowledge action shows both resolved `knowledge_root` and `knowledge_index`; an index outside the root is a separate exact write target within that action.
3. Prefer no proposal over a speculative store. A missing manifest or common `docs/` convention is not evidence that Memory, Knowledge, plans, or a Wiki should exist.
4. Give every proposed write an action ID and show the complete manifest delta plus each `create-store` action. Ask for one exact transaction decision; the user may approve all listed actions or a stated subset in one response. A declaration-only action does not imply target creation unless the same transaction also lists and approves that `create-store` action.
5. Apply only the approved action IDs. This skill owns a new minimal manifest; `project-context-update` owns approved `declare-only` or `register-existing` keys in an existing manifest. For Knowledge, the approved action binds `knowledge_root` and `knowledge_index`; every delegate and later consumer must reuse those values. For `create-store`, delegate both the minimal target scaffold and that store's own manifest section to `memory-bank-init` or `knowledge-base-init`; do not pre-write the same section through two owners. Do not ask for a second approval when owner, resolved path, storage, and action are unchanged; ask again only for a changed or newly introduced write. Never initialize a plan tree, skill root, or LLM Wiki; register an existing exact path only when approved.
6. Read back the final manifest and each approved created/registered entrypoint. Report a newly created owner-defined empty scaffold as `initialized-empty`, not as populated project Memory or Knowledge. Preserve unapproved candidates as `unavailable`, not as TODO writes.

Bootstrap coordinates location setup only. It does not populate knowledge, copy chat, synthesize Memory, choose an issue tracker, or become the ordinary task orchestrator.

## Output

Return `mode`, inspected root/manifest, findings or proposal, exact approval boundary, applied actions, delegated store owners, resolver/readback, and unavailable/unapproved items. Report declaration, target existence, and content initialization as separate states.
