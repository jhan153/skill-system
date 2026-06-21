import tempfile
import unittest
from pathlib import Path

from kanboard_plan_sync.bootstrap import init_workspace
from kanboard_plan_sync.config import load_config


def _make_repo(d, n_plans=2):
    root = Path(d)
    (root / "docs" / "plan").mkdir(parents=True)
    for i in range(n_plans):
        (root / "docs" / "plan" / f"2026-0{i+1}-01-plan{i}.md").write_text(
            f"# Plan {i}\n\n## 12) TODO\n- [ ] `todo` task (P{i})\n", encoding="utf-8"
        )
    return root


class InitWorkspaceTest(unittest.TestCase):
    def test_creates_config_and_state_and_loads(self):
        with tempfile.TemporaryDirectory() as d:
            root = _make_repo(d)
            rep = init_workspace(str(root))
            self.assertEqual(rep["status"], "created")
            self.assertEqual(rep["plan_count"], 2)
            self.assertTrue((root / ".kanboard-plan.yml").is_file())
            self.assertTrue((root / ".kanboard-plan" / "state.json").is_file())

            cfg = load_config(str(root))
            self.assertEqual(cfg.name, root.name)
            self.assertEqual(len(cfg.plans), 2)
            self.assertEqual(cfg.plans[0].kanboard_project_strategy, "workspace-project")
            self.assertTrue(cfg.plans[0].sync)

    def test_does_not_clobber_existing_without_force(self):
        with tempfile.TemporaryDirectory() as d:
            root = _make_repo(d)
            (root / ".kanboard-plan.yml").write_text("workspace:\n  name: hand\n", encoding="utf-8")
            rep = init_workspace(str(root))
            self.assertEqual(rep["status"], "exists")
            self.assertFalse(rep["config_written"])
            # hand-authored config preserved
            self.assertIn("name: hand", (root / ".kanboard-plan.yml").read_text())

    def test_force_regenerates(self):
        with tempfile.TemporaryDirectory() as d:
            root = _make_repo(d)
            (root / ".kanboard-plan.yml").write_text("workspace:\n  name: hand\n", encoding="utf-8")
            rep = init_workspace(str(root), force=True)
            self.assertEqual(rep["status"], "forced")
            self.assertTrue(rep["config_written"])
            cfg = load_config(str(root))
            self.assertEqual(len(cfg.plans), 2)

    def test_missing_dir_errors(self):
        rep = init_workspace("/no/such/repo-xyz")
        self.assertEqual(rep["status"], "error")


if __name__ == "__main__":
    unittest.main()
