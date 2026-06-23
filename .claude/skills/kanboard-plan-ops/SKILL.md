---
name: kanboard-plan-ops
description: "Operate an already-registered Kanboard plan board — push markdown status, pull manual board changes, record validation/session updates, curate. Not for onboarding new repos — use kanboard-plan-rollout."
---

# Kanboard Plan Ops

## Routing Card
- role: primary
- intent_signature:
  - plan 변경 보드 반영(push markdown status)
  - 보드 상태/수동 변경 확인(pull board status)
  - validation 기록(record_validation)
  - 세션 종료 후 작업 요약 기록(record_session_update)
  - board curation
- use_when:
  - a workspace is already registered and the user wants to push plan status changes to its board.
  - the user wants to read manual Kanboard changes and get plan-update candidates.
  - the user wants to record validation evidence or curate orphan/completed/foreign cards.
  - the user wants the current agent session result reflected on the mapped Kanboard task.
- do_not_use_when:
  - the repo is not yet onboarded or the user wants bulk registration/sync; use `kanboard-plan-rollout`.
  - the request is about Kanboard runtime install, themes, or plugins (out of scope).
  - the user is editing the Markdown plan content itself; use `plan-short-term-docs`.
- expected_inputs:
  - registered workspace + plan path
  - desired op (push / pull / validation / session update / curate) and dry-run vs apply
  - explicit `task_reference` or `plan_id + task_key` for session/validation writes
- expected_outputs:
  - dry-run/applied push report, pull candidate list (markdown unchanged), validation/session projection, curation classification
  - stop reason when live connection, registration, token, idempotency, or approval requirements are not satisfied
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
- `record_session_update(task_reference | plan_id+task_key, session_summary, result_label?, validation_evidence?, changed_files?, blocked_reason?, dry_run=true)`: post-session comment; creates an evidence subtask only when validation evidence is supplied.
- `curate_plan_board(plan_id, workspace)`: classify orphan / completed / foreign cards.

## Workflow
1. Confirm Kanboard is running and the workspace is registered.
2. `sync_plan_to_board(dry_run=true)` → review → `dry_run=false` to apply.
3. `pull_board_status` → present candidates; promote to Markdown `done` ONLY with implementation/doc/test evidence.
4. For post-session reflection, call `record_session_update(dry_run=true)` with an explicit task mapping. Apply only when the projection is concise and does not include raw transcripts, secrets, or unrelated work.
5. `record_validation` / `curate_plan_board` as needed.
6. Verify on the board (My projects → board; the board view auto-refreshes).

## Card Projection Rules
- Kanboard card titles should be end-user Kanban work items, not copied raw plan lines.
- Descriptions must keep a source section with plan id, task reference, Markdown status, source line, and raw source title.
- Sync may refresh existing card title/description/color from Markdown, but Kanboard comments remain operational evidence rather than plan authority.

## Post-Session Hook Opt-In
- Default: disabled. Do not assume Stop hook writes to Kanboard.
- To enable dry-run reflection: set `KANBOARD_PLAN_POST_SESSION=dry-run` and an exact `KANBOARD_PLAN_TASK_REFERENCE` or `KANBOARD_PLAN_ID` + `KANBOARD_PLAN_TASK_KEY`.
- To enable live reflection: set `KANBOARD_PLAN_POST_SESSION=apply`; live apply still needs workspace config, Kanboard token, and a synced task.
- Optional fields: `KANBOARD_PLAN_WORKSPACE`, `KANBOARD_PLAN_VALIDATION_EVIDENCE`, `KANBOARD_PLAN_CHANGED_FILES`, `KANBOARD_PLAN_RESULT_LABEL`.
- The hook must skip rather than guess when task mapping is missing.

## Stop Policy
- `success`: dry-run or apply report matches the requested operation and includes affected project/swimlane/task ids when available.
- `blocked`: workspace is unregistered, Kanboard is not reachable, the target plan path is missing, or token/config discovery fails.
- `approval`: live board writes are requested without an immediately preceding dry-run summary and explicit user approval.
- `idempotency`: planned writes cannot be matched to stable repo/plan/task keys or would duplicate existing board cards.
- `mapping`: session/validation write lacks `task_reference` or `plan_id + task_key`; do not guess from conversation text.
- `unsafe`: the next action would write SQLite directly, store a token in config/state/plan, or auto-promote pulled board status into Markdown without evidence.
- `fatal`: board state or local state cache is inconsistent enough that the operation cannot be trusted.

## Idempotency
- Treat Markdown plan keys and registered workspace ids as the stable write keys.
- Prefer dry-run diffs over live writes until the affected board objects are visible.
- On retries, re-run dry-run and compare intended operations before applying.
- Post-session updates should be one comment per mapped task per session; combine related file/test notes into the same comment.
- Never infer completion from a Kanboard card alone; Markdown promotion still needs implementation/doc/test evidence.

## Safety
- Write tools default `dry_run=true`; applying needs a live connection (token via env / local DB).
- Pull/curate never mutate Markdown; completion is a candidate, not an auto-promotion. JSON-RPC only.
