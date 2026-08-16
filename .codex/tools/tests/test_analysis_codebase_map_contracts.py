from __future__ import annotations

import unittest
from pathlib import Path

import yaml


def find_bundle_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "source" / "skills").is_dir():
            return parent
        if (parent / ".codex" / "skills").is_dir():
            return parent
    raise RuntimeError("could not locate Skill System bundle root")


ROOT = find_bundle_root()
SOURCE = ROOT / "source"


def canonical(relative: str) -> Path:
    source_path = SOURCE / relative
    if source_path.is_file():
        return source_path
    runtime_path = ROOT / ".codex" / relative.removeprefix("platform/codex/")
    if runtime_path.is_file():
        return runtime_path
    raise FileNotFoundError(relative)


class AnalysisCodebaseMapContractTests(unittest.TestCase):
    def test_skill_payload_contains_only_map_assets(self) -> None:
        skill_root = canonical("skills/analysis-codebase-map/SKILL.md").parent
        observed = {
            path.relative_to(skill_root).as_posix()
            for path in skill_root.rglob("*")
            if path.is_file()
        }
        self.assertEqual(
            observed,
            {"SKILL.md", "reference.md", "agents/openai.yaml"},
        )

    def test_skill_is_read_only_and_honors_explicit_altitude(self) -> None:
        skill = canonical("skills/analysis-codebase-map/SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("An explicit user-requested `hld` or `lld` wins", skill)
        self.assertIn("writes: none by default", skill)
        self.assertIn("Generic codebase-analysis/report wording still returns", skill)
        for retired_surface in (
            "scripts/collect.sh",
            "scripts/report.py",
            "references/policy-default.json",
        ):
            self.assertNotIn(retired_surface, skill)

    def test_eval_cases_preserve_map_first_reporting_and_altitude_precedence(self) -> None:
        routing = yaml.safe_load(
            canonical("shared/eval/routing_cases.yaml").read_text(encoding="utf-8")
        )
        negative = yaml.safe_load(
            canonical("shared/eval/negative_routing_cases.yaml").read_text(
                encoding="utf-8"
            )
        )
        routing_cases = {case["case_id"]: case for case in routing["cases"]}
        negative_cases = {case["case_id"]: case for case in negative["cases"]}

        altitude_case = routing_cases[
            "route-analysis-codebase-map-explicit-hld-slice-001"
        ]
        self.assertEqual(
            altitude_case["expected_primary_skill"], "analysis-codebase-map"
        )
        self.assertIn(
            "honor_explicit_hld_altitude", altitude_case["expected_behaviors"]
        )
        self.assertIn(
            "override_explicit_hld_with_scope_default",
            altitude_case["forbidden_behaviors"],
        )

        report_case = negative_cases["hs-neg-008"]
        self.assertEqual(report_case["expected_primary_skill"], "analysis-codebase-map")
        self.assertIn("intentionally retired", report_case["quality_notes"])


if __name__ == "__main__":
    unittest.main()
