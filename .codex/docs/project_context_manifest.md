# Project Context Manifest

`project-context.yaml` is a project-owned location manifest for portable context stores. It answers where a project keeps context; it is not a router, database, index, or permission grant.

## Resolution

1. An exact path in the current user request wins.
2. Otherwise use the nearest `project-context.yaml` from the working path toward the repository root.
3. Do not merge parent and child manifests implicitly.
4. Resolve declared relative paths from the manifest directory. An absolute path is allowed only when the user supplied or approved that exact path; do not infer or normalize a relative declaration into an unrelated external location.
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

All sections except `schema_version` and `project_id` are optional. `storage` documents persistence intent; it does not authorize a write. `local` means locally persisted and not necessarily committed or located under the repository, while `repository` means the project expects normal repository persistence.

For Knowledge consumers, bind location once and use the resolved variables everywhere:

```text
knowledge_root  := exact approved path, otherwise resolve knowledge_base.root from the nearest manifest
knowledge_index := resolve knowledge_base.index when declared, otherwise knowledge_root/index.md
```

The example path above is only a default proposal. No reader, writer, maintenance operation, or hygiene check may substitute `docs/knowledge-base/` after `knowledge_root` is bound. Show the resolved absolute target before an external or home-level write. If `knowledge_index` resolves outside `knowledge_root`, show and authorize it as a second exact target. Exact path approval does not authorize scanning either target's parent or neighboring stores.

## Ownership And Updates

- Initializers update only their own section and preserve every unknown or unrelated section.
- In a bootstrap transaction, `project-context-init` owns a new minimal manifest and `project-context-update` owns approved declaration/registration changes to an existing manifest. A Memory or Knowledge `create-store` action delegates both its minimal target scaffold and its own manifest section to that store initializer, so two owners never write the same section.
- Persistent Memory or Knowledge writes still require the owning workflow and current user authorization.
- `llm_wikis` is a map of named, independent Wikis. If several are declared, the user or calling task must select one; consumers do not merge them automatically.
- A Wiki `guide` is its native navigation entrypoint. The manifest does not prescribe folder layout, page IDs, query syntax, or domain vocabulary.
- Common or home-level Memory is outside the default manifest contract.

## Explicit Setup Modes

- `manifest-init` creates only the minimal manifest and any exact location supplied or approved in the same request.
- `doctor` is read-only: resolve declarations, distinguish declared-missing from undeclared, and report findings without repair.
- `bootstrap` may inspect bounded repository-local setup signals and propose manifest/store actions. One transaction must enumerate the exact manifest delta and every store creation as separate action IDs; the user may approve all or a subset in one response. Approved Memory/Knowledge creation is delegated to its owning initializer without a second approval unless its owner, path, storage, or action changes.

No mode runs during ordinary project work merely because a manifest or store is absent. Declaration, target existence, and content initialization remain separate states.

For setup reporting, `initialized-empty` means the owning initializer created its required minimal index/meta/scaffold and registered it. It does not mean that project facts, inferred Memory, chat content, or Knowledge records were populated; those writes still require their content-owning workflows.
