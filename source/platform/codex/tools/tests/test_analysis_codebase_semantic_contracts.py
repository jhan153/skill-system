from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


def skill_script(name: str) -> Path:
    test_path = Path(__file__).resolve()
    for parent in test_path.parents:
        if parent.name == ".codex":
            candidate = parent / "skills" / "analysis-codebase" / "scripts" / name
            if candidate.is_file():
                return candidate
        if parent.name == "source":
            candidate = parent / "skills" / "analysis-codebase" / "scripts" / name
            if candidate.is_file():
                return candidate
    raise RuntimeError(f"could not locate analysis-codebase script: {name}")


ARCHITECTURE_BUILDER = skill_script("build_architecture_models.py")
REPORT_GENERATOR = skill_script("report.py")


def load_report_generator():
    spec = importlib.util.spec_from_file_location(
        "analysis_codebase_report_for_semantic_contract_tests",
        REPORT_GENERATOR,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load report generator: {REPORT_GENERATOR}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_architecture_builder():
    spec = importlib.util.spec_from_file_location(
        "analysis_codebase_architecture_for_semantic_contract_tests",
        ARCHITECTURE_BUILDER,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load architecture builder: {ARCHITECTURE_BUILDER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SemanticContractRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = load_report_generator()
        cls.architecture = load_architecture_builder()

    def run_architecture_builder(
        self,
        *,
        files: dict[str, str],
    ) -> tuple[subprocess.CompletedProcess[str], dict[str, object], dict[str, object]]:
        with tempfile.TemporaryDirectory(prefix="analysis-codebase-contract-") as tmp:
            temp_root = Path(tmp)
            repo_path = temp_root / "repo"
            artifacts_dir = temp_root / "artifacts"
            static_dir = artifacts_dir / "static"
            repo_path.mkdir()
            static_dir.mkdir(parents=True)

            classification_rows = ["file\tcategory\tincluded\treason\text"]
            for rel_path, content in files.items():
                source_path = repo_path / rel_path
                source_path.parent.mkdir(parents=True, exist_ok=True)
                source_path.write_text(content, encoding="utf-8")
                classification_rows.append(
                    f"{rel_path}\tcode\ttrue\ttest-fixture\t{source_path.suffix.lower()}"
                )

            (static_dir / "path-classification.tsv").write_text(
                "\n".join(classification_rows) + "\n",
                encoding="utf-8",
            )
            policy_path = temp_root / "policy.json"
            policy_path.write_text(
                json.dumps(
                    {
                        "collection": {
                            "code_extensions": sorted(
                                {Path(rel_path).suffix.lower() for rel_path in files}
                            )
                        },
                        "architecture_model": {
                            "component_depth": 3,
                            "max_components": 18,
                            "max_container_edges": 16,
                            "max_component_edges": 24,
                            "max_scenarios": 4,
                            "max_scenario_steps": 7,
                            "max_decision_candidates": 6,
                        },
                    }
                ),
                encoding="utf-8",
            )

            env = dict(os.environ)
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ARCHITECTURE_BUILDER),
                    "--repo-path",
                    str(repo_path),
                    "--artifacts-dir",
                    str(artifacts_dir),
                    "--policy",
                    str(policy_path),
                ],
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=30,
            )
            decision_payload = json.loads(
                (artifacts_dir / "architecture" / "decision-candidates.json").read_text(
                    encoding="utf-8"
                )
            )
            scenario_payload = json.loads(
                (artifacts_dir / "architecture" / "scenario-model.json").read_text(
                    encoding="utf-8"
                )
            )
            return result, decision_payload, scenario_payload

    def test_coexisting_cpp_and_dotnet_files_are_not_a_semantic_contract_difference(self) -> None:
        result, decision_payload, _ = self.run_architecture_builder(
            files={
                "desktop/price.cpp": "int price(int amount) { return amount; }\n",
                "service/Price.cs": (
                    "namespace Service;\n"
                    "public static class Price {\n"
                    "    public static int Apply(int amount) => amount;\n"
                    "}\n"
                ),
            }
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        candidates = decision_payload.get("candidates", [])
        runtime_contracts = [
            item
            for item in candidates
            if isinstance(item, dict) and item.get("type") == "runtime-contract"
        ]
        self.assertEqual(
            runtime_contracts,
            [],
            "implementation-stack coexistence alone must not be reported as an "
            "end-to-end semantic contract difference",
        )

    def classify(self, item: dict[str, object]) -> dict[str, object]:
        classifier = getattr(self.report, "classify_contract_comparison", None)
        self.assertTrue(
            callable(classifier),
            "report.py must expose classify_contract_comparison(item)",
        )
        result = classifier(item)
        self.assertIsInstance(result, dict)
        return result

    def test_toolkit_difference_is_filtered_from_semantic_contract_table(self) -> None:
        result = self.classify(
            {
                "scenario": "render the account summary",
                "dimension": "toolkit",
                "baseline": {
                    "value": "Qt Widgets",
                    "evidence_refs": ["desktop/AccountView.cpp:24"],
                    "evidence_kind": "static",
                },
                "candidate": {
                    "value": ".NET WPF",
                    "evidence_refs": ["desktop/AccountView.xaml.cs:31"],
                    "evidence_kind": "static",
                },
                "verification": "compare the rendered output for the same account fixture",
            }
        )

        self.assertEqual(result.get("classification"), "implementation-only")
        self.assertFalse(result.get("include_in_semantic_table"))
        self.assertFalse(result.get("finding_eligible"))

    def test_static_cross_runtime_claim_remains_an_unverified_gap(self) -> None:
        result = self.classify(
            {
                "pair_key": "payment-submit|invalid-amount|http-status-and-error-code",
                "scenario": "submit an invalid payment request",
                "dimension": "error",
                "baseline": {
                    "value": "returns a validation result",
                    "evidence_refs": ["desktop/PaymentController.cpp:88"],
                    "evidence_kind": "static",
                },
                "candidate": {
                    "value": "throws InvalidPaymentException",
                    "evidence_refs": ["service/PaymentController.cs:74"],
                    "evidence_kind": "static",
                },
                "verification": "run both entrypoints with the same invalid request fixture",
            }
        )

        self.assertEqual(result.get("classification"), "unverified")
        self.assertTrue(result.get("include_in_semantic_table"))
        self.assertFalse(result.get("finding_eligible"))
        self.assertEqual(result.get("status"), "Unverified")
        self.assertTrue(str(result.get("reason", "")).strip())

    def test_paired_runtime_observation_promotes_an_observable_difference(self) -> None:
        result = self.classify(
            {
                "pair_key": "payment-submit|invalid-amount|http-status-and-error-code",
                "scenario": "submit an invalid payment request",
                "dimension": "error",
                "baseline": {
                    "value": "returns HTTP 400 with error_code=INVALID_AMOUNT",
                    "evidence_refs": ["artifacts/runtime/qt-invalid-payment.json"],
                    "evidence_kind": "runtime",
                },
                "candidate": {
                    "value": "returns HTTP 500 without an error code",
                    "evidence_refs": ["artifacts/runtime/dotnet-invalid-payment.json"],
                    "evidence_kind": "runtime",
                },
                "verification": "replay the paired request fixture",
            }
        )

        self.assertEqual(result.get("classification"), "behavior-difference")
        self.assertTrue(result.get("include_in_semantic_table"))
        self.assertTrue(result.get("finding_eligible"))
        self.assertEqual(result.get("status"), "different")

    def test_test_source_locations_do_not_count_as_executed_behavior(self) -> None:
        result = self.classify(
            {
                "pair_key": "payment-submit|invalid-amount|error",
                "scenario": "submit invalid payment",
                "dimension": "error",
                "baseline": {
                    "value": "returns INVALID_AMOUNT",
                    "evidence_refs": ["tests/baseline_contract_test.py:31"],
                    "evidence_kind": "contract_test",
                },
                "candidate": {
                    "value": "throws InvalidAmount",
                    "evidence_refs": ["tests/candidate_contract_test.cs:44"],
                    "evidence_kind": "contract_test",
                },
            }
        )

        self.assertEqual(result.get("classification"), "unverified")
        self.assertIn("result artifacts", str(result.get("reason", "")))

    def test_test_source_copied_under_artifacts_is_still_not_a_result(self) -> None:
        result = self.classify(
            {
                "pair_key": "payment-submit|invalid-amount|error",
                "scenario": "submit invalid payment",
                "dimension": "error",
                "baseline": {
                    "value": "returns INVALID_AMOUNT",
                    "evidence_refs": ["artifacts/static/BaselineContractTest.py"],
                    "evidence_kind": "contract_test",
                },
                "candidate": {
                    "value": "throws InvalidAmount",
                    "evidence_refs": ["artifacts/static/CandidateContractTest.cs"],
                    "evidence_kind": "contract_test",
                },
            }
        )

        self.assertEqual(result.get("classification"), "unverified")
        self.assertFalse(result.get("finding_eligible"))

    def test_static_or_traversal_artifact_refs_are_not_runtime_results(self) -> None:
        result = self.classify(
            {
                "pair_key": "payment-submit|invalid-amount|error",
                "scenario": "submit invalid payment",
                "dimension": "error",
                "baseline": {
                    "value": "returns INVALID_AMOUNT",
                    "evidence_refs": ["artifacts/static/baseline.cpp"],
                    "evidence_kind": "runtime",
                },
                "candidate": {
                    "value": "throws InvalidAmount",
                    "evidence_refs": ["../../artifacts/runtime/candidate.json"],
                    "evidence_kind": "runtime",
                },
            }
        )

        self.assertEqual(result.get("classification"), "unverified")
        self.assertFalse(result.get("finding_eligible"))

    def test_main_path_requires_behavioral_result_files_to_exist(self) -> None:
        item = {
            "pair_key": "payment-submit|invalid-amount|error",
            "scenario": "submit invalid payment",
            "dimension": "error",
            "baseline": {
                "value": "returns INVALID_AMOUNT",
                "evidence_refs": ["artifacts/runtime/baseline.json"],
                "evidence_kind": "runtime",
            },
            "candidate": {
                "value": "throws InvalidAmount",
                "evidence_refs": ["artifacts/runtime/candidate.json"],
                "evidence_kind": "runtime",
            },
        }
        with tempfile.TemporaryDirectory(prefix="semantic-result-artifacts-") as tmp:
            evidence_root = Path(tmp)
            runtime_dir = evidence_root / "artifacts" / "runtime"
            runtime_dir.mkdir(parents=True)
            (runtime_dir / "baseline.json").write_text("{}", encoding="utf-8")

            missing_result = self.report.classify_contract_comparison(
                item,
                evidence_root=evidence_root,
            )
            (runtime_dir / "candidate.json").write_text("{}", encoding="utf-8")
            paired_result = self.report.classify_contract_comparison(
                item,
                evidence_root=evidence_root,
            )

        self.assertEqual(missing_result.get("classification"), "unverified")
        self.assertEqual(paired_result.get("classification"), "behavior-difference")

    def test_behavioral_records_without_shared_pair_key_remain_unverified(self) -> None:
        result = self.classify(
            {
                "scenario": "submit an invalid payment request",
                "dimension": "error",
                "baseline": {
                    "value": "returns HTTP 400",
                    "evidence_refs": ["artifacts/runtime/baseline.json"],
                    "evidence_kind": "runtime",
                },
                "candidate": {
                    "value": "returns HTTP 500",
                    "evidence_refs": ["artifacts/runtime/candidate.json"],
                    "evidence_kind": "runtime",
                },
                "verification": "replay one shared fixture with one oracle",
            }
        )

        self.assertEqual(result.get("classification"), "unverified")
        self.assertEqual(result.get("status"), "Unverified")
        self.assertIn("pair_key", str(result.get("reason", "")))

    def test_explicit_non_comparable_pair_is_excluded(self) -> None:
        result = self.classify(
            {
                "scenario": "unrelated entrypoints",
                "dimension": "output",
                "comparable": False,
                "reason": "capabilities do not share an input or oracle",
            }
        )

        self.assertEqual(result.get("classification"), "not-comparable")
        self.assertFalse(result.get("include_in_semantic_table"))
        self.assertFalse(result.get("finding_eligible"))

    def test_unsupported_dimension_is_an_excluded_input_gap(self) -> None:
        model = {
            "comparisons": [
                {
                    "scenario": "render invoice",
                    "dimension": "presentation_stack",
                    "baseline": {"value": "Qt"},
                    "candidate": {"value": ".NET"},
                }
            ]
        }
        rows, counts, gaps = self.report.build_contract_comparison_rows(model)

        self.assertEqual(rows, [])
        self.assertEqual(counts.get("invalid-dimension"), 1)
        self.assertEqual(len(gaps), 1)
        self.assertNotIn("Qt", json.dumps(rows))

    def test_verified_behavior_difference_becomes_a_finding(self) -> None:
        findings = self.report.build_contract_findings(
            {
                "comparisons": [
                    {
                        "pair_key": "invoice|disk-full|error-and-file-state",
                        "scenario": "export invoice on disk full",
                        "dimension": "error",
                        "baseline": {
                            "value": "DISK_FULL and no file",
                            "evidence_refs": ["artifacts/runtime/baseline-disk.json"],
                            "evidence_kind": "runtime",
                        },
                        "candidate": {
                            "value": "IO_ERROR and partial file",
                            "evidence_refs": ["artifacts/runtime/candidate-disk.json"],
                            "evidence_kind": "runtime",
                        },
                        "related_files": ["src/export_invoice.py"],
                        "verification": "replay the paired disk-full fixture",
                    }
                ]
            },
            policy={
                "owners": {"default": "invoice-team"},
                "priority_model": {"due_days_by_severity": {"medium": 30, "info": 120}},
            },
            commit_range="HEAD",
            start_index=1,
        )

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].get("evidence_grade"), "A")
        self.assertEqual(findings[0].get("decision", {}).get("status"), "confirmed-difference")
        self.assertEqual(findings[0].get("scope", {}).get("category"), "semantic-contract")
        self.assertEqual(findings[0].get("improvement_plan", {}).get("related_files"), ["src/export_invoice.py"])

    def test_comparison_rows_keep_logic_gaps_and_drop_stack_vocabulary(self) -> None:
        rows, counts, gaps = self.report.build_contract_comparison_rows(
            {
                "comparisons": [
                    {
                        "scenario": "render invoice",
                        "dimension": "toolkit",
                        "baseline": {"value": "Qt", "evidence_refs": ["a.cpp:1"], "evidence_kind": "static"},
                        "candidate": {"value": ".NET", "evidence_refs": ["b.cs:1"], "evidence_kind": "static"},
                    },
                    {
                        "pair_key": "invoice|invalid-currency|error-code",
                        "scenario": "export invoice with invalid currency",
                        "dimension": "error",
                        "baseline": {
                            "value": "INVALID_CURRENCY",
                            "evidence_refs": ["artifacts/runtime/baseline.json"],
                            "evidence_kind": "runtime",
                        },
                        "candidate": {
                            "value": "throws CurrencyException",
                            "evidence_refs": ["src/Export.cs:31"],
                            "evidence_kind": "static",
                        },
                        "verification": "run the same invalid-currency fixture on both sides",
                    },
                    {
                        "pair_key": "invoice|disk-full|error-and-file-state",
                        "scenario": "export invoice on disk full",
                        "dimension": "error",
                        "baseline": {
                            "value": "returns DISK_FULL and leaves no file",
                            "evidence_refs": ["artifacts/runtime/baseline-disk.json"],
                            "evidence_kind": "runtime",
                        },
                        "candidate": {
                            "value": "returns IO_ERROR and leaves a partial file",
                            "evidence_refs": ["artifacts/runtime/candidate-disk.json"],
                            "evidence_kind": "runtime",
                        },
                        "verification": "replay the paired disk-full fixture",
                    },
                ]
            }
        )

        self.assertEqual(counts.get("implementation-only"), 1)
        self.assertEqual(counts.get("unverified"), 1)
        self.assertEqual(counts.get("behavior-difference"), 1)
        self.assertEqual(counts.get("total"), 3)
        self.assertEqual(len(rows), 2)
        self.assertEqual(len(gaps), 1)
        rendered = "\n".join(" | ".join(row) for row in rows)
        self.assertNotIn("Qt", rendered)
        self.assertNotIn(".NET", rendered)
        self.assertIn("Unverified", rendered)
        self.assertIn("different", rendered)
        self.assertIn("pair_key=invoice|invalid-currency|error-code", rendered)
        self.assertIn("baseline(runtime)=", rendered)
        self.assertIn("candidate(static)=", rendered)

    def test_static_entrypoint_scenario_is_marked_as_fallback(self) -> None:
        scenarios = self.architecture.build_static_scenarios(
            entrypoints=[
                {
                    "id": "http-create-payment",
                    "kind": "http-route",
                    "label": "POST /payments",
                    "component_id": "api/payments",
                    "evidence_refs": ["api/payments.py:20"],
                }
            ],
            component_relations=[],
            component_nodes={
                "api/payments": {
                    "label": "Payments API",
                }
            },
            interface_items=[],
            max_scenarios=4,
            max_steps=7,
        )

        self.assertEqual(len(scenarios), 1)
        self.assertEqual(scenarios[0].get("source"), "static-entrypoint")
        self.assertIs(scenarios[0].get("fallback"), True)

    def test_static_only_scenario_model_requires_verification(self) -> None:
        result, _, scenario_payload = self.run_architecture_builder(
            files={"src/main.cpp": "int main() { return 0; }\n"}
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(scenario_payload.get("status"), "verification-needed")
        self.assertGreater(scenario_payload.get("summary", {}).get("fallback_static", 0), 0)

    def test_unverified_only_comparison_can_fail_quality_gate(self) -> None:
        views = [
            {
                "view_type": view_type,
                "fallback": False,
                "provenance": ["artifact.json"],
                "meta": {"entrypoint_id": "entry"} if view_type == "runtime" else {},
            }
            for view_type in ["context", "container", "component", "runtime", "deployment"]
        ]
        gate = self.report.evaluate_quality_gate(
            findings=[],
            unverified_items=[{"section": "semantic-comparison", "reason": "paired result missing"}],
            exceptions=[],
            policy={
                "quality_gates": {
                    "default": {
                        "unverified_warn_ratio": 0.2,
                        "unverified_fail_ratio": 0.5,
                        "require_top10_plan_fields": False,
                        "max_missing_architecture_views": 0,
                        "max_fallback_diagrams": 0,
                        "max_diagrams_without_provenance": 0,
                        "max_runtime_views_without_entrypoint": 0,
                    }
                }
            },
            risk_model="default",
            architecture_views=views,
        )

        self.assertEqual(gate.get("metrics", {}).get("unverified_ratio"), 1.0)
        self.assertEqual(gate.get("status"), "FAIL")

    def test_cpp_without_semantic_index_fails_quality_gate(self) -> None:
        evidence = self.report.assess_c_cpp_structural_evidence(
            {
                "src/main.cpp": {
                    "category": "code",
                    "included": True,
                    "reason": "test-fixture",
                    "ext": ".cpp",
                }
            }
        )
        views = [
            {
                "view_type": view_type,
                "fallback": False,
                "provenance": ["artifact.json"],
                "meta": {"entrypoint_id": "entry"} if view_type == "runtime" else {},
            }
            for view_type in ["context", "container", "component", "runtime", "deployment"]
        ]
        gate = self.report.evaluate_quality_gate(
            findings=[],
            unverified_items=[],
            exceptions=[],
            policy={
                "quality_gates": {
                    "default": {
                        "require_top10_plan_fields": False,
                        "max_missing_architecture_views": 0,
                        "max_fallback_diagrams": 0,
                        "max_diagrams_without_provenance": 0,
                        "max_runtime_views_without_entrypoint": 0,
                    }
                }
            },
            risk_model="default",
            architecture_views=views,
            structural_evidence=evidence,
        )

        self.assertEqual(evidence.get("status"), "not_evidenced")
        self.assertEqual(gate.get("status"), "FAIL")
        self.assertIn("c_cpp_structural_evidence=not_evidenced", gate.get("reasons", []))

    def test_non_cpp_repo_does_not_require_cpp_semantic_index(self) -> None:
        evidence = self.report.assess_c_cpp_structural_evidence(
            {
                "src/main.py": {
                    "category": "code",
                    "included": True,
                    "reason": "test-fixture",
                    "ext": ".py",
                }
            }
        )

        self.assertIs(evidence.get("required"), False)
        self.assertEqual(evidence.get("status"), "not_applicable")

    def test_critical_semantic_contract_finding_fails_quality_gate(self) -> None:
        findings = self.report.build_contract_findings(
            {
                "comparisons": [
                    {
                        "pair_key": "checkout|duplicate-submit|charge-count",
                        "scenario": "submit checkout twice",
                        "dimension": "side_effect",
                        "severity": "critical",
                        "baseline": {
                            "value": "one charge",
                            "evidence_refs": ["artifacts/runtime/baseline.json"],
                            "evidence_kind": "runtime",
                        },
                        "candidate": {
                            "value": "two charges",
                            "evidence_refs": ["artifacts/runtime/candidate.json"],
                            "evidence_kind": "runtime",
                        },
                    }
                ]
            },
            policy={
                "owners": {"default": "checkout-team"},
                "priority_model": {"due_days_by_severity": {"critical": 1, "info": 120}},
            },
            commit_range="HEAD",
            start_index=1,
        )
        views = [
            {
                "view_type": view_type,
                "fallback": False,
                "provenance": ["artifact.json"],
                "meta": {"entrypoint_id": "entry"} if view_type == "runtime" else {},
            }
            for view_type in ["context", "container", "component", "runtime", "deployment"]
        ]
        gate = self.report.evaluate_quality_gate(
            findings=findings,
            unverified_items=[],
            exceptions=[],
            policy={
                "quality_gates": {
                    "default": {
                        "semantic_contract_critical_max": 0,
                        "semantic_contract_high_max": 0,
                        "require_top10_plan_fields": True,
                        "max_missing_architecture_views": 0,
                        "max_fallback_diagrams": 0,
                        "max_diagrams_without_provenance": 0,
                        "max_runtime_views_without_entrypoint": 0,
                    }
                }
            },
            risk_model="default",
            architecture_views=views,
        )

        self.assertEqual(gate.get("metrics", {}).get("semantic_contract_critical"), 1)
        self.assertEqual(gate.get("status"), "FAIL")
        self.assertTrue(
            any(str(reason).startswith("semantic_contract_critical=") for reason in gate.get("reasons", [])),
            gate,
        )

    def test_markdown_table_escapes_pipes_and_newlines(self) -> None:
        rendered = self.report.to_markdown_table(
            ["Value", "Detail"],
            [["left|right", "line one\nline two"]],
        )

        self.assertIn("left\\|right", rendered)
        self.assertIn("line one<br>line two", rendered)

    def test_three_static_signals_are_grade_b_and_high_is_capped_at_medium(self) -> None:
        findings = self.report.build_hotspot_findings(
            seed=[
                {
                    "rank": 1,
                    "file": "src/payment_hotspot.py",
                    "category": "code",
                    "churn": 100,
                    "complexity": 50,
                    "architecture": 25,
                    "evidence_refs": [
                        "artifacts/git/churn_all.tsv",
                        "artifacts/static/complexity.json",
                        "artifacts/static/architecture.json",
                    ],
                }
            ],
            policy={
                "priority_model": {
                    "weights": {
                        "architecture": 1.0,
                        "algorithm": 0.0,
                        "performance": 0.0,
                        "refactor": 0.0,
                        "test_guard": 0.0,
                    },
                    "category_bias": {"code": 0.0, "unknown": 0.0},
                    "severity_thresholds": {
                        "critical": 100.0,
                        "high": 5.0,
                        "medium": 3.0,
                        "low": 1.0,
                    },
                    "profile_thresholds": {
                        "architecture": 0.0,
                        "algorithm": 0.0,
                        "performance": 0.0,
                        "refactor": 0.0,
                        "test_guard": 0.0,
                    },
                    "due_days_by_severity": {
                        "medium": 30,
                        "info": 120,
                    },
                },
                "action_profiles": {
                    "architecture": {
                        "title": "Verify architecture hotspot",
                        "summary": "Confirm impact before changing the boundary.",
                        "quality_attribute": "maintainability",
                        "verification": ["Run a representative workflow."],
                    }
                },
                "owners": {"default": "Unverified"},
            },
            risk_model="default",
            commit_range="HEAD",
        )

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].get("evidence_grade"), "B")
        self.assertEqual(findings[0].get("estimated_severity"), "high")
        self.assertEqual(findings[0].get("severity"), "medium")

    def test_static_security_scan_is_a_verification_candidate_not_grade_a(self) -> None:
        findings = self.report.build_security_findings(
            raw_security=[
                {
                    "source": "semgrep",
                    "file": "src/payment.py",
                    "rule": "python.lang.security.audit",
                    "summary": "scanner-reported sink",
                    "severity": "high",
                    "evidence_ref": "artifacts/static/semgrep.json",
                }
            ],
            policy={
                "priority_model": {"due_days_by_severity": {"high": 7}},
                "action_profiles": {
                    "security": {
                        "title": "Verify security candidate",
                        "summary": "Confirm applicability and reachability.",
                        "quality_attribute": "security",
                        "verification": ["Confirm source-to-sink reachability."],
                    }
                },
                "owners": {"security": "security-team"},
            },
            risk_model="default",
            commit_range="HEAD",
            start_index=1,
        )

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].get("evidence_grade"), "B")
        self.assertEqual(findings[0].get("decision", {}).get("status"), "verification-needed")
        self.assertEqual(findings[0].get("decision", {}).get("evidence_basis"), "static-security-scan")

    def test_architecture_decision_rows_expose_verification_status_and_action(self) -> None:
        rows = self.report.build_decision_rows(
            {
                "candidates": [
                    {
                        "title": "Verify the service boundary",
                        "type": "boundary",
                        "status": "verification-needed",
                        "summary": "Static imports suggest a boundary candidate.",
                        "verification": "Trace one request across both components.",
                        "evidence_refs": ["src/api.py:12", "src/service.py:31"],
                    }
                ]
            }
        )

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][2], "verification-needed")
        self.assertEqual(rows[0][4], "Trace one request across both components.")


if __name__ == "__main__":
    unittest.main()
