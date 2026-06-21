# Kanboard Plan Sync

`kanboard-plan-sync` projects Markdown `docs/plan/*.md` work plans onto a local Kanboard through JSON-RPC.

Markdown remains the source of truth. Kanboard is the operational projection for board visibility, status review, validation notes, and lightweight curation.

## Included

- Python CLI under `kanboard_plan_sync`
- MCP server under `kanboard_plan_sync_mcp`
- Workspace registration and dry-run/apply sync
- Pull/status/validation helpers
- MCP registration examples in `examples/`
- Localhost setup notes in `docs/kanboard-localhost-setup.md`

## Excluded

- The Kanboard application
- Kanboard database, logs, and uploaded files
- API tokens or credentials
- Custom Kanboard themes/plugins

## Source Of Truth

- Markdown plans are authoritative.
- Kanboard tasks are generated projections.
- Pull operations produce candidates; they do not edit Markdown automatically.
- Completion in Markdown still requires implementation, documentation, test, or validation evidence.

## CLI

Run from the repository root:

```bash
PYTHONPATH=integrations/kanboard-plan-sync/src python -m kanboard_plan_sync --help
```

Common commands:

```bash
PYTHONPATH=integrations/kanboard-plan-sync/src python -m kanboard_plan_sync init-workspace
PYTHONPATH=integrations/kanboard-plan-sync/src python -m kanboard_plan_sync register
PYTHONPATH=integrations/kanboard-plan-sync/src python -m kanboard_plan_sync sync-all
PYTHONPATH=integrations/kanboard-plan-sync/src python -m kanboard_plan_sync sync-all --apply
PYTHONPATH=integrations/kanboard-plan-sync/src python -m kanboard_plan_sync check-secrets
```

Use dry-run commands before any live apply.

## MCP

Example registrations:

- `examples/mcp.codex.toml`
- `examples/mcp.claude.json`

The MCP server exposes rollout and ops tools used by:

- `.codex/skills/kanboard-plan-rollout/SKILL.md`
- `.codex/skills/kanboard-plan-ops/SKILL.md`
- `.claude/skills/kanboard-plan-rollout/SKILL.md`
- `.claude/skills/kanboard-plan-ops/SKILL.md`

## Security

- The API token must come from `KANBOARD_API_TOKEN` or the local Kanboard DB resolver.
- The token is never written to workspace config, state, plan Markdown, or board comments.
- Live writes go through Kanboard JSON-RPC only.
- The integration does not write SQLite directly.
- Run `check-secrets` before packaging or sharing outputs.

## Local Runtime

See `docs/kanboard-localhost-setup.md` for local Kanboard setup expectations.
