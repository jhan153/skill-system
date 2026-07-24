from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / ".codex" / "tools" / "validate_work_item.py"
EXAMPLE = ROOT / ".codex" / "schemas" / "workitem" / "examples" / "work-item.example.yaml"


def run_validate(path: Path) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, str(TOOL), str(path)],
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=30,
    )


BASE_WORK_ITEM = """\
schema_version: 1
work_item_id: WI-20260627-999
title: "Demo"
source:
  type: user_request
  ref: "demo"
state: closed
owner: agent
primary_skill: workflow-task-ledger
task_run_ref: null
loop_run_ref: null
runtime_boundary:
  mode: state_model
  queue_runtime: false
  scheduler_runtime: false
  kanboard_source_of_truth: false
  looprun_replacement: false
history:
  - state: triage
    at: "2026-06-27T00:00:00Z"
    actor: human
    evidence_refs: []
  - state: explore
    at: "2026-06-27T00:01:00Z"
    actor: agent
    evidence_refs: []
  - state: ready
    at: "2026-06-27T00:02:00Z"
    actor: agent
    evidence_refs: []
  - state: implement
    at: "2026-06-27T00:03:00Z"
    actor: agent
    evidence_refs: []
  - state: verify
    at: "2026-06-27T00:04:00Z"
    actor: agent
    evidence_refs: []
  - state: review
    at: "2026-06-27T00:05:00Z"
    actor: agent
    evidence_refs: []
  - state: closed
    at: "2026-06-27T00:06:00Z"
    actor: agent
    evidence_refs:
      - type: command
        command: "pytest"
        exit_code: 0
evidence_refs:
  - type: command
    command: "pytest"
    exit_code: 0
open_findings: []
next_action: ""
"""

V2_ACTIVE_WORK_ITEM = """\
schema_version: 2
work_item_id: WI-20260723-999
title: "Nonblocking work contract projection"
source:
  type: user_request
  ref: "demo"
state: implement
owner: agent
primary_skill: workflow-task-ledger
task_run_ref: TR-20260723-999
loop_run_ref: LR-20260723-999
work_contract_ref: task-runs/TR-20260723-999/work-contract.yaml
work_contract_hash: "0000000000000000000000000000000000000000000000000000000000000000"
result_label: pending
deferred_actions:
  - action_ref: validation
    intent_key: validate-product
    work_kind: agent_validation
    reason: user owns verification
    interaction_required: false
runnable_action_refs:
  - implement-parser
runtime_boundary:
  mode: state_model
  queue_runtime: false
  scheduler_runtime: false
  kanboard_source_of_truth: false
  looprun_replacement: false
history:
  - state: implement
    at: "2026-07-23T00:00:00Z"
    actor: agent
    evidence_refs: []
evidence_refs: []
open_findings: []
next_action: "implement-parser"
"""


class WorkItemLifecycleTests(unittest.TestCase):
    def write_case(self, text: str) -> Path:
        fd, raw = tempfile.mkstemp(prefix="work-item-", suffix=".yaml")
        os.close(fd)
        path = Path(raw)
        path.write_text(text, encoding="utf-8")
        self.addCleanup(lambda: path.unlink(missing_ok=True))
        return path

    def test_example_passes(self) -> None:
        result = run_validate(EXAMPLE)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_closed_with_open_finding_fails(self) -> None:
        path = self.write_case(
            BASE_WORK_ITEM.replace(
                "open_findings: []",
                (
                    "open_findings:\n"
                    "  - id: F001\n"
                    "    title: unresolved\n"
                    "    severity: high\n"
                    "    status: open\n"
                    "    evidence_refs: []"
                ),
            )
        )
        result = run_validate(path)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unresolved findings", result.stdout)

    def test_invalid_transition_fails(self) -> None:
        path = self.write_case(BASE_WORK_ITEM.replace("  - state: ready", "  - state: verify", 1))
        result = run_validate(path)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid transition", result.stdout)

    def test_runtime_queue_claim_fails(self) -> None:
        path = self.write_case(BASE_WORK_ITEM.replace("queue_runtime: false", "queue_runtime: true"))
        result = run_validate(path)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("queue_runtime", result.stdout)

    def test_v2_local_defer_can_coexist_with_independent_runnable_work(self) -> None:
        result = run_validate(self.write_case(V2_ACTIVE_WORK_ITEM))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_v2_blocked_rejects_remaining_runnable_work(self) -> None:
        text = (
            V2_ACTIVE_WORK_ITEM
            .replace("state: implement", "state: blocked")
            .replace("result_label: pending", "result_label: blocked")
            .replace('next_action: "implement-parser"', 'blocked_reason: "approval unavailable"\nnext_action: "ask user"')
        )
        result = run_validate(self.write_case(text))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("runnable", result.stdout)

    def test_v2_rejects_duplicate_deferred_semantic_intent(self) -> None:
        duplicate = (
            "  - action_ref: validation-retry\n"
            "    intent_key: validate-product\n"
            "    work_kind: validation_artifact\n"
            "    reason: alternate form of the same purpose\n"
            "    interaction_required: false\n"
        )
        text = V2_ACTIVE_WORK_ITEM.replace(
            "runnable_action_refs:\n",
            duplicate + "runnable_action_refs:\n",
        )
        result = run_validate(self.write_case(text))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("semantic intents", result.stdout)


if __name__ == "__main__":
    unittest.main()
