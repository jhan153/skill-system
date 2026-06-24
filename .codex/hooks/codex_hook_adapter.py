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


sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / ".codex" / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from hook_runtime import add_chain_fields, utc_now, write_event  # noqa: E402


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
BLOCKING_VALIDATION_PATTERNS = (
    "agent-verified result has nonzero command validation",
    "agent-verified result has failed hook event",
    "assistant_message.sha256 does not match",
    "last_assistant_message sha256 does not match",
    "evidence file not found",
    "evidence path is not run-relative",
)
SENSITIVE_PATTERN = re.compile(
    r"(?i)(api[_-]?key|authorization|bearer|cookie|password|passwd|secret|token|client[_-]?secret|database[_-]?url)"
)
SECRET_VALUE_PATTERN = re.compile(r"(?i)(sk-[A-Za-z0-9_-]{12,}|[A-Za-z0-9_./+-]{24,})")
EXIT_CODE_PATTERN = re.compile(r"(?i)(?:exit(?:ed)?(?:\s+with)?\s+code|exit_code|returncode|status)\D{0,20}(-?\d+)")
KANBOARD_POST_SESSION_MODES = {"dry-run", "apply"}
DESKTOP_NOTIFY_DISABLED = {"0", "false", "off", "no", "none", "disabled"}
DESKTOP_NOTIFY_DRY_RUN = {"dry-run", "dry_run", "test"}


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


def desktop_notify_setting(data: dict[str, Any]) -> str:
    value = data.get("skill_system_desktop_notify")
    if value is None:
        value = os.environ.get("SKILL_SYSTEM_DESKTOP_NOTIFY", "")
    return str(value).strip().lower()


def desktop_notify_enabled(data: dict[str, Any]) -> bool:
    return desktop_notify_setting(data) not in DESKTOP_NOTIFY_DISABLED


def desktop_notify_dry_run(data: dict[str, Any]) -> bool:
    return desktop_notify_setting(data) in DESKTOP_NOTIFY_DRY_RUN


def load_codex_config() -> dict[str, Any]:
    path = Path.home() / ".codex" / "config.toml"
    try:
        import tomllib  # noqa: PLC0415
    except ModuleNotFoundError:
        return {}
    try:
        with path.open("rb") as handle:
            value = tomllib.load(handle)
    except Exception:  # noqa: BLE001 - notification labels are best-effort only.
        return {}
    return value if isinstance(value, dict) else {}


def current_codex_effort(data: dict[str, Any]) -> str:
    for key in ("model_reasoning_effort", "reasoning_effort", "effort_level"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return truncate(redact_text(value.strip()), 12)
    for key in ("CODEX_MODEL_REASONING_EFFORT", "CODEX_EFFORT_LEVEL", "MODEL_REASONING_EFFORT"):
        value = os.environ.get(key)
        if value and value.strip():
            return truncate(redact_text(value.strip()), 12)
    config = load_codex_config()
    value = config.get("model_reasoning_effort")
    return truncate(redact_text(value.strip()), 12) if isinstance(value, str) and value.strip() else ""


def current_codex_model(data: dict[str, Any]) -> str:
    for key in ("model", "model_name", "model_id"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    for key in ("CODEX_MODEL", "OPENAI_MODEL", "MODEL"):
        value = os.environ.get(key)
        if value and value.strip():
            return value.strip()
    config = load_codex_config()
    value = config.get("model")
    return value.strip() if isinstance(value, str) and value.strip() else ""


def short_codex_model(model: str, effort: str = "") -> str:
    text = str(model or "").strip().lower()
    text = text.removesuffix("-codex")
    if text.startswith("gpt-"):
        label = "gpt" + text[len("gpt-") :]
    else:
        label = text.replace("-codex", "")
    label = re.sub(r"[^a-z0-9.]+", "-", label).strip("-")
    if effort:
        label = f"{label}-{effort}" if label else effort
    return truncate(redact_text(label), 24)


def notify_model_label(data: dict[str, Any]) -> str:
    return short_codex_model(current_codex_model(data), current_codex_effort(data))


# Backward-compatible aliases.
def permission_notification_enabled(data: dict[str, Any]) -> bool:
    return desktop_notify_enabled(data)


def permission_notification_dry_run(data: dict[str, Any]) -> bool:
    return desktop_notify_dry_run(data)


def run_desktop_notify(
    data: dict[str, Any],
    *,
    event: str,
    title: str,
    message: str,
    topic: str = "",
    app: str = "codex",
) -> dict[str, Any]:
    """Best-effort desktop notification. Never raises; never blocks the hook."""
    if not desktop_notify_enabled(data):
        return {"status": "disabled", "event": event}
    cmd = [
        sys.executable,
        str(ROOT / ".codex" / "tools" / "notify_desktop.py"),
        "--event",
        event,
        "--title",
        title,
        "--message",
        message,
        "--mode",
        "overlay",
        "--app",
        app,
    ]
    if topic:
        cmd += ["--topic", topic]
    model = notify_model_label(data)
    if model:
        cmd.append(f"--model={model}")
    session = notify_label(data)
    if session:
        cmd.append(f"--session={session}")
    if desktop_notify_dry_run(data):
        cmd.append("--dry-run")
    try:
        completed = subprocess.run(
            cmd,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=8,
        )
    except Exception as exc:  # noqa: BLE001 - notification must not block hook recording.
        return {"status": "error", "event": event, "reason": truncate(str(exc), 500)}
    output = "\n".join(part for part in [completed.stdout.strip(), completed.stderr.strip()] if part)
    if completed.returncode != 0:
        return {"status": "error", "event": event, "returncode": completed.returncode, "reason": truncate(output, 500)}
    try:
        report = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {"status": "error", "event": event, "reason": "notify_desktop returned non-JSON output"}
    if not isinstance(report, dict):
        return {"status": "error", "event": event, "reason": "notify_desktop returned non-object JSON"}
    return report


def notify_label(data: dict[str, Any]) -> str:
    """Short, redaction-safe context label (task subject / plan / workspace)."""
    for key in ("task_subject", "plan_name", "compact_summary"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return truncate(redact_text(value), 80)
    cwd = data.get("cwd")
    if isinstance(cwd, str) and cwd.strip():
        return Path(cwd).name
    return ""


def first_meaningful_line(value: object, limit: int) -> str:
    if not isinstance(value, str):
        return ""
    for line in value.splitlines():
        text = line.strip()
        if not text or text in {"```", "---"}:
            continue
        if text.startswith("```"):
            continue
        return truncate(redact_text(text), limit)
    return ""


def notify_completion_message(data: dict[str, Any]) -> str:
    summary = first_meaningful_line(data.get("last_assistant_message"), 150)
    label = notify_label(data)
    if summary and label and label not in summary:
        return truncate(f"{summary} - {label}", 220)
    return summary or label or "turn complete"


def notify_permission_request(data: dict[str, Any]) -> dict[str, Any]:
    tool_name = str(data.get("tool_name") or "A tool")
    cwd = safe_path(data.get("cwd"))
    location = f" in {cwd}" if cwd else ""
    return run_desktop_notify(
        data,
        event="approval-requested",
        topic="approval",
        title="Codex approval requested",
        message=f"{tool_name} is waiting for approval{location}.",
    )


LOOP_ACTION_TOPIC = {
    "success": "done",
    "recover": "error",
    "blocked": "input",
    "budget_exhausted": "error",
    "continue": "progress",
}


def notify_loop_iteration(data: dict[str, Any], loop_evaluation: dict[str, Any]) -> dict[str, Any]:
    """Fire one desktop notification per loop iteration (each Stop with an active LoopRun)."""
    if loop_evaluation.get("status") != "PASS":
        return run_desktop_notify(
            data,
            event="loop-iteration",
            topic="error",
            title="Codex loop",
            message=f"loop evaluation unavailable: {truncate(str(loop_evaluation.get('reason', 'unknown')), 120)}",
        )
    decision = loop_evaluation.get("decision") if isinstance(loop_evaluation.get("decision"), dict) else {}
    action = str(decision.get("action") or "?")
    reason = str(decision.get("reason_code") or "")
    loop_id = str(loop_evaluation.get("loop_run_id") or "loop")
    label = notify_label(data)
    label_text = f" - {label}" if label else ""
    return run_desktop_notify(
        data,
        event="loop-iteration",
        topic=LOOP_ACTION_TOPIC.get(action, "progress"),
        title=f"Codex loop {loop_id}",
        message=f"{action}: {reason}{label_text}",
    )


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


def load_run_manifest(path: Path) -> Any:
    try:
        from _validation import load_yaml_file  # noqa: PLC0415
    except SystemExit as exc:
        raise RuntimeError(str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"manifest loader unavailable: {exc}") from exc
    return load_yaml_file(path)


def run_id_for_event(args: argparse.Namespace, data: dict[str, Any]) -> str:
    run_dir = current_run_dir(args, data)
    if run_dir is not None and (run_dir / "run.yaml").exists():
        try:
            manifest = load_run_manifest(run_dir / "run.yaml")
        except Exception:  # noqa: BLE001 - fallback below preserves recording.
            manifest = {}
        if isinstance(manifest, dict) and isinstance(manifest.get("run_id"), str):
            return manifest["run_id"]
    if isinstance(data.get("run_id"), str):
        return data["run_id"]
    session_id = sanitize_id(data.get("session_id"), "unknown-session")
    turn_id = sanitize_id(data.get("turn_id"), "unknown-turn")
    return f"{session_id}:{turn_id}"


def run_dir_has_passing_turn_finalize(run_dir: Path) -> bool:
    manifest_path = run_dir / "run.yaml"
    try:
        manifest = load_run_manifest(manifest_path)
    except Exception:  # noqa: BLE001
        return False
    if not isinstance(manifest, dict) or not isinstance(manifest.get("hook_events"), str):
        return False
    ledger = run_dir / manifest["hook_events"]
    if not ledger.exists():
        return False
    for line in ledger.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if (
            isinstance(event, dict)
            and event.get("neutral_event") == "turn_finalize"
            and event.get("status") == "pass"
        ):
            return True
    return False


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


def build_event_payload(
    args: argparse.Namespace,
    data: dict[str, Any],
    status: str,
    extra: dict[str, Any] | None = None,
    neutral_event_override: str | None = None,
) -> dict[str, Any]:
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
    return payload


def record_event(
    args: argparse.Namespace,
    data: dict[str, Any],
    status: str,
    extra: dict[str, Any] | None = None,
    neutral_event_override: str | None = None,
) -> dict[str, Any]:
    payload = build_event_payload(args, data, status, extra, neutral_event_override)
    ledger = hook_ledger_path(args, data)
    try:
        ledger.parent.mkdir(parents=True, exist_ok=True)
        ledger.parent.chmod(0o700)
    except OSError:
        pass
    write_event(payload, ledger, run_id_for_event(args, data))
    try:
        ledger.chmod(0o600)
    except OSError:
        pass
    return payload


def candidate_event(
    args: argparse.Namespace,
    data: dict[str, Any],
    status: str,
    extra: dict[str, Any] | None = None,
    neutral_event_override: str | None = None,
) -> dict[str, Any]:
    payload = build_event_payload(args, data, status, extra, neutral_event_override)
    ledger = hook_ledger_path(args, data)
    return add_chain_fields(payload, ledger, run_id_for_event(args, data))


def validate_last_assistant_message(run_dir: Path, data: dict[str, Any]) -> tuple[int, str]:
    manifest_path = run_dir / "run.yaml"
    try:
        manifest = load_run_manifest(manifest_path)
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


def run_agent_output_validation(
    args: argparse.Namespace,
    data: dict[str, Any],
    phase: str,
    candidate_final_event: dict[str, Any] | None = None,
) -> tuple[int, str]:
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
        "--context-pack-schema",
        str(ROOT / ".codex" / "schemas" / "knowledge" / "context-pack.schema.json"),
        "--phase",
        phase,
    ]
    if candidate_final_event is not None:
        cmd.extend(["--candidate-final-event", json.dumps(candidate_final_event, sort_keys=True)])
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


def has_blocking_validation_failure(validation_output: str) -> bool:
    return any(pattern in validation_output for pattern in BLOCKING_VALIDATION_PATTERNS)


def stop_output(data: dict[str, Any], validation_code: int, validation_output: str) -> dict[str, Any]:
    if validation_code == 0:
        return {
            "continue": True,
            "systemMessage": "Agent output validation passed.",
        }
    observation = (
        "Agent output validation recorded a non-blocking observation. "
        "Do not repair repository-wide metadata, plans, or eval fixtures because of this Stop hook result.\n\n"
        f"{validation_output}"
    )
    if not strict_gate_enabled(data):
        return {
            "continue": True,
            "systemMessage": observation,
        }
    if validation_code == 4 or not has_blocking_validation_failure(validation_output):
        return {
            "continue": True,
            "systemMessage": observation,
        }
    reason = "Agent output validation found a strict-mode blocking contradiction in current-turn evidence."
    return {
        "decision": "block",
        "reason": f"{reason}\n\n{validation_output}",
    }


def _env_list(name: str) -> list[str]:
    raw = os.environ.get(name, "")
    return [item.strip() for item in raw.split(",") if item.strip()]


def _kanboard_task_reference_from_env() -> str | None:
    reference = os.environ.get("KANBOARD_PLAN_TASK_REFERENCE")
    if reference:
        return reference.strip()
    plan_id = os.environ.get("KANBOARD_PLAN_ID")
    task_key = os.environ.get("KANBOARD_PLAN_TASK_KEY")
    if plan_id and task_key:
        return f"{plan_id.strip()}:{task_key.strip()}"
    return None


def _load_kanboard_run_tool():
    candidates = [
        ROOT / "integrations" / "kanboard-plan-sync" / "src",
        Path.home() / ".ai" / "infra" / "kanboard-plan-sync" / "src",
    ]
    for candidate in candidates:
        if candidate.is_dir() and str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))
    from kanboard_plan_sync_mcp.tools import run_tool  # noqa: PLC0415

    return run_tool


def maybe_record_kanboard_post_session(
    data: dict[str, Any], validation_code: int, loop_context: dict[str, Any] | None = None
) -> dict[str, Any] | None:
    """Optionally reflect the completed session on a mapped Kanboard task.

    Disabled by default. Set ``KANBOARD_PLAN_POST_SESSION=dry-run`` or
    ``apply`` and provide ``KANBOARD_PLAN_TASK_REFERENCE`` (or plan id + task
    key). The hook never guesses the task from conversation text.
    """
    mode = os.environ.get("KANBOARD_PLAN_POST_SESSION", "").strip().lower()
    if not mode:
        return None
    if mode not in KANBOARD_POST_SESSION_MODES:
        return {"status": "skipped", "reason": "invalid KANBOARD_PLAN_POST_SESSION mode"}

    reference = _kanboard_task_reference_from_env()
    if not reference:
        return {
            "status": "needs_task_reference",
            "reason": "set KANBOARD_PLAN_TASK_REFERENCE or KANBOARD_PLAN_ID + KANBOARD_PLAN_TASK_KEY",
        }
    if mode == "apply" and validation_code != 0 and os.environ.get("KANBOARD_PLAN_POST_SESSION_ALLOW_UNVERIFIED") != "1":
        return {
            "status": "skipped_unverified",
            "task_reference": reference,
            "reason": "agent output validation did not pass; set KANBOARD_PLAN_POST_SESSION_ALLOW_UNVERIFIED=1 to override",
        }

    message = data.get("last_assistant_message")
    if not isinstance(message, str) or not message.strip():
        return {
            "status": "unverified",
            "task_reference": reference,
            "reason": "Stop hook input did not include last_assistant_message",
        }

    workspace = os.environ.get("KANBOARD_PLAN_WORKSPACE") or data.get("cwd")
    session_summary = redact_text(message)
    if loop_context:
        session_summary = (
            f"{session_summary}\n[loop {loop_context.get('loop_run_id')} -> "
            f"{loop_context.get('action')}/{loop_context.get('reason_code')}]"
        )
    args: dict[str, Any] = {
        "task_reference": reference,
        "session_summary": session_summary,
        "result_label": os.environ.get("KANBOARD_PLAN_RESULT_LABEL")
        or ("agent-verified" if validation_code == 0 else "unverified"),
        "validation_evidence": os.environ.get("KANBOARD_PLAN_VALIDATION_EVIDENCE") or None,
        "changed_files": _env_list("KANBOARD_PLAN_CHANGED_FILES"),
        "dry_run": mode != "apply",
    }
    if workspace:
        args["workspace"] = str(workspace)
    try:
        result = _load_kanboard_run_tool()("record_session_update", args)
    except Exception as exc:  # noqa: BLE001 - hook must stay non-blocking.
        return {
            "status": "error",
            "task_reference": reference,
            "mode": mode,
            "reason": truncate(str(exc), 500),
        }
    return {
        "status": result.get("status"),
        "applied": result.get("applied"),
        "mode": mode,
        "task_reference": reference,
        "tool": result.get("tool"),
    }


KANBOARD_AUTOSYNC_DISABLED = {"0", "false", "off", "no", "none", "disabled"}


def maybe_autosync_kanboard(data: dict[str, Any]) -> dict[str, Any] | None:
    """On session start, sync the ACTIVE workspace's plan(s) to its Kanboard board.

    Scoped to the current workspace (cwd) only — not every registered board. A
    cwd that is not a registered workspace, or an unreachable Kanboard, degrades
    to a no-op. Enabled by default; set KANBOARD_PLAN_AUTOSYNC to off/dry-run to
    disable or soften. Non-blocking.
    """
    mode = os.environ.get("KANBOARD_PLAN_AUTOSYNC", "apply").strip().lower()
    if mode in KANBOARD_AUTOSYNC_DISABLED:
        return None
    workspace = os.environ.get("KANBOARD_PLAN_WORKSPACE") or data.get("cwd")
    if not isinstance(workspace, str) or not workspace.strip():
        return None
    try:
        result = _load_kanboard_run_tool()(
            "sync_all", {"apply": mode == "apply", "workspace": str(workspace)}
        )
    except Exception as exc:  # noqa: BLE001 - hook must stay non-blocking.
        return {"status": "error", "workspace": str(workspace), "reason": truncate(str(exc), 500)}
    return {
        "status": "ok",
        "mode": mode,
        "workspace": str(workspace),
        "totals": result.get("totals") if isinstance(result, dict) else None,
    }


def _active_loops_dir() -> Path:
    # Mirror of loop_policy.active_loops_dir(); inlined so the hook never has to
    # import yaml-bearing tool modules (it must stay import-robust).
    base = os.environ.get("CODEX_HOME") or str(Path.home() / ".codex")
    return Path(base).expanduser() / "harness" / "active-loops"


def _session_pointer_loop_dir(session_id: str) -> Path | None:
    safe = "".join(ch if ch.isalnum() or ch in "._-" else "-" for ch in session_id).strip(".-")[:96] or "unknown-session"
    pointer = _active_loops_dir() / f"{safe}.json"
    if not pointer.is_file():
        return None
    try:
        info = json.loads(pointer.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(info, dict) or info.get("status") != "active":
        return None
    loop_dir = info.get("loop_run_dir")
    if isinstance(loop_dir, str) and loop_dir.strip():
        return Path(loop_dir).expanduser()
    return None


def active_loop_run_dir(data: dict[str, Any]) -> Path | None:
    # 1) explicit override (custom Stop field), 2) parent env var,
    # 3) session-scoped activation pointer keyed by session_id (the bridge).
    raw = data.get("skill_system_loop_run_dir") or os.environ.get("SKILL_SYSTEM_LOOP_RUN_DIR")
    if isinstance(raw, str) and raw.strip():
        return Path(raw).expanduser()
    session_id = data.get("session_id")
    if isinstance(session_id, str) and session_id.strip():
        return _session_pointer_loop_dir(session_id)
    return None


TERMINAL_LOOP_ACTIONS = {"success", "blocked", "budget_exhausted", "unsafe", "fatal", "stalled"}


def _deactivate_session_pointer(session_id: str, expected_loop_dir: Any, final_action: str) -> dict[str, Any] | None:
    """Close the session->LoopRun pointer once its loop reaches a terminal state.

    Closes only if the pointer still points at the loop we just finalized, so an
    unrelated loop newly activated in the same session is not clobbered. Without
    this, a finished LoopRun stays bound to the session and every later unrelated
    Stop keeps re-evaluating it. The file is kept (status=terminal) for audit.
    """
    if not isinstance(session_id, str) or not session_id.strip():
        return None
    safe = "".join(ch if ch.isalnum() or ch in "._-" else "-" for ch in session_id).strip(".-")[:96] or "unknown-session"
    pointer = _active_loops_dir() / f"{safe}.json"
    if not pointer.is_file():
        return None
    try:
        info = json.loads(pointer.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(info, dict) or info.get("status") != "active":
        return None
    if isinstance(expected_loop_dir, str) and expected_loop_dir and isinstance(info.get("loop_run_dir"), str):
        if str(Path(info["loop_run_dir"]).expanduser()) != str(Path(expected_loop_dir).expanduser()):
            return None  # a different loop is active for this session; leave it
    info["status"] = "terminal"
    info["final_action"] = final_action
    info["deactivated_at"] = utc_now()
    try:
        pointer.write_text(json.dumps(info, sort_keys=True) + "\n", encoding="utf-8")
    except OSError:
        return None
    return {"deactivated": True, "final_action": final_action}


def maybe_evaluate_active_loop(data: dict[str, Any], validation_code: int) -> dict[str, Any] | None:
    loop_dir = active_loop_run_dir(data)
    if loop_dir is None:
        return None
    # Decoupled from strict generic validation: an explicitly-activated LoopRun is
    # evaluated on a clean turn (0) or an UNVERIFIED generic manifest (4). Only a
    # hard validation failure (other codes) skips loop drive.
    if validation_code not in (0, 4):
        return None
    cmd = [
        sys.executable,
        str(ROOT / ".codex" / "tools" / "evaluate_loop_run.py"),
        str(loop_dir),
    ]
    # Observe mode never requests a continuation, so it must not consume the
    # stop-continuation budget; only blocking mode records a continuation.
    if loop_continuation_blocking(data):
        cmd.append("--record-stop-continuation")
    cmd += ["--format", "json"]
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
        return {
            "status": "error",
            "loop_run_dir": str(loop_dir),
            "reason": truncate(output or f"evaluate_loop_run exited {completed.returncode}", 1000),
        }
    try:
        report = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {
            "status": "error",
            "loop_run_dir": str(loop_dir),
            "reason": "evaluate_loop_run did not return JSON",
        }
    if not isinstance(report, dict):
        return {
            "status": "error",
            "loop_run_dir": str(loop_dir),
            "reason": "evaluate_loop_run returned non-object JSON",
        }
    report["loop_run_dir"] = str(loop_dir)
    return report


def loop_continuation_blocking(data: dict[str, Any]) -> bool:
    """Whether an active LoopRun may block the Stop turn to force continuation.

    Blocking is the default for active loops (that is how a bounded loop drives
    its next iteration), but it can be downgraded to observational — unifying it
    with the base observational-by-default Stop policy — via
    SKILL_SYSTEM_LOOP_CONTINUATION=observe (also: off/false/0). This is the loop
    kill switch.
    """
    configured = data.get("skill_system_loop_continuation") or os.environ.get("SKILL_SYSTEM_LOOP_CONTINUATION", "")
    return str(configured).lower() not in {"observe", "off", "false", "0"}


def loop_stop_output(loop_evaluation: dict[str, Any], data: dict[str, Any]) -> dict[str, Any] | None:
    if loop_evaluation.get("status") != "PASS":
        return {
            "continue": True,
            "systemMessage": f"Loop evaluation unavailable: {loop_evaluation.get('reason', 'unknown error')}",
        }
    decision = loop_evaluation.get("decision")
    if not isinstance(decision, dict):
        return None
    action = decision.get("action")
    reason_code = decision.get("reason_code")
    prompt = decision.get("continuation_prompt")
    if action in {"continue", "recover"} and isinstance(prompt, str) and prompt:
        if loop_continuation_blocking(data):
            return {
                "decision": "block",
                "reason": prompt,
            }
        return {
            "continue": True,
            "systemMessage": f"Loop continuation (observational): {prompt}",
        }
    return {
        "continue": True,
        "systemMessage": f"Loop evaluation {action}: {reason_code}",
    }


def handle(args: argparse.Namespace) -> int:
    try:
        data = read_input(args)
    except Exception as exc:  # noqa: BLE001
        print(f"hook input error: {exc}", file=sys.stderr)
        return 2
    hook_event = str(data.get("hook_event_name") or "")
    if hook_event == "Stop":
        validation_code, validation_output = run_agent_output_validation(args, data, "pre-finalize")
        status = "pass" if validation_code == 0 else "warn" if validation_code == 4 else "fail"
        record_event(args, data, status, {"agent_output_validation": validation_output}, "turn_finalize_attempt")
        finalize_extra: dict[str, Any] = {"agent_output_validation": validation_output}
        if validation_code == 0:
            run_dir = current_run_dir(args, data)
            final_candidate = (
                None
                if run_dir is not None and run_dir_has_passing_turn_finalize(run_dir)
                else candidate_event(args, data, "pass", finalize_extra, "turn_finalize")
            )
            post_code, post_output = run_agent_output_validation(
                args,
                data,
                "post-finalize",
                candidate_final_event=final_candidate,
            )
            if post_code != 0:
                validation_code = post_code
                validation_output = post_output
                finalize_extra["agent_output_validation"] = validation_output
        loop_evaluation = maybe_evaluate_active_loop(data, validation_code)
        loop_context: dict[str, Any] | None = None
        if loop_evaluation is not None:
            finalize_extra["loop_evaluation"] = loop_evaluation
            _decision = loop_evaluation.get("decision") if isinstance(loop_evaluation.get("decision"), dict) else {}
            loop_context = {
                "loop_run_id": loop_evaluation.get("loop_run_id"),
                "action": _decision.get("action"),
                "reason_code": _decision.get("reason_code"),
            }
            if _decision.get("action") in TERMINAL_LOOP_ACTIONS:
                deactivated = _deactivate_session_pointer(
                    str(data.get("session_id") or ""),
                    loop_evaluation.get("loop_run_dir"),
                    str(_decision.get("action")),
                )
                if deactivated is not None:
                    finalize_extra["loop_pointer_deactivated"] = deactivated
        kanboard_post_session = maybe_record_kanboard_post_session(data, validation_code, loop_context)
        if kanboard_post_session is not None:
            finalize_extra["kanboard_post_session"] = kanboard_post_session
        notifications: dict[str, Any] = {}
        if loop_evaluation is not None:
            # Loop turns notify per iteration (its decision already conveys success/continue/recover).
            notifications["loop_iteration"] = notify_loop_iteration(data, loop_evaluation)
        else:
            # Ordinary non-loop Stop completion. Send the finish cue even when
            # validation is unverified/failed; attention alerts are added below.
            label = notify_label(data)
            notifications["turn_complete"] = run_desktop_notify(
                data,
                event="turn-complete",
                topic="done",
                title="Codex task complete",
                message=notify_completion_message(data),
            )
        if validation_code not in (0, 4):
            first_line = validation_output.splitlines()[0] if validation_output else "validation failed"
            notifications["stop_failure"] = run_desktop_notify(
                data,
                event="stop-failure",
                topic="error",
                title="Codex turn needs attention",
                message=f"agent output validation: {truncate(first_line, 120)}",
            )
        if kanboard_post_session is not None and kanboard_post_session.get("status"):
            notifications["kanboard_sync"] = run_desktop_notify(
                data,
                event="kanboard-sync",
                topic="kanboard",
                title="Codex Kanboard",
                message=f"{kanboard_post_session.get('status')} {kanboard_post_session.get('task_reference', '')}".strip(),
            )
        if notifications:
            finalize_extra["desktop_notifications"] = notifications
        if validation_code == 0:
            record_event(args, data, "pass", finalize_extra, "turn_finalize")
        elif kanboard_post_session is not None or notifications:
            status = "warn" if validation_code == 4 else "fail"
            record_event(args, data, status, finalize_extra, "turn_finalize_attempt")
        output = loop_stop_output(loop_evaluation, data) if loop_evaluation is not None else None
        print(json.dumps(output or stop_output(data, validation_code, validation_output), sort_keys=True))
        return 0
    extra = None
    if hook_event == "PermissionRequest":
        extra = {"desktop_notification": notify_permission_request(data)}
    elif hook_event == "SessionStart":
        autosync = maybe_autosync_kanboard(data)
        if autosync is not None:
            extra = {"kanboard_autosync": autosync}
    record_event(args, data, classify_status(data), extra)
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
