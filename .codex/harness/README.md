# Harness Runtime

The harness records execution evidence; it does not prove user success, grant permission, or run repository repair.

## Runtime Modes

| mode | activation | effect |
| --- | --- | --- |
| observation | default | write redacted lifecycle metadata to the configured exact file or durable per-run ledger; Stop remains non-blocking |
| recovery observation | default (`SKILL_SYSTEM_RECOVERY_GUARD=observe`) | maintain compact session counters and record `would_audit` without prompt injection or blocking |
| recovery audit | `SKILL_SYSTEM_RECOVERY_GUARD=audit` | after context pressure, block at most one Stop per correction episode (three per session) only for correction + rhetoric-only recovery + missing progress evidence |
| recovery emergency off | `SKILL_SYSTEM_RECOVERY_GUARD=off` | disable observation and blocking; the environment switch overrides per-event audit mode |
| agent-run envelope | `SKILL_SYSTEM_AGENT_RUN_BOOTSTRAP=1` | create a session/turn run manifest and validate its evidence bindings |
| strict output gate | `SKILL_SYSTEM_AGENT_OUTPUT_GATE=strict` | block only narrow current-turn evidence contradictions |
| verifier receipt monitor | `SKILL_SYSTEM_REFERENCE_MONITOR=1` | record whether one pre-bound verifier receipt is current for its declared subjects; never select a task label or control Stop/LoopRun |
| LoopRun continuation | explicit active LoopRun | evaluate its accepted contract; bounded continuation may block Stop |

Kanboard autosync and post-session reflection are disabled unless their own `dry-run` or `apply` environment mode is explicitly set.

## Runtime State

Live run output is stored under `.codex/harness/agent-runs/<session>/<turn>/` and excluded from release evidence. Synthetic fixtures live under `.codex/tools/tests/fixtures/agent-runs/`.

When no agent-run manifest and no `SKILL_SYSTEM_HOOK_LEDGER` exact-file override are present, observational events are stored under `${CODEX_HOME:-~/.codex}/harness/hook-ledgers/<run-key>/hook-events.jsonl`. `<run-key>` is a stable SHA-256 key, so the raw run/session ID is not exposed in the path. Each fallback file contains one `run_id` and can be checked with the existing single-run verifier. The former global temp path is no longer selected implicitly; existing files there are not migrated automatically.

Recovery Guard state is session-scoped under `${CODEX_HOME:-~/.codex}/harness/recovery-guard/sessions/<session-hash>.json`. It stores counters, booleans, signal codes, and event hashes only; raw prompts, assistant messages, commands, and session IDs are not persisted. State updates use a lock and atomic replacement. `SessionEnd`/TTL garbage collection is not implemented yet, so old files require periodic operator cleanup.

The guard becomes armed after any one of these context-pressure observations: `PostCompact`, six user turns, twenty unique tool preflights, or two correction episodes. Arming alone never intervenes. A Stop audit requires all of: an armed session, a pending explicit correction, an apology/agreement opener coupled to an operational promise, and no explicit changed-file or validation progress receipt since the correction. A successful progress receipt, a concrete direct conclusion, or another substantive response resolves the pending correction. An explicit user instruction to stop, including the supported Korean and English stop forms, cancels the pending episode before Stop evaluation.

The default `observe` mode records the decision out of band. `audit` mode injects one compact `recovery_audit` request per episode, capped at three actual blocks per session, records both the blocked Stop and the following handoff as `turn_finalize_attempt`, and marks the reducer `awaiting_user`; the next user prompt cancels that pending handoff. Only a host-marked continuation (`stop_hook_active=true`) can consume the requested audit packet. An inactive near-duplicate Stop preserves and replays the audit request instead of becoming a handoff. The audit path does not finalize the agent-run report, notify completion, or synchronize Kanboard. An active explicit LoopRun suppresses the soft recovery block. Recovery Guard does not inspect unstable transcript formats or deny tool calls in this first release.

One Stop call records one lifecycle outcome:

- `turn_finalize` only for a validated terminal observation;
- `turn_finalize_attempt` for failed, skipped, unverified, strict-blocked, Recovery Guard audit/handoff, or LoopRun-continuation attempts.

An assistant report may declare claims, but it cannot serve as its own `agent-verified` evidence. Schema-v2 `command_exit` evidence must match the recorded `PreToolUse`/`PostToolUse` command hash and exit code.

## Commands

```bash
python3 .codex/tools/hook_runtime.py status
python3 .codex/tools/hook_runtime.py show --ledger <hook-events.jsonl>
python3 .codex/tools/hook_runtime.py verify --ledger <hook-events.jsonl>
python3 .codex/tools/validate_agent_run_artifact.py <run-dir>
python3 .codex/tools/verify_bundle.py --profile agent-output --format text
python3 .codex/tools/compare_harness_versions.py --samples 1
```

The monitor is a small declared-subject receipt monitor, not a semantic evaluator, task-label authority, or test generator. Before `UserPromptSubmit`, the host may supply `SKILL_SYSTEM_VERIFIER_CONTRACT` with `contract_id`, one `verifier_command_hash`, `verifier_origin`, and workspace-relative `subject_refs`. Legacy oracle and negative-control fields are accepted but ignored. `PostToolUse` records matching verifier receipts. At `Stop`, the monitor reports `current_for_declared_subjects`, `missing`, `failed`, `stale`, `supporting_only`, `untrusted_origin`, `unavailable`, or `integrity_error`; it re-hashes only the declared subject files, bounded to 16 MiB total. Read-only or unrelated later tool use does not stale the receipt; a declared subject change does.

Receipt status is additive ledger metadata. It does not read the assistant result label, produce a validation code, feed LoopRun, choose Stop output, block or reissue a response, suppress Agent Run bootstrap/finalization, or change independently enabled Kanboard and notification behavior. An internal monitor observation error is caught at the adapter boundary and recorded as `unavailable`; it cannot abort those ordinary paths. The monitor itself starts no verifier or subprocess. Ordinary Agent Run/output validation and external side effects keep their own enablement, so the total Stop subprocess count is not a monitor contract and latency comparison is advisory. Missing or failed receipts do not imply a user-only check; an agent-authored or agent-modified verifier remains `supporting_only`. Plans should retain the selected verifier and latest decisive result only, not raw logs, receipts, retry history, or repeated passes.

Harness changes use the bundle version and release tag. Earlier 9.2.1 comparison artifacts that describe result-label authorization remain historical diagnostics, not a separately versioned current protocol.

`status` reports `agent_output_gate_mode` and `recovery_guard_mode` independently. A strict output gate and Recovery Guard audit/off state are separate controls and must not be collapsed into one observational/active label.

Use the first failed invariant as the repair scope. Do not widen a hook or harness failure into plan synchronization, release validation, memory mutation, or repository-wide repair.
