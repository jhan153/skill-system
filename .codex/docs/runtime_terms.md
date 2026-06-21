# Runtime Terms

## manual drop-in

The user unpacks the bundle and copies files manually. The bundle does not install itself or modify live runtime state.

## runtime canonical

Codex runtime material lives inside `.codex`.

- `.codex/docs`: runtime guidance
- `.codex/eval`: usage-quality cases
- `.codex/tools`: small read-only sanity tools

Claude runtime material lives inside `.claude`.

## root packaging layer

Root files explain the bundle to a human. Root files are not runtime dependencies.

## runtime config policy

This bundle intentionally excludes `.codex/config.toml` to preserve the user's existing runtime config. It also excludes `automations/` because 7.3.1 core is a manual drop-in skill bundle, not an automatic runtime loop.

Review `.codex/rules/default.rules` against local policy before copying it.

## app-managed system skills

`.codex/skills/.system` is app-managed and is not part of the default copy payload. Optional snapshots belong under `optional-system-skills-snapshot/` and must not overwrite an existing runtime `.system` folder without explicit user intent.

## skill maturity

Maturity is a conservative use-readiness label. Allowed values are `skeleton`, `usable`, `field_tuned`, `experimental`, and `deprecated`.

## improvement track

Improvement track is the next specific work needed to improve a skill. It is not a status calculation.

## runtime usage eval

Runtime usage eval cases are examples for observing skill behavior in real use. They do not approve the bundle and do not prove skill quality.

## field feedback

Field feedback is real-use observation collected for future skill text, routing, maturity, or eval updates.

## bundle hygiene

Bundle hygiene checks only structure and obvious packaging mistakes. It is read-only and does not make quality decisions.

## 7.3.1 Core Boundary

7.3.1 core keeps skills, routing docs, maturity docs, usage cases, feedback guidance, source registry, generated mirror checks, and small sanity checkers.

7.3.1 core excludes install automation, live runtime mutation, deployment/signoff workflows, rollback flow, evidence finality workflows, package scoring, runtime config replacement, automations, default `.system` payload, and skill-system finality modeling.

## MCP integration vs local runtime (7.3.1)

The Kanboard plan-sync MCP/core under `integrations/kanboard-plan-sync` is **integration payload**: a plan-centric MCP facade + CLI that projects Markdown plans onto a local Kanboard via JSON-RPC. It is in-bundle.

The Kanboard application itself — runtime, SQLite DB, logs, API token, and the ThemeRevision/UI plugin — is **local third-party runtime** and is NOT bundled. The bundle ships only a setup methodology doc (`integrations/kanboard-plan-sync/docs/kanboard-localhost-setup.md`); MCP registration is provided as example files, never live config. The token is resolved from an env var or the local Kanboard DB at call time and is never stored in the bundle.
