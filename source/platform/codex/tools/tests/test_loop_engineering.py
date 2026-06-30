#!/usr/bin/env python3
"""Loop-engineering invariants added in the 8.2 bounded-loop hardening.

Covers: activation bridge (session pointer), monotonic iteration, terminal
immutability, idempotent replay, iterations/ audit records, and explicit resume.
Run: python3 .codex/tools/tests/test_loop_engineering.py
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / ".codex" / "tools"
FIXTURE = TOOLS / "tests" / "fixtures" / "loop-runs" / "valid"


def run(tool: str, *args: str, **kw) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TOOLS / tool), *args],
        cwd=str(TOOLS),
        text=True,
        capture_output=True,
        check=False,
        **kw,
    )


def write_result(path: Path, iteration: int, rid: str, status: str, evidence=(), side_effects=()) -> None:
    path.write_text(
        yaml.safe_dump(
            {
                "schema_version": 1,
                "loop_run_id": "LR-20260623-010",
                "iteration": iteration,
                "iteration_result_id": rid,
                "condition_results": [
                    {"condition_id": "SC-001", "status": status, "evidence_refs": list(evidence)}
                ],
                "side_effects": list(side_effects),
            }
        ),
        encoding="utf-8",
    )


class LoopEngineeringTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(__import__("tempfile").mkdtemp(dir="/private/tmp"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.loop = self.tmp / "loop"
        shutil.copytree(FIXTURE, self.loop)
        self.ir = self.tmp / "ir.yaml"

    def evaluate(self) -> subprocess.CompletedProcess[str]:
        return run("evaluate_loop_run.py", str(self.loop), "--iteration-result", str(self.ir), "--format", "json")

    def state(self) -> dict:
        return yaml.safe_load((self.loop / "state.yaml").read_text(encoding="utf-8"))

    # --- P2: monotonic sequencing -------------------------------------------
    def test_monotonic_rejects_iteration_skip(self) -> None:
        write_result(self.ir, 2, "IR-skip", "fail")  # state is at iteration 0; expected 1
        result = self.evaluate()
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertIn("sequence conflict", result.stdout)
        self.assertEqual(self.state()["iteration"], 0)

    # --- P2: terminal immutability ------------------------------------------
    def test_terminal_loop_rejects_new_result(self) -> None:
        write_result(self.ir, 1, "IR-pass", "pass", evidence=["artifacts/x"])
        self.assertEqual(self.evaluate().returncode, 0)
        self.assertEqual(self.state()["status"], "success")
        write_result(self.ir, 2, "IR-late", "fail")
        result = self.evaluate()
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertIn("terminal", result.stdout)
        self.assertEqual(self.state()["status"], "success")  # not reopened

    # --- P2: idempotent replay ----------------------------------------------
    def test_replay_is_idempotent_and_does_not_duplicate_side_effects(self) -> None:
        write_result(self.ir, 1, "IR-x", "fail", side_effects=["wrote X"])
        self.assertEqual(self.evaluate().returncode, 0)
        self.assertEqual(self.state()["side_effect_journal"], ["wrote X"])
        # resubmit the same result id
        replay = self.evaluate()
        self.assertEqual(replay.returncode, 0)
        self.assertTrue(json.loads(replay.stdout).get("replay"))
        self.assertEqual(self.state()["side_effect_journal"], ["wrote X"])  # no duplication

    def test_replay_id_reused_with_different_payload_is_conflict(self):
        write_result(self.ir, 1, "IR-c", "fail")
        self.assertEqual(self.evaluate().returncode, 0)
        # Same iteration_result_id, different payload (pass vs fail) -> conflict.
        write_result(self.ir, 1, "IR-c", "pass", evidence=["artifacts/x"])
        result = self.evaluate()
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertIn("conflict", result.stdout)

    # --- P2: iterations/ audit ----------------------------------------------
    def test_iterations_audit_records_input_and_decision(self) -> None:
        write_result(self.ir, 1, "IR-a", "fail")
        self.assertEqual(self.evaluate().returncode, 0)
        self.assertTrue((self.loop / "iterations" / "0001.input.yaml").is_file())
        self.assertTrue((self.loop / "iterations" / "0001.decision.yaml").is_file())

    # --- P2: explicit resume ------------------------------------------------
    def test_resume_reopens_terminal_loop(self) -> None:
        write_result(self.ir, 1, "IR-pass", "pass", evidence=["artifacts/x"])
        self.assertEqual(self.evaluate().returncode, 0)
        self.assertEqual(self.state()["status"], "success")
        resumed = run("resume_loop_run.py", str(self.loop), "--reason", "manual retry")
        self.assertEqual(resumed.returncode, 0, resumed.stdout + resumed.stderr)
        self.assertEqual(self.state()["status"], "active")
        self.assertEqual(self.state()["resumes"][0]["from"], "success")

    # --- P1: activation bridge ----------------------------------------------
    def test_activation_pointer_roundtrip(self) -> None:
        env = {**os.environ, "CODEX_HOME": str(self.tmp / "codexhome")}
        act = run("activate_loop_run.py", "--session-id", "SESS-1", "--loop-run-dir", str(self.loop), env=env)
        self.assertEqual(act.returncode, 0, act.stdout + act.stderr)
        pointer = self.tmp / "codexhome" / "harness" / "active-loops" / "SESS-1.json"
        self.assertTrue(pointer.is_file())
        self.assertEqual(json.loads(pointer.read_text())["status"], "active")
        deact = run("deactivate_loop_run.py", "--session-id", "SESS-1", env=env)
        self.assertEqual(deact.returncode, 0, deact.stdout + deact.stderr)
        self.assertEqual(json.loads(pointer.read_text())["status"], "inactive")

    def test_hook_resolves_loop_by_session_and_decouples_unverified(self) -> None:
        codexhome = self.tmp / "codexhome"
        env = {**os.environ, "CODEX_HOME": str(codexhome)}
        self.assertEqual(
            run("activate_loop_run.py", "--session-id", "SESS-2", "--loop-run-dir", str(self.loop), env=env).returncode,
            0,
        )
        os.environ["CODEX_HOME"] = str(codexhome)
        self.addCleanup(os.environ.pop, "CODEX_HOME", None)
        sys.path.insert(0, str(ROOT / ".codex" / "hooks"))
        import codex_hook_adapter as hook

        resolved = hook.active_loop_run_dir({"session_id": "SESS-2"})
        self.assertIsNotNone(resolved)
        self.assertEqual(Path(resolved).resolve(), self.loop.resolve())
        # validation_code 4 (UNVERIFIED manifest) still evaluates an active loop
        self.assertIsNotNone(hook.maybe_evaluate_active_loop({"session_id": "SESS-2"}, 4))
        # hard failure (other codes) skips loop drive
        self.assertIsNone(hook.maybe_evaluate_active_loop({"session_id": "SESS-2"}, 1))


    # --- P5: wall-time enforcement + precedence vocabulary ------------------
    def _init_contract(self, max_wall: int) -> Path:
        contract = self.tmp / "wc.yaml"
        contract.write_text(
            yaml.safe_dump(
                {
                    "schema_version": 1,
                    "contract_id": "LC-20260623-777",
                    "activation": "explicit",
                    "goal": {
                        "statement": "wall-time test",
                        "success_conditions": [
                            {
                                "id": "SC-001",
                                "statement": "primary",
                                "required": True,
                                "verifier": {"type": "command_exit", "command": "true", "expected_exit_code": 0},
                            }
                        ],
                    },
                    "control": {
                        "max_iterations": 99,
                        "max_wall_time_seconds": max_wall,
                        "no_progress_limit": 99,
                        "same_failure_limit": 99,
                        "max_stop_continuations": 99,
                    },
                    "termination": {
                        "precedence": [
                            "unsafe", "fatal", "blocked", "success",
                            "approval_required", "stalled", "budget_exhausted", "recover", "continue",
                        ]
                    },
                }
            ),
            encoding="utf-8",
        )
        out = run("init_loop_run.py", str(contract), "--output-root", str(self.tmp / "runs"), "--workspace-root", str(self.tmp))
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        return Path(json.loads(out.stdout)["loop_run_dir"])

    def test_wall_time_budget_is_enforced(self) -> None:
        loop = self._init_contract(max_wall=1)
        state_path = loop / "state.yaml"
        state = yaml.safe_load(state_path.read_text(encoding="utf-8"))
        state["started_at"] = "2020-01-01T00:00:00Z"  # far in the past
        state_path.write_text(yaml.safe_dump(state, sort_keys=False), encoding="utf-8")
        ir = self.tmp / "irw.yaml"
        ir.write_text(
            yaml.safe_dump(
                {
                    "schema_version": 1,
                    "loop_run_id": "LR-20260623-777",
                    "iteration": 1,
                    "iteration_result_id": "IR-w1",
                    "condition_results": [{"condition_id": "SC-001", "status": "fail", "evidence_refs": []}],
                }
            ),
            encoding="utf-8",
        )
        result = run("evaluate_loop_run.py", str(loop), "--iteration-result", str(ir), "--format", "json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        decision = json.loads(result.stdout)["decision"]
        self.assertEqual(decision["action"], "budget_exhausted")
        self.assertEqual(decision["reason_code"], "wall_time_exhausted")

    def test_precedence_vocabulary_accepts_recover_and_blocked(self) -> None:
        # A contract listing the controller's real vocabulary (recover/blocked)
        # validates and runs — the vocabulary is coherent end-to-end.
        loop = self._init_contract(max_wall=0)
        self.assertTrue((loop / "state.yaml").is_file())

    # --- F1/F3: activation lifecycle ----------------------------------------
    def _activate(self, session_id: str, codexhome: Path):
        return run("activate_loop_run.py", "--session-id", session_id, "--loop-run-dir", str(self.loop),
                   env={**os.environ, "CODEX_HOME": str(codexhome)})

    def _hook(self, codexhome: Path):
        os.environ["CODEX_HOME"] = str(codexhome)
        self.addCleanup(os.environ.pop, "CODEX_HOME", None)
        sys.path.insert(0, str(ROOT / ".codex" / "hooks"))
        import codex_hook_adapter as hook
        return hook

    def test_terminal_loop_deactivates_session_pointer(self):
        codexhome = self.tmp / "ch1"
        self.assertEqual(self._activate("SX", codexhome).returncode, 0)
        hook = self._hook(codexhome)
        self.assertIsNotNone(hook.active_loop_run_dir({"session_id": "SX"}))
        deact = hook._deactivate_session_pointer("SX", str(self.loop), "success")
        self.assertEqual(deact, {"deactivated": True, "final_action": "success"})
        self.assertIsNone(hook.active_loop_run_dir({"session_id": "SX"}))
        pointer = codexhome / "harness" / "active-loops" / "SX.json"
        self.assertEqual(json.loads(pointer.read_text())["status"], "terminal")

    def test_deactivate_guards_against_a_different_loop(self):
        codexhome = self.tmp / "ch2"
        self.assertEqual(self._activate("SY", codexhome).returncode, 0)
        hook = self._hook(codexhome)
        self.assertIsNone(hook._deactivate_session_pointer("SY", "/some/other/loop", "success"))
        self.assertIsNotNone(hook.active_loop_run_dir({"session_id": "SY"}))

    def test_observe_mode_does_not_consume_continuation_budget(self):
        st = yaml.safe_load((self.loop / "state.yaml").read_text())
        st["started_at"] = "2099-01-01T00:00:00Z"  # keep non-terminal (no wall-time exhaustion)
        (self.loop / "state.yaml").write_text(yaml.safe_dump(st, sort_keys=False), encoding="utf-8")
        codexhome = self.tmp / "ch3"
        self.assertEqual(self._activate("SZ", codexhome).returncode, 0)
        hook = self._hook(codexhome)

        def used():
            return yaml.safe_load((self.loop / "state.yaml").read_text())["budgets"]["stop_continuations_used"]

        base = used()
        os.environ["SKILL_SYSTEM_LOOP_CONTINUATION"] = "observe"
        self.addCleanup(os.environ.pop, "SKILL_SYSTEM_LOOP_CONTINUATION", None)
        hook.maybe_evaluate_active_loop({"session_id": "SZ"}, 0)
        self.assertEqual(used(), base, "observe must not consume continuation budget")
        os.environ.pop("SKILL_SYSTEM_LOOP_CONTINUATION", None)
        hook.maybe_evaluate_active_loop({"session_id": "SZ"}, 0)
        self.assertEqual(used(), base + 1, "blocking must consume continuation budget")

    # --- P3: convergence verifier soundness ---------------------------------
    def test_evidence_ledger_partial_does_not_pass(self) -> None:
        for verdict, expect_pass in (("confirmed", True), ("partial", False), ("refuted", False)):
            ledger = self.tmp / f"ledger-{verdict}.yaml"
            ledger.write_text(
                yaml.safe_dump(
                    {
                        "schema_version": 1,
                        "claims": [
                            {
                                "id": "C-001",
                                "retained": True,
                                "citation_status": "verified",
                                "verdict": verdict,
                                "sources": ["https://example.com/s"],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            result = run("check_evidence_ledger.py", str(ledger))
            self.assertEqual(result.returncode == 0, expect_pass, f"{verdict}: {result.stdout}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
