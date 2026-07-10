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
| `turn_finalize_attempt` | Record a failed, skipped, unverified, strict-blocked, Recovery Guard audit/handoff, or LoopRun-continuation `Stop` without terminal evidence. | recoverable finalization attempt |
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

Each `Stop` call records one lifecycle outcome. A validated terminal observation records one `turn_finalize`; failed, skipped, unverified, strict-blocked, Recovery Guard audit/handoff, and blocking LoopRun-continuation checks record one `turn_finalize_attempt`. Attempts preserve evidence without making later repair calls invalid, and the live hook continues by default unless an explicit bounded gate blocks.

### Context-pressure Recovery Guard

The Codex adapter maintains an out-of-band, session-scoped reducer in default `observe` mode. It stores only counters, booleans, signal codes, and event hashes. `PostCompact`, six user turns, twenty tool preflights, or two correction episodes arm the reducer, but arming never blocks by itself. A soft audit is eligible only when an armed session has a pending explicit correction, the Stop message combines an apology/agreement opener with a rhetoric-only operational promise, contains no substantive result, and no changed-file or validation progress receipt followed the correction. Concrete direct conclusions count as substantive; an explicit Korean or English instruction to stop cancels the pending correction episode.

`SKILL_SYSTEM_RECOVERY_GUARD=audit` allows one Stop block per correction episode, capped at three blocks per session. The block requests a compact `recovery_audit`; only the host-marked `stop_hook_active=true` continuation can consume that response and move the reducer to `awaiting_user`. An inactive near-duplicate preserves the audit request. The handoff is recorded as a nonterminal `turn_finalize_attempt`, while the next user prompt cancels the pending handoff. Both paths skip agent-run finalization, completion notification, and post-session synchronization. A malformed packet is recorded but does not cause another block, preventing a hook-created recovery loop. An explicit active LoopRun has precedence and makes Recovery Guard shadow-only; this release does not deny tool calls. `SKILL_SYSTEM_RECOVERY_GUARD=off` is the environment-level emergency disable and overrides per-event audit mode.

The guard is a quality-recovery control, not a permission or security boundary. It does not parse transcript files, infer semantic goal drift, or deny PreToolUse in this release. Missing session identity, corrupt state, or unavailable locking fails open and records an observation when possible. `SessionStart(source=clear)` resets the state; resume preserves it, and `SessionStart(source=compact)` arms it.

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
- Kanboard SessionStart autosync is also explicit-only (`KANBOARD_PLAN_AUTOSYNC=dry-run|apply`); the default hook path performs no board mutation.
- Keep repair/sync workflows explicit and separate from read-only hook observation.
- Project-local hooks may run automatically only after project trust and hook trust. They still do not install themselves or mutate user config.
- Use hook records as structured evidence for behavior evals and final report consistency checks.
- Loop-specific progress and bounded continuation are evaluated only for an explicitly active LoopRun state directory. Wiki feedback, reward-hacking, context-poisoning, idempotency, oscillation, over-orchestration, and event-runtime claims still belong in loop governance artifacts unless a dedicated validator is explicitly wired for that evidence.
- A `manual_check` pass requires a durable `user_acceptance` event captured from actual user input and bound to the contract, LoopRun, condition, actor, scope, and receipt digest. This is procedural audit evidence, not cryptographic identity proof; if the event is absent, ambiguous, or not sourced from `user_input`, manual verification remains unavailable.
- An agent-run final report is a claim surface, not an independent receipt. `agent-verified` cannot use `manual_check` or the final report itself as claim evidence, and schema-v2 `command_exit` evidence must bind to matching tool lifecycle receipts.
