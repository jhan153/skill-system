import tempfile
import unittest
from pathlib import Path

from kanboard_plan_sync import registry


class RegistryTest(unittest.TestCase):
    def _reg(self, d):
        return str(Path(d) / "workspaces.yml")

    def test_empty_when_absent(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(registry.load_workspaces(self._reg(d)), [])
            self.assertEqual(registry.list_workspaces(self._reg(d)), [])

    def test_register_is_idempotent_and_normalized(self):
        with tempfile.TemporaryDirectory() as d:
            reg = self._reg(d)
            ws = str(Path(d).resolve())
            registry.register(ws, reg)
            # registering again (with a trailing slash) does not duplicate
            registry.register(ws + "/", reg)
            items = registry.load_workspaces(reg)
            self.assertEqual(items, [ws])

    def test_unregister(self):
        with tempfile.TemporaryDirectory() as d:
            reg = self._reg(d)
            a, b = str(Path(d).resolve()), str((Path(d) / "..").resolve())
            registry.register(a, reg)
            registry.register(b, reg)
            registry.unregister(a, reg)
            self.assertEqual(registry.load_workspaces(reg), [b])

    def test_list_reports_presence(self):
        with tempfile.TemporaryDirectory() as d:
            reg = self._reg(d)
            registry.register(d, reg)
            registry.register("/no/such/dir-xyz", reg)
            rows = registry.list_workspaces(reg)
            by_path = {r["path"]: r for r in rows}
            self.assertTrue(by_path[str(Path(d).resolve())]["exists"])
            self.assertFalse(by_path["/no/such/dir-xyz"]["exists"])


if __name__ == "__main__":
    unittest.main()
