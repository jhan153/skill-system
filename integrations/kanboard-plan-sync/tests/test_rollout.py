import tempfile
import unittest
from pathlib import Path

from kanboard_plan_sync import registry
from kanboard_plan_sync.bootstrap import init_workspace
from kanboard_plan_sync.rollout import sync_all
from kanboard_plan_sync.state import load_state

from tests._fakes import FakeKanboard


def _make_repo(parent, name, n_plans=2):
    root = Path(parent) / name
    (root / "docs" / "plan").mkdir(parents=True)
    for i in range(n_plans):
        (root / "docs" / "plan" / f"2026-0{i+1}-01-{name}{i}.md").write_text(
            f"# {name} {i}\n\n## 12) TODO\n- [ ] `todo` task (P{i})\n- [x] `done` done (Q{i})\n",
            encoding="utf-8",
        )
    init_workspace(str(root))
    return root


class SyncAllTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        self.reg = str(self.base / "workspaces.yml")
        self.repo_a = _make_repo(self.base, "repoA", n_plans=2)
        self.repo_b = _make_repo(self.base, "repoB", n_plans=1)
        registry.register(str(self.repo_a), self.reg)
        registry.register(str(self.repo_b), self.reg)

    def tearDown(self):
        self._tmp.cleanup()

    def test_dry_run_aggregates_all_workspaces(self):
        rep = sync_all(apply=False, registry_file=self.reg)
        self.assertEqual(rep["mode"], "dry-run")
        self.assertEqual(rep["totals"]["workspaces"], 2)
        self.assertEqual(rep["totals"]["plans"], 3)  # 2 + 1
        self.assertEqual(rep["totals"]["errors"], 0)
        for ws in rep["workspaces"]:
            for pr in ws["plans"]:
                self.assertEqual(pr["status"], "dry_run")
                self.assertIn("create_task", pr["summary"])

    def test_workspace_root_filter_scopes_to_one(self):
        # Session-start autosync targets only the active workspace, not all boards.
        full = sync_all(apply=False, registry_file=self.reg)
        scoped = sync_all(apply=False, registry_file=self.reg, workspace_root=str(self.repo_a))
        unmatched = sync_all(apply=False, registry_file=self.reg, workspace_root=str(self.repo_a) + "-nope")
        self.assertEqual(full["totals"]["workspaces"], 2)
        self.assertEqual(scoped["totals"]["workspaces"], 1)
        self.assertEqual(unmatched["totals"]["workspaces"], 0)

    def test_missing_config_is_isolated(self):
        # register a bare dir with no config
        bare = self.base / "bare"
        bare.mkdir()
        registry.register(str(bare), self.reg)
        rep = sync_all(apply=False, registry_file=self.reg)
        errs = [w for w in rep["workspaces"] if w.get("error")]
        self.assertEqual(len(errs), 1)
        self.assertEqual(rep["totals"]["workspaces"], 3)

    def test_skipped_plan_flag(self):
        # turn off sync for one plan in repoA config
        cfg = (self.repo_a / ".kanboard-plan.yml").read_text()
        cfg = cfg.replace("    sync: true\n", "    sync: false\n", 1)
        (self.repo_a / ".kanboard-plan.yml").write_text(cfg)
        rep = sync_all(apply=False, registry_file=self.reg)
        self.assertGreaterEqual(rep["totals"]["skipped"], 1)

    def test_apply_with_fake_client_writes_and_saves_state(self):
        clients = {}

        def factory(config):
            c = FakeKanboard()
            clients[config.name] = c
            return c

        rep = sync_all(apply=True, registry_file=self.reg, client_factory=factory)
        self.assertEqual(rep["mode"], "apply")
        self.assertGreater(rep["totals"]["applied"], 0)
        self.assertEqual(rep["totals"]["errors"], 0)
        # repoA: 2 plans => 1 Project (workspace) with 2 swimlanes
        a = clients["repoA"]
        self.assertEqual(len(a.projects), 1)
        self.assertEqual(list(a.projects.values())[0]["name"], "repoA")
        sl_names = list(list(a.swimlanes.values())[0].values())
        self.assertEqual(sum(1 for n in sl_names if n != "Default"), 2)
        # state persisted for repoA
        self.assertGreater(len(load_state(str(self.repo_a)).references), 0)


if __name__ == "__main__":
    unittest.main()
