import unittest

from kanboard_plan_sync.config import parse_config
from kanboard_plan_sync.diff import build_diff
from kanboard_plan_sync.models import PlanManifest, PlanTask
from kanboard_plan_sync.state import SyncState
from kanboard_plan_sync.status import column_for_status
from kanboard_plan_sync.sync import (
    apply_diff,
    board_target,
    default_assignee,
    ensure_swimlane,
)

from tests._fakes import FakeKanboard


def _manifest(strategy=None):
    tasks = [
        PlanTask("A1", "demo:A1", "alpha", "todo", column_for_status("todo")),
        PlanTask("A2", "demo:A2", "beta", "done", column_for_status("done")),
    ]
    return PlanManifest(
        plan_id="demo",
        plan_path="docs/plan/demo.md",
        plan_title="Demo Plan",
        kanboard_project_strategy=strategy or "workspace-project",
        tasks=tasks,
    )


def _config(strategy):
    raw = {
        "workspace": {"name": "myrepo"},
        "plans": [{"path": "docs/plan/demo.md", "kanboard_project_strategy": strategy}],
    }
    return parse_config(raw, workspace_root="/ws", config_path="x")


class BoardTargetTest(unittest.TestCase):
    def test_workspace_project_maps_plan_to_swimlane(self):
        cfg = _config("workspace-project")
        project, swimlane = board_target(cfg, _manifest())
        self.assertEqual(project, "myrepo")  # repo = Project
        self.assertEqual(swimlane, "Demo Plan")  # plan = Swimlane

    def test_dedicated_project_owns_its_project(self):
        cfg = _config("dedicated-project")
        project, swimlane = board_target(cfg, _manifest("dedicated-project"))
        self.assertEqual(project, "Demo Plan")
        self.assertIsNone(swimlane)

    def test_no_config_defaults_to_workspace_project(self):
        project, swimlane = board_target(None, _manifest())
        # no workspace name available -> falls back to plan_id as project
        self.assertEqual(project, "demo")
        self.assertEqual(swimlane, "Demo Plan")


class EnsureSwimlaneTest(unittest.TestCase):
    def test_creates_and_reuses(self):
        fake = FakeKanboard()
        pid = fake.create_project("myrepo")
        sid = ensure_swimlane(fake, pid, "Demo Plan")
        self.assertIsNotNone(sid)
        # idempotent: same swimlane id on second call
        self.assertEqual(ensure_swimlane(fake, pid, "Demo Plan"), sid)
        self.assertIsNone(ensure_swimlane(fake, pid, None))  # default swimlane


class WorkspaceProjectApplyTest(unittest.TestCase):
    def test_tasks_created_in_plan_swimlane_of_repo_project(self):
        fake = FakeKanboard()
        manifest = _manifest("workspace-project")
        state = SyncState()
        ops = build_diff(manifest, state)
        report = apply_diff(
            fake, manifest, state, ops,
            project_name="myrepo", swimlane_name="Demo Plan",
        )
        self.assertEqual(report["project_name"], "myrepo")
        # one Project named myrepo, one custom swimlane "Demo Plan"
        self.assertEqual(list(fake.projects.values())[0]["name"], "myrepo")
        sl_names = list(fake.swimlanes[report["project_id"]].values())
        self.assertIn("Demo Plan", sl_names)
        # both cards carry the swimlane id
        for t in fake.tasks.values():
            self.assertEqual(t["swimlane_id"], report["swimlane_id"])


class AssigneeTest(unittest.TestCase):
    def test_default_assignee_falls_back_to_first_member(self):
        cfg = _config("workspace-project")  # board_members default [admin], no board_assignee
        self.assertEqual(default_assignee(cfg), "admin")

    def test_explicit_board_assignee_wins(self):
        raw = {
            "workspace": {"name": "r"},
            "kanboard": {"board_members": ["admin", "bob"], "board_assignee": "bob"},
            "plans": [],
        }
        cfg = parse_config(raw, workspace_root="/ws", config_path="x")
        self.assertEqual(default_assignee(cfg), "bob")

    def test_apply_assigns_owner_to_every_card(self):
        fake = FakeKanboard()  # has user admin (id 1)
        manifest = _manifest("workspace-project")
        state = SyncState()
        ops = build_diff(manifest, state)
        apply_diff(
            fake, manifest, state, ops,
            project_name="myrepo", swimlane_name="Demo Plan", assignee="admin",
        )
        self.assertTrue(fake.tasks)
        for t in fake.tasks.values():
            self.assertEqual(t["owner_id"], 1)  # admin


if __name__ == "__main__":
    unittest.main()
