#!/usr/bin/env python3
"""Compare historical bundle cuts with the current receipt-only monitor."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import shutil
import statistics
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path
from typing import Any

import yaml


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / ".codex" / "eval" / "harness_versions.json"
REFERENCE_VERSION = "9.3.1"


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_metrics(paths: list[Path]) -> dict[str, int]:
    payloads = [path.read_bytes() for path in paths]
    return {
        "files": len(paths),
        "lines": sum(payload.count(b"\n") for payload in payloads),
        "bytes": sum(len(payload) for payload in payloads),
    }


def percentile(samples: list[float], quantile: float) -> float:
    values = sorted(samples)
    return values[min(len(values) - 1, int((len(values) - 1) * quantile))]


def run_command(command: list[str], cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=30,
    )


def git_text(*args: str) -> str:
    result = run_command(["git", *args], ROOT)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip()


def extract_ref(ref: str, destination: Path) -> None:
    result = subprocess.run(
        ["git", "archive", "--format=tar", ref, ".codex"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace"))
    destination.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(result.stdout), mode="r:") as archive:
        archive.extractall(destination)


def base_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    env = dict(os.environ)
    env.update({
        "PYTHONDONTWRITEBYTECODE": "1",
        "SKILL_SYSTEM_RECOVERY_GUARD": "off",
        "SKILL_SYSTEM_DESKTOP_NOTIFY": "off",
    })
    env.pop("SKILL_SYSTEM_AGENT_RUN_BOOTSTRAP", None)
    env.pop("SKILL_SYSTEM_VERIFIER_CONTRACT", None)
    env.pop("SKILL_SYSTEM_REFERENCE_MONITOR", None)
    if extra:
        env.update(extra)
    return env


def invoke_hook(
    version_root: Path,
    payload: dict[str, Any],
    input_path: Path,
    *,
    ledger: Path | None = None,
    run_dir: Path | None = None,
    env: dict[str, str] | None = None,
) -> tuple[dict[str, Any], float]:
    input_path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    command = [sys.executable, str(version_root / ".codex" / "hooks" / "codex_hook_adapter.py"), "--input-file", str(input_path)]
    if ledger is not None:
        command.extend(["--ledger", str(ledger)])
    if run_dir is not None:
        command.extend(["--run-dir", str(run_dir)])
    started = time.perf_counter()
    result = run_command(command, version_root, env)
    elapsed_ms = (time.perf_counter() - started) * 1000
    if result.returncode != 0:
        raise RuntimeError(f"hook failed: {result.stdout}\n{result.stderr}")
    try:
        output = json.loads(result.stdout) if result.stdout.strip() else {}
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"hook returned non-JSON output: {result.stdout}") from exc
    return output, elapsed_ms


def remove_fixture_finalize(run_dir: Path) -> None:
    ledger = run_dir / "hook-events.jsonl"
    lines = ledger.read_text(encoding="utf-8").splitlines()
    ledger.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")


def legacy_case(version_root: Path, case_id: str, case_root: Path) -> dict[str, Any]:
    fixture = version_root / ".codex" / "tools" / "tests" / "fixtures" / "agent-runs" / "current-run"
    run_dir = case_root / "current-run"
    shutil.copytree(fixture, run_dir)
    remove_fixture_finalize(run_dir)
    report = (run_dir / "final-report.md").read_text(encoding="utf-8")
    env = base_env()
    if case_id == "semantic-contradiction-without-trust":
        (run_dir / "artifacts" / "verification.txt").write_text(
            "$ python3 .codex/tools/verify_bundle.py --profile agent-output --format text\n"
            "PASS\n"
            "ORACLE_REQUIRED=HIGH_RES\n"
            "ACTUAL_SELECTED=LOW_RES\n",
            encoding="utf-8",
        )
    elif case_id == "verifier-failure":
        manifest_path = run_dir / "run.yaml"
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        manifest["validations"][0]["exit_code"] = 1
        manifest["outputs"]["claims"][0]["support"]["exit_code"] = 1
        manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    elif case_id == "ledger-tamper":
        ledger = run_dir / "hook-events.jsonl"
        events = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines()]
        events[-1]["status"] = "fail"
        ledger.write_text("".join(json.dumps(event, sort_keys=True) + "\n" for event in events), encoding="utf-8")
    if case_id == "unrelated-post-verifier-tool-use":
        command = "inspect after verifier"
        common = {
            "session_id": "session-test",
            "turn_id": "turn-test",
            "cwd": str(version_root),
            "permission_mode": "workspace-write",
            "tool_name": "Bash",
            "tool_use_id": "tool-after-verifier",
            "tool_input": {"command": command},
        }
        invoke_hook(version_root, {"hook_event_name": "PreToolUse", **common}, case_root / "pre.json", run_dir=run_dir, env=env)
        invoke_hook(
            version_root,
            {"hook_event_name": "PostToolUse", **common, "tool_response": {"exit_code": 0, "stdout": "PASS"}},
            case_root / "post.json",
            run_dir=run_dir,
            env=env,
        )
    stop_payload = {
        "hook_event_name": "Stop",
        "session_id": "session-test",
        "turn_id": "turn-test",
        "cwd": str(version_root),
        "permission_mode": "workspace-write",
        "skill_system_agent_output_gate": "strict",
        "last_assistant_message": report,
    }
    output, elapsed = invoke_hook(version_root, stop_payload, case_root / "stop.json", run_dir=run_dir, env=env)
    granted = bool(output.get("continue") and "passed" in str(output.get("systemMessage", "")).lower())
    recovery_allowed = granted
    if not granted:
        downgraded = dict(stop_payload)
        downgraded["last_assistant_message"] = report.replace(
            "result_label: agent-verified", "result_label: user-verification-needed"
        )
        second, _ = invoke_hook(version_root, downgraded, case_root / "stop-downgraded.json", run_dir=run_dir, env=env)
        recovery_allowed = bool(second.get("continue"))
    return {
        "authority": "grant" if granted else "deny",
        "reason": output.get("reason") or output.get("systemMessage"),
        "response_allowed_after_downgrade": recovery_allowed,
        "stop_ms": round(elapsed, 1),
    }


def contract_for_case(case_id: str, positive: str) -> dict[str, Any] | None:
    if case_id == "semantic-contradiction-without-trust":
        return None
    contract: dict[str, Any] = {
        "contract_id": f"VC-{case_id}",
        "verifier_command_hash": sha256_text(positive),
        "verifier_origin": "agent_modified" if case_id == "agent-modified-supporting-only" else "repository",
        "subject_refs": ["subject.txt"],
    }
    return contract


def reference_case(version_root: Path, case_id: str, case_root: Path) -> dict[str, Any]:
    ledger = case_root / "hook-events.jsonl"
    (case_root / "subject.txt").write_text(
        "ACTUAL_SELECTED=LOW_RES\n" if case_id == "semantic-contradiction-without-trust" else "production state\n",
        encoding="utf-8",
    )
    positive = "verify production subject"
    contract = contract_for_case(case_id, positive)
    extra_env = {"SKILL_SYSTEM_REFERENCE_MONITOR": "1"}
    if contract is not None:
        extra_env["SKILL_SYSTEM_VERIFIER_CONTRACT"] = json.dumps(contract, sort_keys=True)
    env = base_env(extra_env)
    common = {
        "session_id": "session-92",
        "turn_id": "turn-92",
        "cwd": str(case_root),
        "permission_mode": "workspace-write",
    }
    invoke_hook(
        version_root,
        {"hook_event_name": "UserPromptSubmit", **common, "prompt": "compare harness authority"},
        case_root / "request.json",
        ledger=ledger,
        env=env,
    )

    def tool(command: str, exit_code: int, tool_id: str) -> None:
        fields = {**common, "tool_name": "Bash", "tool_use_id": tool_id, "tool_input": {"command": command}}
        invoke_hook(version_root, {"hook_event_name": "PreToolUse", **fields}, case_root / f"pre-{tool_id}.json", ledger=ledger, env=env)
        invoke_hook(
            version_root,
            {"hook_event_name": "PostToolUse", **fields, "tool_response": {"exit_code": exit_code, "stdout": "PASS" if exit_code == 0 else "FAIL"}},
            case_root / f"post-{tool_id}.json",
            ledger=ledger,
            env=env,
        )

    if contract is not None:
        tool(positive, 1 if case_id == "verifier-failure" else 0, "tool-positive")
    if case_id == "unrelated-post-verifier-tool-use":
        tool("inspect after verifier", 0, "tool-after")
    if case_id == "ledger-tamper":
        events = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines()]
        events[-1]["evidence"]["verifier_receipt"]["exit_code"] = 9
        ledger.write_text("".join(json.dumps(event, sort_keys=True) + "\n" for event in events), encoding="utf-8")
    stop_payload = {
        "hook_event_name": "Stop",
        **common,
        "skill_system_agent_output_gate": "strict",
        "last_assistant_message": "Harness comparison stop.\n",
    }
    output, elapsed = invoke_hook(version_root, stop_payload, case_root / "stop.json", ledger=ledger, env=env)
    last_event = json.loads(ledger.read_text(encoding="utf-8").splitlines()[-1])
    receipt = last_event.get("evidence", {}).get("verifier_receipt_status", {})
    return {
        "receipt_status": receipt.get("receipt_status"),
        "reason": receipt.get("reason_code"),
        "response_continues": bool(output.get("continue")),
        "stop_ms": round(elapsed, 1),
    }


def benchmark_stop(version: str, version_root: Path, samples: int, benchmark_root: Path) -> dict[str, Any]:
    values: list[float] = []
    for index in range(samples):
        case_root = benchmark_root / f"sample-{index}"
        case_root.mkdir(parents=True)
        result = (
            reference_case(version_root, "trusted-verifier-success", case_root)
            if version == REFERENCE_VERSION
            else legacy_case(version_root, "trusted-verifier-success", case_root)
        )
        values.append(float(result["stop_ms"]))
    return {
        "samples": samples,
        "median_ms": round(statistics.median(values), 1),
        "p95_ms": round(percentile(values, 0.95), 1),
        "min_ms": round(min(values), 1),
        "max_ms": round(max(values), 1),
        "monitor_added_subprocesses": 0 if version == REFERENCE_VERSION else None,
        "latency_gate": "advisory",
    }


def benchmark_verifier_event_path(
    version: str, version_root: Path, samples: int, benchmark_root: Path
) -> dict[str, Any]:
    phases = {"user_prompt": [], "pre_tool": [], "post_tool": [], "total": []}
    positive = "verify production subject"
    for index in range(samples):
        case_root = benchmark_root / f"sample-{index}"
        case_root.mkdir(parents=True)
        ledger = case_root / "hook-events.jsonl"
        (case_root / "subject.txt").write_text("production state\n", encoding="utf-8")
        extra_env: dict[str, str] = {}
        if version == REFERENCE_VERSION:
            contract = contract_for_case("trusted-verifier-success", positive)
            extra_env.update({
                "SKILL_SYSTEM_REFERENCE_MONITOR": "1",
                "SKILL_SYSTEM_VERIFIER_CONTRACT": json.dumps(contract, sort_keys=True),
            })
        env = base_env(extra_env)
        common = {
            "session_id": "session-event-benchmark",
            "turn_id": f"turn-{index}",
            "cwd": str(case_root),
            "permission_mode": "workspace-write",
        }
        _, user_prompt_ms = invoke_hook(
            version_root,
            {"hook_event_name": "UserPromptSubmit", **common, "prompt": "benchmark verifier event path"},
            case_root / "request.json",
            ledger=ledger,
            env=env,
        )
        tool_fields = {
            **common,
            "tool_name": "Bash",
            "tool_use_id": "tool-positive",
            "tool_input": {"command": positive},
        }
        _, pre_tool_ms = invoke_hook(
            version_root,
            {"hook_event_name": "PreToolUse", **tool_fields},
            case_root / "pre.json",
            ledger=ledger,
            env=env,
        )
        _, post_tool_ms = invoke_hook(
            version_root,
            {
                "hook_event_name": "PostToolUse",
                **tool_fields,
                "tool_response": {"exit_code": 0, "stdout": "PASS"},
            },
            case_root / "post.json",
            ledger=ledger,
            env=env,
        )
        phases["user_prompt"].append(user_prompt_ms)
        phases["pre_tool"].append(pre_tool_ms)
        phases["post_tool"].append(post_tool_ms)
        phases["total"].append(user_prompt_ms + pre_tool_ms + post_tool_ms)
    return {
        "samples": samples,
        **{f"{phase}_median_ms": round(statistics.median(values), 1) for phase, values in phases.items()},
        "total_p95_ms": round(percentile(phases["total"], 0.95), 1),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--candidate-root", type=Path, default=ROOT)
    parser.add_argument("--samples", type=int, default=3)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    if args.samples < 1:
        raise SystemExit("--samples must be positive")
    results: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(dir="/private/tmp") as raw:
        temp_root = Path(raw)
        for version_spec in manifest["versions"]:
            version = version_spec["version"]
            ref = version_spec["source_ref"]
            if ref == "worktree":
                version_root = args.candidate_root.resolve()
                commit = git_text("rev-parse", "HEAD")
                source_state = "dirty-worktree" if git_text("status", "--porcelain") else "clean-worktree"
            else:
                commit = git_text("rev-parse", f"{ref}^{{commit}}")
                if commit != version_spec["commit"]:
                    raise RuntimeError(f"{version} ref {ref} moved from pinned commit")
                version_root = temp_root / f"version-{version}"
                extract_ref(ref, version_root)
                source_state = "pinned-ref"
            case_results: list[dict[str, Any]] = []
            for case in manifest["cases"]:
                case_id = case["case_id"]
                case_root = temp_root / f"cases-{version}" / case_id
                case_root.mkdir(parents=True)
                observed = (
                    reference_case(version_root, case_id, case_root)
                    if version == REFERENCE_VERSION
                    else legacy_case(version_root, case_id, case_root)
                )
                observed["case_id"] = case_id
                if version == REFERENCE_VERSION:
                    observed["expected_receipt_status"] = case["expected_receipt_status"]
                    observed["passed"] = observed["receipt_status"] == case["expected_receipt_status"]
                else:
                    observed["expected_authority"] = case["expected_authority"]
                    observed["passed"] = observed["authority"] == case["expected_authority"]
                case_results.append(observed)
            hook = version_root / ".codex" / "hooks" / "codex_hook_adapter.py"
            validator = version_root / ".codex" / "tools" / "validate_agent_run_artifact.py"
            bootstrap = version_root / ".codex" / "tools" / "init_agent_run.py"
            runtime_paths = [hook, validator, bootstrap]
            reference_monitor = version_root / ".codex" / "tools" / "reference_monitor.py"
            if reference_monitor.exists():
                runtime_paths.append(reference_monitor)
            performance = benchmark_stop(
                version,
                version_root,
                args.samples,
                temp_root / f"benchmark-stop-{version}",
            )
            performance["trusted_verifier_event_path"] = benchmark_verifier_event_path(
                version,
                version_root,
                args.samples,
                temp_root / f"benchmark-events-{version}",
            )
            results.append({
                "version": version,
                "source_ref": ref,
                "source_state": source_state,
                "commit": commit,
                "hook_sha256": file_sha256(hook),
                "validator_sha256": file_sha256(validator),
                "runtime_python_surface": source_metrics(runtime_paths),
                "cases_passed": sum(1 for case in case_results if case["passed"]),
                "cases_total": len(case_results),
                "cases": case_results,
                "performance": performance,
            })
    report = {
        "schema_version": 2,
        "manifest": args.manifest.as_posix(),
        "versions": results,
        "historical_harness_code_identical": (
            results[0]["hook_sha256"] == results[1]["hook_sha256"]
            and results[0]["validator_sha256"] == results[1]["validator_sha256"]
        ),
    }
    output = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
