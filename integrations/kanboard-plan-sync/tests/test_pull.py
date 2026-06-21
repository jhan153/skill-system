import unittest

from kanboard_plan_sync.models import (
    PULL_COMPLETION_CANDIDATE,
    PULL_DELETION_CANDIDATE,
    PULL_DEMOTION_CANDIDATE,
    PULL_IN_SYNC,
    PULL_NEW_ISSUE_CANDIDATE,
    PULL_SAFE_DEMOTION,
    PlanManifest,
    PlanTask,
)
from kanboard_plan_sync.pull import classify_pull, summarize_pull
from kanboard_plan_sync.state import SyncState, TaskState
from kanboard_plan_sync.status import column_for_status


def _task(key, status):
    return PlanTask(
        task_key=key,
        task_reference=f"plan:{key}",
        title=key,
        markdown_status=status,
        kanboard_column=column_for_status(status),
    )


class PullClassifierTest(unittest.TestCase):
    def _by_ref(self, candidates):
        return {c.task_reference: c for c in candidates}

    def test_classifications(self):
        manifest = PlanManifest(
            plan_id="plan",
            plan_path="x",
            plan_title="Plan",
            tasks=[
                _task("A", "done"),  # board 완료 -> in_sync
                _task("B", "todo"),  # board 완료 -> completion_candidate
                _task("C", "done"),  # board 진행중 -> safe_demotion
                _task("E", "done"),  # board TODO -> demotion_candidate
                _task("F", "todo"),  # board 진행중 -> forward (completion_candidate)
                _task("D", "doing"),  # missing on board, was synced -> deletion
            ],
        )
        board = [
            {"reference": "plan:A", "column": "완료", "task_id": 1},
            {"reference": "plan:B", "column": "완료", "task_id": 2},
            {"reference": "plan:C", "column": "진행중", "task_id": 3},
            {"reference": "plan:E", "column": "TODO", "task_id": 5},
            {"reference": "plan:F", "column": "진행중", "task_id": 6},
            {"reference": "plan:X", "column": "TODO", "task_id": 9},  # new issue
            {"reference": "", "column": "TODO", "task_id": 10},  # manual card
        ]
        state = SyncState(
            references={
                "plan:D": TaskState(kanboard_task_id=4, kanboard_project_id=1)
            }
        )
        candidates = classify_pull(manifest, board, state)
        by_ref = self._by_ref(candidates)

        self.assertEqual(by_ref["plan:A"].kind, PULL_IN_SYNC)
        self.assertEqual(by_ref["plan:B"].kind, PULL_COMPLETION_CANDIDATE)
        self.assertEqual(by_ref["plan:C"].kind, PULL_SAFE_DEMOTION)
        self.assertEqual(by_ref["plan:E"].kind, PULL_DEMOTION_CANDIDATE)
        self.assertEqual(by_ref["plan:F"].kind, PULL_COMPLETION_CANDIDATE)
        self.assertEqual(by_ref["plan:D"].kind, PULL_DELETION_CANDIDATE)
        self.assertEqual(by_ref["plan:X"].kind, PULL_NEW_ISSUE_CANDIDATE)
        # manual card with no reference
        manual = [c for c in candidates if c.task_reference is None]
        self.assertEqual(len(manual), 1)
        self.assertEqual(manual[0].kind, PULL_NEW_ISSUE_CANDIDATE)

    def test_unsynced_missing_task_is_not_a_candidate(self):
        # task in markdown, never pushed, absent on board -> no pull signal
        manifest = PlanManifest(
            plan_id="plan", plan_path="x", plan_title="P", tasks=[_task("Z", "todo")]
        )
        candidates = classify_pull(manifest, [], SyncState())
        self.assertEqual(candidates, [])

    def test_summary_counts(self):
        manifest = PlanManifest(
            plan_id="plan", plan_path="x", plan_title="P", tasks=[_task("A", "done")]
        )
        board = [{"reference": "plan:A", "column": "완료", "task_id": 1}]
        summary = summarize_pull(classify_pull(manifest, board, SyncState()))
        self.assertEqual(summary, {PULL_IN_SYNC: 1})


if __name__ == "__main__":
    unittest.main()
