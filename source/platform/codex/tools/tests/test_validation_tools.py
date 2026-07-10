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

import yaml


ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / ".codex" / "tools" / "tests" / "fixtures"
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / ".codex" / "tools"))

from _validation import resolve_bundle_path  # noqa: E402
from recovery_guard import state_path_for_session  # noqa: E402


def bundle_path(rel: str) -> Path:
    path = resolve_bundle_path(ROOT, rel)
    if path is None:
        raise AssertionError(f"bundle path not found: {rel}")
    return path


class ValidationToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self._guard_state_tmp = tempfile.TemporaryDirectory(dir="/private/tmp")
        self._previous_guard_state_dir = os.environ.get("SKILL_SYSTEM_RECOVERY_GUARD_STATE_DIR")
        os.environ["SKILL_SYSTEM_RECOVERY_GUARD_STATE_DIR"] = self._guard_state_tmp.name

    def tearDown(self) -> None:
        if self._previous_guard_state_dir is None:
            os.environ.pop("SKILL_SYSTEM_RECOVERY_GUARD_STATE_DIR", None)
        else:
            os.environ["SKILL_SYSTEM_RECOVERY_GUARD_STATE_DIR"] = self._previous_guard_state_dir
        self._guard_state_tmp.cleanup()

    def run_tool_env(self, extra_env: dict[str, str | None], *args: str) -> subprocess.CompletedProcess[str]:
        env = dict(os.environ)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["SKILL_SYSTEM_DESKTOP_NOTIFY"] = "dry-run"
        env["SKILL_SYSTEM_RECOVERY_GUARD"] = "off"
        env.setdefault("CODEX_MODEL", "gpt-5.5")
        env.setdefault("CODEX_MODEL_REASONING_EFFORT", "xhigh")
        for name, value in extra_env.items():
            if value is None:
                env.pop(name, None)
            else:
                env[name] = value
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

    def run_tool(self, *args: str) -> subprocess.CompletedProcess[str]:
        return self.run_tool_env({}, *args)

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

    def test_hooks_json_event_and_launcher_invariants(self) -> None:
        hooks = json.loads((ROOT / ".codex" / "hooks.json").read_text(encoding="utf-8"))["hooks"]
        expected = {
            "UserPromptSubmit", "SessionStart", "PreToolUse", "PermissionRequest",
            "PostToolUse", "Stop", "PreCompact", "PostCompact",
        }
        self.assertEqual(set(hooks), expected)
        commands = {spec[0]["hooks"][0]["command"] for spec in hooks.values()}
        self.assertEqual(len(commands), 1, "all hook events must use one trusted adapter launcher")
        for event_name, spec in hooks.items():
            timeout = spec[0]["hooks"][0]["timeout"]
            self.assertEqual(timeout, 45 if event_name == "Stop" else 30)

    def write_loop_contract(self, path: Path, max_iterations: int = 3, same_failure_limit: int = 2) -> None:
        path.write_text(
            f"""schema_version: 2
contract_id: LC-20260623-001
activation: explicit
goal:
  statement: "Implement the bounded loop test task."
  success_conditions:
    - id: SC-001
      statement: "Primary verifier passes."
      required: true
      verifier:
        type: artifact_exists
        owner: "agent:codex"
        path: "artifacts/sc-001.ok"
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

    def test_work_item_example_validates(self) -> None:
        self.assert_passes(
            ".codex/tools/validate_work_item.py",
            ".codex/schemas/workitem/examples/work-item.example.yaml",
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
                    str(bundle_path(".codex/skills/analysis-codebase/scripts/collect.sh")),
                    "--repo-path",
                    str(repo),
                    "--mode",
                    "static",
                    "--output-dir",
                    str(output),
                    "--policy",
                    str(bundle_path(".codex/skills/analysis-codebase/references/policy-default.json")),
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
                str(bundle_path(".codex/skills/analysis-codebase/scripts/report.py")),
                "--input-dir",
                str(output),
                "--output",
                str(report),
                "--policy",
                str(bundle_path(".codex/skills/analysis-codebase/references/policy-default.json")),
            )
            self.assertEqual(
                result.returncode,
                2,
                "static-only architecture views must render but fail the default fallback gate\n"
                + result.stdout
                + result.stderr,
            )
            report_text = report.read_text(encoding="utf-8")
            self.assertIn("c_cpp_lizard_status", report_text)
            self.assertIn("architecture.c_cpp_semantic_depth", report_text)
            self.assertIn("Not evidenced: C/C++ symbol, class, and call-graph structure", report_text)
            gate = json.loads(
                (output / "artifacts" / "quality-gate-result.json").read_text(encoding="utf-8")
            )
            self.assertEqual(gate.get("status"), "FAIL")
            self.assertIn("c_cpp_structural_evidence=not_evidenced", gate.get("reasons", []))
            self.assertTrue(
                any(str(reason).startswith("fallback_diagrams=") for reason in gate.get("reasons", [])),
                gate,
            )

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

    def test_hook_runtime_verify_detects_hash_tamper(self) -> None:
        ledger = self.temp_ledger("hook-verify")
        self.assert_passes(
            ".codex/tools/hook_runtime.py", "record",
            "--event", "request_received",
            "--host", "codex",
            "--host-event", "UserPromptSubmit",
            "--support-level", "native",
            "--ledger", str(ledger),
            "--run-id", "AR-TEST-VERIFY",
        )
        self.assert_passes(".codex/tools/hook_runtime.py", "verify", "--ledger", str(ledger))
        ledger.write_text(ledger.read_text(encoding="utf-8").replace('"status": "pass"', '"status": "fail"'), encoding="utf-8")
        result = self.run_tool(".codex/tools/hook_runtime.py", "verify", "--ledger", str(ledger))
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("event_hash mismatch", result.stdout)

    def test_codex_hook_fallback_is_durable_per_run_and_hides_run_ids(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            tmp_path = Path(tmp)
            codex_home = tmp_path / "codex-home"
            session_a = f"session-fallback-a-{os.getpid()}"
            turn_a = f"turn-fallback-a-{os.getpid()}"
            session_b = f"session-fallback-b-{os.getpid()}"
            turn_b = f"turn-fallback-b-{os.getpid()}"
            payloads = [
                {
                    "hook_event_name": "UserPromptSubmit",
                    "session_id": session_a,
                    "turn_id": turn_a,
                    "cwd": str(ROOT),
                    "permission_mode": "workspace-write",
                    "prompt": "first run request",
                },
                {
                    "hook_event_name": "PreCompact",
                    "session_id": session_a,
                    "turn_id": turn_a,
                    "cwd": str(ROOT),
                    "permission_mode": "workspace-write",
                },
                {
                    "hook_event_name": "UserPromptSubmit",
                    "session_id": session_b,
                    "turn_id": turn_b,
                    "cwd": str(ROOT),
                    "permission_mode": "workspace-write",
                    "prompt": "second run request",
                },
            ]
            for index, payload in enumerate(payloads):
                input_path = tmp_path / f"hook-{index}.json"
                input_path.write_text(json.dumps(payload), encoding="utf-8")
                result = self.run_tool_env(
                    {
                        "CODEX_HOME": str(codex_home),
                        "SKILL_SYSTEM_HOOK_LEDGER": None,
                        "SKILL_SYSTEM_RUN_ID": None,
                        "SKILL_SYSTEM_AGENT_RUN_BOOTSTRAP": None,
                        "SKILL_SYSTEM_AGENT_OUTPUT_GATE": None,
                    },
                    ".codex/hooks/codex_hook_adapter.py",
                    "--input-file", str(input_path),
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            root = codex_home / "harness" / "hook-ledgers"
            ledgers = sorted(root.glob("*/hook-events.jsonl"))
            self.assertEqual(len(ledgers), 2)
            events_by_run: dict[str, list[dict[str, object]]] = {}
            for ledger in ledgers:
                events = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines()]
                run_ids = {event["run_id"] for event in events}
                self.assertEqual(len(run_ids), 1)
                events_by_run[next(iter(run_ids))] = events
                self.assert_passes(".codex/tools/hook_runtime.py", "verify", "--ledger", str(ledger))
                relative = ledger.relative_to(root).as_posix()
                for raw_id in (session_a, turn_a, session_b, turn_b):
                    self.assertNotIn(raw_id, relative)

            run_a = f"{session_a}:{turn_a}"
            run_b = f"{session_b}:{turn_b}"
            self.assertEqual(set(events_by_run), {run_a, run_b})
            self.assertEqual([event["seq"] for event in events_by_run[run_a]], [1, 2])
            self.assertEqual(events_by_run[run_a][1]["prev_event_hash"], events_by_run[run_a][0]["event_hash"])
            self.assertEqual([event["seq"] for event in events_by_run[run_b]], [1])

    def test_codex_hook_fallback_does_not_merge_sanitize_collisions(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            tmp_path = Path(tmp)
            codex_home = tmp_path / "codex-home"
            raw_runs = [("session/a", "turn?one"), ("session?a", "turn/one")]
            for index, (session_id, turn_id) in enumerate(raw_runs):
                input_path = tmp_path / f"collision-{index}.json"
                input_path.write_text(
                    json.dumps(
                        {
                            "hook_event_name": "UserPromptSubmit",
                            "session_id": session_id,
                            "turn_id": turn_id,
                            "cwd": str(ROOT),
                            "permission_mode": "workspace-write",
                            "prompt": f"collision run {index}",
                        }
                    ),
                    encoding="utf-8",
                )
                result = self.run_tool_env(
                    {
                        "CODEX_HOME": str(codex_home),
                        "SKILL_SYSTEM_HOOK_LEDGER": None,
                        "SKILL_SYSTEM_RUN_ID": None,
                        "SKILL_SYSTEM_AGENT_RUN_BOOTSTRAP": None,
                        "SKILL_SYSTEM_AGENT_OUTPUT_GATE": None,
                    },
                    ".codex/hooks/codex_hook_adapter.py",
                    "--input-file",
                    str(input_path),
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            root = codex_home / "harness" / "hook-ledgers"
            ledgers = sorted(root.glob("*/hook-events.jsonl"))
            self.assertEqual(len(ledgers), 2)
            observed_run_ids = {
                json.loads(path.read_text(encoding="utf-8").splitlines()[0])["run_id"]
                for path in ledgers
            }
            self.assertEqual(
                observed_run_ids,
                {f"{session_id}:{turn_id}" for session_id, turn_id in raw_runs},
            )
            for ledger in ledgers:
                relative = ledger.relative_to(root).as_posix()
                for session_id, turn_id in raw_runs:
                    self.assertNotIn(session_id, relative)
                    self.assertNotIn(turn_id, relative)

    def test_hook_runtime_default_record_uses_the_explicit_run_id_path(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            codex_home = Path(tmp) / "codex-home"
            for run_id in ("CLI-RUN-A", "CLI-RUN-B"):
                result = self.run_tool_env(
                    {
                        "CODEX_HOME": str(codex_home),
                        "SKILL_SYSTEM_HOOK_LEDGER": None,
                        "SKILL_SYSTEM_RUN_ID": None,
                    },
                    ".codex/tools/hook_runtime.py",
                    "record",
                    "--event", "request_received",
                    "--host", "codex",
                    "--host-event", "UserPromptSubmit",
                    "--support-level", "native",
                    "--run-id", run_id,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            ledgers = sorted((codex_home / "harness" / "hook-ledgers").glob("*/hook-events.jsonl"))
            self.assertEqual(len(ledgers), 2)
            self.assertEqual(
                {json.loads(path.read_text(encoding="utf-8"))["run_id"] for path in ledgers},
                {"CLI-RUN-A", "CLI-RUN-B"},
            )

    def test_hook_fallback_preserves_exact_file_override_and_manifest_priority(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            tmp_path = Path(tmp)
            codex_home = tmp_path / "codex-home"
            configured = tmp_path / "configured.jsonl"
            input_path = tmp_path / "request.json"
            input_path.write_text(
                json.dumps({
                    "hook_event_name": "UserPromptSubmit",
                    "session_id": "session-configured",
                    "turn_id": "turn-configured",
                    "cwd": str(ROOT),
                    "permission_mode": "workspace-write",
                    "prompt": "configured ledger",
                }),
                encoding="utf-8",
            )
            result = self.run_tool_env(
                {
                    "CODEX_HOME": str(codex_home),
                    "SKILL_SYSTEM_HOOK_LEDGER": str(configured),
                    "SKILL_SYSTEM_AGENT_RUN_BOOTSTRAP": None,
                },
                ".codex/hooks/codex_hook_adapter.py",
                "--input-file", str(input_path),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(configured.is_file())
            self.assertFalse((codex_home / "harness" / "hook-ledgers").exists())

            run_dir = tmp_path / "manifest-run"
            shutil.copytree(FIXTURES / "agent-runs" / "current-run", run_dir)
            run_ledger = run_dir / "hook-events.jsonl"
            run_ledger.unlink()
            configured.unlink()
            result = self.run_tool_env(
                {
                    "SKILL_SYSTEM_HOOK_LEDGER": str(configured),
                    "SKILL_SYSTEM_AGENT_RUN_BOOTSTRAP": None,
                },
                ".codex/hooks/codex_hook_adapter.py",
                "--input-file", str(input_path),
                "--run-dir", str(run_dir),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(run_ledger.is_file())
            self.assertFalse(configured.exists())

    def test_claude_hook_fallback_is_session_scoped(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            tmp_path = Path(tmp)
            codex_home = tmp_path / "codex-home"
            session_ids = ["claude/session-a", "claude-session-b"]
            env = {
                **os.environ,
                "CODEX_HOME": str(codex_home),
                "PYTHONDONTWRITEBYTECODE": "1",
            }
            env.pop("SKILL_SYSTEM_HOOK_LEDGER", None)
            env.pop("SKILL_SYSTEM_RUN_ID", None)
            for session_id in session_ids:
                result = subprocess.run(
                    [sys.executable, ".claude/hooks/claude_hook_adapter.py"],
                    cwd=ROOT,
                    env=env,
                    input=json.dumps({
                        "hook_event_name": "UserPromptSubmit",
                        "session_id": session_id,
                        "cwd": str(ROOT),
                        "permission_mode": "workspace-write",
                    }),
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                    timeout=30,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            root = codex_home / "harness" / "hook-ledgers"
            ledgers = sorted(root.glob("*/hook-events.jsonl"))
            self.assertEqual(len(ledgers), 2)
            observed = set()
            for ledger in ledgers:
                event = json.loads(ledger.read_text(encoding="utf-8").splitlines()[0])
                observed.add(event["run_id"])
                self.assertEqual(event["host"], "claude")
                self.assert_passes(".codex/tools/hook_runtime.py", "verify", "--ledger", str(ledger))
                for raw_id in session_ids:
                    self.assertNotIn(raw_id, ledger.relative_to(root).as_posix())
            self.assertEqual(observed, set(session_ids))

    def test_hook_runtime_status_reports_gate_modes_independently(self) -> None:
        result = self.run_tool_env(
            {
                "SKILL_SYSTEM_AGENT_OUTPUT_GATE": "strict",
                "SKILL_SYSTEM_RECOVERY_GUARD": "off",
            },
            ".codex/tools/hook_runtime.py", "status",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["agent_output_gate_mode"], "strict")
        self.assertEqual(report["recovery_guard_mode"], "off")

        result = self.run_tool_env(
            {
                "SKILL_SYSTEM_AGENT_OUTPUT_GATE": None,
                "SKILL_SYSTEM_RECOVERY_GUARD": "audit",
            },
            ".codex/tools/hook_runtime.py", "status",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["agent_output_gate_mode"], "observe")
        self.assertEqual(report["recovery_guard_mode"], "audit")




    def test_agent_run_artifact_fixture_passes(self) -> None:
        self.assert_passes(
            ".codex/tools/validate_agent_run_artifact.py",
            str(FIXTURES / "agent-runs" / "current-run"),
            "--schema",
            ".codex/schemas/harness/agent-run.schema.json",
        )

    def test_agent_verified_rejects_self_referential_manual_check(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            run_dir = Path(tmp) / "current-run"
            shutil.copytree(FIXTURES / "agent-runs" / "current-run", run_dir)
            manifest_path = run_dir / "run.yaml"
            manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            manifest["outputs"]["claims"][0]["support"] = {
                "type": "manual_check",
                "evidence_ref": "final-report.md",
            }
            manifest["validations"] = [{"type": "manual_check", "evidence_ref": "final-report.md"}]
            manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
            result = self.run_tool(
                ".codex/tools/validate_agent_run_artifact.py",
                str(run_dir),
                "--schema", ".codex/schemas/harness/agent-run.schema.json",
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("cannot rely on manual_check", result.stdout)
            self.assertIn("cannot use final_report as its own evidence", result.stdout)

    def test_schema_v2_command_claim_requires_hook_receipt(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            run_dir = Path(tmp) / "current-run"
            shutil.copytree(FIXTURES / "agent-runs" / "current-run", run_dir)
            manifest_path = run_dir / "run.yaml"
            manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            fake_command = "python3 fake_verifier.py"
            manifest["outputs"]["claims"][0]["support"]["command"] = fake_command
            manifest["validations"][0]["command"] = fake_command
            manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
            (run_dir / "artifacts" / "verification.txt").write_text(
                f"$ {fake_command}\nPASS\n", encoding="utf-8"
            )
            result = self.run_tool(
                ".codex/tools/validate_agent_run_artifact.py",
                str(run_dir),
                "--schema", ".codex/schemas/harness/agent-run.schema.json",
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("no matching PreToolUse/PostToolUse receipt", result.stdout)








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
                str(tmp_path),
                "--output-root",
                str(output_root),
            )
            self.assertEqual(init.returncode, 0, init.stdout + init.stderr)
            loop_dir = Path(json.loads(init.stdout)["loop_run_dir"])

            failed = tmp_path / "iteration-1.yaml"
            failed.write_text(
                """schema_version: 2
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

            target = tmp_path / "artifacts" / "sc-001.ok"
            target.parent.mkdir()
            target.write_text("complete\n", encoding="utf-8")
            target_digest = hashlib.sha256(target.read_bytes()).hexdigest()
            observed_at = yaml.safe_load((loop_dir / "state.yaml").read_text(encoding="utf-8"))["started_at"]
            passed = tmp_path / "iteration-2.yaml"
            passed.write_text(
                f"""schema_version: 2
loop_run_id: LR-20260623-001
iteration: 2
agent_run_id: AR-20260623-002
condition_results:
  - condition_id: SC-001
    status: pass
    evidence_refs:
      - artifacts/sc-001.ok
    evidence:
      - kind: artifact_exists
        verifier_owner: agent:codex
        observed_at: '{observed_at}'
        outcome: pass
        artifact_ref: artifacts/sc-001.ok
        artifact_scope: workspace
        artifact_sha256: {target_digest}
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
                str(tmp_path),
                "--output-root",
                str(output_root),
            )
            self.assertEqual(init.returncode, 0, init.stdout + init.stderr)
            loop_dir = Path(json.loads(init.stdout)["loop_run_dir"])
            for iteration in [1, 2]:
                result_file = tmp_path / f"iteration-{iteration}.yaml"
                result_file.write_text(
                    f"""schema_version: 2
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


    def test_loop_run_pass_without_structured_evidence_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            tmp_path = Path(tmp)
            contract = tmp_path / "contract.yaml"
            output_root = tmp_path / "loop-runs"
            self.write_loop_contract(contract)
            init = self.run_tool(
                ".codex/tools/init_loop_run.py", str(contract),
                "--workspace-root", str(tmp_path), "--output-root", str(output_root),
            )
            self.assertEqual(init.returncode, 0, init.stdout + init.stderr)
            loop_dir = Path(json.loads(init.stdout)["loop_run_dir"])
            hacked = tmp_path / "iteration-1.yaml"
            hacked.write_text(
                """schema_version: 2
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
            self.assertEqual(evaluation.returncode, 1, evaluation.stdout + evaluation.stderr)
            self.assertIn("structured evidence receipt", evaluation.stdout)
            state = yaml.safe_load((loop_dir / "state.yaml").read_text(encoding="utf-8"))
            self.assertEqual(state["status"], "active")
            self.assertEqual(state["iteration"], 0)







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

    def test_codex_hook_adapter_event_mapping_matrix(self) -> None:
        cases = [
            ("userpromptsubmit.json", "request_received", "pass", "native"),
            ("sessionstart.json", "context_loaded", "pass", "approximate"),
            ("pretooluse.json", "tool_preflight", "pass", "native"),
            ("permissionrequest.json", "permission_requested", "pass", "native"),
            ("posttooluse-fail.json", "tool_result", "fail", "native"),
            ("precompact.json", "compact_before", "pass", "native"),
            ("postcompact.json", "compact_after", "pass", "native"),
        ]
        for fixture, neutral_event, status, support_level in cases:
            with self.subTest(fixture=fixture):
                ledger = self.temp_ledger(f"mapping-{fixture}")
                result = self.run_tool(
                    ".codex/hooks/codex_hook_adapter.py",
                    "--input-file", str(FIXTURES / "hooks" / fixture),
                    "--ledger", str(ledger),
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                event = json.loads(ledger.read_text(encoding="utf-8").splitlines()[0])
                self.assertEqual(event["neutral_event"], neutral_event)
                self.assertEqual(event["status"], status)
                self.assertEqual(event["support_level"], support_level)
                if fixture == "sessionstart.json":
                    self.assertNotIn("kanboard_autosync", event["evidence"])

    def test_codex_hook_adapter_rejects_unknown_event_without_ledger(self) -> None:
        ledger = self.temp_ledger("unknown-event")
        result = self.run_tool(
            ".codex/hooks/codex_hook_adapter.py",
            "--input-file", str(FIXTURES / "hooks" / "unknown-event.json"),
            "--ledger", str(ledger),
        )
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(ledger.exists())
        self.assertIn("unsupported hook_event_name", result.stderr)

    def test_recovery_guard_observes_long_session_risk_without_blocking_by_default(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            tmp_path = Path(tmp)
            ledger = tmp_path / "events.jsonl"
            session_id = "session-recovery-observe"

            def invoke(
                name: str,
                payload: dict[str, object],
                mode: str = "audit",
            ) -> subprocess.CompletedProcess[str]:
                path = tmp_path / f"{name}.json"
                path.write_text(json.dumps(payload), encoding="utf-8")
                return self.run_tool_env(
                    {"SKILL_SYSTEM_RECOVERY_GUARD": None},
                    ".codex/hooks/codex_hook_adapter.py",
                    "--input-file", str(path),
                    "--ledger", str(ledger),
                )

            base = {"session_id": session_id, "cwd": str(ROOT), "permission_mode": "workspace-write"}
            self.assertEqual(invoke("compact", {**base, "hook_event_name": "PostCompact", "turn_id": "t1"}).returncode, 0)
            self.assertEqual(invoke("correction", {
                **base,
                "hook_event_name": "UserPromptSubmit",
                "turn_id": "t2",
                "prompt": "그게 아니잖아. 런타임 로직을 비교해줘.",
            }).returncode, 0)
            result = invoke("stop", {
                **base,
                "hook_event_name": "Stop",
                "turn_id": "t2",
                "last_assistant_message": "맞습니다. 이제 다시 시작하겠습니다.",
            })
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            output = json.loads(result.stdout)
            self.assertTrue(output["continue"])
            event = json.loads(ledger.read_text(encoding="utf-8").splitlines()[-1])
            guard = event["evidence"]["recovery_guard"]
            self.assertTrue(guard["armed"])
            self.assertTrue(guard["would_audit"])
            self.assertFalse(guard["did_audit_block"])
            self.assertEqual(guard["suppressed_by"], "observe_mode")

    def test_recovery_guard_environment_off_overrides_payload_audit(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            tmp_path = Path(tmp)
            ledger = tmp_path / "events.jsonl"
            session_id = "session-recovery-emergency-off"
            payload = {
                "hook_event_name": "Stop",
                "session_id": session_id,
                "turn_id": "t1",
                "cwd": str(ROOT),
                "permission_mode": "workspace-write",
                "skill_system_recovery_guard": "audit",
                "last_assistant_message": "맞습니다. 이제 다시 시작하겠습니다.",
            }
            inp = tmp_path / "stop.json"
            inp.write_text(json.dumps(payload), encoding="utf-8")
            result = self.run_tool(
                ".codex/hooks/codex_hook_adapter.py",
                "--input-file", str(inp),
                "--ledger", str(ledger),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(json.loads(result.stdout)["continue"])
            self.assertFalse(
                state_path_for_session(session_id, Path(self._guard_state_tmp.name)).exists()
            )
            recorded = json.loads(ledger.read_text(encoding="utf-8").splitlines()[-1])
            self.assertNotIn("recovery_guard", recorded["evidence"])

    def test_recovery_guard_audit_blocks_once_then_hands_packet_to_user(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            tmp_path = Path(tmp)
            ledger = tmp_path / "events.jsonl"
            session_id = "session-recovery-audit"

            def invoke(
                name: str,
                payload: dict[str, object],
                mode: str = "audit",
            ) -> subprocess.CompletedProcess[str]:
                path = tmp_path / f"{name}.json"
                path.write_text(json.dumps(payload), encoding="utf-8")
                return self.run_tool_env(
                    {"SKILL_SYSTEM_RECOVERY_GUARD": mode},
                    ".codex/hooks/codex_hook_adapter.py",
                    "--input-file", str(path),
                    "--ledger", str(ledger),
                )

            base = {"session_id": session_id, "cwd": str(ROOT), "permission_mode": "workspace-write"}
            invoke("compact", {**base, "hook_event_name": "PostCompact", "turn_id": "t1"})
            invoke("correction", {
                **base,
                "hook_event_name": "UserPromptSubmit",
                "turn_id": "t2",
                "prompt": "그게 아니잖아. 실제 로직 차이를 확인해줘.",
            })
            blocked = invoke("stop-risk", {
                **base,
                "hook_event_name": "Stop",
                "turn_id": "t2",
                "stop_hook_active": False,
                "last_assistant_message": "맞습니다. 앞으로는 로직을 중심으로 다시 하겠습니다.",
            })
            self.assertEqual(blocked.returncode, 0, blocked.stdout + blocked.stderr)
            blocked_output = json.loads(blocked.stdout)
            self.assertEqual(blocked_output["decision"], "block")
            self.assertIn("recovery_audit", blocked_output["reason"])
            ledger_after_block = ledger.read_bytes()
            replayed_block = invoke("stop-risk-replay", {
                **base,
                "hook_event_name": "Stop",
                "turn_id": "t2",
                "stop_hook_active": False,
                "last_assistant_message": "맞습니다. 앞으로는 로직을 중심으로 다시 하겠습니다.",
            })
            self.assertEqual(json.loads(replayed_block.stdout)["decision"], "block")
            self.assertEqual(ledger.read_bytes(), ledger_after_block)

            near_duplicate = invoke("stop-risk-near-duplicate", {
                **base,
                "hook_event_name": "Stop",
                "turn_id": "t2",
                "stop_hook_active": False,
                "last_assistant_message": "맞습니다. 앞으로는 로직을 중심으로 다시 하겠습니다.",
                "hook_source": "near-duplicate",
            })
            self.assertEqual(json.loads(near_duplicate.stdout)["decision"], "block")
            guard_state = json.loads(
                state_path_for_session(session_id, Path(self._guard_state_tmp.name)).read_text(encoding="utf-8")
            )
            self.assertEqual(guard_state["phase"], "audit_requested")
            self.assertEqual(guard_state["audit_responses"], 0)
            self.assertEqual(guard_state["audit_blocks"], 1)

            packet = """recovery_audit:
  goal_anchor: compare runtime logic
  latest_user_delta: ignore framework labels
  observed_changes: []
  verified_progress: []
  open_gap_and_next_action: inspect the behavioral contract
"""
            handed = invoke("stop-audit", {
                **base,
                "hook_event_name": "Stop",
                "turn_id": "t2",
                "stop_hook_active": True,
                "last_assistant_message": packet,
            }, mode="observe")
            self.assertEqual(handed.returncode, 0, handed.stdout + handed.stderr)
            handed_output = json.loads(handed.stdout)
            self.assertTrue(handed_output["continue"])
            self.assertIn("handed to the user", handed_output["systemMessage"])
            events = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines()]
            stop_events = [event for event in events if event["neutral_event"] == "turn_finalize_attempt"]
            self.assertEqual(len(stop_events), 3)
            self.assertTrue(stop_events[0]["evidence"]["recovery_guard"]["did_audit_block"])
            self.assertIn(
                "awaiting_active_audit_response",
                stop_events[1]["evidence"]["recovery_guard"]["reason_codes"],
            )
            self.assertEqual(stop_events[2]["evidence"]["recovery_guard"]["action"], "handoff")
            self.assertTrue(stop_events[2]["evidence"]["recovery_guard"]["audit_packet_valid"])
            self.assertNotIn("agent_run_finalize", stop_events[0]["evidence"])
            self.assertNotIn("desktop_notifications", stop_events[2]["evidence"])
            ledger_after_handoff = ledger.read_bytes()
            replayed_handoff = invoke("stop-audit-replay", {
                **base,
                "hook_event_name": "Stop",
                "turn_id": "t2",
                "stop_hook_active": True,
                "last_assistant_message": packet,
            })
            self.assertTrue(json.loads(replayed_handoff.stdout)["continue"])
            self.assertEqual(ledger.read_bytes(), ledger_after_handoff)

    def test_recovery_guard_does_not_arm_on_short_correction(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            tmp_path = Path(tmp)
            ledger = tmp_path / "events.jsonl"
            base = {
                "session_id": "session-recovery-short",
                "turn_id": "t1",
                "cwd": str(ROOT),
                "permission_mode": "workspace-write",
            }
            user = tmp_path / "user.json"
            user.write_text(json.dumps({
                **base,
                "hook_event_name": "UserPromptSubmit",
                "prompt": "그게 아니잖아. 다시 봐줘.",
            }), encoding="utf-8")
            self.run_tool_env(
                {"SKILL_SYSTEM_RECOVERY_GUARD": "audit"},
                ".codex/hooks/codex_hook_adapter.py", "--input-file", str(user), "--ledger", str(ledger),
            )
            stop = tmp_path / "stop.json"
            stop.write_text(json.dumps({
                **base,
                "hook_event_name": "Stop",
                "last_assistant_message": "맞습니다. 이제 다시 수정하겠습니다.",
            }), encoding="utf-8")
            result = self.run_tool_env(
                {"SKILL_SYSTEM_RECOVERY_GUARD": "audit"},
                ".codex/hooks/codex_hook_adapter.py", "--input-file", str(stop), "--ledger", str(ledger),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(json.loads(result.stdout)["continue"])
            event = json.loads(ledger.read_text(encoding="utf-8").splitlines()[-1])
            self.assertFalse(event["evidence"]["recovery_guard"]["armed"])

    def test_recovery_guard_corrupt_state_fails_open(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            tmp_path = Path(tmp)
            ledger = tmp_path / "events.jsonl"
            session_id = "session-recovery-corrupt"
            state_path = state_path_for_session(session_id, Path(self._guard_state_tmp.name))
            state_path.parent.mkdir(parents=True, exist_ok=True)
            state_path.write_text('{"prompt":"must-not-be-trusted"}', encoding="utf-8")
            inp = tmp_path / "user.json"
            inp.write_text(json.dumps({
                "hook_event_name": "UserPromptSubmit",
                "session_id": session_id,
                "turn_id": "t1",
                "cwd": str(ROOT),
                "permission_mode": "workspace-write",
                "prompt": "continue normally",
            }), encoding="utf-8")
            result = self.run_tool_env(
                {"SKILL_SYSTEM_RECOVERY_GUARD": "observe"},
                ".codex/hooks/codex_hook_adapter.py", "--input-file", str(inp), "--ledger", str(ledger),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            event = json.loads(ledger.read_text(encoding="utf-8").splitlines()[-1])
            self.assertEqual(event["evidence"]["recovery_guard"]["status"], "error")

    def test_recovery_guard_is_shadow_only_when_loop_is_explicitly_active(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            tmp_path = Path(tmp)
            ledger = tmp_path / "events.jsonl"
            loop_dir = tmp_path / "active-loop"
            shutil.copytree(FIXTURES / "loop-runs" / "valid", loop_dir)
            session_id = "session-recovery-loop"

            def invoke(name: str, payload: dict[str, object]) -> subprocess.CompletedProcess[str]:
                path = tmp_path / f"{name}.json"
                path.write_text(json.dumps(payload), encoding="utf-8")
                return self.run_tool_env(
                    {"SKILL_SYSTEM_RECOVERY_GUARD": "audit"},
                    ".codex/hooks/codex_hook_adapter.py", "--input-file", str(path), "--ledger", str(ledger),
                )

            base = {"session_id": session_id, "cwd": str(ROOT), "permission_mode": "workspace-write"}
            invoke("compact", {**base, "hook_event_name": "PostCompact", "turn_id": "t1"})
            invoke("correction", {
                **base,
                "hook_event_name": "UserPromptSubmit",
                "turn_id": "t2",
                "prompt": "그게 아니잖아. 실제 동작을 확인해줘.",
            })
            result = invoke("stop", {
                **base,
                "hook_event_name": "Stop",
                "turn_id": "t2",
                "skill_system_loop_run_dir": str(loop_dir),
                "skill_system_loop_continuation": "observe",
                "last_assistant_message": "맞습니다. 이제 다시 시작하겠습니다.",
            })
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(json.loads(result.stdout)["continue"])
            event = json.loads(ledger.read_text(encoding="utf-8").splitlines()[-1])
            guard = event["evidence"]["recovery_guard"]
            self.assertTrue(guard["would_audit"])
            self.assertFalse(guard["did_audit_block"])
            self.assertEqual(guard["suppressed_by"], "active_loop")

    def test_terminal_loop_path_does_not_suppress_recovery_guard(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            tmp_path = Path(tmp)
            ledger = tmp_path / "events.jsonl"
            loop_dir = tmp_path / "terminal-loop"
            shutil.copytree(FIXTURES / "loop-runs" / "valid", loop_dir)
            state_path = loop_dir / "state.yaml"
            state_path.write_text(
                state_path.read_text(encoding="utf-8").replace("status: active", "status: terminal", 1),
                encoding="utf-8",
            )
            session_id = "session-recovery-terminal-loop"

            def invoke(name: str, payload: dict[str, object]) -> subprocess.CompletedProcess[str]:
                path = tmp_path / f"{name}.json"
                path.write_text(json.dumps(payload), encoding="utf-8")
                return self.run_tool_env(
                    {"SKILL_SYSTEM_RECOVERY_GUARD": "audit"},
                    ".codex/hooks/codex_hook_adapter.py", "--input-file", str(path), "--ledger", str(ledger),
                )

            base = {"session_id": session_id, "cwd": str(ROOT), "permission_mode": "workspace-write"}
            invoke("compact", {**base, "hook_event_name": "PostCompact", "turn_id": "t1"})
            invoke("correction", {
                **base,
                "hook_event_name": "UserPromptSubmit",
                "turn_id": "t2",
                "prompt": "그게 아니잖아. 실제 동작을 확인해줘.",
            })
            result = invoke("stop", {
                **base,
                "hook_event_name": "Stop",
                "turn_id": "t2",
                "skill_system_loop_run_dir": str(loop_dir),
                "last_assistant_message": "맞습니다. 이제 다시 시작하겠습니다.",
            })
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["decision"], "block")



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

    def test_codex_hook_adapter_redacts_env_assignment_category_and_url_userinfo(self) -> None:
        env_ledger = self.temp_ledger("live-hook-env-secret")
        self.assert_passes(
            ".codex/hooks/codex_hook_adapter.py",
            "--input-file", str(FIXTURES / "hooks" / "pretooluse-env-assignment.json"),
            "--ledger", str(env_ledger),
        )
        env_raw = env_ledger.read_text(encoding="utf-8")
        self.assertNotIn("OPENAI_API_KEY", env_raw)
        self.assertNotIn("short-secret", env_raw)
        env_event = json.loads(env_raw.splitlines()[0])
        self.assertEqual(env_event["evidence"]["command_category"], "<redacted>")

        url_ledger = self.temp_ledger("live-hook-url-secret")
        self.assert_passes(
            ".codex/hooks/codex_hook_adapter.py",
            "--input-file", str(FIXTURES / "hooks" / "posttooluse-redaction.json"),
            "--ledger", str(url_ledger),
        )
        url_raw = url_ledger.read_text(encoding="utf-8")
        self.assertNotIn("alice", url_raw)
        self.assertNotIn("shortpass", url_raw)
        self.assertIn("example.com", url_raw)



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

    def test_codex_hook_adapter_stop_missing_current_run_skips_in_notification_mode(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            tmp_path = Path(tmp)
            ledger = tmp_path / "hook-events.jsonl"
            session_id = f"session-notification-skip-{os.getpid()}"
            turn_id = f"turn-notification-skip-{os.getpid()}"
            inp = tmp_path / "stop.json"
            inp.write_text(
                json.dumps(
                    {
                        "hook_event_name": "Stop",
                        "session_id": session_id,
                        "turn_id": turn_id,
                        "cwd": str(ROOT),
                        "permission_mode": "workspace-write",
                        "last_assistant_message": "Plain final answer without an agent-run manifest.",
                    }
                ),
                encoding="utf-8",
            )
            env = {
                **os.environ,
                "PYTHONDONTWRITEBYTECODE": "1",
                "SKILL_SYSTEM_DESKTOP_NOTIFY": "dry-run",
                "SKILL_SYSTEM_HOOK_LEDGER": str(ledger),
                "CODEX_MODEL": "gpt-5.5",
                "CODEX_MODEL_REASONING_EFFORT": "xhigh",
            }
            env.pop("SKILL_SYSTEM_AGENT_OUTPUT_GATE", None)
            env.pop("SKILL_SYSTEM_AGENT_RUN_BOOTSTRAP", None)
            result = subprocess.run(
                [sys.executable, ".codex/hooks/codex_hook_adapter.py", "--input-file", str(inp)],
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
            self.assertIn("SKIP: agent output validation skipped", output["systemMessage"])
            self.assertNotIn("UNVERIFIED", output["systemMessage"])
            events = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(events[0]["neutral_event"], "turn_finalize_attempt")
            self.assertEqual(events[0]["status"], "skip")
            self.assertEqual(len(events), 1)
            note = events[0]["evidence"]["desktop_notifications"]["turn_complete"]
            self.assertEqual(note["status"], "dry_run")

    def test_codex_hook_adapter_stop_is_idempotent_after_finalize(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            run_dir = Path(tmp) / "current-run"
            shutil.copytree(FIXTURES / "agent-runs" / "current-run", run_dir)
            hook_file = run_dir / "hook-events.jsonl"
            before = hook_file.read_bytes()
            result = self.run_tool(
                ".codex/hooks/codex_hook_adapter.py",
                "--input-file", str(FIXTURES / "hooks" / "stop.json"),
                "--run-dir", str(run_dir),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            output = json.loads(result.stdout)
            self.assertIn("already finalized", output["systemMessage"])
            self.assertEqual(hook_file.read_bytes(), before)

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
                            "result_label: user-verification-needed\n\n"
                            "## Claims\n\n"
                            "- C-002: live bootstrap finalization synchronized the task claim manifest.\n"
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
            manifest = yaml.safe_load((run_dir / "run.yaml").read_text(encoding="utf-8"))
            self.assertEqual(manifest["task"]["result_label"], "user-verification-needed")
            self.assertEqual(manifest["assistant_message"]["result_label"], "user-verification-needed")
            self.assertEqual(manifest["assistant_message"]["claim_ids"], ["C-002"])
            self.assertEqual(manifest["outputs"]["claims"][0]["claim_id"], "C-002")
            self.assertEqual(manifest["outputs"]["claims"][0]["support"]["evidence_ref"], "final-report.md")
            self.assert_passes(
                ".codex/tools/validate_agent_run_artifact.py",
                str(run_dir),
                "--schema",
                ".codex/schemas/harness/agent-run.schema.json",
            )

    def test_live_agent_run_cannot_self_certify_agent_verified(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            tmp_path = Path(tmp)
            run_dir = tmp_path / "self-cert-run"
            self.assert_passes(
                ".codex/tools/init_agent_run.py", "init",
                "--session-id", "session-self-cert",
                "--turn-id", "turn-self-cert",
                "--user-request-summary", "attempt self certification",
                "--run-dir", str(run_dir),
            )
            for name, event_name in [("request", "UserPromptSubmit"), ("session", "SessionStart")]:
                inp = tmp_path / f"{name}.json"
                inp.write_text(json.dumps({
                    "hook_event_name": event_name,
                    "session_id": "session-self-cert",
                    "turn_id": "turn-self-cert",
                    "cwd": str(ROOT),
                    "permission_mode": "workspace-write",
                }), encoding="utf-8")
                result = self.run_tool(
                    ".codex/hooks/codex_hook_adapter.py",
                    "--input-file", str(inp),
                    "--run-dir", str(run_dir),
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            stop = tmp_path / "stop-self-cert.json"
            stop.write_text(json.dumps({
                "hook_event_name": "Stop",
                "session_id": "session-self-cert",
                "turn_id": "turn-self-cert",
                "cwd": str(ROOT),
                "permission_mode": "workspace-write",
                "skill_system_agent_output_gate": "strict",
                "last_assistant_message": (
                    "# Agent Run Final Report\n\n"
                    "result_label: agent-verified\n\n"
                    "## Claims\n\n"
                    "- C-999: production is correct without independent evidence.\n"
                ),
            }), encoding="utf-8")
            self.assert_passes(
                ".codex/tools/init_agent_run.py", "finalize", str(run_dir),
                "--input-file", str(stop),
            )
            result = self.run_tool(
                ".codex/hooks/codex_hook_adapter.py",
                "--input-file", str(stop),
                "--run-dir", str(run_dir),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            output = json.loads(result.stdout)
            self.assertEqual(output["decision"], "block")
            self.assertIn("manual_check", output["reason"])
            events = [json.loads(line) for line in (run_dir / "hook-events.jsonl").read_text(encoding="utf-8").splitlines()]
            self.assertEqual(events[-1]["neutral_event"], "turn_finalize_attempt")
            self.assertEqual(events[-1]["status"], "fail")


if __name__ == "__main__":
    unittest.main()
