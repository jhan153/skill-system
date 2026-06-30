---
name: kanboard-plan-rollout
description: "Onboard a repo's docs/plan to the local Kanboard and bulk register/sync across workspaces (init-workspace, register, sync-all dry-run→apply). Not for ad-hoc single-board ops — use kanboard-plan-ops."
---

# Kanboard Plan Rollout

## Routing Card
- role: primary
- intent_signature:
  - repo plan 도입(adopt docs/plan to Kanboard)
  - 일괄 등록/동기화(bulk register + sync-all)
  - multi-workspace onboarding
  - kanboard rollout / sync-all dry-run→apply
- use_when:
  - the user wants to put a repo's `docs/plan/*.md` onto the local Kanboard for the first time.
  - the user wants to register multiple workspaces and sync them at once.
  - the user asks for a dry-run preview of what a sync would create before applying.
- do_not_use_when:
  - the board is already registered and the user only wants ongoing status push/pull/validation; use `kanboard-plan-ops`.
  - the request is about Kanboard runtime install, themes, or plugins (out of scope).
  - the user is editing the Markdown plan content itself; use `plan-short-term-docs`.
- expected_inputs:
  - workspace/repo path(s) with `docs/plan/*.md`
  - approval boundary for live writes (dry-run first)
  - which plans to sync (per-plan `sync` flag)
- expected_outputs:
  - workspace config + registry entry, dry-run op summary, applied Kanban-facing projection report, per-repo failure isolation
  - stop reason when onboarding, secret hygiene, idempotency, or live-write approval requirements are not satisfied
- context_targets:
  must_read:
    - target workspace `docs/plan/*.md` and `.kanboard-plan.yml`
    - current onboarding request
  read_if_needed:
    - global registry (`workspaces.yml`)
    - integrations/kanboard-plan-sync README + localhost setup doc
  do_not_load_by_default:
    - full repo
    - other workspaces' plan bodies
- risk_profile:
  reads:
    - workspace config/plans/state, registry
  writes:
    - WRITE_WORKSPACE_CONFIG (`.kanboard-plan.yml`, state) and Kanboard projection via JSON-RPC on apply
  tools:
    - CALL_PROCESS for `kanboard_plan_sync` CLI / MCP tools; live apply needs a running Kanboard + token
  sensitive_resources:
    - API token from env/local DB only; never store secrets in config/state/plan
- entry_scene:
  - PREPARE

## Tools (MCP server: `kanboard-plan-sync`)
- `register_workspace(workspace_path)`: scaffold `.kanboard-plan.yml` from discovered `docs/plan/*.md` (per-plan `sync` flag) and add it to the global registry.
- `list_workspaces()`: registered workspaces + config/dir presence.
- `sync_all(apply=false)`: dry-run across registered workspaces; `apply=true` writes live.
- CLI equivalent: `python -m kanboard_plan_sync {init-workspace|register|list-workspaces|sync-all [--apply]|status-all|check-secrets}` (`PYTHONPATH=integrations/kanboard-plan-sync/src`).

## Workflow
1. `inspect_workspace(path)` — read-only: config, discovered plans, state, secret hygiene.
2. `register_workspace(path)` — init config + register (idempotent; won't clobber a hand-authored config).
3. `sync_all()` — DRY-RUN first; review planned ops per repo with the user.
4. On explicit approval: `sync_all(apply=true)` — repo=Project, plan=Swimlane, item=Task, members/assignee auto-set.
5. Hand ongoing status work to `kanboard-plan-ops`.

## Projection Quality
- Treat Kanboard as an execution board for end users, not a raw Markdown clone.
- Generated cards should use concise action-oriented titles and descriptions with source metadata.
- If a plan item is too broad or ambiguous to become a card, report it as a plan-authoring issue before live apply.

## Stop Policy
- `success`: all requested workspaces are registered or dry-run/applied reports identify isolated per-repo failures.
- `blocked`: target workspace is unavailable, no eligible `docs/plan` exists, Kanboard is unreachable, or token/config discovery fails.
- `approval`: `sync_all(apply=true)` is requested without a reviewed dry-run summary and explicit approval.
- `idempotency`: workspace identity, plan identity, or generated task keys are unstable or would duplicate existing board objects.
- `unsafe`: the next action would store secrets, overwrite hand-authored config without confirmation, write SQLite directly, or apply a bulk sync with unresolved dry-run errors.
- `fatal`: global registry or local state is corrupted enough that workspace mapping cannot be trusted.

## Idempotency
- `register_workspace(path)` must be treated as idempotent and must not clobber hand-authored config.
- Bulk sync retries must start with a fresh dry-run and compare repo/project/plan/task keys before apply.
- Isolate failures by workspace; do not apply unrelated workspaces when one workspace has ambiguous identity or unsafe state.

## Safety
- Dry-run before any apply; get approval for live writes.
- Token only from env (`KANBOARD_API_TOKEN`) or the local Kanboard DB. Run `check-secrets` when unsure.
- Requires the local Kanboard running (see the localhost setup doc). JSON-RPC only; never write SQLite.
