"""End-to-end live-path integration test through the MCP tools, using an
in-memory FakeKanboard injected via the ``_client`` seam. Exercises:
create board -> sync (with projection) -> live pull (fetched snapshot) ->
record validation -> state persistence.
"""

import tempfile
import unittest
from pathlib import Path

from kanboard_plan_sync.state import load_state
from kanboard_plan_sync_mcp.tools import run_tool

from tests._fakes import FakeKanboard

PLAN_TEXT = """# WS Plan

## 12) TODO
- [ ] `todo` alpha task (A1)
- [x] `done` beta task (A2)
"""

CONFIG_YAML = """
workspace:
  name: ws
kanboard:
  url: http://127.0.0.1:8080/jsonrpc.php
  token_env: KANBOARD_API_TOKEN
plans:
  - path: docs/plan/2026-02-02-ws.md
    plan_type: short-term
"""


class LiveRoundTripTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "docs" / "plan").mkdir(parents=True)
        self.plan = self.root / "docs" / "plan" / "2026-02-02-ws.md"
        self.plan.write_text(PLAN_TEXT, encoding="utf-8")
        (self.root / ".kanboard-plan.yml").write_text(CONFIG_YAML, encoding="utf-8")
        self.fake = FakeKanboard()

    def tearDown(self):
        self._tmp.cleanup()

    def _args(self, **extra):
        base = {"workspace": str(self.root), "_client": self.fake}
        base.update(extra)
        return base

    def test_full_round_trip(self):
        # 1) create board skeleton (live)
        out1 = run_tool(
            "create_board_from_plan",
            self._args(plan_path=str(self.plan), dry_run=False),
        )
        self.assertEqual(out1["status"], "ok")
        self.assertTrue(out1["applied"])
        # our 5 status columns now exist alongside the default ones
        for col in ("TODO", "진행중", "검토 필요", "보류", "완료"):
            self.assertIn(col, out1["result"]["columns"])
        # admin auto-added as a member so the board is visible (no manual step)
        self.assertEqual(out1["result"]["added_members"], ["admin"])
        self.assertIn("admin", self.fake.get_project_users(1).values())

        # 2) sync (live apply with projection)
        out2 = run_tool(
            "sync_plan_to_board",
            self._args(plan_path=str(self.plan), dry_run=False),
        )
        self.assertEqual(out2["status"], "ok")
        self.assertEqual(out2["result"]["applied_count"], 2)

        by_ref = {t["reference"]: t for t in self.fake.tasks.values()}
        self.assertIn("2026-02-02-ws:A1", by_ref)
        a1 = by_ref["2026-02-02-ws:A1"]
        self.assertEqual(a1["color_id"], "grey")  # todo -> grey
        self.assertIn("plan-sync", a1["tags"])
        self.assertIn("2026-02-02-ws", a1["tags"])
        self.assertIn("reference", a1["description"])

        # state persisted with project + task ids
        state = load_state(str(self.root))
        self.assertEqual(len(state.references), 2)
        self.assertIsNotNone(state.get("2026-02-02-ws:A1").kanboard_task_id)

        # 3) pull with no snapshot -> fetched live -> both in_sync
        out3 = run_tool("pull_board_status", self._args(plan_path=str(self.plan)))
        self.assertEqual(out3["status"], "ok")
        self.assertEqual(out3["snapshot_source"], "fetched")
        self.assertEqual(out3["summary"].get("in_sync"), 2)

        # 4) record validation (live) -> comment + subtask written
        out4 = run_tool(
            "record_validation",
            self._args(plan_id="2026-02-02-ws", task_key="A1", evidence="unittest green", dry_run=False),
        )
        self.assertEqual(out4["status"], "ok")
        self.assertTrue(out4["applied"])
        self.assertEqual(len(self.fake.comments), 1)
        self.assertEqual(len(self.fake.subtasks), 1)
        self.assertEqual(self.fake.subtasks[0]["status"], 2)  # done

    def test_pull_reports_completion_candidate_after_manual_move(self):
        run_tool("create_board_from_plan", self._args(plan_path=str(self.plan), dry_run=False))
        run_tool("sync_plan_to_board", self._args(plan_path=str(self.plan), dry_run=False))
        # manually move A1 (todo) to the 완료 column on the fake board
        a1_id = next(
            t["id"] for t in self.fake.tasks.values() if t["reference"] == "2026-02-02-ws:A1"
        )
        pid = self.fake.tasks[a1_id]["project_id"]
        done_col = next(
            cid for cid, title in self.fake.columns[pid].items() if title == "완료"
        )
        self.fake.move_task_position(pid, a1_id, done_col)

        out = run_tool("pull_board_status", self._args(plan_path=str(self.plan)))
        kinds = {c["task_reference"]: c["kind"] for c in out["candidates"]}
        self.assertEqual(kinds["2026-02-02-ws:A1"], "completion_candidate")
        self.assertTrue(out["markdown_unchanged"])


if __name__ == "__main__":
    unittest.main()
