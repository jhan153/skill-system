---
name: kanboard-plan-ops
description: "Operate an already-registered Kanboard plan board without changing Markdown authority; use kanboard-plan-rollout for onboarding."
---

# Kanboard Plan Ops

## Routing Card
- role: primary
- intent_signature:
  - plan→board push, board change candidates, validation/session record, board curation
- use_when:
  - a registered workspace needs an ongoing push, pull, mapped evidence/session record, or curation classification.
- do_not_use_when:
  - onboarding/bulk registration (`kanboard-plan-rollout`), Kanboard installation/themes/plugins, or Markdown plan editing (`plan-short-term-docs`).
- expected_inputs:
  - registered workspace, plan path, operation, dry-run/apply intent, and explicit task mapping for mapped writes
- expected_outputs:
  - scoped projection/readback or candidate report, with exact stop reason for unmet write gates
- context_targets:
  must_read:
    - target plan `docs/plan/*.md` and `.kanboard-plan.yml`
    - current ops request
  read_if_needed:
    - workspace state cache, live board snapshot
    - integrations/kanboard-plan-sync README
  do_not_load_by_default:
    - full repo or other workspaces
- risk_profile:
  reads: plan, workspace config/state, and live board snapshot
  writes: Kanboard JSON-RPC projection on explicit apply; pull never edits Markdown
  tools: `kanboard-plan-sync` MCP; live ops need reachable Kanboard and token
  sensitive_resources: API token from env/local DB only
- entry_scene:
  - PREPARE

## Tools (MCP server: `kanboard-plan-sync`)
- `sync_plan_to_board(plan_path, workspace, dry_run=true)`: Markdown→board push (markdown-primary).
- `pull_board_status(plan_path, workspace)`: board→plan candidates (completion / demotion / new / deletion); never edits Markdown.
- `record_validation(plan_id, task_key, evidence, dry_run=true)`: comment + subtask evidence.
- `record_session_update(task_reference | plan_id+task_key, session_summary, result_label?, validation_evidence?, changed_files?, blocked_reason?, dry_run=true)`: mapped session comment; evidence subtask only when evidence is supplied.
- `curate_plan_board(plan_id, workspace)`: classify orphan / completed / foreign cards.

## Authority And Write Gates
- Markdown plan keys plus registered workspace IDs are stable projection keys and Markdown remains plan authority. Board state, comments, result labels, and validation records are operational evidence only.
- Pull and curation return candidates/classifications; they never mutate or auto-promote Markdown. A board completion candidate needs condition-matched implementation/doc/test evidence before a separate Markdown edit.
- Every live write starts with the same operation as `dry_run=true`. Dry-run proves only the intended projection. Apply only after its concise diff is reviewed and the user authorizes that live write; verify applied IDs/state through the board response or readback.
- Session/validation writes require exact `task_reference` or `plan_id + task_key`. Missing or unstable mapping blocks; never infer it from conversation text.
- Retries repeat dry-run and compare stable keys/intended operations. Combine one session's related file/evidence notes in one mapped comment rather than duplicating cards/comments.

## Workflow
1. Confirm the plan/config, registered workspace, operation, connection, and task mapping when required.
2. For push or mapped writes, run dry-run and report affected project/swimlane/task IDs plus missing gates. Apply only within the authorized projection.
3. For pull, return completion/demotion/new/deletion candidates with Markdown unchanged and state what evidence would justify a later plan edit.
4. For session updates, include only concise summary, relevant changed files, actual validation evidence, result label, or blocker; exclude transcripts, secrets, and unrelated work.
5. Verify live apply via returned identifiers or board readback. A dry-run result must not be reported as applied state.

## Projection Rules
- Kanboard card titles should be end-user Kanban work items, not copied raw plan lines.
- Descriptions must keep a source section with plan id, task reference, Markdown status, source line, and raw source title.
- Sync may refresh title/description/color from Markdown; never write SQLite directly or store tokens in config/state/plan.

## Post-Session Hook Opt-In
- Disabled by default; never assume Stop writes to Kanboard. `KANBOARD_PLAN_POST_SESSION=dry-run|apply` also requires exact `KANBOARD_PLAN_TASK_REFERENCE` or plan/task keys; apply still needs config, token, synced task, and the live-write gate above. Missing mapping skips rather than guesses.

## Stop Policy
- `success`: requested dry-run/candidate report is explicit, or an authorized apply is confirmed by IDs/readback.
- `blocked`: missing plan/registration/config/token/connection/mapping, unstable keys/duplicates, or inconsistent board/cache state.
- `approval`: apply lacks the matching dry-run summary or user authorization.
- `unsafe`: direct SQLite/token persistence, guessed mapping, or unevidenced Markdown promotion would be required.
