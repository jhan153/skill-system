# Agent Output Validation

## Purpose
Agent output validation checks artifacts produced by a real Codex agent run. It is not a replacement for bundle hygiene or unit tests. Its job is to verify that the final report, explicit claims, command evidence, and hook event trail agree with each other.

Use this layer when an agent run claims `agent-verified`, `user-verification-needed`, `unverified`, or `blocked` in the final task result.

## Artifact Layout
Synthetic examples live under `.codex/tools/tests/fixtures/agent-runs/`.
Live Codex hooks bind evidence to the current session and turn only when that run directory already has a `run.yaml` manifest:

```text
.codex/harness/agent-runs/<session-id>/<turn-id>/
  run.yaml
  final-report.md
  hook-events.jsonl
  artifacts/
    verification.txt
```

`run.yaml` is the canonical manifest. It must reference files relative to the run directory.

```yaml
schema_version: 1
run_id: AR-20260620-001
bundle_version: "7.3.1"
task:
  user_request_summary: "Validate execution-loop outputs."
  result_label: agent-verified
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
      support:
        type: command_exit
        command: "python3 .codex/tools/run_verification_pipeline.py --profiles core execution research --release"
        exit_code: 0
        evidence_ref: artifacts/verification.txt
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
- `assistant_message.sha256` must match the actual `Stop.last_assistant_message`; the message must mention the declared result label and claim IDs.
- Hook events must be JSONL objects with valid timestamps, valid enum values, matching event hashes, and a per-`tool_use_id` lifecycle state.
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
`.codex/hooks.json` wires `PreToolUse`, `PermissionRequest`, `PostToolUse`, and `Stop` to `.codex/hooks/codex_hook_adapter.py`.

The adapter records hook events to `SKILL_SYSTEM_HOOK_LEDGER` when that environment variable is set. Otherwise, when Codex provides `session_id` and `turn_id` and the current run manifest already exists, it writes to `.codex/harness/agent-runs/<session-id>/<turn-id>/hook-events.jsonl`. If the manifest is missing, it falls back to `hook_runtime.py`'s temp ledger path so release packages do not accumulate orphan runtime traces.

`Stop` validates only the current session/turn run directory. It does not treat static sample runs as evidence for the current turn.

- current run exists and is valid: `pass`
- current run exists and is invalid: `turn_finalize_attempt` plus continuation/block response
- current run is missing: `turn_finalize_attempt` with `UNVERIFIED`/`warn`, not pass

Set `SKILL_SYSTEM_AGENT_OUTPUT_GATE=strict` to turn missing current-run evidence into a blocking completion gate.

By default, hook evidence is metadata-only. Commands and large tool inputs are recorded as categories and hashes; raw previews require `SKILL_SYSTEM_HOOK_CAPTURE_VERBOSE=1` and still pass through redaction.

Codex still requires project trust and hook trust before these project-local hooks run. Use `/hooks` in Codex to review and trust the current hook definitions.
