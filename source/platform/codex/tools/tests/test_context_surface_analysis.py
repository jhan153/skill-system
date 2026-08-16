from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


def find_bundle_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / ".codex" / "tools" / "analyze_context_surface.py").is_file():
            return parent
    raise RuntimeError("could not locate bundle root with generated .codex tools")


ROOT = find_bundle_root()


class ContextSurfaceAnalysisTests(unittest.TestCase):
    def run_tool(self, *args: str) -> subprocess.CompletedProcess[str]:
        env = dict(os.environ)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [sys.executable, ".codex/tools/analyze_context_surface.py", *args],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=30,
        )

    def test_json_report_contains_current_skill_surface(self) -> None:
        result = self.run_tool("--format", "json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        data = json.loads(result.stdout)
        analysis_skill = next(item for item in data["metrics"] if item["skill_id"] == "analysis-bug")
        self.assertEqual(analysis_skill["invocation_surface"], "explicit_procedure")
        self.assertTrue(analysis_skill["allow_implicit_invocation"])
        for key in [
            "reference_fanout_risk",
            "cache_stability_risk",
            "volatile_context_risk",
            "support_attachment_risk",
            "token_cost_risk_score",
        ]:
            self.assertIn(key, analysis_skill)
            self.assertIsInstance(analysis_skill[key], int)

    def test_large_selective_reference_library_is_not_scored_as_eager_loading(self) -> None:
        result = self.run_tool("--format", "json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        data = json.loads(result.stdout)
        package = next(item for item in data["metrics"] if item["skill_id"] == "plan-long-term-package")
        self.assertGreater(package["reference_count"], 10)
        self.assertGreater(package["reference_inventory_risk"], 0)
        self.assertTrue(package["selective_reference_admission"])
        self.assertLess(package["reference_fanout_risk"], package["reference_inventory_risk"])

    def test_support_only_skills_get_attachment_risk(self) -> None:
        result = self.run_tool("--format", "json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        data = json.loads(result.stdout)
        handoff = next(item for item in data["metrics"] if item["skill_id"] == "plan-task-handoff")
        self.assertEqual(handoff["invocation_surface"], "support_only")
        self.assertGreater(handoff["support_attachment_risk"], 0)

    def test_markdown_report_is_advisory(self) -> None:
        result = self.run_tool("--format", "markdown", "--top", "3")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("advisory only", result.stdout)
        self.assertIn("| Skill | Surface |", result.stdout)
        self.assertIn("Token-cost risk", result.stdout)


if __name__ == "__main__":
    unittest.main()
