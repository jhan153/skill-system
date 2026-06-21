import tempfile
import unittest
from pathlib import Path

from kanboard_plan_sync.config import parse_config
from kanboard_plan_sync.manifest import build_manifest

PLAN_TEXT = """# Demo Plan

## 12) TODO
- [ ] `todo` first task (A1)
- [x] `done` second task (A2)
"""


class ManifestTest(unittest.TestCase):
    def _write_plan(self, root: Path) -> Path:
        plan_dir = root / "docs" / "plan"
        plan_dir.mkdir(parents=True)
        plan = plan_dir / "2026-01-01-demo.md"
        plan.write_text(PLAN_TEXT, encoding="utf-8")
        return plan

    def test_manifest_without_config(self):
        with tempfile.TemporaryDirectory() as d:
            plan = self._write_plan(Path(d))
            m = build_manifest(str(plan))
            self.assertEqual(m.plan_id, "2026-01-01-demo")
            self.assertEqual(m.plan_title, "Demo Plan")
            self.assertEqual(len(m.tasks), 2)
            self.assertEqual(m.plan_type, "short-term")  # default
            d2 = m.to_dict()
            self.assertEqual(d2["task_count"], 2)
            self.assertEqual(d2["candidate_count"], 0)  # both keyed

    def test_manifest_uses_config_metadata(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            plan = self._write_plan(root)
            raw = {
                "workspace": {"name": "demo-ws"},
                "plans": [
                    {
                        "path": "docs/plan/2026-01-01-demo.md",
                        "plan_type": "long-term",
                        "parent_plan_id": "parent-x",
                        "kanboard_project_strategy": "ops-swimlane",
                    }
                ],
            }
            cfg = parse_config(raw, workspace_root=str(root), config_path="x")
            m = build_manifest(str(plan), config=cfg)
            self.assertEqual(m.plan_type, "long-term")
            self.assertEqual(m.parent_plan_id, "parent-x")
            self.assertEqual(m.kanboard_project_strategy, "ops-swimlane")


if __name__ == "__main__":
    unittest.main()
