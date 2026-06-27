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


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TOOL), *args], text=True, capture_output=True, check=False
    )


CMD_EVIDENCE = '{"type": "command", "command": "pytest", "exit_code": 0}'


class TaskLedgerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(dir="/private/tmp"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.dir = self.tmp / "run"
        self.assertEqual(run("init", str(self.dir), "--objective", "demo").returncode, 0)

    def state(self) -> dict:
        return yaml.safe_load((self.dir / "task-run.yaml").read_text(encoding="utf-8"))

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


if __name__ == "__main__":
    unittest.main()
