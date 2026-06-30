from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


class InvocationSurfacePolicyTests(unittest.TestCase):
    def run_tool(self, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        env = dict(os.environ)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [sys.executable, ".codex/tools/check_invocation_surface_policy.py", *args],
            cwd=cwd or ROOT,
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

    def test_implicit_non_router_fails(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            root = Path(tmp)
            skill = root / ".codex" / "skills" / "sample-skill"
            (skill / "agents").mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "# Sample\n\n## Routing Card\n- role: primary\n",
                encoding="utf-8",
            )
            (skill / "agents" / "openai.yaml").write_text(
                (
                    "interface:\n"
                    "  display_name: Sample\n"
                    "policy:\n"
                    "  invocation_surface: explicit_procedure\n"
                    "  allow_implicit_invocation: true\n"
                    "  may_own_execution: true\n"
                ),
                encoding="utf-8",
            )
            result = self.run_tool("--root", str(root))
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("implicit invocation is only allowed", result.stdout)


if __name__ == "__main__":
    unittest.main()
