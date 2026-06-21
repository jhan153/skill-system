#!/usr/bin/env python3
"""Codex lifecycle hook adapter for Skill-System execution assurance."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit


ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / ".codex" / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from hook_runtime import event_hash, utc_now  # noqa: E402
from _validation import load_yaml_file  # noqa: E402


EVENT_MAP = {
    "UserPromptSubmit": "request_received",
    "SessionStart": "context_loaded",
    "PreToolUse": "tool_preflight",
    "PermissionRequest": "permission_requested",
    "PostToolUse": "tool_result",
    "Stop": "turn_finalize",
    "PreCompact": "compact_before",
    "PostCompact": "compact_after",
}
SUPPORTED_HOOK_EVENTS = set(EVENT_MAP)
MAX_TEXT = 1200
STRICT_GATE = "strict"
SENSITIVE_PATTERN = re.compile(
    r"(?i)(api[_-]?key|authorization|bearer|cookie|password|passwd|secret|token|client[_-]?secret|database[_-]?url)"
)
SECRET_VALUE_PATTERN = re.compile(r"(?i)(sk-[A-Za-z0-9_-]{12,}|[A-Za-z0-9_./+-]{24,})")
EXIT_CODE_PATTERN = re.compile(r"(?i)(?:exit(?:ed)?(?:\s+with)?\s+code|exit_code|returncode|status)\D{0,20}(-?\d+)")


def sanitize_id(value: object, fallback: str) -> str:
    raw = str(value or fallback)
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "-", raw).strip(".-")
    return safe[:80] or fallback


def truncate(value: str, limit: int = MAX_TEXT) -> str:
    if len(value) <= limit:
        return value
    return value[:limit] + f"...<truncated {len(value) - limit} chars>"


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def redact_text(value: str) -> str:
    redacted = SECRET_VALUE_PATTERN.sub("<redacted>", value)
    if SENSITIVE_PATTERN.search(redacted):
        return "<redacted-sensitive>"
    return truncate(redacted)


def verbose_capture_enabled() -> bool:
    return os.environ.get("SKILL_SYSTEM_HOOK_CAPTURE_VERBOSE") == "1"


def stable_json(value: Any) -> str:
    try:
        return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    except TypeError:
        return json.dumps(str(value), ensure_ascii=True)


def safe_path(value: object) -> str:
    raw = str(value or "")
    if not raw:
        return ""
    path = Path(raw).expanduser()
    if path.is_absolute():
        try:
            return path.resolve().relative_to(ROOT).as_posix()
        except ValueError:
            return "<external-path>"
    return redact_text(raw)


def safe_url(value: object) -> str:
    raw = str(value or "")
    if not raw:
        return ""
    redacted = SECRET_VALUE_PATTERN.sub("<redacted>", raw)
    try:
        parsed = urlsplit(redacted)
    except ValueError:
        return redact_text(redacted)
    if not parsed.scheme or not parsed.netloc:
        return redact_text(redacted)
    query = "<redacted-query>" if parsed.query else ""
    fragment = "<redacted-fragment>" if parsed.fragment else ""
    path = redact_text(parsed.path) if parsed.path else ""
    return urlunsplit((parsed.scheme, parsed.netloc, path, query, fragment))


def extract_exit_code(value: object) -> int | None:
    if isinstance(value, dict):
        exit_code = value.get("exit_code")
        return exit_code if isinstance(exit_code, int) else None
    if isinstance(value, str):
        match = EXIT_CODE_PATTERN.search(value)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return None
    return None


def summarize_tool_input(data: dict[str, Any]) -> dict[str, Any]:
    tool_input = data.get("tool_input")
    summary: dict[str, Any] = {}
    if isinstance(tool_input, dict):
        command = tool_input.get("command")
        if isinstance(command, str):
            summary["command_hash"] = sha256_text(command)
            summary["command_category"] = command.strip().split(maxsplit=1)[0] if command.strip() else ""
            if verbose_capture_enabled():
                summary["command_preview"] = redact_text(command)
        else:
            raw = stable_json(tool_input)
            summary["args_hash"] = sha256_text(raw)
            if verbose_capture_enabled():
                summary["args_preview"] = redact_text(raw)
    elif tool_input is not None:
        raw = stable_json(tool_input)
        summary["args_hash"] = sha256_text(raw)
        if verbose_capture_enabled():
            summary["args_preview"] = redact_text(raw)
    return summary


def summarize_tool_response(data: dict[str, Any]) -> dict[str, Any]:
    response = data.get("tool_response")
    if response is None:
        return {}
    if not isinstance(response, dict):
        raw = stable_json(response)
        result: dict[str, Any] = {"response_hash": sha256_text(raw), "output_truncated": len(raw) > MAX_TEXT}
        exit_code = extract_exit_code(response)
        if exit_code is not None:
            result["exit_code"] = exit_code
            result["success"] = exit_code == 0
        if verbose_capture_enabled():
            result["response_preview"] = redact_text(str(response))
        return {"tool_result": result}
    result: dict[str, Any] = {"output_truncated": len(stable_json(response)) > MAX_TEXT}
    exit_code = extract_exit_code(response)
    if exit_code is not None:
        result["exit_code"] = exit_code
    success = response.get("success")
    if isinstance(success, bool):
        result["success"] = success
    elif exit_code is not None:
        result["success"] = exit_code == 0
    changed_files = response.get("changed_files")
    if isinstance(changed_files, list):
        result["changed_files"] = [safe_path(item) for item in changed_files]
    network_targets = response.get("network_targets")
    if isinstance(network_targets, list):
        result["network_targets"] = [safe_url(item) for item in network_targets]
    stderr = response.get("stderr")
    if isinstance(stderr, str) and stderr:
        result["stderr_hash"] = sha256_text(stderr)
        if verbose_capture_enabled():
            result["stderr_preview"] = redact_text(stderr)
    stdout = response.get("stdout")
    if isinstance(stdout, str) and stdout:
        result["stdout_hash"] = sha256_text(stdout)
        if verbose_capture_enabled():
            result["stdout_preview"] = redact_text(stdout)
    return {"tool_result": result}


def classify_status(data: dict[str, Any]) -> str:
    hook_event = str(data.get("hook_event_name") or "")
    response = data.get("tool_response")
    if hook_event == "PostToolUse":
        exit_code = extract_exit_code(response)
        if exit_code is not None:
            return "pass" if exit_code == 0 else "fail"
        if isinstance(response, dict):
            if response.get("success") is True:
                return "pass"
            if response.get("success") is False or response.get("error"):
                return "fail"
            if response.get("stderr"):
                return "warn"
        return "warn"
    if hook_event == "PermissionRequest" and str(data.get("decision", "")).lower() in {"deny", "denied"}:
        return "fail"
    return "pass"


def current_run_dir(args: argparse.Namespace, data: dict[str, Any]) -> Path | None:
    if args.run_dir is not None:
        return args.run_dir
    session_id = data.get("session_id")
    turn_id = data.get("turn_id")
    if not session_id or not turn_id:
        return None
    return ROOT / ".codex" / "harness" / "agent-runs" / sanitize_id(session_id, "unknown-session") / sanitize_id(turn_id, "unknown-turn")


def hook_ledger_path(args: argparse.Namespace, data: dict[str, Any]) -> Path:
    if args.ledger is not None:
        return args.ledger
    run_dir = current_run_dir(args, data)
    if run_dir is not None and (run_dir / "run.yaml").exists():
        return run_dir / "hook-events.jsonl"
    from hook_runtime import default_ledger  # noqa: PLC0415

    return default_ledger()


def read_input(args: argparse.Namespace) -> dict[str, Any]:
    if args.input_file:
        raw = args.input_file.read_text(encoding="utf-8")
    else:
        raw = sys.stdin.read()
    if not raw.strip():
        return {}
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("hook input must be a JSON object")
    return data


def support_level_for(data: dict[str, Any], neutral_event: str) -> str:
    if neutral_event == "permission_requested" and not data.get("tool_use_id"):
        return "approximate"
    hook_event = str(data.get("hook_event_name") or "")
    return "native" if hook_event in SUPPORTED_HOOK_EVENTS else "unsupported"


def record_event(
    args: argparse.Namespace,
    data: dict[str, Any],
    status: str,
    extra: dict[str, Any] | None = None,
    neutral_event_override: str | None = None,
) -> None:
    hook_event = data.get("hook_event_name", "")
    neutral_event = neutral_event_override or EVENT_MAP.get(str(hook_event), "turn_finalize")
    evidence: dict[str, Any] = {
        "session_id": data.get("session_id"),
        "turn_id": data.get("turn_id"),
        "cwd": safe_path(data.get("cwd")),
        "permission_mode": data.get("permission_mode"),
        "tool_name": data.get("tool_name"),
        "tool_use_id": data.get("tool_use_id"),
    }
    evidence.update(summarize_tool_input(data))
    evidence.update(summarize_tool_response(data))
    if isinstance(extra, dict):
        evidence.update(extra)
    payload = {
        "schema_version": 1,
        "recorded_at": utc_now(),
        "neutral_event": neutral_event,
        "host": "codex",
        "host_event": hook_event or "unknown",
        "support_level": support_level_for(data, neutral_event),
        "tool_id": str(data.get("tool_name") or ""),
        "session_id": data.get("session_id") or "",
        "turn_id": data.get("turn_id") or "",
        "tool_use_id": data.get("tool_use_id") or "",
        "status": status,
        "evidence": evidence,
    }
    payload["event_hash"] = event_hash(payload)
    ledger = hook_ledger_path(args, data)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    try:
        ledger.parent.chmod(0o700)
    except OSError:
        pass
    with ledger.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True, ensure_ascii=True) + "\n")
    try:
        ledger.chmod(0o600)
    except OSError:
        pass


def validate_last_assistant_message(run_dir: Path, data: dict[str, Any]) -> tuple[int, str]:
    manifest_path = run_dir / "run.yaml"
    try:
        manifest = load_yaml_file(manifest_path)
    except Exception as exc:  # noqa: BLE001
        return 1, f"FAIL: current run manifest is not readable for assistant message validation: {exc}"
    if not isinstance(manifest, dict):
        return 1, "FAIL: current run manifest is not an object."
    expected = manifest.get("assistant_message")
    if not isinstance(expected, dict):
        return 1, "FAIL: run manifest does not declare assistant_message binding."
    message = data.get("last_assistant_message")
    if not isinstance(message, str) or not message:
        return 1, "FAIL: Stop input did not include last_assistant_message for current run binding."
    actual_hash = sha256_text(message)
    if actual_hash != expected.get("sha256"):
        return 1, "FAIL: last_assistant_message sha256 does not match run manifest assistant_message.sha256."
    result_label = expected.get("result_label")
    if isinstance(result_label, str) and result_label not in message:
        return 1, f"FAIL: last_assistant_message does not mention result_label {result_label!r}."
    for claim_id in expected.get("claim_ids", []) or []:
        if isinstance(claim_id, str) and claim_id not in message:
            return 1, f"FAIL: last_assistant_message does not mention claim_id {claim_id}."
    return 0, "PASS: last_assistant_message matches run manifest assistant_message binding."


def run_agent_output_validation(args: argparse.Namespace, data: dict[str, Any]) -> tuple[int, str]:
    run_dir = current_run_dir(args, data)
    if run_dir is None:
        return 4, "UNVERIFIED: hook input did not include session_id and turn_id for current run binding."
    if not (run_dir / "run.yaml").exists():
        return 4, f"UNVERIFIED: current run manifest not found: {run_dir / 'run.yaml'}"
    cmd = [
        sys.executable,
        str(ROOT / ".codex" / "tools" / "validate_agent_run_artifact.py"),
        str(run_dir),
        "--schema",
        str(ROOT / ".codex" / "schemas" / "harness" / "agent-run.schema.json"),
    ]
    completed = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=20,
    )
    output = "\n".join(part for part in [completed.stdout.strip(), completed.stderr.strip()] if part)
    if completed.returncode != 0:
        return completed.returncode, truncate(output, 2000)
    message_code, message_output = validate_last_assistant_message(run_dir, data)
    combined = "\n".join(part for part in [output, message_output] if part)
    return message_code, truncate(combined, 2000)


def strict_gate_enabled(data: dict[str, Any]) -> bool:
    configured = data.get("skill_system_agent_output_gate") or os.environ.get("SKILL_SYSTEM_AGENT_OUTPUT_GATE", "")
    return str(configured).lower() == STRICT_GATE


def stop_output(data: dict[str, Any], validation_code: int, validation_output: str) -> dict[str, Any]:
    if validation_code == 0:
        return {
            "continue": True,
            "systemMessage": "Agent output validation passed.",
        }
    if validation_code == 4 and not strict_gate_enabled(data):
        return {
            "continue": True,
            "systemMessage": validation_output,
        }
    reason = "Agent output validation failed before final response. Fix the run artifact evidence and rerun validation."
    return {
        "decision": "block",
        "reason": f"{reason}\n\n{validation_output}",
    }


def handle(args: argparse.Namespace) -> int:
    try:
        data = read_input(args)
    except Exception as exc:  # noqa: BLE001
        print(f"hook input error: {exc}", file=sys.stderr)
        return 2
    hook_event = str(data.get("hook_event_name") or "")
    if hook_event == "Stop":
        validation_code, validation_output = run_agent_output_validation(args, data)
        status = "pass" if validation_code == 0 else "warn" if validation_code == 4 else "fail"
        neutral_event = "turn_finalize" if validation_code == 0 else "turn_finalize_attempt"
        record_event(args, data, status, {"agent_output_validation": validation_output}, neutral_event)
        print(json.dumps(stop_output(data, validation_code, validation_output), sort_keys=True))
        return 0
    record_event(args, data, classify_status(data))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path)
    parser.add_argument("--run-dir", type=Path)
    parser.add_argument("--input-file", type=Path)
    args = parser.parse_args()
    try:
        return handle(args)
    except BrokenPipeError:
        return 1
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
