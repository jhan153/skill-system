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

## app-managed system skills

`.codex/skills/.system` is app-managed. Optional snapshots belong under `optional-system-skills-snapshot/` and require explicit user intent before replacing an existing runtime `.system` folder.

## skill maturity

Maturity is a conservative use-readiness label. Allowed values are `skeleton`, `usable`, `field_tuned`, `experimental`, and `deprecated`.

## improvement track

Improvement track is the next specific work needed to improve a skill. It is not a status calculation.

## runtime usage eval

Runtime usage eval cases are examples for observing skill behavior in real use and collecting improvement evidence.

## field feedback

Field feedback is real-use observation collected for future skill text, routing, maturity, or eval updates.

## Core Runtime Scope

The core runtime scope keeps skills, routing docs, maturity docs, usage cases, feedback guidance, source registry, generated mirror checks, and small sanity checkers.

Host-managed assets include runtime config such as `.codex/config.toml`, automations, deployment/signoff workflows, rollback operations, app-managed system skills, and local third-party runtimes.

## MCP integration vs local runtime (7.3.1)

The Kanboard plan-sync MCP/core under `integrations/kanboard-plan-sync` is **integration payload**: a plan-centric MCP facade + CLI that projects Markdown plans onto a local Kanboard via JSON-RPC. It is in-bundle.

The Kanboard application itself — runtime, SQLite DB, logs, API token, and the ThemeRevision/UI plugin — is **local third-party runtime** and is NOT bundled. The bundle ships only a setup methodology doc (`integrations/kanboard-plan-sync/docs/kanboard-localhost-setup.md`); MCP registration is provided as example files, never live config. The token is resolved from an env var or the local Kanboard DB at call time and is never stored in the bundle.
