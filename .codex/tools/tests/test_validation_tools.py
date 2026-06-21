from __future__ import annotations

import subprocess
import sys
import unittest
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / ".codex" / "tools" / "tests" / "fixtures"


class ValidationToolTests(unittest.TestCase):
    def run_tool(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=30,
        )

    def assert_passes(self, *args: str) -> None:
        result = self.run_tool(*args)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def assert_fails(self, *args: str) -> None:
        result = self.run_tool(*args)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_eval_valid_fixture_passes(self) -> None:
        self.assert_passes(
            ".codex/tools/validate_eval_cases.py",
            str(FIXTURES / "eval-valid.yaml"),
            "--schema",
            ".codex/eval/eval-case.schema.json",
        )

    def test_eval_invalid_fixture_fails(self) -> None:
        self.assert_fails(
            ".codex/tools/validate_eval_cases.py",
            str(FIXTURES / "eval-invalid.yaml"),
            "--schema",
            ".codex/eval/eval-case.schema.json",
        )

    def test_field_feedback_valid_fixture_passes(self) -> None:
        self.assert_passes(
            ".codex/tools/validate_field_feedback.py",
            str(FIXTURES / "field-feedback-valid.yaml"),
            "--schema",
            ".codex/field-feedback/field-feedback.schema.json",
        )

    def test_field_feedback_invalid_fixture_fails(self) -> None:
        self.assert_fails(
            ".codex/tools/validate_field_feedback.py",
            str(FIXTURES / "field-feedback-invalid.yaml"),
            "--schema",
            ".codex/field-feedback/field-feedback.schema.json",
        )

    def test_source_registry_valid_fixture_passes(self) -> None:
        self.assert_passes(".codex/tools/validate_source_registry.py", str(FIXTURES / "source-registry-valid.yaml"))

    def test_source_registry_invalid_fixture_fails(self) -> None:
        self.assert_fails(".codex/tools/validate_source_registry.py", str(FIXTURES / "source-registry-invalid.yaml"))

    def test_behavior_invalid_fixture_fails(self) -> None:
        self.assert_fails(
            ".codex/tools/run_behavior_evals.py",
            "--mode",
            "replay",
            "--eval-path",
            str(FIXTURES / "eval-valid.yaml"),
            "--observed-runs",
            str(FIXTURES / "observed-runs"),
        )

    def test_research_ledger_passes(self) -> None:
        self.assert_passes(
            ".codex/tools/validate_research_ledger.py",
            ".codex/research/ledger.yaml",
            "--schema",
            ".codex/research/research-ledger.schema.json",
        )

    def test_hook_runtime_records_event(self) -> None:
        ledger = Path("/private/tmp/skill-system-test-hook-events.jsonl")
        if ledger.exists():
            ledger.unlink()
        self.assert_passes(
            ".codex/tools/hook_runtime.py",
            "record",
            "--event",
            "tool_preflight",
            "--host",
            "codex",
            "--host-event",
            "PreToolUse",
            "--support-level",
            "native",
            "--tool-id",
            "functions.exec_command",
            "--evidence",
            "{}",
            "--ledger",
            str(ledger),
        )
        self.assertTrue(ledger.exists())
        ledger.unlink()

    def test_agent_run_artifact_fixture_passes(self) -> None:
        self.assert_passes(
            ".codex/tools/validate_agent_run_artifact.py",
            str(FIXTURES / "agent-runs" / "current-run"),
            "--schema",
            ".codex/schemas/harness/agent-run.schema.json",
        )

    def test_agent_run_artifact_invalid_fixture_fails(self) -> None:
        self.assert_fails(
            ".codex/tools/validate_agent_run_artifact.py",
            str(FIXTURES / "agent-runs" / "invalid-claim-mismatch"),
            "--schema",
            ".codex/schemas/harness/agent-run.schema.json",
        )

    def test_agent_run_artifact_repeated_tool_pairs_pass(self) -> None:
        self.assert_passes(
            ".codex/tools/validate_agent_run_artifact.py",
            str(FIXTURES / "agent-runs" / "repeated-tools"),
            "--schema",
            ".codex/schemas/harness/agent-run.schema.json",
        )

    def test_agent_run_artifact_permission_without_tool_id_passes(self) -> None:
        self.assert_passes(
            ".codex/tools/validate_agent_run_artifact.py",
            str(FIXTURES / "agent-runs" / "permission-no-tool-id"),
            "--schema",
            ".codex/schemas/harness/agent-run.schema.json",
        )

    def test_agent_run_artifact_failed_stop_attempt_is_recoverable(self) -> None:
        self.assert_passes(
            ".codex/tools/validate_agent_run_artifact.py",
            str(FIXTURES / "agent-runs" / "stop-recovery"),
            "--schema",
            ".codex/schemas/harness/agent-run.schema.json",
        )

    def test_agent_run_artifact_unfinished_tool_fails(self) -> None:
        self.assert_fails(
            ".codex/tools/validate_agent_run_artifact.py",
            str(FIXTURES / "agent-runs" / "unfinished-tool"),
            "--schema",
            ".codex/schemas/harness/agent-run.schema.json",
        )

    def test_codex_hook_adapter_records_pretooluse(self) -> None:
        ledger = Path("/private/tmp/skill-system-test-live-hook-pretooluse.jsonl")
        if ledger.exists():
            ledger.unlink()
        self.assert_passes(
            ".codex/hooks/codex_hook_adapter.py",
            "--input-file",
            str(FIXTURES / "hooks" / "pretooluse.json"),
            "--ledger",
            str(ledger),
        )
        self.assertTrue(ledger.exists())
        event = json.loads(ledger.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(event["neutral_event"], "tool_preflight")
        self.assertEqual(event["host_event"], "PreToolUse")
        self.assertEqual(event["status"], "pass")
        ledger.unlink()

    def test_codex_hook_adapter_marks_failed_posttooluse(self) -> None:
        ledger = Path("/private/tmp/skill-system-test-live-hook-posttooluse-fail.jsonl")
        if ledger.exists():
            ledger.unlink()
        self.assert_passes(
            ".codex/hooks/codex_hook_adapter.py",
            "--input-file",
            str(FIXTURES / "hooks" / "posttooluse-fail.json"),
            "--ledger",
            str(ledger),
        )
        event = json.loads(ledger.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(event["neutral_event"], "tool_result")
        self.assertEqual(event["status"], "fail")
        self.assertEqual(event["evidence"]["tool_result"]["exit_code"], 1)
        ledger.unlink()

    def test_codex_hook_adapter_marks_string_failed_posttooluse(self) -> None:
        ledger = Path("/private/tmp/skill-system-test-live-hook-posttooluse-string-fail.jsonl")
        if ledger.exists():
            ledger.unlink()
        self.assert_passes(
            ".codex/hooks/codex_hook_adapter.py",
            "--input-file",
            str(FIXTURES / "hooks" / "posttooluse-string-fail.json"),
            "--ledger",
            str(ledger),
        )
        event = json.loads(ledger.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(event["status"], "fail")
        self.assertEqual(event["evidence"]["tool_result"]["exit_code"], 1)
        ledger.unlink()

    def test_codex_hook_adapter_marks_unknown_posttooluse_warn(self) -> None:
        ledger = Path("/private/tmp/skill-system-test-live-hook-posttooluse-string-unknown.jsonl")
        if ledger.exists():
            ledger.unlink()
        self.assert_passes(
            ".codex/hooks/codex_hook_adapter.py",
            "--input-file",
            str(FIXTURES / "hooks" / "posttooluse-string-unknown.json"),
            "--ledger",
            str(ledger),
        )
        event = json.loads(ledger.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(event["status"], "warn")
        self.assertNotIn("exit_code", event["evidence"]["tool_result"])
        ledger.unlink()

    def test_codex_hook_adapter_redacts_sensitive_tool_input(self) -> None:
        ledger = Path("/private/tmp/skill-system-test-live-hook-secret.jsonl")
        if ledger.exists():
            ledger.unlink()
        self.assert_passes(
            ".codex/hooks/codex_hook_adapter.py",
            "--input-file",
            str(FIXTURES / "hooks" / "pretooluse-redaction.json"),
            "--ledger",
            str(ledger),
        )
        raw = ledger.read_text(encoding="utf-8")
        self.assertNotIn("sk-secretsecretsecretsecret", raw)
        self.assertNotIn("Authorization", raw)
        event = json.loads(raw.splitlines()[0])
        self.assertEqual(event["evidence"]["command_category"], "curl")
        self.assertIn("command_hash", event["evidence"])
        ledger.unlink()

    def test_codex_hook_adapter_redacts_sensitive_tool_response_fields(self) -> None:
        ledger = Path("/private/tmp/skill-system-test-live-hook-response-redaction.jsonl")
        if ledger.exists():
            ledger.unlink()
        self.assert_passes(
            ".codex/hooks/codex_hook_adapter.py",
            "--input-file",
            str(FIXTURES / "hooks" / "posttooluse-redaction.json"),
            "--ledger",
            str(ledger),
        )
        raw = ledger.read_text(encoding="utf-8")
        self.assertNotIn("/Users/alice/private/token-secret.txt", raw)
        self.assertNotIn("api_key=sk-secretsecretsecretsecret", raw)
        event = json.loads(raw.splitlines()[0])
        result = event["evidence"]["tool_result"]
        self.assertIn("<external-path>", result["changed_files"])
        self.assertIn("https://example.com/?<redacted-query>", result["network_targets"])
        ledger.unlink()

    def test_codex_hook_adapter_stop_runs_agent_output_validation(self) -> None:
        ledger = Path("/private/tmp/skill-system-test-live-hook-stop.jsonl")
        if ledger.exists():
            ledger.unlink()
        result = self.run_tool(
            ".codex/hooks/codex_hook_adapter.py",
            "--input-file",
            str(FIXTURES / "hooks" / "stop.json"),
            "--run-dir",
            str(FIXTURES / "agent-runs" / "current-run"),
            "--ledger",
            str(ledger),
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        output = json.loads(result.stdout)
        self.assertTrue(output["continue"])
        event = json.loads(ledger.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(event["neutral_event"], "turn_finalize")
        self.assertEqual(event["status"], "pass")
        ledger.unlink()

    def test_codex_hook_adapter_stop_message_mismatch_blocks_recoverably(self) -> None:
        ledger = Path("/private/tmp/skill-system-test-live-hook-stop-message-mismatch.jsonl")
        if ledger.exists():
            ledger.unlink()
        result = self.run_tool(
            ".codex/hooks/codex_hook_adapter.py",
            "--input-file",
            str(FIXTURES / "hooks" / "stop-message-mismatch.json"),
            "--run-dir",
            str(FIXTURES / "agent-runs" / "current-run"),
            "--ledger",
            str(ledger),
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["decision"], "block")
        self.assertNotIn("continue", output)
        event = json.loads(ledger.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(event["neutral_event"], "turn_finalize_attempt")
        self.assertEqual(event["status"], "fail")
        ledger.unlink()

    def test_codex_hook_adapter_stop_missing_current_run_is_unverified(self) -> None:
        ledger = Path("/private/tmp/skill-system-test-live-hook-stop-missing.jsonl")
        if ledger.exists():
            ledger.unlink()
        result = self.run_tool(
            ".codex/hooks/codex_hook_adapter.py",
            "--input-file",
            str(FIXTURES / "hooks" / "stop-missing-run.json"),
            "--ledger",
            str(ledger),
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        output = json.loads(result.stdout)
        self.assertTrue(output["continue"])
        self.assertIn("UNVERIFIED", output["systemMessage"])
        event = json.loads(ledger.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(event["neutral_event"], "turn_finalize_attempt")
        self.assertEqual(event["status"], "warn")
        self.assertIn("UNVERIFIED", event["evidence"]["agent_output_validation"])
        ledger.unlink()


if __name__ == "__main__":
    unittest.main()
