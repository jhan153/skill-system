from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


class WorkHorizonPolicyTests(unittest.TestCase):
    def run_tool(self, *args: str) -> subprocess.CompletedProcess[str]:
        env = dict(os.environ)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [sys.executable, ".codex/tools/check_work_horizon_policy.py", *args],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=30,
        )

    def test_current_bundle_passes(self) -> None:
        result = self.run_tool()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_missing_task_ledger_horizon_fails(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            root = Path(tmp)
            for ns in [".codex", ".claude"]:
                skill = root / ns / "skills" / "workflow-task-ledger"
                (skill / "agents").mkdir(parents=True)
                (skill / "SKILL.md").write_text("# Task\n\n## Routing Card\n- role: execution_modifier\n", encoding="utf-8")
                (skill / "agents" / "openai.yaml").write_text(
                    (
                        "interface:\n"
                        "  display_name: Task\n"
                        "policy:\n"
                        "  invocation_surface: support_only\n"
                        "  allow_implicit_invocation: false\n"
                        "  may_own_execution: false\n"
                    ),
                    encoding="utf-8",
                )
            result = self.run_tool("--root", str(root), "--allow-partial")
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("work_horizon.level", result.stdout)


if __name__ == "__main__":
    unittest.main()
