---
name: kanboard-plan-rollout
description: Onboard repository Markdown plans to local Kanboard projections through idempotent registration, reviewed bulk dry-runs, guarded apply, and live readback.
disable-model-invocation: true
---

# Kanboard Plan Rollout

## Routing Card
- role: primary
- intent_signature: first-time plan onboarding, multi-workspace registration, bulk sync dry-run/apply
- use_when:
  - a repo's `docs/plan/*.md` must be registered and projected for the first time
  - several workspaces must be registered or dry-run together
- do_not_use_when:
  - ongoing push/pull/validation on an already registered board: `kanboard-plan-ops`
  - Markdown plan authoring: `plan-short-term-docs`
  - concept explanation or Kanboard install/theme/plugin work: no rollout owner
- expected_inputs: exact workspace/plan selection, config/registry state, live-write boundary
- expected_outputs: registration and per-workspace dry-run/apply/readback receipts with partial/blocked state
- context_targets:
  must_read:
    - target plans, `.kanboard-plan.yml`, onboarding request
  read_if_needed:
    - host-local `workspaces.yml`, integration README, localhost setup
  do_not_load_by_default:
    - full repos or other workspaces' plan bodies
- risk_profile:
  reads:
    - plans/config/state and host-local registry
  writes:
    - WRITE_WORKSPACE_CONFIG for config/state/registry; live Kanboard projection only after its gate
  tools:
    - CALL_PROCESS for CLI/MCP; JSON-RPC for live apply/readback
  sensitive_resources:
    - token from env/local DB only; never config, state, plan, log, or board text
- entry_scene: PREPARE

## Route Decision
| Request | Exact owner/action |
| --- | --- |
| first-time or multi-workspace onboarding | `kanboard-plan-rollout` |
| registered-board push/pull/validation | hand off to `kanboard-plan-ops` |
| Markdown plan authoring | hand off to `plan-short-term-docs` |
| concept explanation or Kanboard install/theme/plugin | no owner; skip rollout |

Use these exact skill IDs; do not invent an adjacent owner name.

## Source And Tool Truth
- Markdown is canonical; Kanboard is a projection. Board changes remain candidates until ops validates them.
- `inspect_workspace(path)` reads config, plans, state, and secret findings without writes.
- `register_workspace(path, init=true)` may scaffold config/state and ensures host-registry membership. Use `init=false` for valid hand-authored config.
- `sync_all(apply=false)` previews every registered sync-enabled plan. `apply=true` writes by JSON-RPC and may continue after an error; its aggregate can be partial.
- CLI equivalents are `init-workspace`, `register`, `list-workspaces`, `sync-all [--apply]`, `status-all`, and `check-secrets` with `PYTHONPATH=integrations/kanboard-plan-sync/src`.

## Workflow
1. Fix the exact workspace/plan set; inspect each workspace before registration or sync.
2. Stop on missing workspace/plan, secret, corrupt mapping, ambiguous identity, or duplicate key.
3. Register idempotently. Existing valid config is not a blocker: preserve it with `init=false`, then continue to dry-run. Report registry/config/state writes separately from live writes.
4. Run `sync_all(apply=false)` and review every error, skip, identity, and operation summary. Dry-run is preview, not completion.
5. Apply requires a clean reviewed dry-run and explicit approval for the exact current workspace/plan/config/registry set. Any change invalidates review. Errors block bulk apply; reduced scope needs a fresh dry-run and approval.
6. Run `sync_all(apply=true)` only inside that boundary. Keep per-workspace/plan receipts; success never erases an error or unexpected skip.
7. Read back affected live objects through pull/ops. A clean command receipt without readback leaves the projection `unverified`.
8. Hand ongoing status push/pull, validation, and curation to `kanboard-plan-ops`.

## Outcome Contract
- `ready_for_review`: registration and current dry-run finished; no live apply is claimed.
- `blocked`: a pre-apply gate failed or reviewed inputs became stale.
- `partial`: requested work mixes applied operations with errors/unexpected skips; enumerate each workspace/plan and next action.
- `complete`: every requested projection applied and live readback has no unresolved mismatch.
- Do not downgrade `error`, ambiguous identity, missing live credentials, secret findings, or absent readback to a warning or whole-run success.

## Projection And Safety
- Generate concise source-traced cards; return broad/ambiguous items to plan authoring.
- Dry-run every retry and compare workspace/plan/task identities. Use JSON-RPC only, never SQLite; run `check-secrets` when needed.
