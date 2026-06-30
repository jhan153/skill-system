# Agent Output Validation

## Purpose
Agent output validation checks artifacts produced by a real Codex agent run. It is not a replacement for source-repo validation or unit tests. Its job is to verify that the final report, explicit claims, command evidence, and hook event trail agree with each other.

Use this layer when an agent run claims `agent-verified`, `user-verification-needed`, `unverified`, or `blocked` in the final task result.

## Artifact Layout
Synthetic examples live under `.codex/tools/tests/fixtures/agent-runs/`.
Live Codex hooks bind evidence to the current session and turn only when that run directory already has a `run.yaml` manifest:

```text
.codex/harness/agent-runs/<session-id>/<turn-id>/
  run.yaml
  context/
    context-pack.yaml
  final-report.md
  hook-events.jsonl
  artifacts/
    verification.txt
```

`run.yaml` is the canonical manifest. It must reference files relative to the run directory.

```yaml
schema_version: 2
run_id: AR-20260620-001
bundle_version: "8.0.2"
task:
  user_request_summary: "Validate execution-loop outputs."
  result_label: agent-verified
context:
  context_pack_ref: context/context-pack.yaml
  context_pack_hash: "<sha256-of-context-pack>"
  admitted_claim_ids:
    - KC-20260621-001
  source_snapshot_refs:
    - SRC-20260621-001
assistant_message:
  sha256: "<sha256-of-last-assistant-message>"
  result_label: agent-verified
  claim_ids:
    - C-001
outputs:
  final_report: final-report.md
  artifact_refs:
    - artifacts/verification.txt
  claims:
    - claim_id: C-001
      text: "core, execution, and research verification profiles passed"
      claim_class: execution_result
      support:
        type: command_exit
        command: "python3 .codex/tools/run_verification_pipeline.py --profiles core execution research --release"
        exit_code: 0
        evidence_ref: artifacts/verification.txt
      context_support:
        claim_ids:
          - KC-20260621-001
        relation_path_ids: []
      source_support:
        source_refs:
          - SRC-20260621-001
validations:
  - type: command_exit
    command: "python3 .codex/tools/run_verification_pipeline.py --profiles core execution research --release"
    exit_code: 0
    evidence_ref: artifacts/verification.txt
hook_events: hook-events.jsonl
```

## Validation Rules
- `final_report` must exist and mention the task `result_label`.
- Every claim must have a stable `claim_id`, and the final report must mention that id.
- Command-backed claims must point to evidence that contains the command and a matching pass/fail marker.
- Command-backed claims must match a record in `validations`.
- Schema v2 runs must include a run-local immutable `context/context-pack.yaml` reference and a matching SHA-256 hash.
- `context_support.claim_ids` must reference claim IDs admitted by the run's context pack record.
- `source_support.source_refs` must reference source snapshots recorded by the run context.
- `assistant_message.sha256` must match the actual `Stop.last_assistant_message`; the message must mention the declared result label and claim IDs.
- Hook events must be JSONL objects with valid timestamps, valid enum values, matching event hashes, and a per-`tool_use_id` lifecycle state.
- Lifecycle event schema v2 records must include `run_id`, monotonic `seq`, `prev_event_hash`, and `event_hash`.
- Schema v2 hook ledgers must include `request_received`, `context_loaded`, and a passing `turn_finalize`.
- `PermissionRequest` may be turn-scoped in Codex. When it has no `tool_use_id`, it must use `support_level: approximate`.
- Repeated tool calls are valid when each `tool_preflight` has a matching `tool_result` before a passing `turn_finalize`.
- Failed or unverified `Stop` records are `turn_finalize_attempt`, not terminal `turn_finalize`, so later repair work remains valid.
- The end of the hook ledger must not contain unfinished tool calls.
- `agent-verified` cannot contain nonzero command validations or failed hook events except recoverable `turn_finalize_attempt` records.

## Commands
Validate recorded agent runs:

```bash
python3 .codex/tools/validate_agent_run_artifact.py .codex/tools/tests/fixtures/agent-runs/current-run --schema .codex/schemas/harness/agent-run.schema.json
```

Run the verification profile:

```bash
python3 .codex/tools/verify_bundle.py --profile agent-output --format text
```

Run the release pipeline with agent output validation:

```bash
python3 .codex/tools/run_verification_pipeline.py --profiles core execution agent-output research --release
```

## Live Codex Hook Wiring
`.codex/hooks.json` wires `UserPromptSubmit`, `SessionStart`, `PreToolUse`, `PermissionRequest`, `PostToolUse`, `Stop`, `PreCompact`, and `PostCompact` to `.codex/hooks/codex_hook_adapter.py`.

The adapter records hook events to `SKILL_SYSTEM_HOOK_LEDGER` when that environment variable is set. Otherwise, when Codex provides `session_id` and `turn_id` and the current run manifest already exists, it writes to `.codex/harness/agent-runs/<session-id>/<turn-id>/hook-events.jsonl`. If the manifest is missing, it falls back to `hook_runtime.py`'s temp ledger path so release packages do not accumulate orphan runtime traces.

New live records are schema v2 hash-chain records. Existing schema v1 fixtures remain readable for compatibility, but new v2 run fixtures are expected to prove request receipt, context load, tool lifecycle, and finalization.

`Stop` validates only the current session/turn run directory. It does not treat static sample runs as evidence for the current turn, and it does not run source-repo validation, behavior evals, release profiles, plan synchronization, or repository-wide repair.

- current run exists and is valid: `pass`
- current run exists and is invalid: `turn_finalize_attempt` plus non-blocking continuation by default
- current run is missing: `turn_finalize_attempt` with `UNVERIFIED`/`warn`, not pass

## Loop Governance Packets

Loop-specific success is not implied by a passing generic `Stop` hook. For accepted loop contracts, `workflow-loop-runner` should emit a `loop_stop_packet` artifact that records final success-condition status, verifier evidence, retry/no-progress state, non-idempotent retry handling, reward-hacking signals, context-poisoning signals, and comprehension-debt review status.

Current hook behavior:
- `Stop` can bind final agent-run evidence to the current session/turn.
- `Stop` evaluates bounded LoopRun progress only when `SKILL_SYSTEM_LOOP_RUN_DIR` or `skill_system_loop_run_dir` points at an active LoopRun state directory.
- `Stop` still does not infer event-runtime support, Wiki feedback promotion, over-orchestration, or arbitrary loop success from hook presence alone.
- If no active LoopRun state was inspected, report `stop_hook_loop_evaluation: unverified`.

Do not claim hook-level loop success from hook presence alone.

Set `SKILL_SYSTEM_AGENT_OUTPUT_GATE=strict` only when the caller wants narrow blocking for current-turn evidence contradictions, such as an `agent-verified` claim backed by a failed command, missing evidence for a reported claim, or an assistant-message hash mismatch. Missing optional evidence, stale unrelated fixtures, old plan text, or release-profile failures remain observations unless an explicit release/audit command is running.

By default, hook evidence is metadata-only. Commands and large tool inputs are recorded as categories and hashes; raw previews require `SKILL_SYSTEM_HOOK_CAPTURE_VERBOSE=1` and still pass through redaction.

Codex still requires project trust and hook trust before these project-local hooks run. Use `/hooks` in Codex to review and trust the current hook definitions.

## RC2 Freeze and 8.0 Policy

The `7.3.1` RC2 hook behavior is frozen as the compatibility baseline. Known live-hook limits are documented rather than expanded into a broader Stop-hook project: hooks only run after project trust, missing current-run manifests are `UNVERIFIED`/`warn`, and permission events may be approximate when Codex does not provide a `tool_use_id`.

The 8.0 branch policy is to preserve the external compatibility interface while moving the internal operating layer to `8.0.0 — Context Compounding / Wiki Bank Architecture`. Run Trace Integrity remains the execution evidence gate that supports the 8.0 Knowledge Store and Context Pack layers.
