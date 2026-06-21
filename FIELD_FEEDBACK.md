# Field Feedback

Generated human-readable view. Machine-readable source lives in `.codex/field-feedback/*.yaml`.

## Status

- measured_entries: 2
- field_evidence_status: measured
- release_gate: user-accepted

## FF-20260620-001

- date: 2026-06-20
- bundle_version: 7.3.1
- host: codex
- request_class: live-hook-runtime-activation
- expected_primary_skill: workflow-minimal-implementation
- actual_primary_skill: workflow-minimal-implementation
- outcome: pass
- friction: TERM=dumb required confirmation in nested Codex TUI; no hook trust regression after re-launch.
- artifact_refs: .codex/hooks.json, .codex/hooks/codex_hook_adapter.py, .codex/tools/validate_agent_run_artifact.py, .codex/tools/tests/test_validation_tools.py, .codex/docs/agent_output_validation.md
- validation_evidence: Codex interactive launch reported: 4 hooks are new or changed., Selected Trust all and continue; Codex displayed Trusting hooks... and entered the main screen., Second Codex interactive launch entered the main screen without showing the hook review prompt., codex features list reported hooks stable true., python3 .codex/tools/run_verification_pipeline.py --profiles core execution agent-output research --release: PASS, python3 .codex/tools/verify_bundle.py --profile execution --format text: PASS, python3 .codex/tools/verify_bundle.py --profile agent-output --format text: PASS

## FF-20260621-001

- date: 2026-06-21
- bundle_version: 7.3.1
- host: codex
- request_class: agent-output-validation-hardening
- expected_primary_skill: workflow-minimal-implementation
- actual_primary_skill: workflow-minimal-implementation
- outcome: pass
- friction: Release integration proof requires a local pytest dependency path when pytest is not globally installed.
- artifact_refs: .codex/hooks/codex_hook_adapter.py, .codex/tools/validate_agent_run_artifact.py, .codex/tools/verify_bundle.py, .codex/tools/tests/test_validation_tools.py, .codex/tools/tests/fixtures/agent-runs/repeated-tools/run.yaml, .codex/tools/tests/fixtures/agent-runs/current-run/run.yaml, docs/plan/2026-06-20-7.2.6-field-evidence-and-harness-hardening.md
- validation_evidence: PYTHONPATH=/private/tmp/skill-system-python-deps python3 .codex/tools/run_verification_pipeline.py --release: PASS for core, execution, agent-output, research, integrations., python3 -c ast.parse over .codex/tools and .codex/hooks Python files: parsed 18 files., python3 -m json.tool .codex/tools/tests/fixtures/hooks/pretooluse-redaction.json: PASS., Stop validation now binds to current session_id/turn_id and reports UNVERIFIED instead of passing missing current run evidence., Per-tool lifecycle validation accepts repeated PreToolUse/PostToolUse pairs by tool_use_id., Failed PostToolUse is recorded as fail and hook evidence defaults to metadata/hash/redaction.

## Guidance

- Record observed behavior, not guesses.
- Prefer one request per entry.
- Mark uncertain conclusions as `user-verification-needed` or keep the entry out of release evidence.
- Do not paste secrets, credentials, session data, private chat logs, or unrelated project content.

## Examples

Examples are intentionally kept out of this generated view so they cannot be mistaken for measured field results.
