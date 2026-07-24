#!/usr/bin/env python3
"""Unit tests for the checkpointed-execution task ledger (workflow-task-ledger).

Run: python3 .codex/tools/tests/test_task_ledger.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / ".codex" / "tools" / "task_ledger.py"
VALIDATOR = ROOT / ".codex" / "tools" / "validate_task_run.py"
TASK_EXAMPLE = ROOT / ".codex" / "schemas" / "task" / "examples" / "task-run.example.yaml"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TOOL), *args], text=True, capture_output=True, check=False
    )


def validate(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(path)],
        text=True,
        capture_output=True,
        check=False,
    )


CMD_EVIDENCE = '{"type": "command", "command": "pytest", "exit_code": 0}'


class TaskLedgerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.dir = self.tmp / "run"
        self.assertEqual(run("init", str(self.dir), "--objective", "demo").returncode, 0)

    def state(self) -> dict:
        return yaml.safe_load((self.dir / "task-run.yaml").read_text(encoding="utf-8"))

    def test_v2_example_and_contract_validate_together(self) -> None:
        result = validate(TASK_EXAMPLE)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_complete_step_requires_evidence(self) -> None:
        run("add-step", str(self.dir), "--id", "S001", "--title", "do")
        no_ev = run("checkpoint", str(self.dir), "--step", "S001", "--status", "complete")
        self.assertNotEqual(no_ev.returncode, 0)
        self.assertIn("evidence", no_ev.stdout + no_ev.stderr)
        ok = run("checkpoint", str(self.dir), "--step", "S001", "--status", "complete", "--evidence", CMD_EVIDENCE)
        self.assertEqual(ok.returncode, 0)
        self.assertEqual(self.state()["steps"][0]["status"], "complete")

    def test_open_finding_blocks_close(self) -> None:
        run("add-step", str(self.dir), "--id", "S001")
        run("checkpoint", str(self.dir), "--step", "S001", "--status", "complete", "--evidence", CMD_EVIDENCE)
        run("final-verify", str(self.dir), "--status", "pass", "--evidence", CMD_EVIDENCE)
        run("finding-add", str(self.dir), "--id", "F001", "--title", "gap", "--severity", "high")
        blocked = run("close", str(self.dir))
        self.assertNotEqual(blocked.returncode, 0)
        self.assertIn("open findings", blocked.stdout)

    def test_close_passes_when_gate_met(self) -> None:
        run("add-step", str(self.dir), "--id", "S001")
        run("checkpoint", str(self.dir), "--step", "S001", "--status", "complete", "--evidence", CMD_EVIDENCE)
        run("finding-add", str(self.dir), "--id", "F001", "--title", "gap", "--severity", "low")
        # accepted_risk closes the open finding via the explicit terminal.
        ar = run("finding-accept-risk", str(self.dir), "--id", "F001",
                 "--accepted-by", "user", "--reason", "out of scope", "--review-at", "next-release")
        self.assertEqual(ar.returncode, 0)
        run("final-verify", str(self.dir), "--status", "pass", "--evidence", CMD_EVIDENCE)
        closed = run("close", str(self.dir))
        self.assertEqual(closed.returncode, 0, closed.stdout + closed.stderr)
        self.assertEqual(self.state()["status"], "complete")

    def test_incomplete_step_blocks_close(self) -> None:
        run("add-step", str(self.dir), "--id", "S001")
        run("final-verify", str(self.dir), "--status", "pass", "--evidence", CMD_EVIDENCE)
        blocked = run("close", str(self.dir))
        self.assertNotEqual(blocked.returncode, 0)
        self.assertIn("steps not complete", blocked.stdout)

    def test_resolve_requires_resolution_and_verification(self) -> None:
        run("finding-add", str(self.dir), "--id", "F001", "--title", "bug", "--severity", "high",
            "--evidence", '{"kind": "discovery", "type": "test", "locator": "t::case"}')
        # resolution but no new (verification) evidence -> fail
        no_ver = run("finding-resolve", str(self.dir), "--id", "F001", "--resolution", "fixed parser")
        self.assertNotEqual(no_ver.returncode, 0)
        self.assertIn("verification", no_ver.stdout + no_ver.stderr)
        # evidence but no resolution -> fail
        no_res = run("finding-resolve", str(self.dir), "--id", "F001",
                     "--evidence", '{"kind": "verification", "type": "command", "command": "pytest", "exit_code": 0}')
        self.assertNotEqual(no_res.returncode, 0)
        # resolution + verification evidence -> resolved
        ok = run("finding-resolve", str(self.dir), "--id", "F001", "--resolution", "fixed parser",
                 "--evidence", '{"kind": "verification", "type": "command", "command": "pytest", "exit_code": 0}')
        self.assertEqual(ok.returncode, 0, ok.stdout + ok.stderr)
        self.assertEqual(self.state()["findings"][0]["status"], "resolved")

    def test_init_can_link_work_item(self) -> None:
        linked_dir = self.tmp / "linked"
        result = run(
            "init",
            str(linked_dir),
            "--objective",
            "linked",
            "--work-item-ref",
            "WI-20260627-001",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        data = yaml.safe_load((linked_dir / "task-run.yaml").read_text(encoding="utf-8"))
        self.assertEqual(data["work_item_ref"], "WI-20260627-001")

    def test_user_owned_verification_closes_as_handoff(self) -> None:
        run_dir = self.tmp / "user-verification"
        initialized = run(
            "init",
            str(run_dir),
            "--objective",
            "implement production behavior",
            "--execution-mode",
            "unattended_goal_loop",
            "--verification-owner",
            "user",
            "--interaction-mode",
            "forbidden",
        )
        self.assertEqual(initialized.returncode, 0, initialized.stdout + initialized.stderr)
        run(
            "add-step",
            str(run_dir),
            "--id",
            "S001",
            "--title",
            "implement production behavior",
            "--kind",
            "core",
        )
        run(
            "checkpoint",
            str(run_dir),
            "--step",
            "S001",
            "--status",
            "complete",
            "--evidence",
            '{"type":"file","locator":"src/product.py"}',
        )
        optional = run(
            "add-step",
            str(run_dir),
            "--id",
            "S002",
            "--title",
            "run extra validation",
            "--kind",
            "agent_validation",
        )
        self.assertEqual(optional.returncode, 0, optional.stdout + optional.stderr)
        data = yaml.safe_load((run_dir / "task-run.yaml").read_text(encoding="utf-8"))
        self.assertEqual(data["steps"][1]["status"], "deferred")
        run("final-verify", str(run_dir), "--status", "user-verification-needed")
        closed = run("close", str(run_dir))
        self.assertEqual(closed.returncode, 0, closed.stdout + closed.stderr)
        data = yaml.safe_load((run_dir / "task-run.yaml").read_text(encoding="utf-8"))
        self.assertEqual(data["status"], "complete")
        self.assertEqual(data["result_label"], "user-verification-needed")
        validated = validate(run_dir / "task-run.yaml")
        self.assertEqual(validated.returncode, 0, validated.stdout + validated.stderr)

    def test_excluded_auxiliary_step_cannot_reactivate_as_required(self) -> None:
        run_dir = self.tmp / "excluded-required"
        initialized = run(
            "init",
            str(run_dir),
            "--objective",
            "implement production behavior",
            "--verification-owner",
            "user",
        )
        self.assertEqual(initialized.returncode, 0, initialized.stdout + initialized.stderr)
        added = run(
            "add-step",
            str(run_dir),
            "--id",
            "S001",
            "--title",
            "run agent validation",
            "--kind",
            "agent_validation",
            "--required",
        )
        self.assertEqual(added.returncode, 0, added.stdout + added.stderr)
        step = yaml.safe_load((run_dir / "task-run.yaml").read_text(encoding="utf-8"))["steps"][0]
        self.assertEqual(step["status"], "deferred")
        self.assertFalse(step["required"])

    def test_local_deferral_keeps_independent_required_work_runnable(self) -> None:
        run_dir = self.tmp / "local-deferral"
        run(
            "init",
            str(run_dir),
            "--objective",
            "two independent changes",
            "--execution-mode",
            "unattended_goal_loop",
            "--interaction-mode",
            "forbidden",
        )
        run(
            "add-step",
            str(run_dir),
            "--id",
            "S001",
            "--title",
            "obtain external approval",
            "--kind",
            "required_prerequisite",
            "--requires-interaction",
        )
        locally_blocked = yaml.safe_load((run_dir / "task-run.yaml").read_text(encoding="utf-8"))
        self.assertEqual(locally_blocked["status"], "blocked")
        self.assertEqual(locally_blocked["result_label"], "blocked")
        run(
            "add-step",
            str(run_dir),
            "--id",
            "S002",
            "--title",
            "implement independent parser",
            "--kind",
            "core",
        )
        data = yaml.safe_load((run_dir / "task-run.yaml").read_text(encoding="utf-8"))
        self.assertEqual(data["steps"][0]["status"], "deferred")
        self.assertEqual(data["status"], "active")
        self.assertEqual(data["result_label"], "pending")
        next_action = run("next-action", str(run_dir), "--format", "json")
        self.assertEqual(next_action.returncode, 0, next_action.stdout + next_action.stderr)
        self.assertEqual(__import__("json").loads(next_action.stdout)["step_id"], "S002")

    def test_attended_work_preserves_normal_interaction(self) -> None:
        run_dir = self.tmp / "attended"
        run(
            "init",
            str(run_dir),
            "--objective",
            "interactive change",
            "--execution-mode",
            "attended",
            "--interaction-mode",
            "forbidden",
        )
        run(
            "add-step",
            str(run_dir),
            "--id",
            "S001",
            "--title",
            "obtain required permission",
            "--kind",
            "required_prerequisite",
            "--requires-interaction",
        )
        data = yaml.safe_load((run_dir / "task-run.yaml").read_text(encoding="utf-8"))
        self.assertEqual(data["steps"][0]["status"], "pending")

    def test_interaction_enabled_goal_preserves_normal_interaction(self) -> None:
        run_dir = self.tmp / "interactive-goal"
        run(
            "init",
            str(run_dir),
            "--objective",
            "interactive long-running change",
            "--execution-mode",
            "unattended_goal_loop",
            "--interaction-mode",
            "allowed",
        )
        run(
            "add-step",
            str(run_dir),
            "--id",
            "S001",
            "--title",
            "obtain required permission",
            "--kind",
            "required_prerequisite",
            "--requires-interaction",
        )
        data = yaml.safe_load((run_dir / "task-run.yaml").read_text(encoding="utf-8"))
        self.assertEqual(data["steps"][0]["status"], "pending")

    def test_alternate_validation_form_reuses_deferred_semantic_intent(self) -> None:
        first = run(
            "add-step",
            str(self.dir),
            "--id",
            "S001",
            "--title",
            "run runtime validation",
            "--kind",
            "agent_validation",
        )
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        deferred = run(
            "checkpoint",
            str(self.dir),
            "--step",
            "S001",
            "--status",
            "deferred",
            "--reason",
            "approval unavailable",
        )
        self.assertEqual(deferred.returncode, 0, deferred.stdout + deferred.stderr)
        alternate = run(
            "add-step",
            str(self.dir),
            "--id",
            "S002",
            "--title",
            "create a verification wrapper",
            "--kind",
            "validation_artifact",
        )
        self.assertEqual(alternate.returncode, 0, alternate.stdout + alternate.stderr)
        self.assertIn("semantic intent is already deferred", alternate.stdout)
        self.assertEqual(len(self.state()["steps"]), 1)


if __name__ == "__main__":
    unittest.main()
