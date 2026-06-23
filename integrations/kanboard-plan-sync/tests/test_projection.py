import unittest

from kanboard_plan_sync.models import PlanManifest, PlanTask
from kanboard_plan_sync.projection import (
    CANDIDATE_TAG,
    PLAN_SYNC_TAG,
    kanban_card_title,
    status_color,
    task_projection,
)
from kanboard_plan_sync.status import column_for_status


def _task(key, status, candidate=False, title=None):
    return PlanTask(
        task_key=key,
        task_reference=f"plan:{key}",
        title=title or f"task {key}",
        markdown_status=status,
        kanboard_column=column_for_status(status),
        is_candidate=candidate,
        source_line=10,
    )


class ProjectionTest(unittest.TestCase):
    def test_status_colors(self):
        self.assertEqual(status_color("todo"), "grey")
        self.assertEqual(status_color("doing"), "blue")
        self.assertEqual(status_color("review"), "purple")
        self.assertEqual(status_color("blocked"), "red")
        self.assertEqual(status_color("done"), "green")
        self.assertEqual(status_color("???"), "grey")  # safe default

    def test_projection_fields(self):
        m = PlanManifest(plan_id="plan", plan_path="x", plan_title="P", tasks=[])
        p = task_projection(m, _task("D5", "done"))
        self.assertEqual(p["reference"], "plan:D5")
        self.assertEqual(p["column"], "완료")
        self.assertEqual(p["color_id"], "green")
        self.assertIn(PLAN_SYNC_TAG, p["tags"])
        self.assertIn("plan", p["tags"])
        self.assertIn("status:done", p["tags"])
        self.assertNotIn(CANDIDATE_TAG, p["tags"])
        self.assertIn("plan:D5", p["description"])
        self.assertIn("Completion Gate", p["description"])
        self.assertEqual(p["title"], "task D5")

    def test_candidate_tag_and_note(self):
        m = PlanManifest(plan_id="plan", plan_path="x", plan_title="P", tasks=[])
        p = task_projection(m, _task("T01", "todo", candidate=True))
        self.assertIn(CANDIDATE_TAG, p["tags"])
        self.assertIn("candidate", p["description"].lower())

    def test_kanban_title_strips_plan_markup(self):
        task = _task(
            "A1",
            "todo",
            title="- [ ] `todo` Phase 2: [Ship board update](docs/plan/x.md)",
        )
        self.assertEqual(kanban_card_title(task), "Ship board update")


if __name__ == "__main__":
    unittest.main()
