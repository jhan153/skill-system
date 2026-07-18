from __future__ import annotations

import importlib.util
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

import yaml


def load_tool():
    path = Path(__file__).resolve().parents[1] / "compare_skill_diet.py"
    spec = importlib.util.spec_from_file_location("compare_skill_diet_under_test", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


TOOL = load_tool()
TEST_REVIEWER_ID = "test-independent-reviewer"
TEST_RSA_N = int(
    "e4c905faf15c0b9e1be76f3302f54c02863bb6bd348160feaae051751c2773894b190c9a152628f341ed7bb0dae8b12f9aa6c34a3173393a1997ad95a41a8cf2f4f9c052a57f9510392b29ae1dcafefc3c9f3f24d2ad639e284d472339d6296aac65cf87531add94910b64c33acc439338ea987b906568a8531436538ca88fbe953c387aea697dd18dbbaae207e7d215ece2df6f86aa78aa83090ac6fbeb03140093826715ba25626b8300c2f2ac0d1a62e06a1670d202a1b8c2766568de2f1351f1306fef7955acc96faa7da09752e3a31c4ca782d96c1f55e4e553b9a44f53b150434994bb7e74fb57d407e6dbcfa9b219657d79f70b7a431d72e9c2979449",
    16,
)
TEST_RSA_E = 65537
TEST_RSA_D = int(
    "36bc6f8d57b4756518f8f86e446d6a878a14fc45ed2b6d08d0da0533170ecb421431048652bc03fd1b0f55d1fcb5c23a88ee0ff80eb7a9ffe0029d79993eeeecebb65b108adee8cb6e5a08c94b00779be2671924d6b0bc0e29473fd74a2d96501ab9eafa4de4361226d78a7e78f148d38ec0f5c54e492cce64be07b75a86338969f7d27c7a033ab5b2cc5fea76cf543131a21a8fe15cda5c252d8f014c003c66e57bd8d9aa47cf44a9be1f982531c4fb076c821a79b2958ebcfeacd5b2d3f5b586ce9766010d382ae6bd120f96e27262e7c0e2ac3de0bcb3b9cc2ed071928eb29dfbe4f047f9e7c23983dd76becdb4d00b373ab1ead883b0a223236734d3ab19",
    16,
)
TEST_TRUSTED_REVIEWERS = {
    TEST_REVIEWER_ID: {
        "algorithm": "rsa-pkcs1v15-sha256",
        "modulus": TEST_RSA_N,
        "exponent": TEST_RSA_E,
        "fingerprint_sha256": "test-fixture",
    }
}


def sign_test_review(message: bytes) -> str:
    width = (TEST_RSA_N.bit_length() + 7) // 8
    digest_info = bytes.fromhex("3031300d060960864801650304020105000420") + hashlib.sha256(message).digest()
    padding = b"\xff" * (width - len(digest_info) - 3)
    encoded = b"\x00\x01" + padding + b"\x00" + digest_info
    return pow(int.from_bytes(encoded, "big"), TEST_RSA_D, TEST_RSA_N).to_bytes(width, "big").hex()


def source_info() -> dict[str, object]:
    return {
        "label": "fixture",
        "commit": "1" * 40,
        "skills_tree": "2" * 40,
        "commit_time": "2026-07-12T00:00:00Z",
        "reproducible": True,
        "tracked_input_digest": "3" * 64,
    }


def write_fixture(
    root: Path,
    *,
    detail: str = "Keep this operational detail in the main body.",
    reference_text: str | None = None,
    admission: str = "read_if_needed",
    forbidden: list[str] | None = None,
) -> None:
    source = root / "source"
    (source / "plugins").mkdir(parents=True, exist_ok=True)
    (source / "plugins" / "core.yaml").write_text(
        'name: skill-system-core\nversion: "9.1.2"\n',
        encoding="utf-8",
    )
    skill = source / "skills" / "alpha"
    (skill / "agents").mkdir(parents=True, exist_ok=True)
    reference_item = "references/detail.md" if reference_text is not None else "current request"
    must_item = reference_item if admission == "must_read" else "current request"
    conditional_item = reference_item if admission == "read_if_needed" else "additional evidence"
    skill_text = f'''---
name: alpha
description: "Alpha description with 한글 and --- inside the quoted value."
---

# Alpha

## Routing Card
- role: primary
- intent_signature:
  - alpha task
- use_when:
  - alpha is requested
- do_not_use_when:
  - beta is requested
- expected_inputs:
  - current request
- expected_outputs:
  - alpha result
- context_targets:
  must_read:
    - {must_item}
  read_if_needed:
    - {conditional_item}
  do_not_load_by_default:
    - unrelated files
- risk_profile:
  reads:
    - scoped files
  writes:
    - none
  tools:
    - read only
  sensitive_resources:
    - credentials denied
- entry_scene:
  - PREPARE

## Workflow

{detail}

---

The horizontal rule above is body content.
'''
    (skill / "SKILL.md").write_text(skill_text, encoding="utf-8")
    (skill / "agents" / "openai.yaml").write_text(
        '''interface:
  display_name: Alpha
  short_description: Route alpha work
  default_prompt: Use alpha for the supplied task.
policy:
  invocation_surface: explicit_procedure
  allow_implicit_invocation: false
  may_own_execution: true
''',
        encoding="utf-8",
    )
    if reference_text is not None:
        (skill / "references").mkdir(parents=True, exist_ok=True)
        (skill / "references" / "detail.md").write_text(reference_text, encoding="utf-8")

    eval_root = source / "shared" / "eval"
    eval_root.mkdir(parents=True, exist_ok=True)
    cases = {
        "version": "9.1.2",
        "cases": [
            {
                "case_id": "alpha-positive-001",
                "schema_version": 2,
                "user_request": "Run alpha.",
                "expected_primary_skill": "alpha",
                "expected_supporting_skills": [],
                "should_not_trigger": [],
                "expected_context": ["fixture"],
                "expected_output_shape": "alpha output",
                "quality_notes": "fixture",
                "friction_risk": "wrong route",
                "expected_behaviors": ["perform_alpha"],
                "forbidden_behaviors": forbidden or ["perform_beta"],
                "required_evidence": [{"type": "route_match", "expected": "alpha"}],
                "required_eval_mode": "host-assisted",
                "behavior_contract_owners": ["alpha"],
                "scenario_tags": ["edge"],
            },
            {
                "case_id": "alpha-negative-001",
                "schema_version": 2,
                "user_request": "Run beta.",
                "expected_primary_skill": None,
                "expected_supporting_skills": [],
                "should_not_trigger": ["alpha"],
                "expected_context": ["fixture"],
                "expected_output_shape": "no alpha",
                "quality_notes": "fixture",
                "friction_risk": "overtrigger",
                "expected_behaviors": ["avoid_alpha"],
                "forbidden_behaviors": ["trigger_alpha"],
                "required_evidence": [{"type": "route_class", "expected": "none"}],
            },
        ],
    }
    (eval_root / "routing_cases.yaml").write_text(
        yaml.safe_dump(cases, sort_keys=False),
        encoding="utf-8",
    )


def write_beta_fixture(root: Path) -> None:
    skill = root / "source" / "skills" / "beta"
    (skill / "agents").mkdir(parents=True, exist_ok=True)
    (skill / "SKILL.md").write_text(
        '''---
name: beta
description: "Beta supporting fixture."
---

# Beta

## Routing Card
- role: supporting
- context_targets:
  must_read:
    - current request
  read_if_needed:
    - additional evidence
  do_not_load_by_default:
    - unrelated files

## Workflow

Support the primary fixture.
''',
        encoding="utf-8",
    )
    (skill / "agents" / "openai.yaml").write_text(
        '''interface:
  display_name: Beta
  short_description: Support beta work
  default_prompt: Use beta only as a supporting fixture.
policy:
  invocation_surface: explicit_procedure
  allow_implicit_invocation: false
  may_own_execution: true
''',
        encoding="utf-8",
    )


def snapshot(root: Path) -> dict:
    info = source_info()
    info["tracked_input_digest"] = TOOL.input_digest(root / "source")
    return TOOL.collect_snapshot(root, info)


def find_frozen_manifest() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        for rel in (
            Path("source/shared/eval/baselines/skill-diet-9.1.2.yaml"),
            Path(".codex/eval/baselines/skill-diet-9.1.2.yaml"),
        ):
            candidate = parent / rel
            if candidate.is_file():
                return candidate
    raise FileNotFoundError("frozen skill-diet baseline not found")


def find_bundle_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "source" / "plugins" / "core.yaml").is_file() and (
            parent / "source" / "skills"
        ).is_dir():
            return parent
    raise FileNotFoundError("canonical bundle root not found")


def find_evidence_schema() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        for rel in (
            Path("source/shared/eval/skill-diet-evidence.schema.json"),
            Path(".codex/eval/skill-diet-evidence.schema.json"),
        ):
            candidate = parent / rel
            if candidate.is_file():
                return candidate
    raise FileNotFoundError("skill-diet evidence schema not found")


def find_local_pilot_evidence_schema() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        for rel in (
            Path("source/shared/eval/skill-diet-local-pilot-evidence.schema.json"),
            Path(".codex/eval/skill-diet-local-pilot-evidence.schema.json"),
        ):
            candidate = parent / rel
            if candidate.is_file():
                return candidate
    raise FileNotFoundError("skill-diet local pilot evidence schema not found")


def find_baseline_schema() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        for rel in (
            Path("source/shared/eval/skill-diet-baseline.schema.json"),
            Path(".codex/eval/skill-diet-baseline.schema.json"),
        ):
            candidate = parent / rel
            if candidate.is_file():
                return candidate
    raise FileNotFoundError("skill-diet baseline schema not found")


def find_reviewer_trust_store() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        for rel in (
            Path("source/shared/eval/skill-diet-trusted-reviewers.json"),
            Path(".codex/eval/skill-diet-trusted-reviewers.json"),
        ):
            candidate = parent / rel
            if candidate.is_file():
                return candidate
    raise FileNotFoundError("skill-diet reviewer trust store not found")


def artifact_ref(path: Path, root: Path) -> dict:
    data = path.read_bytes()
    return {
        "path": path.relative_to(root).as_posix(),
        "sha256": TOOL.sha256_bytes(data),
        "utf8_bytes": len(data),
    }


def write_paired_evidence(
    root: Path,
    manifest: dict,
    *,
    side: str,
    oracle_manifest: dict | None = None,
    model: str = "test-model",
    case_ids: tuple[str, ...] = ("alpha-positive-001", "alpha-negative-001"),
    extra_context: dict[str, list[tuple[str, str]]] | None = None,
    omit_required_results_for: set[str] | None = None,
    observed_supporting_override: dict[str, list[str]] | None = None,
    verification_tier: str = TOOL.INDEPENDENT_SIGNED_TIER,
    required_basis: str = "run-output",
    local_prompt_suffix: str = "",
    local_review_result: str = "pass",
    skill_id: str = "alpha",
    execution_contract_overrides: dict[str, str] | None = None,
) -> dict:
    root.mkdir(parents=True, exist_ok=True)
    skill = TOOL.index_skills(manifest)[skill_id]
    oracle = oracle_manifest or manifest
    coverage = TOOL.index_skills(oracle)[skill_id]["eval_coverage"]
    context_units = TOOL.context_unit_index(manifest)
    source = {
        "commit": manifest["source"].get("commit"),
        "skills_tree": manifest["source"].get("skills_tree"),
        "tracked_input_digest": manifest["source"]["tracked_input_digest"],
    }
    runs = []
    local_pilot = verification_tier == TOOL.AGENT_REVIEWED_LOCAL_PILOT_TIER
    reviewer_id = "agent:fixture-reviewer" if local_pilot else TEST_REVIEWER_ID
    for case_id in case_ids:
        run_id = f"{side}-{case_id}"
        executed_at = "2026-07-12T01:02:03Z"
        routes = coverage["declared_route_cases"]
        invoked = case_id in set(routes["primary"]) | set(routes["supporting"])
        observed_primary = coverage["case_expected_primary_skills"][case_id]
        observed_supporting = (observed_supporting_override or {}).get(
            case_id,
            coverage["case_expected_supporting_skills"][case_id],
        )
        admitted_keys: list[tuple[str, str]] = []
        if invoked:
            admitted_keys.append((skill["source_path"], "full_file"))
        else:
            admitted_keys.append((skill["source_path"], "frontmatter_description"))
        source_skills = {item["skill_id"]: item for item in manifest["skills"]}
        for invoked_skill_id in [observed_primary, *observed_supporting]:
            invoked_skill = source_skills.get(invoked_skill_id)
            key = (invoked_skill["source_path"], "full_file") if invoked_skill is not None else None
            if key is not None and key not in admitted_keys:
                admitted_keys.append(key)
        admitted_keys.extend((extra_context or {}).get(case_id, []))
        admitted = [
            {
                "path": context_units[key]["path"],
                "content_unit": context_units[key]["content_unit"],
                "sha256": context_units[key]["sha256"],
                "words": context_units[key]["words"],
                "utf8_bytes": context_units[key]["utf8_bytes"],
            }
            for key in admitted_keys
        ]
        prompt_path = root / f"{run_id}.prompt.txt"
        prompt_path.write_text(
            f"paired prompt for {case_id}{local_prompt_suffix}\n",
            encoding="utf-8",
        )
        prompt = artifact_ref(prompt_path, root)
        execution_contract = {
            "host_id": "fixture-host-v1",
            "prompt_sha256": prompt["sha256"],
            "input_sha256": TOOL.sha256_bytes(f"fixture-input:{case_id}".encode("utf-8")),
            "permission_profile_sha256": TOOL.sha256_bytes(b"read-only"),
            "validator_sha256": TOOL.sha256_bytes(b"fixture-validator-v1"),
        }
        execution_contract.update(execution_contract_overrides or {})
        execution_contract_sha256 = TOOL.sha256_json(execution_contract)
        output_path = root / f"{run_id}.output.txt"
        output_path.write_text(f"{side} output for {case_id}\n", encoding="utf-8")
        output = artifact_ref(output_path, root)
        eval_mode = coverage["case_required_eval_modes"].get(case_id, "declared_only")
        if eval_mode not in {"host-assisted", "replay"}:
            eval_mode = "host-assisted"
        run_payload = {
            "schema_version": 1,
            "run_id": run_id,
            "case_id": case_id,
            "skill_id": skill["skill_id"],
            "source": source,
            "model": model,
            "executed_at": executed_at,
            "eval_mode": eval_mode,
            "eval_contract_digest": oracle["evaluation_contract"]["digest"],
            "case_oracle_sha256": coverage["case_oracle_digests"][case_id],
            "execution_contract": execution_contract,
            "execution_contract_sha256": execution_contract_sha256,
            "observed_primary_skill": observed_primary,
            "observed_supporting_skills": observed_supporting,
            "skill_invoked": invoked,
            "admitted_context": admitted,
            "output_sha256": output["sha256"],
            "producer": {
                "kind": "host_instrumentation",
                "id": "fixture-runner",
                "version": "1",
            },
        }
        if local_pilot:
            run_payload.update(
                {
                    "verification_tier": TOOL.AGENT_REVIEWED_LOCAL_PILOT_TIER,
                    "prompt_sha256": prompt["sha256"],
                    "context_capture": "declared_context_pack",
                }
            )
        run_path = root / f"{run_id}.run.json"
        run_path.write_text(json.dumps(run_payload, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        run_artifact = artifact_ref(run_path, root)
        required_contracts = coverage["case_required_evidence_contracts"][case_id]
        if case_id in (omit_required_results_for or set()):
            required_contracts = []
        review_path = root / f"{run_id}.review.txt"
        if local_pilot:
            review_path.write_text(
                json.dumps(
                    {
                        "case_id": case_id,
                        "reviewer_id": reviewer_id,
                        "result": local_review_result,
                        "baseline_result": local_review_result,
                        "candidate_result": local_review_result,
                        "invariant_checks": [
                            {
                                "invariant": "route and behavior",
                                "result": local_review_result,
                                "evidence": "paired fixture artifacts",
                            }
                        ],
                        "regression_assessment": "No fixture regression observed.",
                        "limitations": [
                            "Agent review is not independent release evidence.",
                            "Admission was not measured.",
                        ],
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                encoding="utf-8",
            )
        else:
            review_path.write_text(
                f"Agent review passed for {side} {case_id}; checked route and required output evidence.\n",
                encoding="utf-8",
            )
        review = artifact_ref(review_path, root)
        receipt_payload = {
            "schema_version": 1,
            "run_id": run_id,
            "case_id": case_id,
            "skill_id": skill["skill_id"],
            "model": model,
            "executed_at": executed_at,
            "reviewed_at": "2026-07-12T01:02:30Z",
            "eval_mode": eval_mode,
            "eval_contract_digest": oracle["evaluation_contract"]["digest"],
            "case_oracle_sha256": coverage["case_oracle_digests"][case_id],
            "execution_contract_sha256": execution_contract_sha256,
            "run_artifact_sha256": run_artifact["sha256"],
            "output_sha256": output["sha256"],
            "verifier": {
                "kind": "agent_review" if local_pilot else "independent_review",
                "id": reviewer_id,
                "version": "1",
            },
            "route_result": "pass",
            "behavior_result": "pass",
            "required_evidence_results": [
                {
                    **contract,
                    "result": "pass",
                    "basis_sha256": (
                        [review["sha256"]]
                        if required_basis == "review-only"
                        else [run_artifact["sha256"], output["sha256"]]
                    ),
                }
                for contract in required_contracts
            ],
            "result": "pass",
        }
        if local_pilot:
            receipt_payload.update(
                {
                    "verification_tier": TOOL.AGENT_REVIEWED_LOCAL_PILOT_TIER,
                    "prompt_sha256": prompt["sha256"],
                    "review_artifact_sha256": review["sha256"],
                    "independent": False,
                    "release_eligible": False,
                }
            )
        receipt_path = root / f"{run_id}.verify.json"
        receipt_path.write_text(json.dumps(receipt_payload, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        run_entry = {
            "run_id": run_id,
            "case_id": case_id,
            "skill_id": skill["skill_id"],
            "reviewer_id": reviewer_id,
            "case_oracle_sha256": coverage["case_oracle_digests"][case_id],
            "execution_contract_sha256": execution_contract_sha256,
            "run_artifact": run_artifact,
            "output_artifact": output,
            "verifier_receipt": artifact_ref(receipt_path, root),
        }
        if local_pilot:
            run_entry.update({"prompt_artifact": prompt, "review_artifact": review})
        else:
            run_entry["verifier_signature"] = sign_test_review(receipt_path.read_bytes())
        runs.append(run_entry)
    evidence = {
        "schema_version": 1 if local_pilot else 2,
        "evidence_id": f"evidence-{manifest['source']['tracked_input_digest'][:8]}",
        "generated_at": "2026-07-12T01:03:00Z",
        "source": source,
        "model": model,
        "eval_contract_digest": oracle["evaluation_contract"]["digest"],
        "runs": runs,
    }
    if local_pilot:
        evidence["verification_tier"] = TOOL.AGENT_REVIEWED_LOCAL_PILOT_TIER
    return evidence


def paired_result(*args, **kwargs):
    kwargs.setdefault("trusted_reviewers", TEST_TRUSTED_REVIEWERS)
    return TOOL.paired_evidence_result(*args, **kwargs)


def add_beta_skill(manifest: dict) -> None:
    beta = deepcopy(manifest["skills"][0])
    beta["skill_id"] = "beta"
    beta["source_path"] = beta["source_path"].replace("/alpha/", "/beta/")
    coverage = beta["eval_coverage"]
    rename = {
        "alpha-positive-001": "beta-positive-001",
        "alpha-negative-001": "beta-negative-001",
    }
    for lane, case_ids in coverage["declared_route_cases"].items():
        coverage["declared_route_cases"][lane] = [rename[case_id] for case_id in case_ids]
    for list_key in (
        "structured_behavior_candidates",
        "structured_observed_candidates",
        "structured_negative_candidates",
        "explicit_edge_cases",
    ):
        coverage[list_key] = [rename[case_id] for case_id in coverage[list_key]]
    for mapping_key in (
        "case_oracle_digests",
        "case_overlay_stable_digests",
        "case_sources",
        "case_required_eval_modes",
        "case_required_evidence_types",
        "case_required_evidence_contracts",
        "case_schema_versions",
        "case_expected_primary_skills",
        "case_expected_supporting_skills",
        "case_should_not_trigger",
        "case_expected_behaviors",
        "case_forbidden_behaviors",
        "case_behavior_contract_owners",
        "case_scenario_tags",
    ):
        coverage[mapping_key] = {rename[case_id]: value for case_id, value in coverage[mapping_key].items()}
    coverage["case_expected_primary_skills"]["beta-positive-001"] = "beta"
    for mapping_key in ("case_expected_supporting_skills", "case_should_not_trigger"):
        coverage[mapping_key] = {
            case_id: ["beta" if item == "alpha" else item for item in values]
            for case_id, values in coverage[mapping_key].items()
        }
    manifest["skills"].append(beta)
    manifest["aggregates"]["skill_count"] += 1


class SkillDietComparisonTests(unittest.TestCase):
    def test_reviewer_entry_cli_emits_only_normalized_public_material(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(Path(TOOL.__file__)),
                "reviewer-entry",
                "--reviewer-id",
                TEST_REVIEWER_ID,
                "--modulus-hex",
                f"00{TEST_RSA_N:x}",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(result.returncode, 0, result.stdout)
        entry = json.loads(result.stdout)
        self.assertEqual(entry["reviewer_id"], TEST_REVIEWER_ID)
        self.assertEqual(entry["modulus_hex"], f"{TEST_RSA_N:x}")
        self.assertEqual(entry["exponent"], TEST_RSA_E)
        self.assertEqual(
            entry["fingerprint_sha256"],
            TOOL.reviewer_key_fingerprint(f"{TEST_RSA_N:x}", TEST_RSA_E),
        )
        self.assertEqual(
            set(entry),
            {"reviewer_id", "algorithm", "modulus_hex", "exponent", "fingerprint_sha256"},
        )

    def test_current_912_snapshot_totals(self) -> None:
        manifest = TOOL.load_manifest(find_frozen_manifest())
        aggregate = manifest["aggregates"]["measurements"]
        self.assertEqual(manifest["aggregates"]["skill_count"], 66)
        self.assertEqual(aggregate["skill_file"]["words"], 52199)
        self.assertEqual(aggregate["skill_file"]["utf8_bytes"], 394611)
        self.assertEqual(aggregate["body"]["words"], 49502)
        self.assertEqual(aggregate["body"]["utf8_bytes"], 372785)
        self.assertEqual(aggregate["frontmatter_description"]["words"], 2367)
        self.assertEqual(aggregate["frontmatter_description"]["characters"], 18389)

    def test_four_pilot_skills_have_body_edit_contracts(self) -> None:
        root = find_bundle_root()
        candidate = TOOL.collect_snapshot(root, TOOL.worktree_source_info(root))
        skills = TOOL.index_skills(candidate)
        expected = {
            "design-frontend": {
                "structured": "design-030",
                "negative": "design-033",
                "competing": "design-033",
                "composition": "design-004",
                "edge": "design-037",
            },
            "design-visual-regression": {
                "structured": "design-035",
                "negative": "design-033",
                "composition": "design-030",
                "edge": "design-035",
            },
            "workflow-comment-maintenance": {
                "structured": "runtime-047",
                "negative": "neg-workflow-comment-maintenance-001",
                "composition": "neg-workflow-comment-maintenance-002",
                "edge": "runtime-047",
            },
            "analysis-router": {
                "structured": "route-grp-001",
                "negative": "neg-002",
                "competing": "route-001",
                "edge": "route-001",
            },
        }
        for skill_id, cases in expected.items():
            coverage = skills[skill_id]["eval_coverage"]
            routes = coverage["declared_route_cases"]
            self.assertTrue(routes["primary"] or routes["supporting"], skill_id)
            self.assertIn(cases["structured"], coverage["structured_observed_candidates"], skill_id)
            self.assertIn(cases["negative"], coverage["structured_negative_candidates"], skill_id)
            self.assertIn(cases["edge"], coverage["explicit_edge_cases"], skill_id)
            if "composition" in cases:
                self.assertIn(cases["composition"], routes["supporting"], skill_id)
            if skills[skill_id]["routing"]["allow_implicit_invocation"] is True:
                competing = {
                    case_id
                    for case_id in routes["negative"]
                    if coverage["case_expected_primary_skills"].get(case_id) is not None
                }
                self.assertIn(cases["competing"], competing, skill_id)

    def test_evidence_schema_accepts_artifact_chain_and_rejects_legacy_pass_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            manifest = snapshot(root)
            evidence = write_paired_evidence(root / "evidence", manifest, side="candidate")
        schema = json.loads(find_evidence_schema().read_text(encoding="utf-8"))
        self.assertEqual(TOOL.validate_schema(evidence, schema), [])
        legacy = {
            "schema_version": 1,
            "evidence_id": "legacy",
            "source": evidence["source"],
            "model": "test-model",
            "runs": [{"case_id": "alpha-positive-001", "result": "pass"}],
        }
        self.assertTrue(TOOL.validate_schema(legacy, schema))

    def test_local_pilot_schema_accepts_agent_review_chain_and_rejects_signature(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            manifest = snapshot(root)
            evidence = write_paired_evidence(
                root / "evidence",
                manifest,
                side="candidate",
                verification_tier=TOOL.AGENT_REVIEWED_LOCAL_PILOT_TIER,
            )
        schema = json.loads(find_local_pilot_evidence_schema().read_text(encoding="utf-8"))
        self.assertEqual(TOOL.validate_schema(evidence, schema), [])
        evidence["runs"][0]["verifier_signature"] = "00"
        self.assertTrue(TOOL.validate_schema(evidence, schema))

    def test_local_pilot_pair_is_agent_reviewed_not_release_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root, detail="Before body detail.")
            baseline = snapshot(root)
            write_fixture(root, detail="After body detail.")
            candidate = snapshot(root)
            baseline_root = root / "baseline-evidence"
            candidate_root = root / "candidate-evidence"
            paired = TOOL.paired_evidence_result(
                baseline,
                candidate,
                write_paired_evidence(
                    baseline_root,
                    baseline,
                    side="baseline",
                    verification_tier=TOOL.AGENT_REVIEWED_LOCAL_PILOT_TIER,
                ),
                write_paired_evidence(
                    candidate_root,
                    candidate,
                    side="candidate",
                    verification_tier=TOOL.AGENT_REVIEWED_LOCAL_PILOT_TIER,
                ),
                baseline_root,
                candidate_root,
                verification_tier=TOOL.AGENT_REVIEWED_LOCAL_PILOT_TIER,
            )
            with (
                patch.object(TOOL, "LOCAL_PILOT_SKILLS", {"alpha"}),
                patch.object(
                    TOOL,
                    "LOCAL_PILOT_EVAL_CONTRACT_DIGEST",
                    candidate["evaluation_contract"]["digest"],
                ),
            ):
                allowed = TOOL.compare_manifests(
                    baseline,
                    candidate,
                    paired_evidence=paired,
                    allow_agent_reviewed_local_pilot=True,
                )
                denied = TOOL.compare_manifests(baseline, candidate, paired_evidence=paired)
        self.assertEqual(paired["behavior"], "agent-reviewed")
        self.assertEqual(paired["admission"], "unverified")
        self.assertFalse(paired["release_eligible"])
        self.assertEqual(allowed["status"], "PASS", allowed["issues"])
        self.assertEqual(allowed["axes"]["behavior"], "agent-reviewed")
        self.assertEqual(allowed["axes"]["admission"], "unverified")
        self.assertFalse(allowed["release_eligible"])
        self.assertEqual(denied["status"], "FAIL")
        self.assertIn("local_pilot_not_enabled", {item["code"] for item in denied["issues"]})

    def test_local_pilot_can_lock_one_accepted_change_and_review_one_new_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            baseline = snapshot(root)
            add_beta_skill(baseline)
            candidate = deepcopy(baseline)
            candidate["source"]["tracked_input_digest"] = "4" * 64
            baseline_skills = TOOL.index_skills(baseline)
            candidate_skills = TOOL.index_skills(candidate)
            candidate_skills["alpha"]["content_digests"]["body"] = "a" * 64
            candidate_skills["beta"]["content_digests"]["body"] = "b" * 64
            baseline_root = root / "baseline-evidence"
            candidate_root = root / "candidate-evidence"
            case_ids = ("beta-positive-001", "beta-negative-001")
            paired = TOOL.paired_evidence_result(
                baseline,
                candidate,
                write_paired_evidence(
                    baseline_root,
                    baseline,
                    side="baseline",
                    verification_tier=TOOL.AGENT_REVIEWED_LOCAL_PILOT_TIER,
                    skill_id="beta",
                    case_ids=case_ids,
                ),
                write_paired_evidence(
                    candidate_root,
                    candidate,
                    side="candidate",
                    verification_tier=TOOL.AGENT_REVIEWED_LOCAL_PILOT_TIER,
                    skill_id="beta",
                    case_ids=case_ids,
                ),
                baseline_root,
                candidate_root,
                verification_tier=TOOL.AGENT_REVIEWED_LOCAL_PILOT_TIER,
            )
            accepted = {
                "alpha": {
                    "body": "a" * 64,
                    "resource_inventory": baseline_skills["alpha"]["content_digests"]["resource_inventory"],
                }
            }
            with (
                patch.object(TOOL, "LOCAL_PILOT_SKILLS", {"alpha", "beta"}),
                patch.object(
                    TOOL,
                    "LOCAL_PILOT_EVAL_CONTRACT_DIGEST",
                    candidate["evaluation_contract"]["digest"],
                ),
            ):
                result = TOOL.compare_manifests(
                    baseline,
                    candidate,
                    paired_evidence=paired,
                    allow_agent_reviewed_local_pilot=True,
                    accepted_local_locks=accepted,
                )
                tampered = deepcopy(candidate)
                TOOL.index_skills(tampered)["alpha"]["content_digests"]["body"] = "c" * 64
                tampered_result = TOOL.compare_manifests(
                    baseline,
                    tampered,
                    paired_evidence=paired,
                    allow_agent_reviewed_local_pilot=True,
                    accepted_local_locks=accepted,
                )
        self.assertEqual(result["status"], "PASS", result["issues"])
        self.assertEqual(result["accepted_local_skills"], ["alpha"])
        self.assertEqual(result["skills_needing_evidence"], ["beta"])
        self.assertEqual(result["release_skills_needing_evidence"], ["alpha", "beta"])
        self.assertIn(
            "local_pilot_accepted_skill_digest_mismatch",
            {item["code"] for item in tampered_result["issues"]},
        )

    def test_local_pilot_rejects_signed_pair_and_nonpilot_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root, detail="Before body detail.")
            baseline = snapshot(root)
            write_fixture(root, detail="After body detail.")
            candidate = snapshot(root)
            baseline_root = root / "baseline-evidence"
            candidate_root = root / "candidate-evidence"
            signed = paired_result(
                baseline,
                candidate,
                write_paired_evidence(baseline_root, baseline, side="baseline"),
                write_paired_evidence(candidate_root, candidate, side="candidate"),
                baseline_root,
                candidate_root,
            )
            signed_as_local = TOOL.compare_manifests(
                baseline,
                candidate,
                paired_evidence=signed,
                allow_agent_reviewed_local_pilot=True,
            )
            local = TOOL.paired_evidence_result(
                baseline,
                candidate,
                write_paired_evidence(
                    baseline_root,
                    baseline,
                    side="local-baseline",
                    verification_tier=TOOL.AGENT_REVIEWED_LOCAL_PILOT_TIER,
                ),
                write_paired_evidence(
                    candidate_root,
                    candidate,
                    side="local-candidate",
                    verification_tier=TOOL.AGENT_REVIEWED_LOCAL_PILOT_TIER,
                ),
                baseline_root,
                candidate_root,
                verification_tier=TOOL.AGENT_REVIEWED_LOCAL_PILOT_TIER,
            )
            nonpilot = TOOL.compare_manifests(
                baseline,
                candidate,
                paired_evidence=local,
                allow_agent_reviewed_local_pilot=True,
            )
        self.assertIn("local_pilot_evidence_tier_required", {item["code"] for item in signed_as_local["issues"]})
        self.assertIn("local_pilot_oracle_not_pinned", {item["code"] for item in signed_as_local["issues"]})
        self.assertIn("local_pilot_skill_not_allowed", {item["code"] for item in nonpilot["issues"]})

    def test_local_pilot_review_cannot_be_its_own_required_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            manifest = snapshot(root)
            baseline_root = root / "baseline-evidence"
            candidate_root = root / "candidate-evidence"
            paired = TOOL.paired_evidence_result(
                manifest,
                manifest,
                write_paired_evidence(
                    baseline_root,
                    manifest,
                    side="baseline",
                    verification_tier=TOOL.AGENT_REVIEWED_LOCAL_PILOT_TIER,
                    required_basis="review-only",
                ),
                write_paired_evidence(
                    candidate_root,
                    manifest,
                    side="candidate",
                    verification_tier=TOOL.AGENT_REVIEWED_LOCAL_PILOT_TIER,
                    required_basis="review-only",
                ),
                baseline_root,
                candidate_root,
                verification_tier=TOOL.AGENT_REVIEWED_LOCAL_PILOT_TIER,
            )
        self.assertIn("evidence_required_result_failed", {item["code"] for item in paired["issues"]})

    def test_local_pilot_requires_same_prompt_and_passing_raw_pair_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            manifest = snapshot(root)
            baseline_root = root / "baseline-evidence"
            candidate_root = root / "candidate-evidence"
            prompt_mismatch = TOOL.paired_evidence_result(
                manifest,
                manifest,
                write_paired_evidence(
                    baseline_root,
                    manifest,
                    side="baseline",
                    verification_tier=TOOL.AGENT_REVIEWED_LOCAL_PILOT_TIER,
                ),
                write_paired_evidence(
                    candidate_root,
                    manifest,
                    side="candidate",
                    verification_tier=TOOL.AGENT_REVIEWED_LOCAL_PILOT_TIER,
                    local_prompt_suffix=" changed",
                ),
                baseline_root,
                candidate_root,
                verification_tier=TOOL.AGENT_REVIEWED_LOCAL_PILOT_TIER,
            )
            failed_review = TOOL.paired_evidence_result(
                manifest,
                manifest,
                write_paired_evidence(
                    baseline_root,
                    manifest,
                    side="failed-baseline",
                    verification_tier=TOOL.AGENT_REVIEWED_LOCAL_PILOT_TIER,
                    local_review_result="fail",
                ),
                write_paired_evidence(
                    candidate_root,
                    manifest,
                    side="failed-candidate",
                    verification_tier=TOOL.AGENT_REVIEWED_LOCAL_PILOT_TIER,
                    local_review_result="fail",
                ),
                baseline_root,
                candidate_root,
                verification_tier=TOOL.AGENT_REVIEWED_LOCAL_PILOT_TIER,
            )
        self.assertIn("paired_prompt_mismatch", {item["code"] for item in prompt_mismatch["issues"]})
        self.assertIn("evidence_agent_review_result_invalid", {item["code"] for item in failed_review["issues"]})

    def test_local_pilot_cli_fails_closed_before_loading_candidate_ref(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(Path(TOOL.__file__)),
                "compare",
                "--manifest",
                "/private/tmp/missing-baseline.yaml",
                "--candidate-ref",
                "HEAD",
                "--allow-agent-reviewed-local-pilot",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("local pilot requires --candidate-worktree", result.stdout)
        self.assertIn("local pilot requires both evidence files", result.stdout)

    def test_accepted_local_state_flag_requires_local_pilot_mode(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(Path(TOOL.__file__)),
                "compare",
                "--manifest",
                "/private/tmp/missing-baseline.yaml",
                "--candidate-worktree",
                "--use-accepted-local-pilot-state",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires --allow-agent-reviewed-local-pilot", result.stdout)

    def test_accepted_local_state_revalidates_persisted_evidence_semantics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root, detail="Keep this longer baseline operational detail in the main body.")
            write_beta_fixture(root)
            baseline = snapshot(root)
            write_fixture(root, detail="Keep this detail.")
            accepted_candidate = snapshot(root)
            accepted_candidate["source"]["skills_tree"] = None
            beta_path = root / "source" / "skills" / "beta" / "SKILL.md"
            beta_path.write_text(
                beta_path.read_text(encoding="utf-8").replace(
                    "Support the primary fixture.",
                    "Support the later unrelated fixture change.",
                ),
                encoding="utf-8",
            )
            candidate = snapshot(root)
            baseline_skill = TOOL.index_skills(baseline)["alpha"]
            candidate_skill = TOOL.index_skills(candidate)["alpha"]
            case_ids = ("alpha-positive-001", "alpha-negative-001")

            eval_root = root / "source" / "shared" / "eval"
            canonical_eval_root = find_bundle_root() / "source" / "shared" / "eval"
            for schema_name in (
                "skill-diet-local-pilot-accepted-state.schema.json",
                "skill-diet-local-pilot-evidence.schema.json",
            ):
                (eval_root / schema_name).write_bytes((canonical_eval_root / schema_name).read_bytes())

            state_root = root / TOOL.LOCAL_PILOT_ACCEPTED_STATE_PATH.parent
            baseline_evidence_root = state_root / "pilot-evidence" / "alpha" / "evidence" / "baseline"
            candidate_evidence_root = state_root / "pilot-evidence" / "alpha" / "evidence" / "candidate"
            baseline_evidence = write_paired_evidence(
                baseline_evidence_root,
                baseline,
                side="baseline",
                verification_tier=TOOL.AGENT_REVIEWED_LOCAL_PILOT_TIER,
                case_ids=case_ids,
            )
            candidate_evidence = write_paired_evidence(
                candidate_evidence_root,
                accepted_candidate,
                side="candidate",
                oracle_manifest=baseline,
                verification_tier=TOOL.AGENT_REVIEWED_LOCAL_PILOT_TIER,
                case_ids=case_ids,
            )
            baseline_evidence_path = baseline_evidence_root / "evidence.json"
            candidate_evidence_path = candidate_evidence_root / "evidence.json"
            baseline_evidence_path.write_text(
                json.dumps(baseline_evidence, ensure_ascii=False, sort_keys=True),
                encoding="utf-8",
            )
            candidate_evidence_path.write_text(
                json.dumps(candidate_evidence, ensure_ascii=False, sort_keys=True),
                encoding="utf-8",
            )
            comparison_path = state_root / "pilot-evidence" / "alpha" / "accepted-comparison.json"
            comparison_path.write_text(
                json.dumps(
                    {
                        "skill_id": "alpha",
                        "status": "PASS",
                        "verification_tier": TOOL.AGENT_REVIEWED_LOCAL_PILOT_TIER,
                        "behavior": "agent-reviewed",
                        "admission": "unverified",
                        "release_eligible": False,
                        "body_delta_words": (
                            candidate_skill["measurements"]["body"]["words"]
                            - baseline_skill["measurements"]["body"]["words"]
                        ),
                        "body_delta_utf8_bytes": (
                            candidate_skill["measurements"]["body"]["utf8_bytes"]
                            - baseline_skill["measurements"]["body"]["utf8_bytes"]
                        ),
                        "case_ids": list(case_ids),
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                encoding="utf-8",
            )
            state = {
                "schema_version": 1,
                "verification_tier": TOOL.AGENT_REVIEWED_LOCAL_PILOT_TIER,
                "baseline": {
                    key: baseline["source"][key]
                    for key in ("commit", "skills_tree", "tracked_input_digest")
                },
                "eval_contract_digest": baseline["evaluation_contract"]["digest"],
                "entries": [
                    {
                        "order": 1,
                        "skill_id": "alpha",
                        "source_sha256": candidate_skill["source_sha256"],
                        "content_digests": candidate_skill["content_digests"],
                        "accepted_candidate_tracked_input_digest": accepted_candidate["source"]["tracked_input_digest"],
                        "model": "test-model",
                        "case_ids": list(case_ids),
                        "baseline_evidence": artifact_ref(baseline_evidence_path, state_root),
                        "candidate_evidence": artifact_ref(candidate_evidence_path, state_root),
                        "comparison": artifact_ref(comparison_path, state_root),
                        "result": {
                            "status": "PASS",
                            "behavior": "agent-reviewed",
                            "admission": "unverified",
                            "release_eligible": False,
                        },
                    }
                ],
            }
            state_path = root / TOOL.LOCAL_PILOT_ACCEPTED_STATE_PATH
            state_path.write_text(json.dumps(state, ensure_ascii=False, sort_keys=True), encoding="utf-8")

            with (
                patch.object(TOOL, "LOCAL_PILOT_SKILLS", {"alpha"}),
                patch.object(
                    TOOL,
                    "LOCAL_PILOT_EVAL_CONTRACT_DIGEST",
                    baseline["evaluation_contract"]["digest"],
                ),
                patch.object(
                    TOOL,
                    "LOCAL_PILOT_ACCEPTED_STATE_SHA256",
                    TOOL.sha256_bytes(state_path.read_bytes()),
                ),
            ):
                locks = TOOL.load_pinned_local_pilot_state(root, baseline, candidate)
            self.assertEqual(locks["alpha"], candidate_skill["content_digests"])

            original_comparison = json.loads(comparison_path.read_text(encoding="utf-8"))
            truncated_baseline_evidence = deepcopy(baseline_evidence)
            truncated_candidate_evidence = deepcopy(candidate_evidence)
            truncated_baseline_evidence["runs"] = truncated_baseline_evidence["runs"][:1]
            truncated_candidate_evidence["runs"] = truncated_candidate_evidence["runs"][:1]
            baseline_evidence_path.write_text(
                json.dumps(truncated_baseline_evidence, ensure_ascii=False, sort_keys=True),
                encoding="utf-8",
            )
            candidate_evidence_path.write_text(
                json.dumps(truncated_candidate_evidence, ensure_ascii=False, sort_keys=True),
                encoding="utf-8",
            )
            truncated_comparison = {**original_comparison, "case_ids": [case_ids[0]]}
            comparison_path.write_text(
                json.dumps(truncated_comparison, ensure_ascii=False, sort_keys=True),
                encoding="utf-8",
            )
            truncated_state = deepcopy(state)
            truncated_state["entries"][0]["case_ids"] = [case_ids[0]]
            truncated_state["entries"][0]["baseline_evidence"] = artifact_ref(
                baseline_evidence_path,
                state_root,
            )
            truncated_state["entries"][0]["candidate_evidence"] = artifact_ref(
                candidate_evidence_path,
                state_root,
            )
            truncated_state["entries"][0]["comparison"] = artifact_ref(comparison_path, state_root)
            state_path.write_text(
                json.dumps(truncated_state, ensure_ascii=False, sort_keys=True),
                encoding="utf-8",
            )
            with (
                patch.object(TOOL, "LOCAL_PILOT_SKILLS", {"alpha"}),
                patch.object(
                    TOOL,
                    "LOCAL_PILOT_EVAL_CONTRACT_DIGEST",
                    baseline["evaluation_contract"]["digest"],
                ),
                patch.object(
                    TOOL,
                    "LOCAL_PILOT_ACCEPTED_STATE_SHA256",
                    TOOL.sha256_bytes(state_path.read_bytes()),
                ),
                self.assertRaisesRegex(TOOL.DietError, "coverage validation failed"),
            ):
                TOOL.load_pinned_local_pilot_state(root, baseline, candidate)

            baseline_evidence_path.write_text(
                json.dumps(baseline_evidence, ensure_ascii=False, sort_keys=True),
                encoding="utf-8",
            )
            candidate_evidence_path.write_text(
                json.dumps(candidate_evidence, ensure_ascii=False, sort_keys=True),
                encoding="utf-8",
            )
            mismatched_comparison = {
                **original_comparison,
                "body_delta_words": original_comparison["body_delta_words"] - 1,
            }
            comparison_path.write_text(
                json.dumps(mismatched_comparison, ensure_ascii=False, sort_keys=True),
                encoding="utf-8",
            )
            mismatched_state = deepcopy(state)
            mismatched_state["entries"][0]["comparison"] = artifact_ref(comparison_path, state_root)
            state_path.write_text(
                json.dumps(mismatched_state, ensure_ascii=False, sort_keys=True),
                encoding="utf-8",
            )
            with (
                patch.object(TOOL, "LOCAL_PILOT_SKILLS", {"alpha"}),
                patch.object(
                    TOOL,
                    "LOCAL_PILOT_EVAL_CONTRACT_DIGEST",
                    baseline["evaluation_contract"]["digest"],
                ),
                patch.object(
                    TOOL,
                    "LOCAL_PILOT_ACCEPTED_STATE_SHA256",
                    TOOL.sha256_bytes(state_path.read_bytes()),
                ),
                self.assertRaisesRegex(TOOL.DietError, "body delta mismatch"),
            ):
                TOOL.load_pinned_local_pilot_state(root, baseline, candidate)

            comparison_path.write_text(
                json.dumps(original_comparison, ensure_ascii=False, sort_keys=True),
                encoding="utf-8",
            )
            state_path.write_text(json.dumps(state, ensure_ascii=False, sort_keys=True), encoding="utf-8")

            candidate_run_path = candidate_evidence_root / candidate_evidence["runs"][0]["run_artifact"]["path"]
            candidate_run = json.loads(candidate_run_path.read_text(encoding="utf-8"))
            candidate_run["skill_invoked"] = False
            candidate_run_path.write_text(
                json.dumps(candidate_run, ensure_ascii=False, sort_keys=True),
                encoding="utf-8",
            )
            candidate_evidence["runs"][0]["run_artifact"] = artifact_ref(
                candidate_run_path,
                candidate_evidence_root,
            )
            candidate_evidence_path.write_text(
                json.dumps(candidate_evidence, ensure_ascii=False, sort_keys=True),
                encoding="utf-8",
            )
            state["entries"][0]["candidate_evidence"] = artifact_ref(candidate_evidence_path, state_root)
            state_path.write_text(json.dumps(state, ensure_ascii=False, sort_keys=True), encoding="utf-8")
            with (
                patch.object(TOOL, "LOCAL_PILOT_SKILLS", {"alpha"}),
                patch.object(
                    TOOL,
                    "LOCAL_PILOT_EVAL_CONTRACT_DIGEST",
                    baseline["evaluation_contract"]["digest"],
                ),
                patch.object(
                    TOOL,
                    "LOCAL_PILOT_ACCEPTED_STATE_SHA256",
                    TOOL.sha256_bytes(state_path.read_bytes()),
                ),
                self.assertRaisesRegex(TOOL.DietError, "semantic validation failed"),
            ):
                TOOL.load_pinned_local_pilot_state(root, baseline, candidate)

    def test_accepted_dependency_locks_reject_route_metadata_and_context_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            write_beta_fixture(root)
            historical = snapshot(root)

        route_drift = deepcopy(historical)
        TOOL.index_skills(route_drift)["beta"]["content_digests"]["agent_default_prompt"] = "f" * 64
        routed_runs = {
            ("alpha", "alpha-positive-001"): {
                "skill_id": "alpha",
                "case_id": "alpha-positive-001",
                "observed_primary_skill": "alpha",
                "observed_supporting_skills": ["beta"],
                "admitted_context": [],
            }
        }
        with self.assertRaisesRegex(TOOL.DietError, "accepted routed skill drift"):
            TOOL.validate_accepted_dependency_locks(
                "alpha",
                historical,
                route_drift,
                routed_runs,
            )

        shared_path = "source/shared/docs/policy.md"
        shared_before = {
            "path": shared_path,
            "kind": "shared_doc",
            "sha256": "a" * 64,
            "size": {"words": 2, "characters": 10, "utf8_bytes": 10, "text_status": "utf8"},
        }
        historical_context = deepcopy(historical)
        historical_context["shared_context_inventory"] = [shared_before]
        context_drift = deepcopy(historical_context)
        context_drift["shared_context_inventory"][0]["sha256"] = "b" * 64
        admitted = TOOL.context_unit_index(historical_context)[(shared_path, "full_file")]
        context_runs = {
            ("alpha", "alpha-positive-001"): {
                "skill_id": "alpha",
                "case_id": "alpha-positive-001",
                "observed_primary_skill": "alpha",
                "observed_supporting_skills": [],
                "admitted_context": [admitted],
            }
        }
        with self.assertRaisesRegex(TOOL.DietError, "accepted admitted context drift"):
            TOOL.validate_accepted_dependency_locks(
                "alpha",
                historical_context,
                context_drift,
                context_runs,
            )

    def test_atomic_dependency_group_uses_shared_closure_prefix_and_requires_scc(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root, detail="Long alpha baseline detail for an atomic dependency fixture.")
            write_beta_fixture(root)
            baseline = snapshot(root)
            write_fixture(root, detail="Short alpha detail.")
            beta_path = root / "source" / "skills" / "beta" / "SKILL.md"
            beta_path.write_text(
                beta_path.read_text(encoding="utf-8").replace(
                    "Support the primary fixture.",
                    "Support it.",
                ),
                encoding="utf-8",
            )
            candidate = snapshot(root)

        entries = [
            {"order": 1, "skill_id": "alpha", "atomic_dependency_group": "alpha-beta"},
            {"order": 2, "skill_id": "beta", "atomic_dependency_group": "alpha-beta"},
        ]
        groups = TOOL.accepted_atomic_dependency_groups(entries, 2)
        prefixes = TOOL.accepted_validation_prefixes(baseline, candidate, entries, groups)
        candidate_skills = TOOL.index_skills(candidate)
        for owner in ("alpha", "beta"):
            prefix_skills = TOOL.index_skills(prefixes[owner])
            self.assertEqual(prefix_skills["alpha"]["source_sha256"], candidate_skills["alpha"]["source_sha256"])
            self.assertEqual(prefix_skills["beta"]["source_sha256"], candidate_skills["beta"]["source_sha256"])

        mutual_runs = {
            "alpha": {
                ("alpha", "alpha-positive-001"): {
                    "observed_primary_skill": "alpha",
                    "observed_supporting_skills": ["beta"],
                }
            },
            "beta": {
                ("beta", "beta-positive-001"): {
                    "observed_primary_skill": "beta",
                    "observed_supporting_skills": ["alpha"],
                }
            },
        }
        TOOL.validate_atomic_dependency_group_routes(groups, mutual_runs)
        one_way = deepcopy(mutual_runs)
        one_way["beta"][("beta", "beta-positive-001")]["observed_supporting_skills"] = []
        with self.assertRaisesRegex(TOOL.DietError, "not strongly connected"):
            TOOL.validate_atomic_dependency_group_routes(groups, one_way)

    def test_atomic_dependency_group_rejects_v1_singleton_and_noncontiguous_members(self) -> None:
        singleton = [{"order": 1, "skill_id": "alpha", "atomic_dependency_group": "alpha-beta"}]
        with self.assertRaisesRegex(TOOL.DietError, "require state schema v2"):
            TOOL.accepted_atomic_dependency_groups(singleton, 1)
        with self.assertRaisesRegex(TOOL.DietError, "not a group"):
            TOOL.accepted_atomic_dependency_groups(singleton, 2)

        noncontiguous = [
            {"order": 1, "skill_id": "alpha", "atomic_dependency_group": "alpha-beta"},
            {"order": 2, "skill_id": "gamma"},
            {"order": 3, "skill_id": "beta", "atomic_dependency_group": "alpha-beta"},
        ]
        with self.assertRaisesRegex(TOOL.DietError, "not contiguous"):
            TOOL.accepted_atomic_dependency_groups(noncontiguous, 2)

    def test_same_snapshot_has_zero_delta_and_unverified_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            baseline = snapshot(root)
            result = TOOL.compare_manifests(baseline, snapshot(root))
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["axes"]["structure"], "unchanged")
        self.assertEqual(result["axes"]["behavior"], "unverified")
        self.assertEqual(result["axes"]["admission"], "unverified")
        self.assertEqual(result["aggregate_deltas"]["body"]["utf8_bytes"], 0)
        self.assertNotIn(
            "risk_profile:",
            baseline["skills"][0]["context_targets"]["do_not_load_by_default"],
        )

    def test_same_size_body_and_reference_changes_are_structural_changes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root, detail="AAAA BBBB", reference_text="CCCC DDDD")
            baseline = snapshot(root)
            write_fixture(root, detail="EEEE FFFF", reference_text="GGGG HHHH")
            result = TOOL.compare_manifests(baseline, snapshot(root))
        self.assertEqual(result["axes"]["structure"], "changed")
        self.assertEqual(result["skill_changes"][0]["classification"], "same_size_content_change")
        self.assertTrue(result["skill_changes"][0]["body_content_changed"])
        self.assertTrue(result["skill_changes"][0]["resources_changed"])

    def test_skill_instruction_change_requires_paired_evidence_without_opt_in_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root, detail="Before body detail.")
            baseline = snapshot(root)
            write_fixture(root, detail="After body detail.")
            result = TOOL.compare_manifests(baseline, snapshot(root))
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("paired_behavior_evidence_missing", {item["code"] for item in result["issues"]})

    def test_same_size_description_change_is_trigger_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            baseline = snapshot(root)
            skill = root / "source" / "skills" / "alpha" / "SKILL.md"
            skill.write_text(
                skill.read_text(encoding="utf-8").replace("Alpha description", "Omega description"),
                encoding="utf-8",
            )
            result = TOOL.compare_manifests(baseline, snapshot(root))
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("trigger_metadata_drift", {item["code"] for item in result["issues"]})

    def test_valid_but_changed_policy_is_routing_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            baseline = snapshot(root)
            agent = root / "source" / "skills" / "alpha" / "agents" / "openai.yaml"
            agent.write_text(
                agent.read_text(encoding="utf-8")
                .replace("explicit_procedure", "selective_router")
                .replace("allow_implicit_invocation: false", "allow_implicit_invocation: true"),
                encoding="utf-8",
            )
            result = TOOL.compare_manifests(baseline, snapshot(root))
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("routing_contract_drift", {item["code"] for item in result["issues"]})

    def test_lost_and_weakened_cases_are_regressions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            baseline = snapshot(root)
            eval_path = root / "source" / "shared" / "eval" / "routing_cases.yaml"
            payload = yaml.safe_load(eval_path.read_text(encoding="utf-8"))
            payload["cases"] = payload["cases"][:1]
            payload["cases"][0]["forbidden_behaviors"] = []
            eval_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
            result = TOOL.compare_manifests(baseline, snapshot(root))
        codes = {item["code"] for item in result["issues"]}
        self.assertIn("declared_case_lost", codes)
        self.assertIn("oracle_contract_weakened", codes)

    def test_eval_request_change_is_oracle_contract_change(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            baseline = snapshot(root)
            eval_path = root / "source" / "shared" / "eval" / "routing_cases.yaml"
            payload = yaml.safe_load(eval_path.read_text(encoding="utf-8"))
            payload["cases"][0]["user_request"] = "An easier unrelated request."
            eval_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
            candidate = snapshot(root)
            result = TOOL.compare_manifests(baseline, candidate)
            allowed = TOOL.compare_manifests(
                baseline,
                candidate,
                allow_oracle_contract_change=True,
            )
        self.assertIn("oracle_contract_nonmonotonic_change", {item["code"] for item in result["issues"]})
        self.assertEqual(allowed["status"], "FAIL")
        self.assertEqual(allowed["axes"]["oracle_contract"], "regressed")

    def test_added_skill_fails_the_fixed_skill_set_lane(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            baseline = snapshot(root)
            candidate = deepcopy(baseline)
            extra = deepcopy(candidate["skills"][0])
            extra["skill_id"] = "beta"
            candidate["skills"].append(extra)
            candidate["aggregates"]["skill_count"] += 1
            result = TOOL.compare_manifests(baseline, candidate)
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("skill_added", {item["code"] for item in result["issues"]})

    def test_body_to_reference_is_possible_relocation(self) -> None:
        detail = "Detailed operational behavior that remains owned. " * 12
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root, detail=detail)
            baseline = snapshot(root)
            write_fixture(root, detail="Read references/detail.md when this variant applies.", reference_text=detail)
            result = TOOL.compare_manifests(baseline, snapshot(root))
        change = result["skill_changes"][0]
        self.assertLess(change["body_delta"]["utf8_bytes"], 0)
        self.assertGreater(change["resource_utf8_bytes_delta"], 0)
        self.assertEqual(change["classification"], "possible_relocation")

    def test_read_if_needed_to_must_read_increases_exact_declared_admission(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root, reference_text="Conditional detail.", admission="read_if_needed")
            baseline = snapshot(root)
            write_fixture(root, reference_text="Conditional detail.", admission="must_read")
            result = TOOL.compare_manifests(baseline, snapshot(root))
        change = result["skill_changes"][0]
        self.assertGreater(change["must_read_exact_utf8_bytes_delta"], 0)
        self.assertEqual(result["axes"]["admission"], "unverified")

    def test_missing_admission_receipt_is_null_not_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            skill = snapshot(root)["skills"][0]
        self.assertEqual(skill["observed_admission"]["status"], "unverified")
        self.assertIsNone(skill["observed_admission"]["words"])
        self.assertIsNone(skill["observed_admission"]["utf8_bytes"])

    def test_nested_body_and_routing_card_units_cannot_be_double_counted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            manifest = snapshot(root)
            add_beta_skill(manifest)
            units = TOOL.context_unit_index(manifest)
            keys = [
                (manifest["skills"][0]["source_path"], "full_file"),
                (manifest["skills"][1]["source_path"], "body"),
                (manifest["skills"][1]["source_path"], "routing_card"),
            ]
            admitted = [
                {
                    "path": units[key]["path"],
                    "content_unit": units[key]["content_unit"],
                    "sha256": units[key]["sha256"],
                    "words": units[key]["words"],
                    "utf8_bytes": units[key]["utf8_bytes"],
                }
                for key in keys
            ]
            issues, _ = TOOL.validate_admitted_context(
                manifest,
                {"skill_invoked": True, "admitted_context": admitted},
                "alpha",
                "alpha-positive-001",
                "candidate",
            )
        self.assertIn("evidence_admitted_context_overlap", {item["code"] for item in issues})

    def test_valid_paired_evidence_can_preserve_behavior(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            baseline = snapshot(root)
            candidate = snapshot(root)
            baseline_root = root / "baseline-evidence"
            candidate_root = root / "candidate-evidence"
            paired = paired_result(
                baseline,
                candidate,
                write_paired_evidence(baseline_root, baseline, side="baseline"),
                write_paired_evidence(candidate_root, candidate, side="candidate"),
                baseline_root,
                candidate_root,
            )
            result = TOOL.compare_manifests(
                baseline,
                candidate,
                require_paired=True,
                paired_evidence=paired,
            )
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["axes"]["behavior"], "preserved")
        self.assertEqual(result["axes"]["admission"], "not_improved")

    def test_hash_consistent_receipts_without_external_trust_anchor_are_unverified(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            baseline = snapshot(root)
            baseline_root = root / "baseline-evidence"
            candidate_root = root / "candidate-evidence"
            paired = TOOL.paired_evidence_result(
                baseline,
                baseline,
                write_paired_evidence(baseline_root, baseline, side="baseline"),
                write_paired_evidence(candidate_root, baseline, side="candidate"),
                baseline_root,
                candidate_root,
            )
        self.assertIn("evidence_trust_anchor_missing", {item["code"] for item in paired["issues"]})
        self.assertEqual(paired["behavior"], "unverified")

    def test_unknown_reviewer_cannot_use_a_self_supplied_public_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            baseline = snapshot(root)
            baseline_root = root / "baseline-evidence"
            candidate_root = root / "candidate-evidence"
            paired = TOOL.paired_evidence_result(
                baseline,
                baseline,
                write_paired_evidence(baseline_root, baseline, side="baseline"),
                write_paired_evidence(candidate_root, baseline, side="candidate"),
                baseline_root,
                candidate_root,
                trusted_reviewers={},
            )
        self.assertIn("evidence_reviewer_untrusted", {item["code"] for item in paired["issues"]})
        self.assertEqual(paired["behavior"], "unverified")

    def test_pinned_reviewer_store_rejects_caller_modified_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "source" / "shared" / "eval" / "skill-diet-trusted-reviewers.json"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(find_reviewer_trust_store().read_bytes())
            self.assertEqual(TOOL.load_pinned_trusted_reviewers(root), {})
            target.write_text('{"schema_version":1,"reviewers":[{"reviewer_id":"attacker"}]}', encoding="utf-8")
            with self.assertRaises(TOOL.DietError):
                TOOL.load_pinned_trusted_reviewers(root)

    def test_full_supporting_route_oracle_is_checked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root, detail="AAAA BBBB")
            write_beta_fixture(root)
            eval_path = root / "source" / "shared" / "eval" / "routing_cases.yaml"
            payload = yaml.safe_load(eval_path.read_text(encoding="utf-8"))
            payload["cases"][0]["expected_supporting_skills"] = ["beta"]
            eval_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
            baseline = snapshot(root)
            skill_path = root / "source" / "skills" / "alpha" / "SKILL.md"
            skill_path.write_text(
                skill_path.read_text(encoding="utf-8").replace("AAAA BBBB", "CCCC DDDD"),
                encoding="utf-8",
            )
            candidate = snapshot(root)
            baseline_root = root / "baseline-evidence"
            candidate_root = root / "candidate-evidence"
            paired = paired_result(
                baseline,
                candidate,
                write_paired_evidence(baseline_root, baseline, side="baseline"),
                write_paired_evidence(
                    candidate_root,
                    candidate,
                    side="candidate",
                    observed_supporting_override={"alpha-positive-001": []},
                ),
                baseline_root,
                candidate_root,
            )
        self.assertIn("evidence_observed_supporting_mismatch", {item["code"] for item in paired["issues"]})

    def test_eval_route_oracle_rejects_unknown_skill_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            eval_path = root / "source" / "shared" / "eval" / "routing_cases.yaml"
            payload = yaml.safe_load(eval_path.read_text(encoding="utf-8"))
            payload["cases"][0]["expected_supporting_skills"] = ["ghost-skill"]
            eval_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
            with self.assertRaises(TOOL.DietError):
                snapshot(root)

    def test_stale_paired_file_hash_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            baseline = snapshot(root)
            candidate = snapshot(root)
            baseline_root = root / "baseline-evidence"
            candidate_root = root / "candidate-evidence"
            baseline_evidence = write_paired_evidence(baseline_root, baseline, side="baseline")
            candidate_evidence = write_paired_evidence(candidate_root, candidate, side="candidate")
            candidate_evidence["runs"][0]["output_artifact"]["sha256"] = "0" * 64
            paired = paired_result(
                baseline,
                candidate,
                baseline_evidence,
                candidate_evidence,
                baseline_root,
                candidate_root,
            )
            result = TOOL.compare_manifests(
                baseline,
                candidate,
                require_paired=True,
                paired_evidence=paired,
            )
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("evidence_artifact_hash_mismatch", {item["code"] for item in result["issues"]})

    def test_invalid_independent_review_signature_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            baseline = snapshot(root)
            baseline_root = root / "baseline-evidence"
            candidate_root = root / "candidate-evidence"
            baseline_evidence = write_paired_evidence(baseline_root, baseline, side="baseline")
            candidate_evidence = write_paired_evidence(candidate_root, baseline, side="candidate")
            candidate_evidence["runs"][0]["verifier_signature"] = "0" * 64
            paired = paired_result(
                baseline,
                baseline,
                baseline_evidence,
                candidate_evidence,
                baseline_root,
                candidate_root,
            )
        self.assertIn("evidence_verifier_signature_invalid", {item["code"] for item in paired["issues"]})

    def test_changed_skill_requires_full_positive_negative_structured_edge_scope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root, detail="AAAA BBBB")
            baseline = snapshot(root)
            write_fixture(root, detail="CCCC DDDD")
            candidate = snapshot(root)
            baseline_root = root / "baseline-evidence"
            candidate_root = root / "candidate-evidence"
            paired = paired_result(
                baseline,
                candidate,
                write_paired_evidence(
                    baseline_root,
                    baseline,
                    side="baseline",
                    case_ids=("alpha-positive-001",),
                ),
                write_paired_evidence(
                    candidate_root,
                    candidate,
                    side="candidate",
                    case_ids=("alpha-positive-001",),
                ),
                baseline_root,
                candidate_root,
            )
            result = TOOL.compare_manifests(
                baseline,
                candidate,
                require_paired=True,
                paired_evidence=paired,
            )
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("paired_negative_coverage_missing", {item["code"] for item in result["issues"]})

    def test_legacy_negative_cannot_satisfy_structured_negative_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root, detail="AAAA BBBB")
            baseline = snapshot(root)
            write_fixture(root, detail="CCCC DDDD")
            candidate = snapshot(root)
            baseline["skills"][0]["eval_coverage"]["structured_negative_candidates"] = []
            candidate["skills"][0]["eval_coverage"]["structured_negative_candidates"] = []
            baseline_root = root / "baseline-evidence"
            candidate_root = root / "candidate-evidence"
            paired = paired_result(
                baseline,
                candidate,
                write_paired_evidence(baseline_root, baseline, side="baseline"),
                write_paired_evidence(candidate_root, candidate, side="candidate"),
                baseline_root,
                candidate_root,
            )
            result = TOOL.compare_manifests(
                baseline,
                candidate,
                require_paired=True,
                paired_evidence=paired,
            )
        self.assertIn("paired_structured_negative_contract_missing", {item["code"] for item in result["issues"]})

    def test_changed_skill_with_complete_artifact_chain_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root, detail="AAAA BBBB")
            baseline = snapshot(root)
            write_fixture(root, detail="CCCC DDDD")
            candidate = snapshot(root)
            baseline_root = root / "baseline-evidence"
            candidate_root = root / "candidate-evidence"
            paired = paired_result(
                baseline,
                candidate,
                write_paired_evidence(baseline_root, baseline, side="baseline"),
                write_paired_evidence(candidate_root, candidate, side="candidate"),
                baseline_root,
                candidate_root,
            )
            result = TOOL.compare_manifests(
                baseline,
                candidate,
                require_paired=True,
                paired_evidence=paired,
            )
        self.assertEqual(result["status"], "PASS", result["issues"])
        self.assertEqual(result["axes"]["behavior"], "preserved")

    def test_support_only_skill_uses_explicitly_owned_supporting_positive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root, detail="AAAA BBBB")
            write_beta_fixture(root)
            eval_path = root / "source" / "shared" / "eval" / "routing_cases.yaml"
            payload = yaml.safe_load(eval_path.read_text(encoding="utf-8"))
            payload["cases"][0]["expected_primary_skill"] = "beta"
            payload["cases"][0]["expected_supporting_skills"] = ["alpha"]
            eval_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
            baseline = snapshot(root)
            skill_path = root / "source" / "skills" / "alpha" / "SKILL.md"
            skill_path.write_text(
                skill_path.read_text(encoding="utf-8").replace("AAAA BBBB", "CCCC DDDD"),
                encoding="utf-8",
            )
            candidate = snapshot(root)
            baseline_root = root / "baseline-evidence"
            candidate_root = root / "candidate-evidence"
            paired = paired_result(
                baseline,
                candidate,
                write_paired_evidence(baseline_root, baseline, side="baseline"),
                write_paired_evidence(candidate_root, candidate, side="candidate"),
                baseline_root,
                candidate_root,
            )
            result = TOOL.compare_manifests(
                baseline,
                candidate,
                require_paired=True,
                paired_evidence=paired,
            )
        self.assertEqual(result["status"], "PASS", result["issues"])
        self.assertEqual(result["axes"]["behavior"], "preserved")

    def test_missing_required_evidence_contract_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            baseline = snapshot(root)
            candidate = snapshot(root)
            baseline_root = root / "baseline-evidence"
            candidate_root = root / "candidate-evidence"
            paired = paired_result(
                baseline,
                candidate,
                write_paired_evidence(baseline_root, baseline, side="baseline"),
                write_paired_evidence(
                    candidate_root,
                    candidate,
                    side="candidate",
                    omit_required_results_for={"alpha-positive-001"},
                ),
                baseline_root,
                candidate_root,
            )
        self.assertIn("evidence_required_contract_mismatch", {item["code"] for item in paired["issues"]})

    def test_required_evidence_mutation_control_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            manifest = snapshot(root)
            baseline_root = root / "baseline-evidence"
            candidate_root = root / "candidate-evidence"
            baseline_evidence = write_paired_evidence(
                baseline_root,
                manifest,
                side="baseline",
            )
            candidate_evidence = write_paired_evidence(
                candidate_root,
                manifest,
                side="candidate",
            )
            run = candidate_evidence["runs"][0]
            receipt_path = candidate_root / run["verifier_receipt"]["path"]
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            receipt["required_evidence_results"][0]["result"] = "fail"
            receipt_path.write_text(
                json.dumps(receipt, ensure_ascii=False, sort_keys=True),
                encoding="utf-8",
            )
            run["verifier_receipt"] = artifact_ref(receipt_path, candidate_root)
            run["verifier_signature"] = sign_test_review(receipt_path.read_bytes())
            result = paired_result(
                manifest,
                manifest,
                baseline_evidence,
                candidate_evidence,
                baseline_root,
                candidate_root,
            )
        self.assertIn(
            "evidence_required_result_failed",
            {item["code"] for item in result["issues"]},
        )

    def test_evidence_for_one_skill_cannot_cover_a_second_changed_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            baseline = snapshot(root)
            add_beta_skill(baseline)
            candidate = deepcopy(baseline)
            candidate["skills"][1]["content_digests"]["body"] = "f" * 64
            baseline_root = root / "baseline-evidence"
            candidate_root = root / "candidate-evidence"
            paired = paired_result(
                baseline,
                candidate,
                write_paired_evidence(baseline_root, baseline, side="baseline"),
                write_paired_evidence(candidate_root, candidate, side="candidate"),
                baseline_root,
                candidate_root,
            )
            result = TOOL.compare_manifests(
                baseline,
                candidate,
                require_paired=True,
                paired_evidence=paired,
            )
        matching = [item for item in result["issues"] if item["code"] == "paired_positive_coverage_missing"]
        self.assertTrue(any(item.get("skill_id") == "beta" for item in matching), result["issues"])

    def test_shared_context_relocation_is_counted_in_observed_admission(self) -> None:
        detail = "Relocated shared operational rule. " * 20
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root, detail=detail)
            baseline = snapshot(root)
            write_fixture(root, detail="Load source/shared/docs/relocated.md for this request.")
            shared = root / "source" / "shared" / "docs" / "relocated.md"
            shared.parent.mkdir(parents=True, exist_ok=True)
            shared.write_text(detail, encoding="utf-8")
            candidate = snapshot(root)
            baseline_root = root / "baseline-evidence"
            candidate_root = root / "candidate-evidence"
            paired = paired_result(
                baseline,
                candidate,
                write_paired_evidence(baseline_root, baseline, side="baseline"),
                write_paired_evidence(
                    candidate_root,
                    candidate,
                    side="candidate",
                    extra_context={"alpha-positive-001": [("source/shared/docs/relocated.md", "full_file")]},
                ),
                baseline_root,
                candidate_root,
            )
            result = TOOL.compare_manifests(
                baseline,
                candidate,
                require_paired=True,
                paired_evidence=paired,
            )
        self.assertEqual(result["status"], "PASS", result["issues"])
        self.assertEqual(result["axes"]["admission"], "not_improved")
        self.assertGreaterEqual(
            paired["candidate_admitted"]["utf8_bytes"],
            paired["baseline_admitted"]["utf8_bytes"],
        )

    def test_global_shared_change_derives_all_skill_consumers_and_requires_observation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            shared = root / "source" / "platform" / "codex" / "context-routing.md"
            shared.parent.mkdir(parents=True, exist_ok=True)
            shared.write_text("Global routing contract v1.\n", encoding="utf-8")
            baseline = snapshot(root)
            shared.write_text("Global routing contract v2.\n", encoding="utf-8")
            candidate = snapshot(root)
            baseline_root = root / "baseline-evidence"
            candidate_root = root / "candidate-evidence"
            paired = paired_result(
                baseline,
                candidate,
                write_paired_evidence(baseline_root, baseline, side="baseline"),
                write_paired_evidence(candidate_root, candidate, side="candidate"),
                baseline_root,
                candidate_root,
            )
            result = TOOL.compare_manifests(
                baseline,
                candidate,
                require_paired=True,
                paired_evidence=paired,
            )
        matching = [item for item in result["issues"] if item["code"] == "paired_shared_context_not_observed"]
        self.assertTrue(any(item.get("skill_id") == "alpha" for item in matching), result["issues"])
        self.assertIn("alpha", result["skills_needing_evidence"])

    def test_global_shared_scope_cannot_omit_a_second_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            shared = root / "source" / "platform" / "codex" / "context-routing.md"
            shared.parent.mkdir(parents=True, exist_ok=True)
            shared.write_text("Global routing contract.\n", encoding="utf-8")
            baseline = snapshot(root)
            add_beta_skill(baseline)
            baseline["shared_context_inventory"][0]["consumers"] = ["alpha", "beta"]
            candidate = deepcopy(baseline)
            candidate["shared_context_inventory"][0]["sha256"] = "f" * 64
            baseline_root = root / "baseline-evidence"
            candidate_root = root / "candidate-evidence"
            paired = paired_result(
                baseline,
                candidate,
                write_paired_evidence(baseline_root, baseline, side="baseline"),
                write_paired_evidence(candidate_root, candidate, side="candidate"),
                baseline_root,
                candidate_root,
            )
            result = TOOL.compare_manifests(
                baseline,
                candidate,
                require_paired=True,
                paired_evidence=paired,
                affected_skills={"alpha"},
            )
        self.assertIn("beta", result["skills_needing_evidence"])
        self.assertTrue(
            any(item.get("skill_id") == "beta" for item in result["issues"] if item["code"].startswith("paired_")),
            result["issues"],
        )

    def test_shared_consumer_graph_propagates_context_routing_references(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            routing = root / "source" / "platform" / "codex" / "context-routing.md"
            indirect = root / "source" / "shared" / "docs" / "indirect.md"
            routing.parent.mkdir(parents=True, exist_ok=True)
            indirect.parent.mkdir(parents=True, exist_ok=True)
            routing.write_text("Read .codex/docs/indirect.md when routing applies.\n", encoding="utf-8")
            indirect.write_text("Indirect contract v1.\n", encoding="utf-8")
            baseline = snapshot(root)
            baseline_item = next(
                item for item in baseline["shared_context_inventory"] if item["path"] == "source/shared/docs/indirect.md"
            )
            self.assertEqual(baseline_item["consumers"], ["alpha"])
            indirect.write_text("Indirect contract v2.\n", encoding="utf-8")
            candidate = snapshot(root)
            baseline_root = root / "baseline-evidence"
            candidate_root = root / "candidate-evidence"
            paired = paired_result(
                baseline,
                candidate,
                write_paired_evidence(baseline_root, baseline, side="baseline"),
                write_paired_evidence(candidate_root, candidate, side="candidate"),
                baseline_root,
                candidate_root,
            )
            result = TOOL.compare_manifests(
                baseline,
                candidate,
                require_paired=True,
                paired_evidence=paired,
            )
        matching = [item for item in result["issues"] if item["code"] == "paired_shared_context_not_observed"]
        self.assertTrue(any(item.get("path") == "source/shared/docs/indirect.md" for item in matching))

    def test_affected_shared_change_must_be_observed_in_that_skills_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            baseline = snapshot(root)
            shared = root / "source" / "shared" / "docs" / "new-contract.md"
            shared.parent.mkdir(parents=True, exist_ok=True)
            shared.write_text("New shared behavior contract.\n", encoding="utf-8")
            candidate = snapshot(root)
            baseline_root = root / "baseline-evidence"
            candidate_root = root / "candidate-evidence"
            paired = paired_result(
                baseline,
                candidate,
                write_paired_evidence(baseline_root, baseline, side="baseline"),
                write_paired_evidence(candidate_root, candidate, side="candidate"),
                baseline_root,
                candidate_root,
            )
            result = TOOL.compare_manifests(
                baseline,
                candidate,
                require_paired=True,
                paired_evidence=paired,
                affected_skills={"alpha"},
            )
        matching = [item for item in result["issues"] if item["code"] == "paired_shared_context_not_observed"]
        self.assertTrue(any(item.get("path") == "source/shared/docs/new-contract.md" for item in matching))

    def test_unsafe_artifact_path_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            baseline = snapshot(root)
            baseline_root = root / "baseline-evidence"
            candidate_root = root / "candidate-evidence"
            baseline_evidence = write_paired_evidence(baseline_root, baseline, side="baseline")
            candidate_evidence = write_paired_evidence(candidate_root, baseline, side="candidate")
            candidate_evidence["runs"][0]["run_artifact"]["path"] = "../outside.json"
            paired = paired_result(
                baseline,
                baseline,
                baseline_evidence,
                candidate_evidence,
                baseline_root,
                candidate_root,
            )
        self.assertIn("evidence_artifact_path_unsafe", {item["code"] for item in paired["issues"]})

    def test_new_public_eval_field_changes_oracle_digest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            baseline = snapshot(root)
            eval_path = root / "source" / "shared" / "eval" / "routing_cases.yaml"
            payload = yaml.safe_load(eval_path.read_text(encoding="utf-8"))
            payload["cases"][0]["new_public_contract_field"] = {"must": "remain bound"}
            eval_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
            result = TOOL.compare_manifests(baseline, snapshot(root))
        codes = {item["code"] for item in result["issues"]}
        self.assertIn("evaluation_contract_drift", codes)
        self.assertIn("oracle_contract_nonmonotonic_change", codes)

    def test_candidate_oracle_overlay_can_evaluate_frozen_baseline_and_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            baseline = snapshot(root)
            eval_path = root / "source" / "shared" / "eval" / "routing_cases.yaml"
            payload = yaml.safe_load(eval_path.read_text(encoding="utf-8"))
            payload["cases"][0]["expected_behaviors"].append("report_stricter_shared_oracle")
            eval_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
            candidate = snapshot(root)
            baseline_root = root / "baseline-evidence"
            candidate_root = root / "candidate-evidence"
            paired = paired_result(
                baseline,
                candidate,
                write_paired_evidence(
                    baseline_root,
                    baseline,
                    side="baseline",
                    oracle_manifest=candidate,
                ),
                write_paired_evidence(
                    candidate_root,
                    candidate,
                    side="candidate",
                    oracle_manifest=candidate,
                ),
                baseline_root,
                candidate_root,
                candidate,
            )
            result = TOOL.compare_manifests(
                baseline,
                candidate,
                require_paired=True,
                allow_oracle_contract_change=True,
                paired_evidence=paired,
            )
        self.assertEqual(result["status"], "PASS", result["issues"])
        self.assertEqual(result["axes"]["oracle_contract"], "changed_allowed")
        self.assertEqual(result["axes"]["behavior"], "preserved")

    def test_monotonic_oracle_overlay_scopes_evidence_to_explicit_behavior_owner(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            write_beta_fixture(root)
            baseline = snapshot(root)
            eval_path = root / "source" / "shared" / "eval" / "routing_cases.yaml"
            payload = yaml.safe_load(eval_path.read_text(encoding="utf-8"))
            payload["cases"][0]["expected_supporting_skills"].append("beta")
            eval_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
            result = TOOL.compare_manifests(
                baseline,
                snapshot(root),
                allow_oracle_contract_change=True,
            )
        self.assertEqual(result["status"], "PASS", result["issues"])
        self.assertEqual(result["skills_needing_evidence"], ["alpha"])

    def test_monotonic_oracle_overlay_requires_explicit_behavior_owner(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            eval_path = root / "source" / "shared" / "eval" / "routing_cases.yaml"
            payload = yaml.safe_load(eval_path.read_text(encoding="utf-8"))
            payload["cases"][0].pop("behavior_contract_owners")
            eval_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
            baseline = snapshot(root)
            payload["cases"][0]["expected_behaviors"].append("stronger_without_owner")
            eval_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
            result = TOOL.compare_manifests(
                baseline,
                snapshot(root),
                allow_oracle_contract_change=True,
            )
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("oracle_overlay_owner_missing", {item["code"] for item in result["issues"]})

    def test_oracle_overlay_cannot_remove_required_behavior_or_forbidden_behavior(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            baseline = snapshot(root)
            eval_path = root / "source" / "shared" / "eval" / "routing_cases.yaml"
            payload = yaml.safe_load(eval_path.read_text(encoding="utf-8"))
            payload["cases"][0]["expected_behaviors"] = []
            payload["cases"][0]["forbidden_behaviors"] = []
            eval_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
            candidate = snapshot(root)
            result = TOOL.compare_manifests(
                baseline,
                candidate,
                allow_oracle_contract_change=True,
            )
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("oracle_contract_weakened", {item["code"] for item in result["issues"]})

    def test_required_paired_evidence_fails_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            baseline = snapshot(root)
            result = TOOL.compare_manifests(baseline, snapshot(root), require_paired=True)
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("paired_behavior_evidence_missing", {item["code"] for item in result["issues"]})

    def test_paired_execution_contract_rejects_host_prompt_input_permission_or_validator_drift(self) -> None:
        fields = {
            "host_id": "other-host",
            "prompt_sha256": "1" * 64,
            "input_sha256": "2" * 64,
            "permission_profile_sha256": "3" * 64,
            "validator_sha256": "4" * 64,
        }
        for field, changed_value in fields.items():
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                write_fixture(root)
                manifest = snapshot(root)
                baseline_root = root / "baseline-evidence"
                candidate_root = root / "candidate-evidence"
                baseline_evidence = write_paired_evidence(
                    baseline_root,
                    manifest,
                    side="baseline",
                )
                candidate_evidence = write_paired_evidence(
                    candidate_root,
                    manifest,
                    side="candidate",
                    execution_contract_overrides={field: changed_value},
                )
                result = paired_result(
                    manifest,
                    manifest,
                    baseline_evidence,
                    candidate_evidence,
                    baseline_root,
                    candidate_root,
                )
            mismatches = [
                issue
                for issue in result["issues"]
                if issue.get("code") == "paired_execution_contract_mismatch"
            ]
            self.assertIn(field, {issue.get("field") for issue in mismatches}, mismatches)

    def test_unmatched_current_run_is_not_forward_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            observed = root / "source" / "shared" / "eval" / "observed-runs"
            observed.mkdir(parents=True)
            (observed / "fake.yaml").write_text(
                '''run_id: fake-current
case_id: missing-case
bundle_version: "9.1.2"
observed_route: alpha
model: fake-model
result: fail
''',
                encoding="utf-8",
            )
            manifest = snapshot(root)
        forward = manifest["aggregates"]["forward_evidence"]
        self.assertEqual(forward["status"], "missing_source_bound_current_bundle")
        self.assertEqual(forward["current_bundle_run_inventory_ids"], [])
        self.assertIn("fake-current", forward["invalid_or_unmatched_run_ids"])

    def test_git_snapshot_ignores_untracked_files_and_tree_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "add", "source"], cwd=root, check=True)
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.name=Test",
                    "-c",
                    "user.email=test@example.com",
                    "-c",
                    "commit.gpgsign=false",
                    "commit",
                    "-qm",
                    "fixture",
                ],
                cwd=root,
                check=True,
            )
            (root / "UNTRACKED.md").write_text("must not enter baseline", encoding="utf-8")
            with TOOL.archived_ref(root, "HEAD", label="fixture-baseline") as (archived, info):
                manifest = TOOL.collect_snapshot(archived, info)
            self.assertNotIn("UNTRACKED.md", yaml.safe_dump(manifest))
            broken = deepcopy(manifest)
            broken["source"]["skills_tree"] = "0" * 40
            errors = TOOL.verify_git_provenance(root, broken)
            digest_broken = deepcopy(manifest)
            digest_broken["source"]["tracked_input_digest"] = "0" * 64
            digest_errors = TOOL.verify_git_provenance(root, digest_broken)
        self.assertTrue(any("skills tree mismatch" in error for error in errors), errors)
        self.assertTrue(any("tracked input digest" in error for error in digest_errors), digest_errors)

    def test_candidate_lineage_requires_descendant_commit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "add", "source"], cwd=root, check=True)
            commit_args = [
                "git",
                "-c",
                "user.name=Test",
                "-c",
                "user.email=test@example.com",
                "-c",
                "commit.gpgsign=false",
            ]
            subprocess.run([*commit_args, "commit", "-qm", "baseline"], cwd=root, check=True)
            baseline_commit = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=root,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            ).stdout.strip()
            subprocess.run(
                [*commit_args, "commit", "--allow-empty", "-qm", "candidate"],
                cwd=root,
                check=True,
            )
            descendant_commit = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=root,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            ).stdout.strip()
            tree = subprocess.run(
                ["git", "rev-parse", f"{baseline_commit}^{{tree}}"],
                cwd=root,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            ).stdout.strip()
            unrelated_commit = subprocess.run(
                [*commit_args, "commit-tree", tree],
                cwd=root,
                check=True,
                input="unrelated\n",
                text=True,
                stdout=subprocess.PIPE,
            ).stdout.strip()
            baseline = {"source": {"commit": baseline_commit}}
            descendant = {"source": {"commit": descendant_commit}}
            unrelated = {"source": {"commit": unrelated_commit}}
            self.assertEqual(TOOL.candidate_lineage_issues(root, baseline, descendant), [])
            issues = TOOL.candidate_lineage_issues(root, baseline, unrelated)
        self.assertEqual({item["code"] for item in issues}, {"candidate_not_descendant"})

    def test_check_cli_applies_schema_and_git_provenance_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "add", "source"], cwd=root, check=True)
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.name=Test",
                    "-c",
                    "user.email=test@example.com",
                    "-c",
                    "commit.gpgsign=false",
                    "commit",
                    "-qm",
                    "fixture",
                ],
                cwd=root,
                check=True,
            )
            with TOOL.archived_ref(root, "HEAD", label="fixture-baseline") as (archived, info):
                manifest = TOOL.collect_snapshot(archived, info)
            schema_target = root / "source" / "shared" / "eval" / "skill-diet-baseline.schema.json"
            schema_target.write_bytes(find_baseline_schema().read_bytes())
            trust_target = root / "source" / "shared" / "eval" / "skill-diet-trusted-reviewers.json"
            trust_target.write_bytes(find_reviewer_trust_store().read_bytes())
            manifest_path = root / "baseline.yaml"
            manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
            valid = subprocess.run(
                [
                    sys.executable,
                    str(Path(TOOL.__file__)),
                    "check",
                    "--root",
                    str(root),
                    "--manifest",
                    str(manifest_path),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            broken = deepcopy(manifest)
            broken["source"]["tracked_input_digest"] = "forged"
            manifest_path.write_text(yaml.safe_dump(broken, sort_keys=False), encoding="utf-8")
            invalid = subprocess.run(
                [
                    sys.executable,
                    str(Path(TOOL.__file__)),
                    "check",
                    "--root",
                    str(root),
                    "--manifest",
                    str(manifest_path),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
        self.assertEqual(valid.returncode, 0, valid.stdout)
        self.assertNotEqual(invalid.returncode, 0, invalid.stdout)


if __name__ == "__main__":
    unittest.main()
