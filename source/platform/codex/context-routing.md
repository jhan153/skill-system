# Context Routing

This file defines only the exceptions that need routing. The current task owner remains responsible for understanding the request, implementation, validation, and final judgment.

## Default Resolution

```text
explicit user skill/path   -> direct use
clear one-specialist match -> direct use
genuine competing owners   -> one narrow router -> one specialist
no skill needed            -> current task owner
```

Do not pre-classify every request. Do not attach skills merely because their names are related to the topic.

Resolve a requested skill in this order:

1. exact path supplied by the user;
2. skill exposed or installed in the current session;
3. repository-local skill root explicitly declared by the nearest project instructions or `project-context.yaml`;
4. `unresolved`.

An exact path is authoritative for discovery but does not broaden the skill's declared scope. Do not declare a skill missing from the visible list before checking an exact supplied path. Do not scan unrelated home directories, plugin versions, adjacent repositories, or guessed local harnesses as fallback.

## Narrow Routers

Use at most one router, and only when its decision is genuinely unresolved:

- `analysis-router`: competing deep technical analysis owners;
- `research-router`: unclear scientific workflow stage;
- `search-router`: unclear cross-domain evidence lane;
- `loop-readiness-router`: explicit durable, repeated, event-driven, or Stop-driven execution whose readiness is not established.

The router returns one owner and stops. It does not acquire evidence, implement, validate, report, mutate Memory or Knowledge, or invoke another router. `workflow-rigor`, `workflow-validation`, reporting skills, `skill-creator`, Memory, and Knowledge are never automatic attachments.

## Direct Owners

| Request | Owner |
| --- | --- |
| direct implementation or refactor | current implementation owner or one clear specialist |
| approved plan/spec execution | `workflow-plan-runner` |
| bug fix with an unclear cause | `workflow-bug-fix`; use `analysis-bug` only for the unresolved cause |
| short persisted plan | `plan-short-term-docs` |
| accepted loop execution | `workflow-loop-runner` after a valid loop contract |
| Memory read | current task owner using `memory-bank-harness` only for a declared, task-relevant slice |
| persistent Memory write | the explicit Memory mutation skill matching the requested operation |
| Knowledge read | current task owner using `knowledge-base-read` for declared project knowledge |
| Knowledge write | the explicit category record, update, maintenance, or plan-sync owner |
| named LLM Wiki context | `llm-wiki-context`, explicitly selected and read-only |
| project context manifest initialization or location update | `project-context-init` or `project-context-update`, only on explicit request |
| repository skill update | current implementation owner; add `skill-system-repo-adapter` only for repository integration |
| personal skill creation | system `skill-creator` when explicitly named or clearly requested |

Requested brevity, a status question, a correction, or a complaint does not change the task owner. A report of harm or undesired behavior is not permission to inspect or mutate external state.

## Project Context Locations

The nearest `project-context.yaml` declares project-local skill roots, Memory Bank, Knowledge Base, plans, and named LLM Wikis. Follow `.codex/docs/project_context_manifest.md` or the Claude mirror for the locator contract.

- An exact user path overrides the manifest.
- The nearest manifest wins; do not merge it with parent manifests.
- A missing declaration or missing target is `unavailable`; do not fallback-scan or auto-initialize.
- Memory, Knowledge, plans, and Wiki content are context. Current instructions and verified source evidence outrank them.
- Context admission never grants write permission or replaces the task owner.

## Memory, Knowledge, And Wiki Boundary

- Memory Bank stores cross-session working rules, recurring interaction mistakes, useful practices, and compact current state. Read only relevant active material; do not load full archives or event ledgers by default.
- Knowledge Base stores durable project/domain/design/algorithm/architecture/code-review knowledge and direct artifact anchors. It is not an intermediate LLM Wiki projection.
- An LLM Wiki is a separate, explicitly selected context source. Read its own guide and navigation contract; do not assume a shared schema or merge multiple Wikis.
- Persistent writes require the owning workflow. General session completion, hook events, complaints, or inferred usefulness do not authorize collection or storage.

## Execution And Runtime Boundary

- Development requests execute source work; an active plan is input, not a substitute for implementation.
- Use one `change -> validation` owner. A verifier does not become a second workflow owner.
- Invoke routine approved executables directly. Use a shell wrapper only when pipeline, redirection, globbing, or other shell semantics are required.
- Live home configuration, plugin caches, app-managed `.system` skills, and other sessions are deployment state. Modify them only on an explicit deployment or live-runtime request.
- Explicit `/goal`, automation, durable repeated execution, or Stop continuation requires loop readiness and an accepted contract before execution.

## Heavy Artifacts And Evidence

- Plans, reports, lifecycle packages, synthetic eval suites, and other heavy artifacts require explicit artifact intent.
- Scenario/replay files prove only their authored contracts; they are not field-quality evidence.
- Hooks, harness records, and verifier receipts do not prove user intent and do not authorize repair.
- Use the smallest existing verifier or actual-path observation that matches the material condition. Do not create fixtures or validation infrastructure merely to obtain a stronger result label.

## Registry Boundary

Skill names, families, aliases, plugin membership, and legacy replacements belong to `docs/skill_registry.md` and skill Routing Cards. This file does not duplicate the full inventory or group matrix. Unknown or stale explicit aliases are `unresolved`; do not invent an installed skill.
