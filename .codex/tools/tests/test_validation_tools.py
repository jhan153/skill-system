from __future__ import annotations

import subprocess
import sys
import unittest
import json
import os
import hashlib
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / ".codex" / "tools" / "tests" / "fixtures"
sys.dont_write_bytecode = True


class ValidationToolTests(unittest.TestCase):
    def run_tool(self, *args: str) -> subprocess.CompletedProcess[str]:
        env = dict(os.environ)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=30,
        )

    def temp_ledger(self, name: str) -> Path:
        fd, path = tempfile.mkstemp(prefix=f"skill-system-test-{name}-", suffix=".jsonl", dir="/private/tmp")
        os.close(fd)
        ledger = Path(path)
        ledger.unlink()
        self.addCleanup(lambda: ledger.unlink(missing_ok=True))
        return ledger

    def hooks_json_command(self, event_name: str = "UserPromptSubmit") -> str:
        hooks_config = json.loads((ROOT / ".codex" / "hooks.json").read_text(encoding="utf-8"))
        return hooks_config["hooks"][event_name][0]["hooks"][0]["command"]

    def assert_passes(self, *args: str) -> None:
        result = self.run_tool(*args)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def assert_fails(self, *args: str) -> None:
        result = self.run_tool(*args)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_eval_valid_fixture_passes(self) -> None:
        self.assert_passes(
            ".codex/tools/validate_eval_cases.py",
            str(FIXTURES / "eval-valid.yaml"),
            "--schema",
            ".codex/eval/eval-case.schema.json",
        )

    def test_eval_invalid_fixture_fails(self) -> None:
        self.assert_fails(
            ".codex/tools/validate_eval_cases.py",
            str(FIXTURES / "eval-invalid.yaml"),
            "--schema",
            ".codex/eval/eval-case.schema.json",
        )

    def test_field_feedback_valid_fixture_passes(self) -> None:
        self.assert_passes(
            ".codex/tools/validate_field_feedback.py",
            str(FIXTURES / "field-feedback-valid.yaml"),
            "--schema",
            ".codex/field-feedback/field-feedback.schema.json",
        )

    def test_field_feedback_invalid_fixture_fails(self) -> None:
        self.assert_fails(
            ".codex/tools/validate_field_feedback.py",
            str(FIXTURES / "field-feedback-invalid.yaml"),
            "--schema",
            ".codex/field-feedback/field-feedback.schema.json",
        )

    def test_source_registry_valid_fixture_passes(self) -> None:
        self.assert_passes(".codex/tools/validate_source_registry.py", str(FIXTURES / "source-registry-valid.yaml"))

    def test_source_registry_invalid_fixture_fails(self) -> None:
        self.assert_fails(".codex/tools/validate_source_registry.py", str(FIXTURES / "source-registry-invalid.yaml"))

    def test_knowledge_store_valid_fixture_passes(self) -> None:
        self.assert_passes(
            ".codex/tools/validate_knowledge_store.py",
            str(FIXTURES / "knowledge-store" / "valid"),
            "--schemas",
            ".codex/schemas/knowledge",
            "--require-projections",
        )

    def test_context_pack_build_check_passes(self) -> None:
        self.assert_passes(
            ".codex/tools/build_context_pack.py",
            str(FIXTURES / "knowledge-store" / "valid"),
            "--rebuild-projections",
            "--build-run-pack",
            "--check",
        )

    def test_context_pack_builder_respects_task_budget_and_hops(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            output_dir = Path(tmp) / "generated"
            self.assert_passes(
                ".codex/tools/build_context_pack.py",
                str(FIXTURES / "knowledge-store" / "valid"),
                "--output",
                str(output_dir),
                "--task",
                "x",
                "--token-budget",
                "1",
                "--max-hops",
                "0",
                "--write",
            )
            pack_text = (output_dir / "context-packs" / "CP-20260621-101.yaml").read_text(encoding="utf-8")
            self.assertIn("admitted_claims: []", pack_text)
            self.assertIn("relation_paths: []", pack_text)
            self.assertFalse((output_dir / "wiki" / "index.md").exists())
            self.assertFalse((output_dir / "runtime" / "index.jsonl").exists())

    def test_context_pack_builder_excludes_unverified_claims(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            store_dir = Path(tmp) / "knowledge-store"
            output_dir = Path(tmp) / "generated"
            shutil.copytree(FIXTURES / "knowledge-store" / "valid", store_dir)
            claims_file = store_dir / "claims.yaml"
            claims_text = claims_file.read_text(encoding="utf-8")
            claims_text = claims_text.replace(
                (
                    "  - claim_id: KC-20260621-103\n"
                    "    claim_type: plan_state\n"
                    "    statement: \"Active Kanboard card KB-20260621-001 anchors the current 8.0 implementation context.\"\n"
                    "    authority_class: operational\n"
                    "    context_density: low\n"
                    "    verification_state: agent-verified\n"
                ),
                (
                    "  - claim_id: KC-20260621-103\n"
                    "    claim_type: plan_state\n"
                    "    statement: \"Active Kanboard card KB-20260621-001 anchors the current 8.0 implementation context.\"\n"
                    "    authority_class: operational\n"
                    "    context_density: low\n"
                    "    verification_state: unverified\n"
                ),
                1,
            )
            claims_file.write_text(claims_text, encoding="utf-8")
            self.assert_passes(
                ".codex/tools/build_context_pack.py",
                str(store_dir),
                "--output",
                str(output_dir),
                "--write",
            )
            pack_text = (output_dir / "context-packs" / "CP-20260621-101.yaml").read_text(encoding="utf-8")
            self.assertNotIn("KC-20260621-103", pack_text)
            self.assertFalse((output_dir / "wiki" / "index.md").exists())

    def test_projection_rebuild_and_validator_share_admissible_claim_policy(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            store_dir = Path(tmp) / "knowledge-store"
            shutil.copytree(FIXTURES / "knowledge-store" / "valid", store_dir)
            claims_file = store_dir / "claims.yaml"
            claims_text = claims_file.read_text(encoding="utf-8").replace(
                "  - claim_id: KC-20260621-103\n"
                "    claim_type: plan_state\n"
                "    statement: \"Active Kanboard card KB-20260621-001 anchors the current 8.0 implementation context.\"\n"
                "    authority_class: operational\n"
                "    context_density: low\n"
                "    verification_state: agent-verified\n",
                "  - claim_id: KC-20260621-103\n"
                "    claim_type: plan_state\n"
                "    statement: \"Active Kanboard card KB-20260621-001 anchors the current 8.0 implementation context.\"\n"
                "    authority_class: operational\n"
                "    context_density: low\n"
                "    verification_state: unverified\n",
                1,
            )
            claims_file.write_text(claims_text, encoding="utf-8")
            self.assert_passes(
                ".codex/tools/build_context_pack.py",
                str(store_dir),
                "--rebuild-projections",
                "--write",
            )
            self.assert_passes(
                ".codex/tools/validate_knowledge_store.py",
                str(store_dir),
                "--schemas",
                ".codex/schemas/knowledge",
                "--require-projections",
            )
            wiki_text = (store_dir / "wiki" / "index.md").read_text(encoding="utf-8")
            self.assertNotIn("KC-20260621-103", wiki_text)

    def test_context_pack_includes_active_kanboard_anchor(self) -> None:
        store_dir = FIXTURES / "knowledge-store" / "valid"
        pack_text = (store_dir / "context-packs" / "CP-20260621-101.yaml").read_text(encoding="utf-8")
        index_text = (store_dir / "runtime" / "index.jsonl").read_text(encoding="utf-8")
        card_text = (store_dir / "runtime" / "cards" / "KC-20260621-103.md").read_text(encoding="utf-8")

        self.assertIn("kanboard://card/KB-20260621-001", pack_text)
        self.assertIn('"source_states":{"SRC-20260621-102":"kanboard:active"}', index_text)
        self.assertIn("SRC-20260621-102=kanboard:active", card_text)

    def test_analysis_codebase_default_policy_collects_cpp_repo(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            repo = Path(tmp) / "cpp-repo"
            output = Path(tmp) / "analysis"
            (repo / "src").mkdir(parents=True)
            (repo / "assets").mkdir()
            (repo / "src" / "main.cpp").write_text(
                (
                    '#include "app.h"\n'
                    "int helper() { return 1; }\n"
                    "int main(int argc, char **argv) {\n"
                    "  if (argc > 1) { return helper(); }\n"
                    "  return 0;\n"
                    "}\n"
                ),
                encoding="utf-8",
            )
            (repo / "src" / "app.h").write_text("struct AppState { int value; };\n", encoding="utf-8")
            (repo / "assets" / "mesh.stl").write_text("solid mesh\nendsolid mesh\n", encoding="utf-8")
            (repo / "CMakeLists.txt").write_text(
                "cmake_minimum_required(VERSION 3.20)\nadd_executable(sample src/main.cpp)\n",
                encoding="utf-8",
            )
            subprocess.run(["git", "init"], cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            subprocess.run(["git", "add", "."], cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)

            result = subprocess.run(
                [
                    "bash",
                    str(ROOT / ".codex/skills/analysis-codebase/scripts/collect.sh"),
                    "--repo-path",
                    str(repo),
                    "--mode",
                    "static",
                    "--output-dir",
                    str(output),
                    "--policy",
                    str(ROOT / ".codex/skills/analysis-codebase/references/policy-default.json"),
                ],
                cwd=ROOT,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
                timeout=30,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            classification = (output / "artifacts" / "static" / "path-classification.tsv").read_text(encoding="utf-8")
            self.assertIn("src/main.cpp\tcode\ttrue\tfallback:code_ext\t.cpp", classification)
            self.assertIn("assets/mesh.stl\texcluded\tfalse\texclude_extension:.stl\t.stl", classification)
            self.assertNotIn("outside_include_prefix", classification)

            complexity = json.loads((output / "artifacts" / "static" / "complexity.json").read_text(encoding="utf-8"))
            main_row = next(row for row in complexity["top_files"] if row["file"] == "src/main.cpp")
            self.assertGreaterEqual(main_row["functions"], 1)

            entrypoints = json.loads((output / "artifacts" / "architecture" / "entrypoints.json").read_text(encoding="utf-8"))
            provenances = {item.get("provenance") for item in entrypoints.get("items", [])}
            self.assertIn("cpp-main", provenances)
            self.assertIn("cmake-add-executable", provenances)

            report = output / "codebase-analysis-report.md"
            result = self.run_tool(
                ".codex/skills/analysis-codebase/scripts/report.py",
                "--input-dir",
                str(output),
                "--output",
                str(report),
                "--policy",
                ".codex/skills/analysis-codebase/references/policy-default.json",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report_text = report.read_text(encoding="utf-8")
            self.assertIn("c_cpp_lizard_status", report_text)

    def test_knowledge_store_missing_source_ref_fails(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            store_dir = Path(tmp) / "knowledge-store"
            shutil.copytree(FIXTURES / "knowledge-store" / "valid", store_dir)
            claims_file = store_dir / "claims.yaml"
            claims_file.write_text(
                claims_file.read_text(encoding="utf-8").replace("SRC-20260621-101", "SRC-20260621-999", 1),
                encoding="utf-8",
            )
            self.assert_fails(
                ".codex/tools/validate_knowledge_store.py",
                str(store_dir),
                "--schemas",
                ".codex/schemas/knowledge",
            )

    def test_knowledge_store_completed_plan_source_admission_fails(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            store_dir = Path(tmp) / "knowledge-store"
            shutil.copytree(FIXTURES / "knowledge-store" / "valid", store_dir)
            claims_file = store_dir / "claims.yaml"
            claims_file.write_text(
                claims_file.read_text(encoding="utf-8").replace(
                    'source_id: SRC-20260621-102\n        span: "kanboard://card/KB-20260621-001#status"',
                    'source_id: SRC-20260621-103\n        span: "docs/plan/2026-06-21-context-assurance-llm-wiki-kanboard.md#closeout"',
                ),
                encoding="utf-8",
            )
            self.assert_fails(
                ".codex/tools/validate_knowledge_store.py",
                str(store_dir),
                "--schemas",
                ".codex/schemas/knowledge",
            )

    def test_knowledge_store_stale_source_propagation_fails(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            store_dir = Path(tmp) / "knowledge-store"
            shutil.copytree(FIXTURES / "knowledge-store" / "valid", store_dir)
            sources_file = store_dir / "sources.yaml"
            sources_file.write_text(
                sources_file.read_text(encoding="utf-8").replace("freshness: current", "freshness: stale", 1),
                encoding="utf-8",
            )
            self.assert_fails(
                ".codex/tools/validate_knowledge_store.py",
                str(store_dir),
                "--schemas",
                ".codex/schemas/knowledge",
            )

    def test_context_pack_build_check_detects_stale_runtime_projection(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            store_dir = Path(tmp) / "knowledge-store"
            shutil.copytree(FIXTURES / "knowledge-store" / "valid", store_dir)
            index_file = store_dir / "runtime" / "index.jsonl"
            index_file.write_text(
                index_file.read_text(encoding="utf-8").replace("KC-20260621-101", "KC-20260621-999", 1),
                encoding="utf-8",
            )
            self.assert_fails(".codex/tools/build_context_pack.py", str(store_dir), "--rebuild-projections", "--check")

    def test_context_pack_build_check_detects_pack_hash_tamper(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            store_dir = Path(tmp) / "knowledge-store"
            shutil.copytree(FIXTURES / "knowledge-store" / "valid", store_dir)
            pack_file = store_dir / "context-packs" / "CP-20260621-101.yaml"
            pack_file.write_text(
                pack_file.read_text(encoding="utf-8").replace(
                    "c9b042b92ead57c671a0a3f6b6915191d23f83252c9d970214d49fd4bcce3f75",
                    "0000000000000000000000000000000000000000000000000000000000000000",
                ),
                encoding="utf-8",
            )
            self.assert_fails(
                ".codex/tools/validate_knowledge_store.py",
                str(store_dir),
                "--schemas",
                ".codex/schemas/knowledge",
                "--require-projections",
            )

    def test_knowledge_store_detects_raw_source_handle_revision_mismatch(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            store_dir = Path(tmp) / "knowledge-store"
            shutil.copytree(FIXTURES / "knowledge-store" / "valid", store_dir)
            pack_file = store_dir / "context-packs" / "CP-20260621-101.yaml"
            pack_file.write_text(
                pack_file.read_text(encoding="utf-8").replace(
                    "revision: b7a029a897634fc162fc795512063c66b2e737eab7fa665dca3f261adec3c235",
                    "revision: 0000000000000000000000000000000000000000000000000000000000000000",
                    1,
                ),
                encoding="utf-8",
            )
            self.assert_fails(
                ".codex/tools/validate_knowledge_store.py",
                str(store_dir),
                "--schemas",
                ".codex/schemas/knowledge",
                "--require-projections",
            )

    def test_behavior_invalid_fixture_fails(self) -> None:
        self.assert_fails(
            ".codex/tools/run_behavior_evals.py",
            "--mode",
            "replay",
            "--eval-path",
            str(FIXTURES / "eval-valid.yaml"),
            "--observed-runs",
            str(FIXTURES / "observed-runs"),
        )

    def test_research_ledger_passes(self) -> None:
        self.assert_passes(
            ".codex/tools/validate_research_ledger.py",
            ".codex/research/ledger.yaml",
            "--schema",
            ".codex/research/research-ledger.schema.json",
        )

    def test_knowledge_profile_passes(self) -> None:
        self.assert_passes(".codex/tools/verify_bundle.py", "--profile", "knowledge", "--format", "text")

    def test_default_release_pipeline_includes_knowledge_profile(self) -> None:
        text = (ROOT / ".codex" / "tools" / "run_verification_pipeline.py").read_text(encoding="utf-8")
        self.assertIn('"knowledge"', text.split("DEFAULT_PROFILES =", 1)[1].split("\n", 1)[0])

    def test_bundle_hygiene_rejects_cache_artifacts(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            root = Path(tmp)
            shutil.copytree(ROOT, root / "bundle", ignore=shutil.ignore_patterns(".git", "*.zip", "__pycache__"))
            cache_dir = root / "bundle" / ".pytest_cache"
            cache_dir.mkdir()
            (cache_dir / "README").write_text("cache", encoding="utf-8")
            self.assert_fails(".codex/tools/check_bundle_hygiene.py", str(root / "bundle"))

    def test_knowledge_routing_eval_cases_pass(self) -> None:
        self.assert_passes(
            ".codex/tools/validate_eval_cases.py",
            ".codex/eval/knowledge_routing_cases.yaml",
            "--schema",
            ".codex/eval/eval-case.schema.json",
        )

    def test_knowledge_negative_eval_cases_pass(self) -> None:
        self.assert_passes(
            ".codex/tools/validate_eval_cases.py",
            ".codex/eval/knowledge_negative_cases.yaml",
            "--schema",
            ".codex/eval/eval-case.schema.json",
        )

    def test_memory_explicit_contract_passes(self) -> None:
        self.assert_passes(".codex/tools/check_memory_explicit_contract.py")

    def test_context_compounding_plan_check_passes(self) -> None:
        self.assert_passes(".codex/tools/check_context_compounding_plan.py")

    def test_context_compounding_plan_check_fails_without_public_contract(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            readme = Path(tmp) / "README.md"
            readme.write_text(
                (ROOT / "README.md").read_text(encoding="utf-8").replace(
                    "8.0.0 — Context Compounding / Wiki Bank Architecture",
                    "8.0.0 Context Compounding",
                ),
                encoding="utf-8",
            )
            self.assert_fails(
                ".codex/tools/check_context_compounding_plan.py",
                "--readme",
                str(readme),
            )

    def test_hook_runtime_records_event(self) -> None:
        ledger = self.temp_ledger("hook-events")
        if ledger.exists():
            ledger.unlink()
        self.assert_passes(
            ".codex/tools/hook_runtime.py",
            "record",
            "--event",
            "tool_preflight",
            "--host",
            "codex",
            "--host-event",
            "PreToolUse",
            "--support-level",
            "native",
            "--tool-id",
            "functions.exec_command",
            "--evidence",
            "{}",
            "--ledger",
            str(ledger),
            "--run-id",
            "AR-TEST-001",
        )
        self.assertTrue(ledger.exists())
        event = json.loads(ledger.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(event["schema_version"], 2)
        self.assertEqual(event["run_id"], "AR-TEST-001")
        self.assertEqual(event["seq"], 1)
        self.assertEqual(event["prev_event_hash"], "0" * 64)
        self.assertRegex(event["event_hash"], r"^[a-f0-9]{64}$")
        ledger.unlink()

    def test_hook_runtime_records_hash_chain(self) -> None:
        ledger = self.temp_ledger("hook-chain")
        if ledger.exists():
            ledger.unlink()
        for event_name, host_event in [("request_received", "UserPromptSubmit"), ("context_loaded", "SessionStart")]:
            self.assert_passes(
                ".codex/tools/hook_runtime.py",
                "record",
                "--event",
                event_name,
                "--host",
                "codex",
                "--host-event",
                host_event,
                "--support-level",
                "native",
                "--evidence",
                "{}",
                "--ledger",
                str(ledger),
                "--run-id",
                "AR-TEST-CHAIN",
            )
        events = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines()]
        self.assertEqual([event["seq"] for event in events], [1, 2])
        self.assertEqual(events[1]["prev_event_hash"], events[0]["event_hash"])
        ledger.unlink()

    def test_hook_runtime_parallel_writers_keep_hash_chain(self) -> None:
        ledger = self.temp_ledger("hook-chain-parallel")
        if ledger.exists():
            ledger.unlink()
        processes = [
            subprocess.Popen(
                [
                    sys.executable,
                    ".codex/tools/hook_runtime.py",
                    "record",
                    "--event",
                    "tool_preflight",
                    "--host",
                    "codex",
                    "--host-event",
                    "PreToolUse",
                    "--support-level",
                    "native",
                    "--tool-id",
                    "functions.exec_command",
                    "--evidence",
                    "{}",
                    "--ledger",
                    str(ledger),
                    "--run-id",
                    "AR-TEST-PARALLEL",
                ],
                cwd=ROOT,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            for _ in range(12)
        ]
        for process in processes:
            stdout, stderr = process.communicate(timeout=30)
            self.assertEqual(process.returncode, 0, stdout + stderr)
        events = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(events), 12)
        self.assertEqual([event["seq"] for event in events], list(range(1, 13)))
        for idx in range(1, len(events)):
            self.assertEqual(events[idx]["prev_event_hash"], events[idx - 1]["event_hash"])
        ledger.unlink()

    def test_lifecycle_event_schema_accepts_current_v2_event(self) -> None:
        if str(ROOT / ".codex" / "tools") not in sys.path:
            sys.path.insert(0, str(ROOT / ".codex" / "tools"))
        from _validation import validate_schema

        schema = json.loads((ROOT / ".codex" / "schemas" / "harness" / "lifecycle-event.schema.json").read_text(encoding="utf-8"))
        schema = schema["$defs"]["lifecycle_event_v2"]
        event = json.loads((FIXTURES / "agent-runs" / "current-run" / "hook-events.jsonl").read_text(encoding="utf-8").splitlines()[0])
        errors = validate_schema(event, schema)
        self.assertEqual(errors, [])

    def test_agent_run_artifact_fixture_passes(self) -> None:
        self.assert_passes(
            ".codex/tools/validate_agent_run_artifact.py",
            str(FIXTURES / "agent-runs" / "current-run"),
            "--schema",
            ".codex/schemas/harness/agent-run.schema.json",
        )

    def test_agent_run_artifact_context_hash_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            run_dir = Path(tmp) / "current-run"
            shutil.copytree(FIXTURES / "agent-runs" / "current-run", run_dir)
            run_file = run_dir / "run.yaml"
            run_text = run_file.read_text(encoding="utf-8")
            run_file.write_text(
                run_text.replace(
                    "context_pack_hash: 217ec8828599eeda2ccb4a4058a5378b36e691d99da30793d4cdd09ba29bec97",
                    "context_pack_hash: 0000000000000000000000000000000000000000000000000000000000000000",
                ),
                encoding="utf-8",
            )
            self.assert_fails(
                ".codex/tools/validate_agent_run_artifact.py",
                str(run_dir),
                "--schema",
                ".codex/schemas/harness/agent-run.schema.json",
            )

    def test_agent_run_artifact_context_claim_set_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            run_dir = Path(tmp) / "current-run"
            shutil.copytree(FIXTURES / "agent-runs" / "current-run", run_dir)
            run_file = run_dir / "run.yaml"
            run_file.write_text(
                run_file.read_text(encoding="utf-8").replace("KC-20260621-001", "KC-20990101-999", 1),
                encoding="utf-8",
            )
            self.assert_fails(
                ".codex/tools/validate_agent_run_artifact.py",
                str(run_dir),
                "--schema",
                ".codex/schemas/harness/agent-run.schema.json",
            )

    def test_agent_run_artifact_context_pack_id_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            run_dir = Path(tmp) / "current-run"
            shutil.copytree(FIXTURES / "agent-runs" / "current-run", run_dir)
            run_file = run_dir / "run.yaml"
            run_file.write_text(
                run_file.read_text(encoding="utf-8").replace("context_pack_id: CP-20260621-001", "context_pack_id: CP-20990101-999", 1),
                encoding="utf-8",
            )
            self.assert_fails(
                ".codex/tools/validate_agent_run_artifact.py",
                str(run_dir),
                "--schema",
                ".codex/schemas/harness/agent-run.schema.json",
            )

    def test_agent_run_artifact_primary_skill_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            run_dir = Path(tmp) / "current-run"
            shutil.copytree(FIXTURES / "agent-runs" / "current-run", run_dir)
            run_file = run_dir / "run.yaml"
            run_file.write_text(
                run_file.read_text(encoding="utf-8").replace("primary_skill: workflow-rigor", "primary_skill: analysis-router", 1),
                encoding="utf-8",
            )
            self.assert_fails(
                ".codex/tools/validate_agent_run_artifact.py",
                str(run_dir),
                "--schema",
                ".codex/schemas/harness/agent-run.schema.json",
            )

    def test_agent_run_artifact_relation_path_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            run_dir = Path(tmp) / "current-run"
            shutil.copytree(FIXTURES / "agent-runs" / "current-run", run_dir)
            run_file = run_dir / "run.yaml"
            run_file.write_text(
                run_file.read_text(encoding="utf-8").replace("relation_path_ids: []", "relation_path_ids:\n          - RP-20990101-999", 1),
                encoding="utf-8",
            )
            self.assert_fails(
                ".codex/tools/validate_agent_run_artifact.py",
                str(run_dir),
                "--schema",
                ".codex/schemas/harness/agent-run.schema.json",
            )

    def test_agent_run_artifact_retrieved_claim_support_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            run_dir = Path(tmp) / "current-run"
            shutil.copytree(FIXTURES / "agent-runs" / "current-run", run_dir)
            run_file = run_dir / "run.yaml"
            run_file.write_text(
                run_file.read_text(encoding="utf-8").replace(
                    (
                        "      support:\n"
                        "        type: command_exit\n"
                        "        command: \"python3 .codex/tools/verify_bundle.py --profile agent-output --format text\"\n"
                        "        exit_code: 0\n"
                        "        evidence_ref: artifacts/verification.txt\n"
                    ),
                    (
                        "      support:\n"
                        "        type: retrieved_claim\n"
                        "        claim_id: KC-20990101-999\n"
                        "        source_id: SRC-20260621-001\n"
                        "        evidence_ref: artifacts/verification.txt\n"
                    ),
                    1,
                ),
                encoding="utf-8",
            )
            self.assert_fails(
                ".codex/tools/validate_agent_run_artifact.py",
                str(run_dir),
                "--schema",
                ".codex/schemas/harness/agent-run.schema.json",
            )

    def test_agent_run_artifact_context_pack_schema_error_fails(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            run_dir = Path(tmp) / "current-run"
            shutil.copytree(FIXTURES / "agent-runs" / "current-run", run_dir)
            pack_file = run_dir / "context" / "context-pack.yaml"
            pack_text = pack_file.read_text(encoding="utf-8").replace("verification_state: agent-verified", "verification_state: verified")
            pack_file.write_text(pack_text, encoding="utf-8")
            new_hash = hashlib.sha256(pack_file.read_bytes()).hexdigest()
            run_file = run_dir / "run.yaml"
            run_file.write_text(
                run_file.read_text(encoding="utf-8").replace(
                    "217ec8828599eeda2ccb4a4058a5378b36e691d99da30793d4cdd09ba29bec97",
                    new_hash,
                ),
                encoding="utf-8",
            )
            self.assert_fails(
                ".codex/tools/validate_agent_run_artifact.py",
                str(run_dir),
                "--schema",
                ".codex/schemas/harness/agent-run.schema.json",
            )

    def test_agent_run_artifact_hook_hash_tamper_fails(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            run_dir = Path(tmp) / "current-run"
            shutil.copytree(FIXTURES / "agent-runs" / "current-run", run_dir)
            hook_file = run_dir / "hook-events.jsonl"
            hook_file.write_text(
                hook_file.read_text(encoding="utf-8").replace(
                    "ed88d6eee32d9f0a7c614db603c47b2097e7852660bdc0cca2264d693f3cdddc",
                    "0000000000000000000000000000000000000000000000000000000000000000",
                    1,
                ),
                encoding="utf-8",
            )
            self.assert_fails(
                ".codex/tools/validate_agent_run_artifact.py",
                str(run_dir),
                "--schema",
                ".codex/schemas/harness/agent-run.schema.json",
            )

    def test_agent_run_artifact_duplicate_finalize_fails(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            run_dir = Path(tmp) / "current-run"
            shutil.copytree(FIXTURES / "agent-runs" / "current-run", run_dir)
            self.assert_passes(
                ".codex/tools/hook_runtime.py",
                "record",
                "--event",
                "turn_finalize",
                "--host",
                "codex",
                "--host-event",
                "Stop",
                "--status",
                "pass",
                "--support-level",
                "native",
                "--evidence",
                "{}",
                "--ledger",
                str(run_dir / "hook-events.jsonl"),
                "--run-id",
                "AR-20260621-004",
            )
            self.assert_fails(
                ".codex/tools/validate_agent_run_artifact.py",
                str(run_dir),
                "--schema",
                ".codex/schemas/harness/agent-run.schema.json",
            )

    def test_agent_run_artifact_missing_finalize_fails(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            run_dir = Path(tmp) / "current-run"
            shutil.copytree(FIXTURES / "agent-runs" / "current-run", run_dir)
            hook_file = run_dir / "hook-events.jsonl"
            lines = hook_file.read_text(encoding="utf-8").splitlines()
            hook_file.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")
            self.assert_fails(
                ".codex/tools/validate_agent_run_artifact.py",
                str(run_dir),
                "--schema",
                ".codex/schemas/harness/agent-run.schema.json",
            )

    def test_agent_run_artifact_prefinalize_without_finalize_passes(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            run_dir = Path(tmp) / "current-run"
            shutil.copytree(FIXTURES / "agent-runs" / "current-run", run_dir)
            hook_file = run_dir / "hook-events.jsonl"
            lines = hook_file.read_text(encoding="utf-8").splitlines()
            hook_file.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")
            self.assert_passes(
                ".codex/tools/validate_agent_run_artifact.py",
                str(run_dir),
                "--schema",
                ".codex/schemas/harness/agent-run.schema.json",
                "--phase",
                "pre-finalize",
            )

    def test_agent_run_artifact_missing_request_or_context_fails(self) -> None:
        for remove_index in [0, 1]:
            with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
                run_dir = Path(tmp) / "current-run"
                shutil.copytree(FIXTURES / "agent-runs" / "current-run", run_dir)
                hook_file = run_dir / "hook-events.jsonl"
                lines = hook_file.read_text(encoding="utf-8").splitlines()
                hook_file.write_text(
                    "\n".join(line for idx, line in enumerate(lines) if idx != remove_index) + "\n",
                    encoding="utf-8",
                )
                self.assert_fails(
                    ".codex/tools/validate_agent_run_artifact.py",
                    str(run_dir),
                    "--schema",
                    ".codex/schemas/harness/agent-run.schema.json",
                )

    def test_agent_run_artifact_invalid_fixture_fails(self) -> None:
        self.assert_fails(
            ".codex/tools/validate_agent_run_artifact.py",
            str(FIXTURES / "agent-runs" / "invalid-claim-mismatch"),
            "--schema",
            ".codex/schemas/harness/agent-run.schema.json",
        )

    def test_agent_run_artifact_repeated_tool_pairs_pass(self) -> None:
        self.assert_passes(
            ".codex/tools/validate_agent_run_artifact.py",
            str(FIXTURES / "agent-runs" / "repeated-tools"),
            "--schema",
            ".codex/schemas/harness/agent-run.schema.json",
        )

    def test_agent_run_artifact_permission_without_tool_id_passes(self) -> None:
        self.assert_passes(
            ".codex/tools/validate_agent_run_artifact.py",
            str(FIXTURES / "agent-runs" / "permission-no-tool-id"),
            "--schema",
            ".codex/schemas/harness/agent-run.schema.json",
        )

    def test_agent_run_artifact_failed_stop_attempt_is_recoverable(self) -> None:
        self.assert_passes(
            ".codex/tools/validate_agent_run_artifact.py",
            str(FIXTURES / "agent-runs" / "stop-recovery"),
            "--schema",
            ".codex/schemas/harness/agent-run.schema.json",
        )

    def test_agent_run_artifact_unfinished_tool_fails(self) -> None:
        self.assert_fails(
            ".codex/tools/validate_agent_run_artifact.py",
            str(FIXTURES / "agent-runs" / "unfinished-tool"),
            "--schema",
            ".codex/schemas/harness/agent-run.schema.json",
        )

    def test_hooks_json_command_launches_from_non_repo_cwd(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            ledger = Path(tmp) / "hook-events.jsonl"
            command = self.hooks_json_command()
            fixture = (FIXTURES / "hooks" / "userpromptsubmit.json").read_text(encoding="utf-8")
            result = subprocess.run(
                command,
                cwd="/",
                env={
                    **os.environ,
                    "HOME": str(Path(tmp) / "empty-home"),
                    "PWD": "/",
                    "PYTHONDONTWRITEBYTECODE": "1",
                    "SKILL_SYSTEM_HOOK_LEDGER": str(ledger),
                    "SKILL_SYSTEM_ROOT": str(ROOT),
                },
                input=fixture,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True,
                check=False,
                timeout=30,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(ledger.exists(), result.stdout + result.stderr)
            self.assertNotIn("/.codex/hooks/codex_hook_adapter.py", result.stdout + result.stderr)
            event = json.loads(ledger.read_text(encoding="utf-8").splitlines()[0])
            self.assertEqual(event["neutral_event"], "request_received")

    def test_hooks_json_command_launches_from_home_codex_without_repo_env(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            home = Path(tmp) / "home"
            codex_home = home / ".codex"
            for rel in [
                Path("hooks/codex_hook_adapter.py"),
                Path("tools/hook_runtime.py"),
                Path("tools/_validation.py"),
            ]:
                target = codex_home / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / ".codex" / rel, target)

            ledger = Path(tmp) / "hook-events.jsonl"
            payload = json.dumps(
                {
                    "hook_event_name": "UserPromptSubmit",
                    "session_id": "session-home",
                    "turn_id": "turn-home",
                    "cwd": "/",
                    "permission_mode": "workspace-write",
                    "prompt": "home hook",
                }
            )
            result = subprocess.run(
                self.hooks_json_command(),
                cwd="/",
                env={
                    "HOME": str(home),
                    "PATH": os.environ.get("PATH", ""),
                    "PWD": "/",
                    "PYTHONDONTWRITEBYTECODE": "1",
                    "SKILL_SYSTEM_HOOK_LEDGER": str(ledger),
                },
                input=payload,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True,
                check=False,
                timeout=30,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(ledger.exists(), result.stdout + result.stderr)
            self.assertNotIn("fatal: not a git repository", result.stdout + result.stderr)
            self.assertNotIn("/.codex/hooks/codex_hook_adapter.py", result.stdout + result.stderr)
            event = json.loads(ledger.read_text(encoding="utf-8").splitlines()[0])
            self.assertEqual(event["neutral_event"], "request_received")

    def test_codex_hook_adapter_records_pretooluse(self) -> None:
        ledger = self.temp_ledger("live-hook-pretooluse")
        if ledger.exists():
            ledger.unlink()
        self.assert_passes(
            ".codex/hooks/codex_hook_adapter.py",
            "--input-file",
            str(FIXTURES / "hooks" / "pretooluse.json"),
            "--ledger",
            str(ledger),
        )
        self.assertTrue(ledger.exists())
        event = json.loads(ledger.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(event["neutral_event"], "tool_preflight")
        self.assertEqual(event["host_event"], "PreToolUse")
        self.assertEqual(event["status"], "pass")
        ledger.unlink()

    def test_codex_hook_adapter_records_request_and_compaction_events(self) -> None:
        ledger = self.temp_ledger("live-hook-context-events")
        if ledger.exists():
            ledger.unlink()
        for fixture_name in ["userpromptsubmit.json", "precompact.json", "postcompact.json"]:
            self.assert_passes(
                ".codex/hooks/codex_hook_adapter.py",
                "--input-file",
                str(FIXTURES / "hooks" / fixture_name),
                "--ledger",
                str(ledger),
            )
        events = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines()]
        self.assertEqual([event["neutral_event"] for event in events], ["request_received", "compact_before", "compact_after"])
        self.assertEqual([event["seq"] for event in events], [1, 2, 3])
        self.assertEqual(events[1]["prev_event_hash"], events[0]["event_hash"])
        self.assertEqual(events[2]["prev_event_hash"], events[1]["event_hash"])
        ledger.unlink()

    def test_codex_hook_adapter_marks_failed_posttooluse(self) -> None:
        ledger = self.temp_ledger("live-hook-posttooluse-fail")
        if ledger.exists():
            ledger.unlink()
        self.assert_passes(
            ".codex/hooks/codex_hook_adapter.py",
            "--input-file",
            str(FIXTURES / "hooks" / "posttooluse-fail.json"),
            "--ledger",
            str(ledger),
        )
        event = json.loads(ledger.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(event["neutral_event"], "tool_result")
        self.assertEqual(event["status"], "fail")
        self.assertEqual(event["evidence"]["tool_result"]["exit_code"], 1)
        ledger.unlink()

    def test_codex_hook_adapter_marks_string_failed_posttooluse(self) -> None:
        ledger = self.temp_ledger("live-hook-posttooluse-string-fail")
        if ledger.exists():
            ledger.unlink()
        self.assert_passes(
            ".codex/hooks/codex_hook_adapter.py",
            "--input-file",
            str(FIXTURES / "hooks" / "posttooluse-string-fail.json"),
            "--ledger",
            str(ledger),
        )
        event = json.loads(ledger.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(event["status"], "fail")
        self.assertEqual(event["evidence"]["tool_result"]["exit_code"], 1)
        ledger.unlink()

    def test_codex_hook_adapter_marks_unknown_posttooluse_warn(self) -> None:
        ledger = self.temp_ledger("live-hook-posttooluse-string-unknown")
        if ledger.exists():
            ledger.unlink()
        self.assert_passes(
            ".codex/hooks/codex_hook_adapter.py",
            "--input-file",
            str(FIXTURES / "hooks" / "posttooluse-string-unknown.json"),
            "--ledger",
            str(ledger),
        )
        event = json.loads(ledger.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(event["status"], "warn")
        self.assertNotIn("exit_code", event["evidence"]["tool_result"])
        ledger.unlink()

    def test_codex_hook_adapter_redacts_sensitive_tool_input(self) -> None:
        ledger = self.temp_ledger("live-hook-secret")
        if ledger.exists():
            ledger.unlink()
        self.assert_passes(
            ".codex/hooks/codex_hook_adapter.py",
            "--input-file",
            str(FIXTURES / "hooks" / "pretooluse-redaction.json"),
            "--ledger",
            str(ledger),
        )
        raw = ledger.read_text(encoding="utf-8")
        self.assertNotIn("sk-secretsecretsecretsecret", raw)
        self.assertNotIn("Authorization", raw)
        event = json.loads(raw.splitlines()[0])
        self.assertEqual(event["evidence"]["command_category"], "curl")
        self.assertIn("command_hash", event["evidence"])
        ledger.unlink()

    def test_codex_hook_adapter_redacts_sensitive_tool_response_fields(self) -> None:
        ledger = self.temp_ledger("live-hook-response-redaction")
        if ledger.exists():
            ledger.unlink()
        self.assert_passes(
            ".codex/hooks/codex_hook_adapter.py",
            "--input-file",
            str(FIXTURES / "hooks" / "posttooluse-redaction.json"),
            "--ledger",
            str(ledger),
        )
        raw = ledger.read_text(encoding="utf-8")
        self.assertNotIn("/Users/alice/private/token-secret.txt", raw)
        self.assertNotIn("api_key=sk-secretsecretsecretsecret", raw)
        event = json.loads(raw.splitlines()[0])
        result = event["evidence"]["tool_result"]
        self.assertIn("<external-path>", result["changed_files"])
        self.assertIn("https://example.com/?<redacted-query>", result["network_targets"])
        ledger.unlink()

    def test_codex_hook_adapter_stop_runs_agent_output_validation(self) -> None:
        ledger = self.temp_ledger("live-hook-stop")
        if ledger.exists():
            ledger.unlink()
        result = self.run_tool(
            ".codex/hooks/codex_hook_adapter.py",
            "--input-file",
            str(FIXTURES / "hooks" / "stop.json"),
            "--run-dir",
            str(FIXTURES / "agent-runs" / "current-run"),
            "--ledger",
            str(ledger),
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        output = json.loads(result.stdout)
        self.assertTrue(output["continue"])
        events = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines()]
        self.assertEqual([event["neutral_event"] for event in events], ["turn_finalize_attempt", "turn_finalize"])
        self.assertEqual([event["status"] for event in events], ["pass", "pass"])
        self.assertEqual(events[1]["prev_event_hash"], events[0]["event_hash"])
        ledger.unlink()

    def test_codex_hook_adapter_stop_finalizes_same_run_ledger_without_cycle(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            run_dir = Path(tmp) / "current-run"
            shutil.copytree(FIXTURES / "agent-runs" / "current-run", run_dir)
            hook_file = run_dir / "hook-events.jsonl"
            lines = hook_file.read_text(encoding="utf-8").splitlines()
            hook_file.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")
            result = self.run_tool(
                ".codex/hooks/codex_hook_adapter.py",
                "--input-file",
                str(FIXTURES / "hooks" / "stop.json"),
                "--run-dir",
                str(run_dir),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            output = json.loads(result.stdout)
            self.assertTrue(output["continue"])
            events = [json.loads(line) for line in hook_file.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(events[-2]["neutral_event"], "turn_finalize_attempt")
            self.assertEqual(events[-1]["neutral_event"], "turn_finalize")
            self.assertEqual(events[-1]["prev_event_hash"], events[-2]["event_hash"])
            self.assert_passes(
                ".codex/tools/validate_agent_run_artifact.py",
                str(run_dir),
                "--schema",
                ".codex/schemas/harness/agent-run.schema.json",
            )

    def test_codex_hook_adapter_stop_message_mismatch_blocks_recoverably(self) -> None:
        ledger = self.temp_ledger("live-hook-stop-message-mismatch")
        if ledger.exists():
            ledger.unlink()
        result = self.run_tool(
            ".codex/hooks/codex_hook_adapter.py",
            "--input-file",
            str(FIXTURES / "hooks" / "stop-message-mismatch.json"),
            "--run-dir",
            str(FIXTURES / "agent-runs" / "current-run"),
            "--ledger",
            str(ledger),
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["decision"], "block")
        self.assertNotIn("continue", output)
        event = json.loads(ledger.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(event["neutral_event"], "turn_finalize_attempt")
        self.assertEqual(event["status"], "fail")
        ledger.unlink()

    def test_codex_hook_adapter_stop_missing_current_run_is_unverified(self) -> None:
        ledger = self.temp_ledger("live-hook-stop-missing")
        if ledger.exists():
            ledger.unlink()
        result = self.run_tool(
            ".codex/hooks/codex_hook_adapter.py",
            "--input-file",
            str(FIXTURES / "hooks" / "stop-missing-run.json"),
            "--ledger",
            str(ledger),
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        output = json.loads(result.stdout)
        self.assertTrue(output["continue"])
        self.assertIn("UNVERIFIED", output["systemMessage"])
        event = json.loads(ledger.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(event["neutral_event"], "turn_finalize_attempt")
        self.assertEqual(event["status"], "warn")
        self.assertIn("UNVERIFIED", event["evidence"]["agent_output_validation"])
        ledger.unlink()


if __name__ == "__main__":
    unittest.main()
