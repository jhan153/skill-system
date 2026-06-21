import unittest

from kanboard_plan_sync.diff import build_diff
from kanboard_plan_sync.models import PlanManifest, PlanTask
from kanboard_plan_sync.state import SyncState, TaskState
from kanboard_plan_sync.status import column_for_status
from kanboard_plan_sync.sync import apply_diff, ensure_members

from tests._fakes import FakeKanboard


def _task(key, status):
    return PlanTask(
        task_key=key,
        task_reference=f"plan:{key}",
        title=f"task {key}",
        markdown_status=status,
        kanboard_column=column_for_status(status),
    )


class FakeClient:
    """In-memory Kanboard double that records calls and assigns ids."""

    DEFAULT_COLUMNS = ["TODO", "진행중", "검토 필요", "보류", "완료"]

    def __init__(self, existing_project=None):
        self.existing_project = existing_project
        self._next_project = 100
        self._next_task = 1000
        self.created_tasks = []
        self.moves = []
        self.updates = []
        self.created_projects = []

    def get_project_by_name(self, name):
        return self.existing_project

    def create_project(self, name, description=""):
        self.created_projects.append(name)
        pid = self._next_project
        self._next_project += 1
        return pid

    def get_columns(self, project_id):
        return [{"id": i + 1, "title": t} for i, t in enumerate(self.DEFAULT_COLUMNS)]

    def add_column(self, project_id, title):  # not expected when all columns exist
        raise AssertionError(f"unexpected add_column for {title!r}")

    def create_task(
        self,
        project_id,
        title,
        reference,
        column_id=None,
        swimlane_id=None,
        owner_id=None,
        description=None,
        color_id=None,
        tags=None,
    ):
        tid = self._next_task
        self._next_task += 1
        self.created_tasks.append(
            {
                "task_id": tid,
                "reference": reference,
                "column_id": column_id,
                "owner_id": owner_id,
                "description": description,
                "color_id": color_id,
                "tags": tags,
            }
        )
        return tid

    def update_task(self, task_id, **fields):
        self.updates.append({"task_id": task_id, **fields})
        return True

    def move_task_position(self, project_id, task_id, column_id, position=1, swimlane_id=0):
        self.moves.append({"task_id": task_id, "column_id": column_id})
        return True


class ApplyDiffTest(unittest.TestCase):
    def test_creates_project_and_tasks_and_updates_state(self):
        manifest = PlanManifest(
            plan_id="plan",
            plan_path="x",
            plan_title="Plan",
            tasks=[_task("A1", "todo"), _task("A2", "done")],
        )
        state = SyncState()
        ops = build_diff(manifest, state)
        client = FakeClient(existing_project=None)

        report = apply_diff(client, manifest, state, ops)

        self.assertEqual(client.created_projects, ["Plan"])
        self.assertEqual(len(client.created_tasks), 2)
        self.assertEqual(report["applied_count"], 2)
        # state now caches both references with the new project id
        self.assertEqual(state.get("plan:A1").kanboard_project_id, 100)
        self.assertIsNotNone(state.get("plan:A2").kanboard_task_id)
        # A2 was created directly in the 완료 column (id 5)
        a2 = [t for t in client.created_tasks if t["reference"] == "plan:A2"][0]
        self.assertEqual(a2["column_id"], 5)

    def test_move_uses_existing_state(self):
        manifest = PlanManifest(
            plan_id="plan", plan_path="x", plan_title="Plan", tasks=[_task("A1", "done")]
        )
        state = SyncState(
            references={
                "plan:A1": TaskState(
                    kanboard_task_id=555,
                    kanboard_project_id=100,
                    last_synced_column="TODO",
                )
            }
        )
        ops = build_diff(manifest, state)
        client = FakeClient(existing_project={"id": 100})

        apply_diff(client, manifest, state, ops)

        self.assertEqual(len(client.moves), 1)
        self.assertEqual(client.moves[0]["task_id"], 555)
        self.assertEqual(client.moves[0]["column_id"], 5)  # 완료
        self.assertEqual(state.get("plan:A1").last_synced_column, "완료")
        # no new project created
        self.assertEqual(client.created_projects, [])


class EnsureMembersTest(unittest.TestCase):
    def test_adds_known_user_once_and_is_idempotent(self):
        fake = FakeKanboard()
        pid = fake.create_project("P")
        added = ensure_members(fake, pid, ["admin"])
        self.assertEqual(added, ["admin"])
        self.assertIn("admin", fake.get_project_users(pid).values())
        # second run: already a member -> nothing added
        self.assertEqual(ensure_members(fake, pid, ["admin"]), [])

    def test_unknown_user_skipped(self):
        fake = FakeKanboard()
        pid = fake.create_project("P")
        self.assertEqual(ensure_members(fake, pid, ["ghost"]), [])

    def test_no_members_requested_is_noop(self):
        fake = FakeKanboard()
        pid = fake.create_project("P")
        self.assertEqual(ensure_members(fake, pid, None), [])
        self.assertEqual(ensure_members(fake, pid, []), [])


if __name__ == "__main__":
    unittest.main()
