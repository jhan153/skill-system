# Kanboard Plan Ops

Use for an already registered workspace.

## Tools

- `sync_plan_to_board(plan_path, workspace, dry_run=true)`: Markdown-to-board push.
- `pull_board_status(plan_path, workspace)`: completion, demotion, new, and deletion candidates; never edits Markdown.
- `record_validation(plan_id, task_key, evidence, dry_run=true)`: mapped comment and evidence subtask.
- `record_session_update(...)`: one mapped session comment; create evidence detail only when supplied.
- `curate_plan_board(plan_id, workspace)`: classify orphan, completed, and foreign cards.

## Workflow

1. Confirm registration, plan/config, operation, connection, and exact task mapping for mapped writes.
2. Push and mapped writes follow the common dry-run/apply gate. Missing or unstable mapping blocks; never infer it from conversation text.
3. Pull returns candidates with Markdown unchanged. State the condition-matched evidence required for a later plan edit.
4. Keep session updates concise and task-local; combine related file/evidence notes instead of duplicating comments.
5. Verify apply by returned identifiers or board readback.

Cards use end-user work-item titles and retain source plan ID, task reference, Markdown status, source line, and raw source title. The optional post-session hook is disabled by default and never guesses mapping or bypasses the live-write gate.
