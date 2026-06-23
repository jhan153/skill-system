import os
import tempfile
import unittest
from pathlib import Path

from kanboard_plan_sync_mcp.tools import PLAN_TOOLS, run_tool, tool_names

PLAN_TEXT = """# WS Plan

## 12) TODO
- [ ] `todo` alpha task (A1)
- [x] `done` beta task (A2)
"""

CONFIG_YAML = """
workspace:
  name: ws
kanboard:
  # Hermetic: never resolve a real token from the ambient env or the local DB,
  # so needs_live assertions don't depend on a running Kanboard / exported token.
  token_env: KPS_TEST_UNSET_TOKEN
  local_db_path: /no/such/kanboard-test.sqlite
plans:
  - path: docs/plan/2026-02-02-ws.md
    plan_type: short-term
"""

RAW_API = {
    "createTask",
    "updateTask",
    "moveTaskPosition",
    "createProject",
    "getColumns",
    "getTaskByReference",
    "createComment",
    "getProjectByName",
}


class McpRegistryTest(unittest.TestCase):
    def test_only_plan_centric_tools(self):
        names = set(tool_names())
        self.assertEqual(
            names,
            {
                "create_board_from_plan",
                "sync_plan_to_board",
                "pull_board_status",
                "record_validation",
                "record_session_update",
                "curate_plan_board",
                "inspect_workspace",
                "register_workspace",
                "list_workspaces",
                "sync_all",
            },
        )
        self.assertFalse(names & RAW_API, "raw Kanboard API leaked into tool list")

    def test_each_tool_has_schema(self):
        for spec in PLAN_TOOLS:
            self.assertEqual(spec.input_schema["type"], "object")
            self.assertIn("properties", spec.input_schema)


class McpHandlerTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        plan_dir = self.root / "docs" / "plan"
        plan_dir.mkdir(parents=True)
        self.plan = plan_dir / "2026-02-02-ws.md"
        self.plan.write_text(PLAN_TEXT, encoding="utf-8")
        (self.root / ".kanboard-plan.yml").write_text(CONFIG_YAML, encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def test_create_board_dry_run(self):
        out = run_tool("create_board_from_plan", {"plan_path": str(self.plan)})
        self.assertEqual(out["status"], "dry_run")
        self.assertFalse(out["applied"])
        self.assertEqual(out["skeleton"]["columns"], ["TODO", "진행중", "검토 필요", "보류", "완료"])
        self.assertEqual(out["skeleton"]["task_count"], 2)

    def test_sync_dry_run_emits_operations(self):
        out = run_tool(
            "sync_plan_to_board",
            {"plan_path": str(self.plan), "workspace": str(self.root)},
        )
        self.assertEqual(out["status"], "dry_run")
        self.assertEqual(out["push_policy"], "markdown-primary")
        self.assertIn("operations", out)
        self.assertEqual(out["summary"].get("create_task"), 2)

    def test_sync_apply_needs_live(self):
        out = run_tool(
            "sync_plan_to_board",
            {"plan_path": str(self.plan), "workspace": str(self.root), "dry_run": False},
        )
        self.assertEqual(out["status"], "needs_live_kanboard")
        self.assertFalse(out["applied"])

    def test_pull_without_snapshot_needs_live(self):
        out = run_tool("pull_board_status", {"plan_path": str(self.plan)})
        self.assertEqual(out["status"], "needs_live_kanboard")
        self.assertEqual(out["candidates"], [])

    def test_pull_with_snapshot_classifies(self):
        board = [{"reference": "2026-02-02-ws:A2", "column": "진행중", "task_id": 1}]
        out = run_tool(
            "pull_board_status",
            {"plan_path": str(self.plan), "board_snapshot": board},
        )
        self.assertEqual(out["status"], "ok")
        self.assertTrue(out["markdown_unchanged"])
        # A2 is done in markdown, 진행중 on board -> safe_demotion
        kinds = {c["task_reference"]: c["kind"] for c in out["candidates"]}
        self.assertEqual(kinds["2026-02-02-ws:A2"], "safe_demotion")

    def test_record_validation_dry_run(self):
        out = run_tool(
            "record_validation",
            {"plan_id": "p", "task_key": "A1", "evidence": "pytest green"},
        )
        self.assertEqual(out["status"], "dry_run")
        self.assertEqual(out["projection"]["task_reference"], "p:A1")
        self.assertIn("pytest green", out["projection"]["comment"])

    def test_record_session_update_requires_task_reference(self):
        out = run_tool(
            "record_session_update",
            {"session_summary": "implemented the mapped task"},
        )
        self.assertEqual(out["status"], "needs_task_reference")
        self.assertFalse(out["applied"])

    def test_record_session_update_dry_run(self):
        out = run_tool(
            "record_session_update",
            {
                "plan_id": "p",
                "task_key": "A1",
                "session_summary": "implemented the mapped task",
                "result_label": "agent-verified",
                "validation_evidence": "pytest green",
                "changed_files": ["src/app.py"],
            },
        )
        self.assertEqual(out["status"], "dry_run")
        self.assertEqual(out["projection"]["task_reference"], "p:A1")
        self.assertIn("implemented the mapped task", out["projection"]["comment"])
        self.assertIn("pytest green", out["projection"]["comment"])
        self.assertEqual(out["projection"]["subtask_title"], "session evidence: agent-verified")

    def test_curate_without_snapshot_needs_live(self):
        out = run_tool("curate_plan_board", {"plan_id": "2026-02-02-ws"})
        self.assertEqual(out["status"], "needs_live_kanboard")

    def test_curate_with_snapshot_classifies(self):
        board = [
            {"reference": "2026-02-02-ws:A1", "column": "TODO"},  # matched
            {"reference": "2026-02-02-ws:GONE", "column": "TODO"},  # orphaned
            {"reference": "other-plan:Z1", "column": "TODO"},  # foreign
            {"reference": "2026-02-02-ws:A2", "column": "완료"},  # completed
            {"reference": "", "column": "TODO"},  # orphaned (no ref)
        ]
        out = run_tool(
            "curate_plan_board",
            {
                "plan_id": "2026-02-02-ws",
                "workspace": str(self.root),
                "board_snapshot": board,
            },
        )
        self.assertEqual(out["status"], "ok")
        cats = out["categories"]
        self.assertIn("2026-02-02-ws:A1", cats["matched"])
        self.assertIn("2026-02-02-ws:GONE", cats["orphaned_candidates"])
        self.assertIn("other-plan:Z1", cats["foreign_cards"])
        self.assertIn("2026-02-02-ws:A2", cats["completed_projection"])

    def test_inspect_workspace_delegates(self):
        out = run_tool("inspect_workspace", {"workspace_path": str(self.root)})
        self.assertTrue(out["config_present"])
        self.assertEqual(out["workspace_name"], "ws")
        # token never exposed; only presence flag
        self.assertIn("token_present", out["kanboard"])
        self.assertNotIn("token", out["kanboard"])


class McpRolloutToolTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        base = Path(self._tmp.name)
        self.repo = base / "repoZ"
        (self.repo / "docs" / "plan").mkdir(parents=True)
        (self.repo / "docs" / "plan" / "2026-03-03-z.md").write_text(
            "# Z\n\n## 12) TODO\n- [ ] `todo` z task (Z1)\n", encoding="utf-8"
        )
        self._prev_reg = os.environ.get("KANBOARD_PLAN_REGISTRY")
        os.environ["KANBOARD_PLAN_REGISTRY"] = str(base / "workspaces.yml")

    def tearDown(self):
        if self._prev_reg is None:
            os.environ.pop("KANBOARD_PLAN_REGISTRY", None)
        else:
            os.environ["KANBOARD_PLAN_REGISTRY"] = self._prev_reg
        self._tmp.cleanup()

    def test_register_then_list_then_sync_all(self):
        reg = run_tool("register_workspace", {"workspace_path": str(self.repo)})
        self.assertEqual(reg["tool"], "register_workspace")
        self.assertIn(str(self.repo.resolve()), reg["registered"])
        # init scaffolded the config
        self.assertEqual(reg["init"]["status"], "created")

        listed = run_tool("list_workspaces", {})
        paths = [w["path"] for w in listed["workspaces"]]
        self.assertIn(str(self.repo.resolve()), paths)

        rep = run_tool("sync_all", {})
        self.assertEqual(rep["tool"], "sync_all")
        self.assertEqual(rep["mode"], "dry-run")
        self.assertEqual(rep["totals"]["workspaces"], 1)
        self.assertEqual(rep["totals"]["plans"], 1)


if __name__ == "__main__":
    unittest.main()
