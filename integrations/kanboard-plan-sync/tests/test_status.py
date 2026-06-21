import unittest

from kanboard_plan_sync.status import (
    column_for_status,
    normalize_status,
    status_for_column,
)


class StatusMappingTest(unittest.TestCase):
    def test_token_aliases_normalize(self):
        self.assertEqual(normalize_status("[ ]"), "todo")
        self.assertEqual(normalize_status("[x]"), "done")
        self.assertEqual(normalize_status("[X]"), "done")  # case-insensitive
        self.assertEqual(normalize_status("doing"), "doing")
        self.assertEqual(normalize_status("[blocked]"), "blocked")
        self.assertEqual(normalize_status("review"), "review")

    def test_unknown_token_is_none(self):
        self.assertIsNone(normalize_status("frobnicate"))
        self.assertIsNone(normalize_status(None))

    def test_status_to_column(self):
        self.assertEqual(column_for_status("todo"), "TODO")
        self.assertEqual(column_for_status("doing"), "진행중")
        self.assertEqual(column_for_status("review"), "검토 필요")
        self.assertEqual(column_for_status("blocked"), "보류")
        self.assertEqual(column_for_status("done"), "완료")

    def test_column_to_status_roundtrip(self):
        for status in ("todo", "doing", "review", "blocked", "done"):
            self.assertEqual(status_for_column(column_for_status(status)), status)

    def test_unknown_column_is_none(self):
        self.assertIsNone(status_for_column("Backlog"))
        self.assertIsNone(status_for_column(None))


if __name__ == "__main__":
    unittest.main()
