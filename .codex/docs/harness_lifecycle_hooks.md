# Harness Lifecycle Hooks

This document defines the host-neutral lifecycle contract for 7.3.1 execution assurance.

Hooks are evidence and control surfaces. They do not replace `.codex/rules`, sandboxing, approval policy, or host permissions.

## Neutral Events

| neutral_event | purpose | required_record |
| --- | --- | --- |
| `request_received` | Capture request intent, routing candidates, and mode. | routing decision record |
| `context_loaded` | Capture loaded guidance, stale-doc risk, and context breadth. | context audit note |
| `tool_preflight` | Check arguments, path boundary, risk, and approval need before a tool call. | tool preflight decision |
| `permission_requested` | Record host approval boundary and policy reason. | permission decision note |
| `tool_result` | Capture exit status, changed files, evidence, and failure attribution. | tool result ledger |
| `tool_batch_completed` | Aggregate related tool results and partial failures. | batch observation summary |
| `turn_finalize_attempt` | Record a failed or unverified `Stop` check without making the turn terminal. | recoverable finalization attempt |
| `turn_finalize` | Record final validation observation and task result label before final response. | final observation record |
| `compact_before` | Preserve active plan, blocker, and validation evidence before compaction. | compaction handoff packet |
| `compact_after` | Confirm handoff packet survived compaction. | compaction restore note |

## Host Adapter Mapping

| neutral_event | Codex mapping | Codex support | Claude mapping | Claude support |
| --- | --- | --- | --- | --- |
| `request_received` | `UserPromptSubmit` | `native` | `UserPromptSubmit` | `native` |
| `context_loaded` | `SessionStart` or static check | `approximate` | `InstructionsLoaded` | `native` |
| `tool_preflight` | `PreToolUse` | `native` | `PreToolUse` | `native` |
| `permission_requested` | `PermissionRequest` | `native` | host-specific permission event | `approximate` |
| `tool_result` | `PostToolUse` | `native` | `PostToolUse` | `native` |
| `tool_batch_completed` | aggregate `PostToolUse` by turn | `approximate` | `PostToolBatch` | `native` |
| `turn_finalize_attempt` | failed or unverified `Stop` | `native` | failed or unverified `Stop` | `native` |
| `turn_finalize` | `Stop` | `native` | `Stop` | `native` |
| `compact_before` | `PreCompact` | `native` | `PreCompact` | `native` |
| `compact_after` | `PostCompact` | `native` | `PostCompact` | `native` |

Allowed support levels:
- `native`
- `approximate`
- `unsupported`

## Adapter Record Shape

```yaml
schema_version: 1
recorded_at: "2026-06-20T00:00:00Z"
neutral_event: tool_result
host: codex
host_event: PostToolUse
support_level: native
status: pass
session_id: session-id
turn_id: turn-id
tool_use_id: tool-use-id
tool_id: Bash
evidence:
  tool_result:
    exit_code: 0
    success: true
    output_truncated: false
```

## Tool Lifecycle Validation

Tool lifecycle validation is per `tool_use_id`, not a single global linear order. The valid pattern is:

```text
tool_preflight
permission_requested?
tool_result
```

Codex `PermissionRequest` can be turn-scoped and may not include `tool_use_id`; record that case with `support_level: approximate`. Multiple tool calls can repeat this sequence before a passing `turn_finalize`. A passing `turn_finalize` event must not arrive while a tool call is still missing its `tool_result`, and the ledger end must not leave a started tool unfinished.

Failed or unverified `Stop` checks are recorded as `turn_finalize_attempt`. They preserve evidence but do not make later repair tool calls invalid, and the live hook continues by default unless strict mode sees a narrow current-turn evidence contradiction.

Status values:
- `pass`: successful event or exit code 0
- `warn`: unverified, partial, missing optional current-run evidence, or unknown outcome
- `fail`: nonzero tool exit, explicit failure, denied action, or invalid current-run evidence; this is an observation status, not an automatic repository repair instruction
- `skip`: intentionally not run

## Boundaries

- Do not treat hook checks as a complete security boundary.
- Do not bypass sandbox, approval, or rule policy because a hook record exists.
- Do not use `Stop` to run source-repo validation, behavior evals, release profiles, plan synchronization, or repository-wide repair.
- A Kanboard post-session reflection is allowed only as an explicit opt-in (`KANBOARD_PLAN_POST_SESSION=dry-run|apply`) with an exact task mapping (`KANBOARD_PLAN_TASK_REFERENCE` or `KANBOARD_PLAN_ID` + `KANBOARD_PLAN_TASK_KEY`). It records a session comment through `record_session_update`; it must not infer tasks, promote Markdown completion, or run broad board sync.
- Keep repair/sync workflows explicit and separate from read-only hook observation.
- Project-local hooks may run automatically only after project trust and hook trust. They still do not install themselves or mutate user config.
- Use hook records as structured evidence for behavior evals and final report consistency checks.
- Loop-specific progress and bounded continuation are evaluated only for an explicitly active LoopRun state directory. Wiki feedback, reward-hacking, context-poisoning, idempotency, oscillation, over-orchestration, and event-runtime claims still belong in loop governance artifacts unless a dedicated validator is explicitly wired for that evidence.
