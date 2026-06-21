---
name: kanboard-plan-ops
description: "Operate an already-registered Kanboard plan board — push markdown plan status, pull manual board changes, record validation, curate. Not for onboarding new repos — use kanboard-plan-rollout."
---

# Kanboard Plan Ops

## Routing Card
- role: primary
- intent_signature:
  - plan 변경 보드 반영(push markdown status)
  - 보드 상태/수동 변경 확인(pull board status)
  - validation 기록(record_validation)
  - board curation
- use_when:
  - a workspace is already registered and the user wants to push plan status changes to its board.
  - the user wants to read manual Kanboard changes and get plan-update candidates.
  - the user wants to record validation evidence or curate orphan/completed/foreign cards.
- do_not_use_when:
  - the repo is not yet onboarded or the user wants bulk registration/sync; use `kanboard-plan-rollout`.
  - the request is about Kanboard runtime install, themes, or plugins (out of scope).
  - the user is editing the Markdown plan content itself; use `plan-short-term-docs`.
- expected_inputs:
  - registered workspace + plan path
  - desired op (push / pull / validation / curate) and dry-run vs apply
- expected_outputs:
  - dry-run/applied push report, pull candidate list (markdown unchanged), validation projection, curation classification
- context_targets:
  must_read:
    - target plan `docs/plan/*.md` and `.kanboard-plan.yml`
    - current ops request
  read_if_needed:
    - workspace state cache, live board snapshot
    - integrations/kanboard-plan-sync README
  do_not_load_by_default:
    - full repo
    - other workspaces
- risk_profile:
  reads:
    - plan, workspace config/state, live board snapshot
  writes:
    - WRITE_KANBOARD projection via JSON-RPC on apply (push/validation); never edits Markdown on pull
  tools:
    - CALL_PROCESS for `kanboard_plan_sync` MCP tools; live ops need a running Kanboard + token
  sensitive_resources:
    - API token from env/local DB only
- entry_scene:
  - PREPARE

## Tools (MCP server: `kanboard-plan-sync`)
- `sync_plan_to_board(plan_path, workspace, dry_run=true)`: Markdown→board push (markdown-primary).
- `pull_board_status(plan_path, workspace)`: board→plan candidates (completion / demotion / new / deletion); never edits Markdown.
- `record_validation(plan_id, task_key, evidence, dry_run=true)`: comment + subtask evidence.
- `curate_plan_board(plan_id, workspace)`: classify orphan / completed / foreign cards.

## Workflow
1. Confirm Kanboard is running and the workspace is registered.
2. `sync_plan_to_board(dry_run=true)` → review → `dry_run=false` to apply.
3. `pull_board_status` → present candidates; promote to Markdown `done` ONLY with implementation/doc/test evidence.
4. `record_validation` / `curate_plan_board` as needed.
5. Verify on the board (My projects → board; the board view auto-refreshes).

## Safety
- Write tools default `dry_run=true`; applying needs a live connection (token via env / local DB).
- Pull/curate never mutate Markdown; completion is a candidate, not an auto-promotion. JSON-RPC only.
