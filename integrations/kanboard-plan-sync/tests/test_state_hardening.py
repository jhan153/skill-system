import tempfile
import unittest
from pathlib import Path

from kanboard_plan_sync.models import PlanManifest, PlanTask
from kanboard_plan_sync.state import (
    StateError,
    SyncState,
    TaskState,
    load_state,
    save_state,
    state_path,
)


class StateHardeningTest(unittest.TestCase):
    def test_atomic_save_leaves_no_tmp(self):
        with tempfile.TemporaryDirectory() as d:
            s = SyncState()
            s.upsert("p:A1", TaskState(kanboard_task_id=1, kanboard_project_id=2))
            save_state(d, s)
            tmp = state_path(d).with_suffix(".json.tmp")
            self.assertFalse(tmp.exists())
            self.assertTrue(state_path(d).is_file())

    def test_corrupt_recovered_and_backed_up(self):
        with tempfile.TemporaryDirectory() as d:
            state_path(d).parent.mkdir(parents=True, exist_ok=True)
            state_path(d).write_text("{ not valid json", encoding="utf-8")
            recovered = load_state(d, recover=True)
            self.assertEqual(recovered.references, {})
            backup = state_path(d).with_suffix(".json.corrupt")
            self.assertTrue(backup.exists())

    def test_corrupt_raises_without_recover(self):
        with tempfile.TemporaryDirectory() as d:
            state_path(d).parent.mkdir(parents=True, exist_ok=True)
            state_path(d).write_text("{ bad", encoding="utf-8")
            with self.assertRaises(StateError):
                load_state(d, recover=False)


class DuplicateReferenceTest(unittest.TestCase):
    def test_detects_duplicates(self):
        def t(k):
            return PlanTask(k, f"p:{k}", k, "todo", "TODO")

        m = PlanManifest("p", "x", "P", tasks=[t("D5"), t("D5"), t("A1")])
        self.assertEqual(m.duplicate_references(), ["p:D5"])

    def test_no_duplicates(self):
        def t(k):
            return PlanTask(k, f"p:{k}", k, "todo", "TODO")

        m = PlanManifest("p", "x", "P", tasks=[t("A1"), t("A2")])
        self.assertEqual(m.duplicate_references(), [])


if __name__ == "__main__":
    unittest.main()
