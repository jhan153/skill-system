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

    def write_projected_skill(
        self,
        root: Path,
        namespace: str,
        *,
        allow_implicit: bool,
        disable_model_invocation: bool = False,
    ) -> None:
        skill = root / namespace / "skills" / "sample-skill"
        (skill / "agents").mkdir(parents=True)
        disable = "disable-model-invocation: true\n" if disable_model_invocation else ""
        (skill / "SKILL.md").write_text(
            f"---\nname: sample-skill\ndescription: Sample.\n{disable}---\n\n"
            "## Routing Card\n- role: primary\n",
            encoding="utf-8",
        )
        (skill / "agents" / "openai.yaml").write_text(
            (
                "interface:\n  display_name: Sample\n"
                "policy:\n"
                "  invocation_surface: explicit_procedure\n"
                f"  allow_implicit_invocation: {str(allow_implicit).lower()}\n"
                "  may_own_execution: true\n"
            ),
            encoding="utf-8",
        )

    def test_current_bundle_passes(self) -> None:
        result = self.run_tool()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_intent_matched_implicit_procedure_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
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
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_governed_loop_skill_must_remain_explicit_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / ".codex" / "skills" / "workflow-loop-runner"
            (skill / "agents").mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "# Workflow Loop Runner\n\n## Routing Card\n- role: primary\n",
                encoding="utf-8",
            )
            (skill / "agents" / "openai.yaml").write_text(
                (
                    "interface:\n"
                    "  display_name: Workflow Loop Runner\n"
                    "policy:\n"
                    "  invocation_surface: explicit_procedure\n"
                    "  allow_implicit_invocation: true\n"
                    "  may_own_execution: true\n"
                ),
                encoding="utf-8",
            )
            result = self.run_tool("--root", str(root))
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("must remain explicit-only", result.stdout)

    def test_current_intent_matched_cohort_is_implicitly_exposed(self) -> None:
        expected = {
            "coordination-handoff",
            "design-layout-translator",
            "design-ui-decomposer",
            "skill-system-repo-adapter",
            "workflow-bug-fix",
            "workflow-comment-maintenance",
            "workflow-dependency-upgrade",
            "workflow-implementation",
            "workflow-plan-runner",
            "workflow-prototype",
            "workflow-recovery",
            "workflow-refactor-safely",
            "workflow-source-maintenance",
        }
        for skill_id in sorted(expected):
            with self.subTest(skill=skill_id):
                metadata = (
                    ROOT / ".codex" / "skills" / skill_id / "agents" / "openai.yaml"
                ).read_text(encoding="utf-8")
                self.assertIn("allow_implicit_invocation: true", metadata)

    def test_approved_implicit_execution_skill_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / ".codex" / "skills" / "design-frontend"
            (skill / "agents").mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "# Design Frontend\n\n## Routing Card\n- role: primary\n",
                encoding="utf-8",
            )
            (skill / "agents" / "openai.yaml").write_text(
                (
                    "interface:\n"
                    "  display_name: Design Frontend\n"
                    "policy:\n"
                    "  invocation_surface: explicit_procedure\n"
                    "  allow_implicit_invocation: true\n"
                    "  may_own_execution: true\n"
                ),
                encoding="utf-8",
            )
            result = self.run_tool("--root", str(root))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_implicit_router_can_handoff_to_implicit_specialist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            router = root / ".codex" / "skills" / "sample-router"
            target = root / ".codex" / "skills" / "sample-target"
            (router / "agents").mkdir(parents=True)
            (target / "agents").mkdir(parents=True)
            (router / "SKILL.md").write_text(
                (
                    "# Router\n\n## Routing Card\n- role: router\n\n"
                    "## Invocation Contract\n"
                    "- automatic_handoff_targets: `sample-target`\n"
                    "- explicit_recommendation_targets: none\n"
                ),
                encoding="utf-8",
            )
            (router / "agents" / "openai.yaml").write_text(
                (
                    "interface:\n  display_name: Router\n"
                    "policy:\n"
                    "  invocation_surface: selective_router\n"
                    "  allow_implicit_invocation: true\n"
                    "  may_own_execution: false\n"
                    "  may_write: false\n"
                ),
                encoding="utf-8",
            )
            (target / "SKILL.md").write_text(
                "# Target\n\n## Routing Card\n- role: primary\n",
                encoding="utf-8",
            )
            (target / "agents" / "openai.yaml").write_text(
                (
                    "interface:\n  display_name: Target\n"
                    "policy:\n"
                    "  invocation_surface: explicit_procedure\n"
                    "  allow_implicit_invocation: true\n"
                    "  may_own_execution: true\n"
                ),
                encoding="utf-8",
            )
            result = self.run_tool("--root", str(root))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_router_may_recommend_globally_implicit_target_without_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            router = root / ".codex" / "skills" / "sample-router"
            automatic = root / ".codex" / "skills" / "sample-auto"
            target = root / ".codex" / "skills" / "sample-target"
            (router / "agents").mkdir(parents=True)
            (automatic / "agents").mkdir(parents=True)
            (target / "agents").mkdir(parents=True)
            (router / "SKILL.md").write_text(
                (
                    "# Router\n\n## Routing Card\n- role: router\n\n"
                    "## Invocation Contract\n"
                    "- automatic_handoff_targets: `sample-auto`\n"
                    "- explicit_recommendation_targets: `sample-target`\n"
                ),
                encoding="utf-8",
            )
            (router / "agents" / "openai.yaml").write_text(
                (
                    "interface:\n  display_name: Router\n"
                    "policy:\n"
                    "  invocation_surface: selective_router\n"
                    "  allow_implicit_invocation: true\n"
                    "  may_own_execution: false\n"
                    "  may_write: false\n"
                ),
                encoding="utf-8",
            )
            (automatic / "SKILL.md").write_text(
                "# Automatic\n\n## Routing Card\n- role: primary\n",
                encoding="utf-8",
            )
            (automatic / "agents" / "openai.yaml").write_text(
                (
                    "interface:\n  display_name: Automatic\n"
                    "policy:\n"
                    "  invocation_surface: explicit_procedure\n"
                    "  allow_implicit_invocation: true\n"
                    "  may_own_execution: true\n"
                ),
                encoding="utf-8",
            )
            (target / "SKILL.md").write_text(
                "# Target\n\n## Routing Card\n- role: primary\n",
                encoding="utf-8",
            )
            (target / "agents" / "openai.yaml").write_text(
                (
                    "interface:\n  display_name: Target\n"
                    "policy:\n"
                    "  invocation_surface: explicit_procedure\n"
                    "  allow_implicit_invocation: true\n"
                    "  may_own_execution: true\n"
                ),
                encoding="utf-8",
            )
            result = self.run_tool("--root", str(root))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_implicit_router_rejects_hidden_automatic_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            router = root / ".codex" / "skills" / "sample-router"
            target = root / ".codex" / "skills" / "sample-target"
            (router / "agents").mkdir(parents=True)
            (target / "agents").mkdir(parents=True)
            (router / "SKILL.md").write_text(
                (
                    "# Router\n\n## Routing Card\n- role: router\n\n"
                    "## Invocation Contract\n"
                    "- automatic_handoff_targets: `sample-target`\n"
                    "- explicit_recommendation_targets: none\n"
                ),
                encoding="utf-8",
            )
            (router / "agents" / "openai.yaml").write_text(
                (
                    "interface:\n  display_name: Router\n"
                    "policy:\n"
                    "  invocation_surface: selective_router\n"
                    "  allow_implicit_invocation: true\n"
                    "  may_own_execution: false\n"
                    "  may_write: false\n"
                ),
                encoding="utf-8",
            )
            (target / "SKILL.md").write_text(
                "# Target\n\n## Routing Card\n- role: primary\n",
                encoding="utf-8",
            )
            (target / "agents" / "openai.yaml").write_text(
                (
                    "interface:\n  display_name: Target\n"
                    "policy:\n"
                    "  invocation_surface: explicit_procedure\n"
                    "  allow_implicit_invocation: false\n"
                    "  may_own_execution: true\n"
                ),
                encoding="utf-8",
            )
            result = self.run_tool("--root", str(root))
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("automatic handoff target is not implicitly invocable", result.stdout)

    def test_claude_explicit_only_skill_requires_disable_projection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_projected_skill(root, ".codex", allow_implicit=False)
            self.write_projected_skill(root, ".claude", allow_implicit=False)
            result = self.run_tool("--root", str(root))
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Claude disable-model-invocation must be true", result.stdout)

    def test_claude_implicit_skill_rejects_disable_projection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_projected_skill(root, ".codex", allow_implicit=True)
            self.write_projected_skill(
                root,
                ".claude",
                allow_implicit=True,
                disable_model_invocation=True,
            )
            result = self.run_tool("--root", str(root))
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Claude disable-model-invocation must be absent", result.stdout)


if __name__ == "__main__":
    unittest.main()
