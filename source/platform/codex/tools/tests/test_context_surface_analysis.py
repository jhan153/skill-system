from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


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

    def test_json_report_contains_router_surface(self) -> None:
        result = self.run_tool("--format", "json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        data = json.loads(result.stdout)
        analysis_router = next(item for item in data["metrics"] if item["skill_id"] == "analysis-router")
        self.assertEqual(analysis_router["invocation_surface"], "selective_router")
        self.assertTrue(analysis_router["allow_implicit_invocation"])

    def test_markdown_report_is_advisory(self) -> None:
        result = self.run_tool("--format", "markdown", "--top", "3")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("advisory only", result.stdout)
        self.assertIn("| Skill | Surface |", result.stdout)


if __name__ == "__main__":
    unittest.main()
