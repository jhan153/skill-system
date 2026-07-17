# Project Context Manifest

`project-context.yaml` is a repository-owned location manifest for portable context stores. It answers where a project keeps context; it is not a router, database, index, or permission grant.

## Resolution

1. An exact path in the current user request wins.
2. Otherwise use the nearest `project-context.yaml` from the working path toward the repository root.
3. Do not merge parent and child manifests implicitly.
4. Resolve declared relative paths from the manifest directory.
5. A missing section or missing declared path is `unavailable`. Do not scan home directories, adjacent repositories, or guessed defaults, and do not initialize a store while resolving it.

Repository `AGENTS.md`, `CLAUDE.md`, or other platform instructions should point to this manifest instead of duplicating its paths.

## Minimal Shape

```yaml
schema_version: 1
project_id: example-project

skill_roots:
  - .codex/skills

memory_bank:
  root: docs/memory-bank/projects/example-project
  storage: local

knowledge_base:
  root: docs/knowledge-base
  index: docs/knowledge-base/index.md
  storage: repository

plans:
  root: docs/plan

llm_wikis:
  product_docs:
    root: ../Product-LLM-Wiki
    guide: README.md
    access: explicit_only
```

All sections except `schema_version` and `project_id` are optional. `storage` documents persistence intent; it does not authorize a write. `local` means project-local but not necessarily committed, while `repository` means the project expects normal repository persistence.

## Ownership And Updates

- Initializers update only their own section and preserve every unknown or unrelated section.
- Persistent Memory or Knowledge writes still require the owning workflow and current user authorization.
- `llm_wikis` is a map of named, independent Wikis. If several are declared, the user or calling task must select one; consumers do not merge them automatically.
- A Wiki `guide` is its native navigation entrypoint. The manifest does not prescribe folder layout, page IDs, query syntax, or domain vocabulary.
- Common or home-level Memory is outside the default manifest contract.
