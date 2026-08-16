# Project Context Manifest Modes

Read only the selected mode.

## `manifest-init`

- Stop if `project-context.yaml` exists unless replacement is explicit; use `update` for selected keys.
- Create the minimal project-owned shape:

```yaml
schema_version: 1
project_id: <project-id>
```

- Add a location only when the same request supplied or approved that exact value. A declaration does not create its target.

## `doctor`

- Read only the complete manifest and declared entrypoints.
- Validate schema/project ID, resolve relative paths from the manifest directory, and classify each entry `declared-existing`, `declared-missing`, or `undeclared`.
- Report stale/conflicting declarations without normalizing, creating, inferring, or repairing anything.

## `update`

- Require an existing valid manifest. Change only keys named by the request.
- Preserve comments, ordering where practical, sibling values, unknown sections, and unrelated named `llm_wikis` entries.
- Preserve an approved relative representation. Accept an absolute value only when the user supplied or approved that exact resolved target.
- Inspect only selected path existence; never move or read store content and never create a missing target.

## `bootstrap`

1. Inspect the repository root, manifest, nearest instructions, and obvious project-local conventions. Inspect an external target only when the user supplied its exact path.
2. Present the minimal proposal. For every action give an ID, manifest value, resolved path, `storage`, action (`register-existing | declare-only | create-store | leave-unavailable`), owner, and reason. Show both Knowledge root and index.
3. Prefer no proposal over a speculative store. A missing manifest or common `docs/` layout is not evidence that Memory, Knowledge, plans, or a Wiki should exist.
4. Show the complete manifest delta and all `create-store` targets, then request one transaction decision covering all or a stated subset.
5. Apply only approved IDs. This skill owns a new minimal manifest or selected existing-manifest keys; a store initializer owns its scaffold and manifest section. Do not pre-write the same section through two owners.
6. Read back the manifest and each approved entrypoint. Label a new owner-defined scaffold `initialized-empty`, not populated context.

Bootstrap does not populate knowledge, copy conversations, choose an issue tracker, initialize a plan tree or skill root, or create an LLM Wiki.
