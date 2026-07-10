from __future__ import annotations

import importlib.util
import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path


def load_runner():
    test_path = Path(__file__).resolve()
    for parent in test_path.parents:
        if parent.name == ".codex":
            candidate = parent / "tools" / "run_behavior_evals.py"
        elif parent.name == "source":
            candidate = parent / "platform" / "codex" / "tools" / "run_behavior_evals.py"
        else:
            continue
        if candidate.is_file():
            sys.path.insert(0, str(candidate.parent))
            spec = importlib.util.spec_from_file_location("behavior_eval_route_class_runner", candidate)
            if spec is None or spec.loader is None:
                break
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise RuntimeError("could not locate run_behavior_evals.py")


class BehaviorEvalRouteClassTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = load_runner()

    def run_payload(self, *, observed_route_class: str, evidence_value: str) -> list[str]:
        case = {
            "case_id": "external-skill-route",
            "expected_primary_skill": None,
            "expected_route_class": "external_system_skill_creator",
            "expected_behaviors": ["author_with_external_skill_creator"],
            "forbidden_behaviors": [],
            "required_evidence": [
                {"type": "route_class", "expected": "external_system_skill_creator"}
            ],
        }
        payload = {
            "run_id": "BR-ROUTE-CLASS-001",
            "case_id": "external-skill-route",
            "host": "codex",
            "host_version": "test",
            "model": "test",
            "model_version": "test",
            "bundle_version": "9.1.1",
            "started_at": "2026-07-09T00:00:00Z",
            "observed_route": None,
            "observed_route_class": observed_route_class,
            "observed_behaviors": ["author_with_external_skill_creator"],
            "artifacts": [],
            "verification": [{"type": "route_class", "value": evidence_value}],
            "result": "pass",
        }
        with tempfile.TemporaryDirectory(prefix="behavior-route-class-") as tmp:
            root = Path(tmp)
            run_path = root / "run.json"
            run_path.write_text(json.dumps(payload), encoding="utf-8")
            _, errors = self.runner.validate_run(
                run_path,
                {"external-skill-route": case},
                root,
                "9.1.1",
            )
        return errors

    def test_matching_external_route_class_passes(self) -> None:
        self.assertEqual(
            self.run_payload(
                observed_route_class="external_system_skill_creator",
                evidence_value="external_system_skill_creator",
            ),
            [],
        )

    def test_wrong_external_route_class_and_evidence_value_fail(self) -> None:
        errors = self.run_payload(
            observed_route_class="ordinary_task",
            evidence_value="ordinary_task",
        )

        self.assertTrue(any("observed_route_class" in error for error in errors), errors)
        self.assertTrue(any("route_class evidence with value" in error for error in errors), errors)

    def test_host_assisted_rejects_placeholder_metadata_and_non_pass_result(self) -> None:
        case = {
            "case_id": "solar-release",
            "expected_primary_skill": "analysis-codebase",
            "expected_behaviors": ["semantic_delta"],
            "forbidden_behaviors": [],
            "required_evidence": [],
        }
        payload = {
            "run_id": "BR-SOLAR-001",
            "case_id": "solar-release",
            "host": "codex",
            "host_version": "unknown",
            "model": "unknown",
            "model_version": "unknown",
            "bundle_version": "9.1.1",
            "started_at": "2026-07-10T00:00:00Z",
            "observed_route": "analysis-codebase",
            "observed_behaviors": ["semantic_delta"],
            "artifacts": [],
            "verification": [{"type": "qualitative_review", "value": "pass"}],
            "result": "partial",
        }
        with tempfile.TemporaryDirectory(prefix="behavior-host-assisted-") as tmp:
            root = Path(tmp)
            run_path = root / "run.json"
            run_path.write_text(json.dumps(payload), encoding="utf-8")
            _, errors = self.runner.validate_run(
                run_path,
                {"solar-release": case},
                root,
                "9.1.1",
                strict_host_assisted=True,
                required_model="gpt-5.6-sol",
            )

        self.assertTrue(any("requires result 'pass'" in error for error in errors), errors)
        self.assertTrue(any("requires attested host_version" in error for error in errors), errors)
        self.assertTrue(any("requires at least one raw artifact" in error for error in errors), errors)
        self.assertTrue(any("required model" in error for error in errors), errors)

    def test_host_assisted_binds_raw_artifact_and_review(self) -> None:
        case = {
            "case_id": "solar-release",
            "expected_primary_skill": "analysis-codebase",
            "expected_behaviors": ["semantic_delta"],
            "forbidden_behaviors": [],
            "required_evidence": [
                {"type": "model_identity", "expected": "gpt-5.6-sol"},
                {"type": "qualitative_review", "expected": "pass"},
            ],
        }
        with tempfile.TemporaryDirectory(prefix="behavior-host-attested-") as tmp:
            root = Path(tmp)
            artifact = root / "raw.md"
            artifact.write_text("semantic result", encoding="utf-8")
            digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
            review_artifact = root / "review.md"
            review_artifact.write_text("review pass", encoding="utf-8")
            review_digest = hashlib.sha256(review_artifact.read_bytes()).hexdigest()
            payload = {
                "run_id": "BR-SOLAR-002",
                "case_id": "solar-release",
                "host": "codex",
                "host_version": "0.144.0-alpha.4",
                "model": "gpt-5.6-sol",
                "model_version": "gpt-5.6-sol",
                "bundle_version": "9.1.1",
                "started_at": "2026-07-10T13:30:56Z",
                "observed_route": "analysis-codebase",
                "observed_behaviors": ["semantic_delta"],
                "artifacts": ["raw.md", "review.md"],
                "verification": [
                    {"type": "model_identity", "value": "gpt-5.6-sol"},
                    {
                        "type": "qualitative_review",
                        "value": "pass",
                        "reviewer": "release-reviewer",
                        "artifact": "raw.md",
                        "reviewed_sha256": digest,
                        "review_artifact": "review.md",
                        "checked_at": "2026-07-10T14:00:00Z",
                    },
                    {"type": "artifact_sha256", "artifact": "raw.md", "sha256": digest},
                    {"type": "artifact_sha256", "artifact": "review.md", "sha256": review_digest},
                ],
                "result": "pass",
            }
            run_path = root / "run.json"
            run_path.write_text(json.dumps(payload), encoding="utf-8")
            _, errors = self.runner.validate_run(
                run_path,
                {"solar-release": case},
                root,
                "9.1.1",
                strict_host_assisted=True,
                required_model="gpt-5.6-sol",
                not_before=self.runner.parse_iso_datetime("2026-07-10T00:00:00Z"),
                not_after=self.runner.parse_iso_datetime("2026-07-11T00:00:00Z"),
            )

        self.assertEqual(errors, [])

    def test_strict_artifact_path_rejects_parent_traversal(self) -> None:
        with tempfile.TemporaryDirectory(prefix="behavior-artifact-root-") as tmp:
            parent = Path(tmp)
            root = parent / "root"
            root.mkdir()
            outside = parent / "outside.md"
            outside.write_text("outside", encoding="utf-8")
            self.assertIsNone(self.runner.strict_artifact_path(root, "../outside.md"))

    def test_review_artifact_must_be_a_distinct_file(self) -> None:
        with tempfile.TemporaryDirectory(prefix="behavior-review-link-") as tmp:
            root = Path(tmp)
            raw = root / "raw.md"
            alias = root / "review.md"
            raw.write_text("same bytes", encoding="utf-8")
            os.link(raw, alias)
            self.assertFalse(self.runner.files_are_distinct(raw, alias))


if __name__ == "__main__":
    unittest.main()
