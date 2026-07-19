# Runtime Terms

## skill system bundle

Skill System runtime material is organized as portable skills, docs, eval cases, tools, hooks, and integration source. Host-level settings remain under local runtime policy.

## runtime canonical

Codex runtime material lives inside `.codex`.

- `.codex/docs`: runtime guidance
- `.codex/eval`: usage-quality cases
- `.codex/tools`: small read-only sanity tools

Claude runtime material lives inside `.claude`.

## root packaging layer

Root files explain the Skill System package to a human. Runtime guidance lives under `.codex` and `.claude`.

## runtime config policy

Runtime configuration and automation assets, including `.codex/config.toml` and `automations`, are host-managed. Preserve existing local settings unless the user explicitly requests replacement.

Review `.codex/rules/default.rules` against local policy before copying it.

The default Codex hook map is empty. Optional hook adapters require explicit project/runtime enablement.

## project context manifest

The nearest `project-context.yaml` declares manifest-relative locations, or exact explicitly approved absolute locations, for optional Memory Bank, Knowledge Base, plans, skill roots, and named LLM Wikis. Missing entries are unavailable and do not trigger home or adjacent-repository discovery. Knowledge consumers bind `knowledge_root` and `knowledge_index` once from that declaration and never substitute a hard-coded default. Explicit setup keeps manifest declaration, target existence, and store initialization as separate states.

Memory Bank stores cross-session goals, rules, recurring mistakes, and proven practices. Knowledge Base stores accepted project knowledge as current artifact-linked Markdown snapshots with typed relations, semantic revisions, and provenance observations; recurrence dimensions are derived without scores. An LLM Wiki is a separately named read-only context source selected explicitly and navigated through its own conventions.

## app-managed system skills

`.codex/skills/.system` is app-managed. Optional snapshots belong under `optional-system-skills-snapshot/` and require explicit user intent before replacing an existing runtime `.system` folder.

## improvement track

Improvement track is the next specific work needed to improve a skill. It is not a status calculation.

## runtime usage eval

Runtime usage eval cases are authored regression examples. They can check their declared syntax and routing contract, but they are not field-quality evidence.

## field feedback

Field feedback means only a behavior or problem the user explicitly reports in conversation. The bundle does not automatically collect or persist prompts, transcripts, usage, or user identifiers.

## WorkItem lifecycle

WorkItem is the 8.5.0 state model for work that needs lifecycle governance before it becomes a `TaskRun`, `LoopRun`, or external board projection. It records source, owner, state history, evidence, findings, and next action.

WorkItem is not a queue runtime, scheduler, autonomous worker, Kanboard source of truth, or LoopRun replacement.

## work horizon

Work horizon is the 8.5.1 model for choosing between direct one-shot work, task/ticket state, short-plan artifacts, long-plan packages, loop overlays, and cross-horizon support facets. See `.codex/docs/work_horizon_model.md`.

For explicit “what next” questions, Work Horizon owns persistence and artifact altitude, Planning State owns admitted transitions only for persisted planning artifacts, and host routing retains the current-turn owner. This composition is non-executing workflow topology, not a registry navigator or orchestrator.

## delivery shape

Multi-batch execution selects one shape from `.codex/docs/delivery_slice_contract.md`: `vertical_slice`, `migration_sequence`, or `evidence_unit`. `single_batch` work does not activate that contract. Shape selection does not mandate TDD or irrelevant architectural layers.

## Core Runtime Scope

The core runtime scope keeps skills, routing docs, usage cases, generated mirror checks, and small sanity checkers. External source revisions, licenses, and adoption rationales are not runtime payload.

Host-managed assets include runtime config such as `.codex/config.toml`, automations, deployment/signoff workflows, rollback operations, app-managed system skills, and local third-party runtimes.

## MCP integration vs local runtime (7.3.1)

The Kanboard plan-sync MCP/core under `integrations/kanboard-plan-sync` is **integration payload**: a plan-centric MCP facade + CLI that projects Markdown plans onto a local Kanboard via JSON-RPC. It is in-bundle.

The Kanboard application itself — runtime, SQLite DB, logs, API token, and the ThemeRevision/UI plugin — is **local third-party runtime** and is NOT bundled. The bundle ships only a setup methodology doc (`integrations/kanboard-plan-sync/docs/kanboard-localhost-setup.md`); MCP registration is provided as example files, never live config. The token is resolved from an env var or the local Kanboard DB at call time and is never stored in the bundle.
