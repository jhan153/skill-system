from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


def load_pipeline():
    test_path = Path(__file__).resolve()
    for parent in test_path.parents:
        candidate = parent / "run_verification_pipeline.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("verification_pipeline_under_test", candidate)
            if spec is None or spec.loader is None:
                break
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise RuntimeError("could not locate run_verification_pipeline.py")


class VerificationPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.pipeline = load_pipeline()

    def report(self, profile: str, check_ids: set[str]) -> dict[str, object]:
        return {
            "profile": profile,
            "status": "PASS",
            "checks": [
                {"id": check_id, "status": "PASS", "required": True}
                for check_id in sorted(check_ids)
            ],
        }

    def test_release_execution_requires_solar_and_full_check_set(self) -> None:
        complete = self.report(
            "execution",
            self.pipeline.RELEASE_REQUIRED_CHECK_IDS["execution"],
        )
        self.assertIsNone(
            self.pipeline.validate_profile_report(complete, "execution", release=True)
        )

        minimal = self.report("execution", {"hook_runtime_smoke"})
        error = self.pipeline.validate_profile_report(minimal, "execution", release=True)
        self.assertIn("missing required checks", error or "")
        self.assertIn("solar_forward_eval_9_1_0", error or "")

    def test_normal_profile_mirrors_optional_failure_semantics(self) -> None:
        report = {
            "profile": "core",
            "status": "PASS",
            "checks": [
                {"id": "required", "status": "PASS", "required": True},
                {"id": "optional", "status": "FAIL", "required": False},
            ],
        }
        self.assertIsNone(
            self.pipeline.validate_profile_report(report, "core", release=False)
        )
        release_report = self.report(
            "core",
            self.pipeline.RELEASE_REQUIRED_CHECK_IDS["core"],
        )
        for check in release_report["checks"]:
            if check["id"] == "field_feedback":
                check["required"] = False
                check["status"] = "FAIL"
        self.assertIn(
            "non-PASS checks",
            self.pipeline.validate_profile_report(release_report, "core", release=True) or "",
        )

    def test_malformed_pass_report_is_rejected(self) -> None:
        error = self.pipeline.validate_profile_report(
            {"status": "PASS"},
            "core",
            release=False,
        )
        self.assertIn("profile identity", error or "")


if __name__ == "__main__":
    unittest.main()
