import unittest

from kanboard_plan_sync.diff import build_diff, summarize_diff
from kanboard_plan_sync.models import (
    OP_CREATE_PROJECT,
    OP_CREATE_TASK,
    OP_MOVE_TASK,
    OP_NOOP,
    PlanManifest,
    PlanTask,
)
from kanboard_plan_sync.state import SyncState, TaskState
from kanboard_plan_sync.status import column_for_status


def _task(ref_key, status):
    return PlanTask(
        task_key=ref_key,
        task_reference=f"plan:{ref_key}",
        title=f"task {ref_key}",
        markdown_status=status,
        kanboard_column=column_for_status(status),
    )


def _manifest(tasks):
    return PlanManifest(
        plan_id="plan", plan_path="x", plan_title="Plan", tasks=tasks
    )


class DiffTest(unittest.TestCase):
    def test_empty_state_creates_project_and_tasks(self):
        m = _manifest([_task("A1", "todo"), _task("A2", "done")])
        ops = build_diff(m, SyncState())
        summary = summarize_diff(ops)
        self.assertEqual(summary.get(OP_CREATE_PROJECT), 1)
        self.assertEqual(summary.get(OP_CREATE_TASK), 2)
        # create_project is first
        self.assertEqual(ops[0].op, OP_CREATE_PROJECT)

    def test_synced_same_column_is_noop(self):
        m = _manifest([_task("A1", "todo")])
        state = SyncState(
            references={
                "plan:A1": TaskState(
                    kanboard_task_id=10,
                    kanboard_project_id=3,
                    last_synced_column="TODO",
                )
            }
        )
        ops = build_diff(m, state)
        # project already known -> no create_project
        self.assertNotIn(OP_CREATE_PROJECT, summarize_diff(ops))
        self.assertEqual(ops[0].op, OP_NOOP)

    def test_changed_column_is_move(self):
        m = _manifest([_task("A1", "done")])  # 완료
        state = SyncState(
            references={
                "plan:A1": TaskState(
                    kanboard_task_id=10,
                    kanboard_project_id=3,
                    last_synced_column="TODO",
                )
            }
        )
        ops = build_diff(m, state)
        move = [o for o in ops if o.op == OP_MOVE_TASK]
        self.assertEqual(len(move), 1)
        self.assertEqual(move[0].detail["from"], "TODO")
        self.assertEqual(move[0].detail["to"], "완료")

    def test_known_project_but_new_task_creates_task_only(self):
        m = _manifest([_task("A1", "todo"), _task("A2", "todo")])
        state = SyncState(
            references={
                "plan:A1": TaskState(
                    kanboard_task_id=10, kanboard_project_id=3, last_synced_column="TODO"
                )
            }
        )
        ops = build_diff(m, state)
        summary = summarize_diff(ops)
        self.assertNotIn(OP_CREATE_PROJECT, summary)
        self.assertEqual(summary.get(OP_CREATE_TASK), 1)  # only A2
        self.assertEqual(summary.get(OP_NOOP), 1)  # A1


if __name__ == "__main__":
    unittest.main()
