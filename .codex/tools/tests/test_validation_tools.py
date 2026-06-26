from __future__ import annotations

import subprocess
import sys
import unittest
import importlib.util
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
        env["SKILL_SYSTEM_DESKTOP_NOTIFY"] = "dry-run"
        env.setdefault("CODEX_MODEL", "gpt-5.5")
        env.setdefault("CODEX_MODEL_REASONING_EFFORT", "xhigh")
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

    def write_loop_contract(self, path: Path, max_iterations: int = 3, same_failure_limit: int = 2) -> None:
        path.write_text(
            f"""schema_version: 1
contract_id: LC-20260623-001
activation: explicit
goal:
  statement: "Implement the bounded loop test task."
  success_conditions:
    - id: SC-001
      statement: "Primary verifier passes."
      required: true
      verifier:
        type: command_exit
        command: "pytest tests/test_loop.py -q"
        expected_exit_code: 0
control:
  max_iterations: {max_iterations}
  max_wall_time_seconds: 3600
  no_progress_limit: 2
  same_failure_limit: {same_failure_limit}
  max_stop_continuations: 3
termination:
  precedence:
    - unsafe
    - fatal
    - success
    - approval_required
    - stalled
    - budget_exhausted
    - continue
""",
            encoding="utf-8",
        )

    def assert_passes(self, *args: str) -> None:
        result = self.run_tool(*args)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def assert_fails(self, *args: str) -> None:
        result = self.run_tool(*args)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)


    def test_eval_invalid_fixture_fails(self) -> None:
        self.assert_fails(
            ".codex/tools/validate_eval_cases.py",
            str(FIXTURES / "eval-invalid.yaml"),
            "--schema",
            ".codex/eval/eval-case.schema.json",
        )








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
















    def test_notify_desktop_dry_run_passes(self) -> None:
        result = self.run_tool(
            ".codex/tools/notify_desktop.py",
            "--event",
            "approval-requested",
            "--title",
            "Codex approval requested",
            "--message",
            "Bash is waiting for approval.",
            "--dry-run",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["event"], "approval-requested")
        self.assertEqual(report["status"], "dry_run")
        self.assertEqual(report["title"], "Codex approval requested")
        self.assertIn("Bash is waiting for approval", report["message"])





    def test_claude_notify_adapter_notifies_turn_complete_on_stop(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            inp = Path(tmp) / "stop.json"
            inp.write_text(
                json.dumps({
                    "hook_event_name": "Stop",
                    "session_id": "test-session",
                    "cwd": str(ROOT),
                    "task_subject": "Add Claude completion notification",
                    "last_assistant_message": "Claude completion notification was added.",
                }),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, ".claude/tools/claude_notify_adapter.py", "--input-file", str(inp), "--print-report"],
                cwd=ROOT,
                env={
                    **os.environ,
                    "CLAUDE_NOTIFY_STATE_DIR": str(Path(tmp) / "state"),
                    "CLAUDE_DESKTOP_NOTIFY": "dry-run",
                    "PYTHONDONTWRITEBYTECODE": "1",
                },
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=30,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["event"], "turn-complete")
            self.assertEqual(report["status"], "dry_run")
            self.assertEqual(report["topic"], "done")
            self.assertEqual(report["app"], "claude")
            self.assertIn("Claude completion notification was added", report["message"])
            self.assertIn("Add Claude completion notification", report["message"])






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




    def test_agent_run_artifact_fixture_passes(self) -> None:
        self.assert_passes(
            ".codex/tools/validate_agent_run_artifact.py",
            str(FIXTURES / "agent-runs" / "current-run"),
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









    def test_loop_run_one_retry_success(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            tmp_path = Path(tmp)
            contract = tmp_path / "contract.yaml"
            output_root = tmp_path / "loop-runs"
            self.write_loop_contract(contract)
            init = self.run_tool(
                ".codex/tools/init_loop_run.py",
                str(contract),
                "--workspace-root",
                str(ROOT),
                "--output-root",
                str(output_root),
            )
            self.assertEqual(init.returncode, 0, init.stdout + init.stderr)
            loop_dir = Path(json.loads(init.stdout)["loop_run_dir"])

            failed = tmp_path / "iteration-1.yaml"
            failed.write_text(
                """schema_version: 1
loop_run_id: LR-20260623-001
iteration: 1
agent_run_id: AR-20260623-001
condition_results:
  - condition_id: SC-001
    status: fail
    evidence_refs:
      - artifacts/sc-001-iteration-1.txt
    failure_fingerprint: sha256:first
""",
                encoding="utf-8",
            )
            first = self.run_tool(
                ".codex/tools/evaluate_loop_run.py",
                str(loop_dir),
                "--iteration-result",
                str(failed),
                "--format",
                "json",
            )
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            self.assertEqual(json.loads(first.stdout)["decision"]["action"], "continue")

            passed = tmp_path / "iteration-2.yaml"
            passed.write_text(
                """schema_version: 1
loop_run_id: LR-20260623-001
iteration: 2
agent_run_id: AR-20260623-002
condition_results:
  - condition_id: SC-001
    status: pass
    evidence_refs:
      - artifacts/sc-001-iteration-2.txt
""",
                encoding="utf-8",
            )
            second = self.run_tool(
                ".codex/tools/evaluate_loop_run.py",
                str(loop_dir),
                "--iteration-result",
                str(passed),
                "--format",
                "json",
            )
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            self.assertEqual(json.loads(second.stdout)["decision"]["action"], "success")
            self.assert_passes(".codex/tools/validate_loop_run.py", str(loop_dir))

    def test_loop_run_repeated_failure_switches_to_recovery(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            tmp_path = Path(tmp)
            contract = tmp_path / "contract.yaml"
            output_root = tmp_path / "loop-runs"
            self.write_loop_contract(contract, same_failure_limit=1)
            init = self.run_tool(
                ".codex/tools/init_loop_run.py",
                str(contract),
                "--workspace-root",
                str(ROOT),
                "--output-root",
                str(output_root),
            )
            self.assertEqual(init.returncode, 0, init.stdout + init.stderr)
            loop_dir = Path(json.loads(init.stdout)["loop_run_dir"])
            for iteration in [1, 2]:
                result_file = tmp_path / f"iteration-{iteration}.yaml"
                result_file.write_text(
                    f"""schema_version: 1
loop_run_id: LR-20260623-001
iteration: {iteration}
agent_run_id: AR-20260623-00{iteration}
condition_results:
  - condition_id: SC-001
    status: fail
    evidence_refs:
      - artifacts/sc-001-iteration-{iteration}.txt
    failure_fingerprint: sha256:stable
""",
                    encoding="utf-8",
                )
                evaluation = self.run_tool(
                    ".codex/tools/evaluate_loop_run.py",
                    str(loop_dir),
                    "--iteration-result",
                    str(result_file),
                    "--format",
                    "json",
                )
                self.assertEqual(evaluation.returncode, 0, evaluation.stdout + evaluation.stderr)
            self.assertEqual(json.loads(evaluation.stdout)["decision"]["action"], "recover")

    def test_evidence_ledger_converged_passes(self) -> None:
        self.assert_passes(
            ".codex/tools/check_evidence_ledger.py",
            str(FIXTURES / "evidence-ledgers" / "converged.yaml"),
            "--min-claims", "2",
        )


    def test_loop_run_pass_without_evidence_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            tmp_path = Path(tmp)
            contract = tmp_path / "contract.yaml"
            output_root = tmp_path / "loop-runs"
            self.write_loop_contract(contract)
            init = self.run_tool(
                ".codex/tools/init_loop_run.py", str(contract),
                "--workspace-root", str(ROOT), "--output-root", str(output_root),
            )
            self.assertEqual(init.returncode, 0, init.stdout + init.stderr)
            loop_dir = Path(json.loads(init.stdout)["loop_run_dir"])
            hacked = tmp_path / "iteration-1.yaml"
            hacked.write_text(
                """schema_version: 1
loop_run_id: LR-20260623-001
iteration: 1
agent_run_id: AR-20260623-001
condition_results:
  - condition_id: SC-001
    status: pass
    evidence_refs: []
""",
                encoding="utf-8",
            )
            evaluation = self.run_tool(
                ".codex/tools/evaluate_loop_run.py", str(loop_dir),
                "--iteration-result", str(hacked), "--format", "json",
            )
            self.assertEqual(evaluation.returncode, 0, evaluation.stdout + evaluation.stderr)
            decision = json.loads(evaluation.stdout)["decision"]
            self.assertEqual(decision["action"], "blocked")
            self.assertEqual(decision["reason_code"], "pass_without_evidence")







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

    def test_hooks_json_command_ignores_untrusted_cwd_adapter(self) -> None:
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

            untrusted = Path(tmp) / "untrusted"
            untrusted.mkdir()
            marker = Path(tmp) / "marker"
            (untrusted / "codex_hook_adapter.py").write_text(
                "from pathlib import Path\nPath(%r).write_text('hijacked')\nprint('UNTRUSTED')\n" % str(marker),
                encoding="utf-8",
            )
            ledger = Path(tmp) / "hook-events.jsonl"
            payload = json.dumps(
                {
                    "hook_event_name": "UserPromptSubmit",
                    "session_id": "session-home",
                    "turn_id": "turn-home",
                    "cwd": str(untrusted),
                    "permission_mode": "workspace-write",
                    "prompt": "home hook",
                }
            )
            result = subprocess.run(
                self.hooks_json_command(),
                cwd=untrusted,
                env={
                    "HOME": str(home),
                    "PATH": os.environ.get("PATH", ""),
                    "PWD": str(untrusted),
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
            self.assertFalse(marker.exists(), result.stdout + result.stderr)
            self.assertNotIn("UNTRUSTED", result.stdout + result.stderr)
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



    def test_codex_hook_adapter_notifies_turn_complete_on_plain_stop(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            ledger = Path(tmp) / "ledger.jsonl"
            result = self.run_tool(
                ".codex/hooks/codex_hook_adapter.py",
                "--input-file", str(FIXTURES / "hooks" / "stop.json"),
                "--run-dir", str(FIXTURES / "agent-runs" / "current-run"),
                "--ledger", str(ledger),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            events = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines() if line.strip()]
            finalize = [
                e for e in events
                if e.get("neutral_event") == "turn_finalize" and "desktop_notifications" in e.get("evidence", {})
            ]
            self.assertTrue(finalize, "plain successful Stop did not carry a desktop notification")
            note = finalize[-1]["evidence"]["desktop_notifications"]["turn_complete"]
            self.assertEqual(note["event"], "turn-complete")
            self.assertEqual(note["status"], "dry_run")
            self.assertEqual(note["display_title"], "[done]-[gpt5.5-xhigh]-[Skill-System]")
            self.assertIn("Agent Run Final Report", note["message"])






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

    def test_codex_hook_adapter_bootstraps_live_agent_run_manifest(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            tmp_path = Path(tmp)
            run_dir = tmp_path / "live-run"
            env = {
                **os.environ,
                "PYTHONDONTWRITEBYTECODE": "1",
                "SKILL_SYSTEM_AGENT_RUN_BOOTSTRAP": "1",
                "SKILL_SYSTEM_DESKTOP_NOTIFY": "dry-run",
                "CODEX_MODEL": "gpt-5.5",
                "CODEX_MODEL_REASONING_EFFORT": "xhigh",
            }
            for name, payload in [
                (
                    "user.json",
                    {
                        "hook_event_name": "UserPromptSubmit",
                        "session_id": "session-live-bootstrap",
                        "turn_id": "turn-live-bootstrap",
                        "cwd": str(ROOT),
                        "permission_mode": "workspace-write",
                        "prompt": "bootstrap a live manifest",
                    },
                ),
                (
                    "session.json",
                    {
                        "hook_event_name": "SessionStart",
                        "session_id": "session-live-bootstrap",
                        "turn_id": "turn-live-bootstrap",
                        "cwd": str(ROOT),
                        "permission_mode": "workspace-write",
                    },
                ),
            ]:
                inp = tmp_path / name
                inp.write_text(json.dumps(payload), encoding="utf-8")
                result = subprocess.run(
                    [sys.executable, ".codex/hooks/codex_hook_adapter.py", "--input-file", str(inp), "--run-dir", str(run_dir)],
                    cwd=ROOT,
                    env=env,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                    timeout=30,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            self.assertTrue((run_dir / "run.yaml").exists())
            stop = tmp_path / "stop.json"
            stop.write_text(
                json.dumps(
                    {
                        "hook_event_name": "Stop",
                        "session_id": "session-live-bootstrap",
                        "turn_id": "turn-live-bootstrap",
                        "cwd": str(ROOT),
                        "permission_mode": "workspace-write",
                        "last_assistant_message": (
                            "# Agent Run Final Report\n\n"
                            "result_label: unverified\n\n"
                            "## Claims\n\n"
                            "- C-001: live agent-run manifest bootstrap initialized current run evidence capture.\n"
                        ),
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, ".codex/hooks/codex_hook_adapter.py", "--input-file", str(stop), "--run-dir", str(run_dir)],
                cwd=ROOT,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=30,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            output = json.loads(result.stdout)
            self.assertTrue(output["continue"])
            self.assertIn("passed", output["systemMessage"])
            events = [json.loads(line) for line in (run_dir / "hook-events.jsonl").read_text(encoding="utf-8").splitlines()]
            self.assertEqual(events[0]["neutral_event"], "request_received")
            self.assertEqual(events[1]["neutral_event"], "context_loaded")
            self.assertEqual(events[-1]["neutral_event"], "turn_finalize")
            self.assert_passes(
                ".codex/tools/validate_agent_run_artifact.py",
                str(run_dir),
                "--schema",
                ".codex/schemas/harness/agent-run.schema.json",
            )


if __name__ == "__main__":
    unittest.main()
