from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HOOK = ROOT / ".codex" / "hooks" / "codex_hook_adapter.py"
sys.dont_write_bytecode = True


class Harness921ReferenceMonitorTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(dir="/private/tmp")
        self.work = Path(self._tmp.name)
        self.ledger = self.work / "hook-events.jsonl"
        (self.work / "subject.txt").write_text("production state\n", encoding="utf-8")
        self.env = dict(os.environ)
        self.env.update({
            "PYTHONDONTWRITEBYTECODE": "1",
            "SKILL_SYSTEM_HARNESS_VERSION": "9.2.1",
            "SKILL_SYSTEM_RECOVERY_GUARD": "off",
            "SKILL_SYSTEM_DESKTOP_NOTIFY": "dry-run",
        })
        self.env.pop("SKILL_SYSTEM_VERIFIER_CONTRACT", None)
        self.event_index = 0

    def tearDown(self) -> None:
        self._tmp.cleanup()

    @staticmethod
    def digest(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def configure_contract(
        self,
        positive_command: str,
        *,
        verifier_origin: str = "repository",
    ) -> None:
        contract = {
            "contract_id": "VC-TEST-001",
            "verifier_command_hash": self.digest(positive_command),
            "verifier_origin": verifier_origin,
            "subject_refs": ["subject.txt"],
        }
        self.env["SKILL_SYSTEM_VERIFIER_CONTRACT"] = json.dumps(contract, sort_keys=True)

    def event(self, hook_event_name: str, **extra: object) -> dict[str, object]:
        self.event_index += 1
        input_path = self.work / f"event-{self.event_index}.json"
        input_path.write_text(json.dumps({
            "hook_event_name": hook_event_name,
            "session_id": "session-92",
            "turn_id": "turn-92",
            "cwd": str(self.work),
            "permission_mode": "workspace-write",
            **extra,
        }), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(HOOK), "--input-file", str(input_path), "--ledger", str(self.ledger)],
            cwd=ROOT,
            env=self.env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads(result.stdout) if result.stdout.strip() else {}

    def tool(self, command: str, exit_code: int, tool_use_id: str) -> None:
        fields = {
            "tool_name": "Bash",
            "tool_use_id": tool_use_id,
            "tool_input": {"command": command},
        }
        self.event("PreToolUse", **fields)
        self.event(
            "PostToolUse",
            **fields,
            tool_response={"exit_code": exit_code, "stdout": "PASS" if exit_code == 0 else "FAIL"},
        )

    def stop(self, label: str = "agent-verified", **extra: object) -> dict[str, object]:
        return self.event(
            "Stop",
            skill_system_agent_output_gate="strict",
            last_assistant_message=f"result_label: {label}\n",
            **extra,
        )

    def last_authority(self) -> dict[str, object]:
        last = json.loads(self.ledger.read_text(encoding="utf-8").splitlines()[-1])
        return last["evidence"]["verification_authority"]

    def test_trusted_fresh_verifier_authorizes_agent_verified(self) -> None:
        command = "verify production subject"
        self.configure_contract(command)
        self.event("UserPromptSubmit", prompt="verify the production subject")
        self.tool(command, 0, "tool-positive")

        output = self.stop()

        self.assertTrue(output["continue"])
        self.assertEqual(self.last_authority()["authorization"], "granted")
        self.assertEqual(self.last_authority()["canonical_result_label"], "agent-verified")
        last = json.loads(self.ledger.read_text(encoding="utf-8").splitlines()[-1])
        self.assertNotIn("desktop_notifications", last["evidence"])

    def test_missing_contract_downgrades_label_without_rejecting_response(self) -> None:
        self.event("UserPromptSubmit", prompt="no trusted verifier is available")

        first = self.stop("agent-verified")
        second = self.stop("user-verification-needed")

        self.assertEqual(first["decision"], "block")
        self.assertIn("Re-emit the same scoped answer", first["reason"])
        self.assertIn("Do not run tools", first["reason"])
        self.assertTrue(second["continue"])
        self.assertEqual(self.last_authority()["reason_code"], "missing_prebound_contract")

    def test_agent_modified_verifier_downgrades_without_requesting_more_tests(self) -> None:
        positive = "run agent modified tests"
        self.configure_contract(positive, verifier_origin="agent_modified")
        self.event("UserPromptSubmit", prompt="verify an agent-modified test")
        self.tool(positive, 0, "tool-positive")

        denied = self.stop()

        self.assertEqual(denied["decision"], "block")
        self.assertEqual(
            self.last_authority()["reason_code"],
            "agent_modified_verifier_is_supporting_evidence",
        )
        self.assertIn("Do not run tools", denied["reason"])

    def test_unrelated_tool_use_after_verifier_keeps_receipt_current(self) -> None:
        command = "verify production subject"
        self.configure_contract(command)
        self.event("UserPromptSubmit", prompt="verify then inspect")
        self.tool(command, 0, "tool-positive")
        self.tool("inspect after verification", 0, "tool-after")

        output = self.stop()

        self.assertTrue(output["continue"])
        self.assertEqual(self.last_authority()["authorization"], "granted")

    def test_subject_change_after_verifier_downgrades_receipt(self) -> None:
        command = "verify production subject"
        self.configure_contract(command)
        self.event("UserPromptSubmit", prompt="verify then change the production subject")
        self.tool(command, 0, "tool-positive")
        (self.work / "subject.txt").write_text("changed production state\n", encoding="utf-8")

        output = self.stop()

        self.assertEqual(output["decision"], "block")
        self.assertEqual(self.last_authority()["reason_code"], "subject_changed_after_verifier")

    def test_receipt_from_another_run_cannot_authorize_current_stop(self) -> None:
        command = "verify production subject"
        self.configure_contract(command)
        self.event("UserPromptSubmit", prompt="verify in the original run")
        self.tool(command, 0, "tool-positive")

        output = self.stop(session_id="session-other")

        self.assertEqual(output["decision"], "block")
        self.assertEqual(self.last_authority()["reason_code"], "contract_run_mismatch")

    def test_failed_verifier_downgrades_label(self) -> None:
        command = "verify production subject"
        self.configure_contract(command)
        self.event("UserPromptSubmit", prompt="observe a verifier failure")
        self.tool(command, 1, "tool-positive")

        output = self.stop()

        self.assertEqual(output["decision"], "block")
        self.assertEqual(self.last_authority()["reason_code"], "verifier_failed_or_subject_unbound")

    def test_tampered_ledger_denies_success_authority(self) -> None:
        command = "verify production subject"
        self.configure_contract(command)
        self.event("UserPromptSubmit", prompt="verify ledger integrity")
        self.tool(command, 0, "tool-positive")
        events = [json.loads(line) for line in self.ledger.read_text(encoding="utf-8").splitlines()]
        events[-1]["evidence"]["verifier_receipt"]["exit_code"] = 9
        self.ledger.write_text("".join(json.dumps(event, sort_keys=True) + "\n" for event in events), encoding="utf-8")

        output = self.stop()

        self.assertEqual(output["decision"], "block")
        self.assertEqual(self.last_authority()["authorization"], "integrity_error")


if __name__ == "__main__":
    unittest.main()
