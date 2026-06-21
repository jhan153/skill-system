import unittest

from kanboard_plan_sync.snapshot import fetch_board_snapshot, resolve_project_id
from kanboard_plan_sync.state import SyncState, TaskState

from tests._fakes import FakeKanboard


class SnapshotTest(unittest.TestCase):
    def test_fetch_maps_columns_and_references(self):
        fake = FakeKanboard()
        pid = fake.create_project("P")
        cols = {title: cid for cid, title in fake.columns[pid].items()}
        fake.create_task(pid, "t1", "plan:A1", column_id=cols["Backlog"])
        fake.create_task(pid, "t2", "plan:A2", column_id=cols["Done"])

        snap = fetch_board_snapshot(fake, pid)
        by_ref = {s["reference"]: s for s in snap}
        self.assertEqual(by_ref["plan:A1"]["column"], "Backlog")
        self.assertEqual(by_ref["plan:A2"]["column"], "Done")
        self.assertIsNotNone(by_ref["plan:A1"]["task_id"])

    def test_resolve_project_id_from_state(self):
        state = SyncState(
            references={"plan:A1": TaskState(kanboard_task_id=1, kanboard_project_id=7)}
        )
        self.assertEqual(resolve_project_id(state), 7)
        self.assertIsNone(resolve_project_id(SyncState()))


if __name__ == "__main__":
    unittest.main()
