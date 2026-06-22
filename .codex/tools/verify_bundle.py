#!/usr/bin/env python3
"""Profile-based verification entry point for the skill bundle."""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path


STATUS_PASS = "PASS"
STATUS_PASS_WITH_SKIPS = "PASS_WITH_SKIPS"
STATUS_FAIL = "FAIL"
STATUS_SKIP = "SKIP"
STATUS_ERROR = "ERROR"
CHECK_TIMEOUT_SECONDS = 60
MAX_CAPTURED_OUTPUT = 12000


class Check:
    def __init__(
        self,
        check_id: str,
        cmd: list[str],
        cwd: Path,
        required: bool = True,
        env: dict[str, str] | None = None,
        timeout_seconds: int | None = None,
    ) -> None:
        self.check_id = check_id
        self.cmd = cmd
        self.cwd = cwd
        self.required = required
        self.env = env
        self.timeout_seconds = timeout_seconds


def terminate_process_group(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGTERM)
            process.wait(timeout=5)
            return
        except (ProcessLookupError, subprocess.TimeoutExpired):
            pass
        if process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
    else:  # pragma: no cover - Windows fallback.
        process.kill()


def run_check(check: Check) -> dict[str, object]:
    started = time.monotonic()
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    if check.env:
        env.update(check.env)
    timeout_seconds = check.timeout_seconds or CHECK_TIMEOUT_SECONDS
    try:
        process = subprocess.Popen(
            check.cmd,
            cwd=check.cwd,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=(os.name == "posix"),
        )
        stdout_raw, stderr_raw = process.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired as exc:
        terminate_process_group(process)
        stdout_raw = text_output(exc.stdout)
        stderr_raw = text_output(exc.stderr)
        return {
            "id": check.check_id,
            "status": STATUS_ERROR,
            "required": check.required,
            "duration_ms": int((time.monotonic() - started) * 1000),
            "command": check.cmd,
            "stdout": truncate(stdout_raw),
            "stderr": truncate((stderr_raw + f"\ntimed out after {timeout_seconds}s").strip()),
        }
    except Exception as exc:  # noqa: BLE001 - top-level verifier should capture all check crashes.
        return {
            "id": check.check_id,
            "status": STATUS_ERROR,
            "required": check.required,
            "duration_ms": int((time.monotonic() - started) * 1000),
            "command": check.cmd,
            "stdout": "",
            "stderr": str(exc),
        }
    stdout = truncate(text_output(stdout_raw).strip())
    stderr = truncate(text_output(stderr_raw).strip())
    if process.returncode == 0 and stdout.startswith("SKIP"):
        status = STATUS_SKIP
    elif process.returncode == 0:
        status = STATUS_PASS
    else:
        status = STATUS_FAIL
    return {
        "id": check.check_id,
        "status": status,
        "required": check.required,
        "duration_ms": int((time.monotonic() - started) * 1000),
        "command": check.cmd,
        "exit_code": process.returncode,
        "stdout": stdout,
        "stderr": stderr,
    }


def profile_status(results: list[dict[str, object]]) -> str:
    required_results = [result for result in results if result.get("required")]
    if any(result["status"] == STATUS_ERROR for result in required_results):
        return STATUS_ERROR
    if any(result["status"] == STATUS_FAIL for result in required_results):
        return STATUS_FAIL
    if any(result["status"] == STATUS_SKIP for result in results):
        return STATUS_PASS_WITH_SKIPS
    return STATUS_PASS


def exit_code(status: str) -> int:
    if status in {STATUS_PASS, STATUS_PASS_WITH_SKIPS}:
        return 0
    if status == STATUS_FAIL:
        return 1
    if status == STATUS_ERROR:
        return 3
    return 1


def print_text(report: dict[str, object]) -> None:
    print(report["status"])
    for check in report["checks"]:
        print(f"- {check['id']}: {check['status']} ({check['duration_ms']} ms)")
        stdout = str(check.get("stdout") or "")
        stderr = str(check.get("stderr") or "")
        if stdout and check["status"] != STATUS_PASS:
            print(f"  stdout: {stdout}")
        if stderr:
            print(f"  stderr: {stderr}")


def truncate(value: str) -> str:
    if len(value) <= MAX_CAPTURED_OUTPUT:
        return value
    return value[:MAX_CAPTURED_OUTPUT] + f"\n... truncated at {MAX_CAPTURED_OUTPUT} chars"


def text_output(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def core_checks(root: Path) -> list[Check]:
    py = sys.executable
    return [
        Check("bundle_hygiene", [py, ".codex/tools/check_bundle_hygiene.py", "."], root),
        Check("doc_freshness", [py, ".codex/tools/check_doc_freshness.py", "."], root),
        Check("tool_requirements", [py, ".codex/tools/check_tool_requirements.py"], root),
        Check("reference_targets", [py, ".codex/tools/check_reference_targets.py"], root),
        Check(
            "eval_cases",
            [
                py,
                ".codex/tools/validate_eval_cases.py",
                ".codex/eval",
                "--schema",
                ".codex/eval/eval-case.schema.json",
                "--min-v2-cases",
                "15",
            ],
            root,
        ),
        Check("field_feedback", [py, ".codex/tools/validate_field_feedback.py", ".codex/field-feedback"], root, False),
        Check("source_registry", [py, ".codex/tools/validate_source_registry.py", ".codex/docs/source_registry.yaml"], root),
        Check("generated_mirrors", [py, ".codex/tools/sync_generated_mirrors.py", "--check"], root),
        Check("context_compounding_plan", [py, ".codex/tools/check_context_compounding_plan.py"], root),
        Check(
            "validator_unit_tests",
            [py, "-m", "unittest", "discover", "-s", ".codex/tools/tests"],
            root,
            timeout_seconds=180,
        ),
    ]


def execution_checks(root: Path) -> list[Check]:
    py = sys.executable
    return [
        Check("execution_assurance_artifacts", [py, ".codex/tools/check_execution_assurance.py"], root),
        Check(
            "hook_runtime_smoke",
            [
                py,
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
                "/private/tmp/skill-system-hook-runtime-smoke.jsonl",
            ],
            root,
        ),
        Check(
            "behavior_replay",
            [py, ".codex/tools/run_behavior_evals.py", "--mode", "replay", "--observed-runs", ".codex/eval/observed-runs"],
            root,
        ),
    ]


def research_checks(root: Path) -> list[Check]:
    py = sys.executable
    return [
        Check(
            "research_ledger",
            [
                py,
                ".codex/tools/validate_research_ledger.py",
                ".codex/research/ledger.yaml",
                "--schema",
                ".codex/research/research-ledger.schema.json",
            ],
            root,
        )
    ]


def agent_output_checks(root: Path) -> list[Check]:
    py = sys.executable
    return [
        Check(
            "agent_run_current_fixture",
            [
                py,
                ".codex/tools/validate_agent_run_artifact.py",
                ".codex/tools/tests/fixtures/agent-runs/current-run",
                "--schema",
                ".codex/schemas/harness/agent-run.schema.json",
            ],
            root,
        ),
        Check(
            "agent_run_permission_fixture",
            [
                py,
                ".codex/tools/validate_agent_run_artifact.py",
                ".codex/tools/tests/fixtures/agent-runs/permission-no-tool-id",
                "--schema",
                ".codex/schemas/harness/agent-run.schema.json",
            ],
            root,
        ),
        Check(
            "agent_run_recovery_fixture",
            [
                py,
                ".codex/tools/validate_agent_run_artifact.py",
                ".codex/tools/tests/fixtures/agent-runs/stop-recovery",
                "--schema",
                ".codex/schemas/harness/agent-run.schema.json",
            ],
            root,
        ),
    ]


def knowledge_checks(root: Path) -> list[Check]:
    py = sys.executable
    return [
        Check(
            "knowledge_store_fixture",
            [
                py,
                ".codex/tools/validate_knowledge_store.py",
                ".codex/tools/tests/fixtures/knowledge-store/valid",
                "--schemas",
                ".codex/schemas/knowledge",
                "--require-projections",
            ],
            root,
        ),
        Check(
            "context_projection_build_check",
            [
                py,
                ".codex/tools/build_context_pack.py",
                ".codex/tools/tests/fixtures/knowledge-store/valid",
                "--rebuild-projections",
                "--build-run-pack",
                "--check",
            ],
            root,
        ),
        Check("memory_explicit_contract", [py, ".codex/tools/check_memory_explicit_contract.py"], root),
        Check(
            "agent_run_context_linkage",
            [
                py,
                ".codex/tools/validate_agent_run_artifact.py",
                ".codex/tools/tests/fixtures/agent-runs/current-run",
                "--schema",
                ".codex/schemas/harness/agent-run.schema.json",
            ],
            root,
        ),
    ]


def integrations_checks(root: Path) -> list[Check]:
    py = sys.executable
    integration = root / "integrations" / "kanboard-plan-sync"
    if not integration.exists():
        return [
            Check(
                "kanboard_integration",
                [py, "-c", "print('SKIP: integrations/kanboard-plan-sync not present; expires_at=2026-07-20')"],
                root,
                False,
            )
        ]
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = "src" if not existing_pythonpath else os.pathsep.join(["src", existing_pythonpath])
    pytest_probe = subprocess.run(
        [py, "-c", "import pytest"],
        cwd=integration,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
        timeout=10,
    )
    if pytest_probe.returncode != 0:
        return [
            Check(
                "kanboard_integration",
                [py, "-c", "print('SKIP: pytest unavailable locally; last reviewed state says 91 passed; expires_at=2026-07-20')"],
                root,
                False,
            )
        ]
    return [
        Check(
            "kanboard_integration",
            [py, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
            integration,
            True,
            env,
        )
    ]


def checks_for(profile: str, root: Path) -> list[Check]:
    if profile == "core":
        return core_checks(root)
    if profile == "integrations":
        return integrations_checks(root)
    if profile == "execution":
        return execution_checks(root)
    if profile == "research":
        return research_checks(root)
    if profile == "agent-output":
        return agent_output_checks(root)
    if profile == "knowledge":
        return knowledge_checks(root)
    raise ValueError(f"unknown profile: {profile}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=["core", "integrations", "execution", "agent-output", "research", "knowledge"], required=True)
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--release", action="store_true", help="fail if any profile check is skipped")
    args = parser.parse_args()
    root = args.root.resolve()
    if not root.exists():
        print(f"ERROR: root not found: {root}")
        return 2
    try:
        checks = checks_for(args.profile, root)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 2
    results = [run_check(check) for check in checks]
    status = profile_status(results)
    if args.release and status == STATUS_PASS_WITH_SKIPS:
        status = STATUS_FAIL
    report = {"profile": args.profile, "status": status, "checks": results}
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print_text(report)
    return exit_code(status)


if __name__ == "__main__":
    raise SystemExit(main())
