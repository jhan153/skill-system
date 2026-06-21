import unittest

from kanboard_plan_sync.parser import parse_plan_text, plan_id_from_path

SAMPLE = """# Sample Plan

## 5) Something
- [x] not in todo section, must be ignored

## 12) TODO
- [x] `done` finished task (D5)
- [ ] `todo` pending KPS-001 work
- [ ] `blocked` waiting on input
- [ ] plain unkeyed item
- [x] checkbox-only done item

## 13) Next
- [ ] should not be parsed
"""


class ParserTest(unittest.TestCase):
    def setUp(self):
        self.title, self.tasks = parse_plan_text(SAMPLE, plan_id="sample", plan_path="x")

    def test_plan_id_from_path(self):
        self.assertEqual(
            plan_id_from_path("/a/b/2026-06-17-kanboard-plan-sync-core-mcp.md"),
            "2026-06-17-kanboard-plan-sync-core-mcp",
        )

    def test_title_and_section_scoping(self):
        self.assertEqual(self.title, "Sample Plan")
        # only the 5 TODO-section items, not section 5 or 13
        self.assertEqual(len(self.tasks), 5)

    def test_explicit_paren_key(self):
        t = self.tasks[0]
        self.assertEqual(t.task_key, "D5")
        self.assertEqual(t.task_reference, "sample:D5")
        self.assertFalse(t.is_candidate)
        self.assertEqual(t.markdown_status, "done")
        self.assertEqual(t.kanboard_column, "완료")
        self.assertNotIn("(D5)", t.title)

    def test_explicit_dash_key(self):
        t = self.tasks[1]
        self.assertEqual(t.task_key, "KPS-001")
        self.assertFalse(t.is_candidate)
        self.assertEqual(t.markdown_status, "todo")
        self.assertIn("pending", t.title)
        self.assertIn("work", t.title)
        self.assertNotIn("KPS-001", t.title)

    def test_token_overrides_checkbox(self):
        # `[ ]` checkbox but `blocked` token -> blocked wins
        t = self.tasks[2]
        self.assertEqual(t.markdown_status, "blocked")
        self.assertEqual(t.kanboard_column, "보류")
        self.assertTrue(t.is_candidate)
        self.assertEqual(t.task_key, "T03")

    def test_auto_candidate_key_from_checkbox(self):
        t_todo = self.tasks[3]
        self.assertEqual(t_todo.markdown_status, "todo")  # [ ] no token
        self.assertTrue(t_todo.is_candidate)
        self.assertEqual(t_todo.task_key, "T04")

        t_done = self.tasks[4]
        self.assertEqual(t_done.markdown_status, "done")  # [x] no token
        self.assertTrue(t_done.is_candidate)
        self.assertEqual(t_done.task_key, "T05")

    def test_source_lines_recorded(self):
        for t in self.tasks:
            self.assertGreater(t.source_line, 0)

    def test_no_todo_section(self):
        title, tasks = parse_plan_text("# Only Title\n\nbody\n", "p", "x")
        self.assertEqual(title, "Only Title")
        self.assertEqual(tasks, [])


if __name__ == "__main__":
    unittest.main()
