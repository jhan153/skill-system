#!/usr/bin/env python3
"""Claude Code notification adapter for Skill-System desktop alerts."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[2]
MAX_TEXT = 240
DISABLED = {"0", "false", "off", "no", "none", "disabled"}
DRY_RUN = {"dry-run", "dry_run", "test"}
SECRET_VALUE_PATTERN = re.compile(r"(?i)(sk-[A-Za-z0-9_-]{12,}|[A-Za-z0-9_./+-]{24,})")
SENSITIVE_PATTERN = re.compile(
    r"(?i)(api[_-]?key|authorization|bearer|cookie|password|passwd|secret|token|client[_-]?secret|database[_-]?url)"
)
STATE_EVENTS = {"UserPromptSubmit", "TaskCreated", "TaskCompleted", "PostCompact", "Stop", "SubagentStop"}
NOTIFY_EVENTS = {"PermissionRequest", "Notification", "StopFailure", "Elicitation", "Stop"}
NOTIFICATION_TYPES = {"permission_prompt", "idle_prompt", "elicitation_dialog"}


def clean(value: object, limit: int = MAX_TEXT) -> str:
    text = " ".join(str(value or "").split())
    text = SECRET_VALUE_PATTERN.sub("<redacted>", text)
    if SENSITIVE_PATTERN.search(text):
        text = "<redacted-sensitive>"
    if len(text) <= limit:
        return text
    return text[: limit - 15].rstrip() + "...<truncated>"


def sanitize_id(value: object) -> str:
    raw = str(value or "unknown-session")
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "-", raw).strip(".-")
    return safe[:80] or "unknown-session"


def read_input(input_file: Path | None) -> dict[str, Any]:
    raw = input_file.read_text(encoding="utf-8") if input_file else sys.stdin.read()
    if not raw.strip():
        return {}
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("hook input must be a JSON object")
    return data


def resolve_transcript(data: dict[str, Any]) -> Path | None:
    """Locate the session transcript .jsonl from the hook payload.

    Prefers the payload's transcript_path; falls back to deriving it from
    cwd + session_id the way Claude Code names project transcript files.
    """
    raw = data.get("transcript_path")
    if isinstance(raw, str) and raw.strip():
        path = Path(raw).expanduser()
        if path.is_file():
            return path
    cwd = data.get("cwd")
    session = data.get("session_id")
    if isinstance(cwd, str) and cwd.strip() and session:
        sanitized = cwd.replace("/", "-")
        path = Path.home() / ".claude" / "projects" / sanitized / f"{sanitize_id(session)}.jsonl"
        if path.is_file():
            return path
    return None


def extract_transcript_info(data: dict[str, Any]) -> dict[str, str]:
    """Pull (summary, model, session title) from the session transcript.

    Claude Code does not always include last_assistant_message / model /
    session title in Stop / Notification payloads, so the transcript is the
    reliable source for a "what was just done" summary and the title parts.
    """
    info = {"summary": "", "model": "", "session": ""}
    path = resolve_transcript(data)
    if path is None:
        return info
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return info
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict):
            continue
        if not info["session"]:
            title = obj.get("aiTitle")
            if isinstance(title, str) and title.strip():
                info["session"] = title.strip()
        if obj.get("type") == "assistant":
            message = obj.get("message")
            if isinstance(message, dict):
                if not info["model"]:
                    model = message.get("model")
                    if isinstance(model, str) and model.strip():
                        info["model"] = model.strip()
                if not info["summary"]:
                    content = message.get("content")
                    texts: list[str] = []
                    if isinstance(content, list):
                        for block in content:
                            if isinstance(block, dict) and block.get("type") == "text":
                                text = block.get("text")
                                if isinstance(text, str) and text.strip():
                                    texts.append(text.strip())
                    elif isinstance(content, str) and content.strip():
                        texts.append(content.strip())
                    if texts:
                        info["summary"] = "\n".join(texts)
        if info["summary"] and info["model"] and info["session"]:
            break
    return info


def current_effort() -> str:
    """Best-effort current reasoning level for the model label (e.g. xhigh)."""
    for key in ("CLAUDE_CODE_EFFORT", "CLAUDE_EFFORT_LEVEL"):
        value = os.environ.get(key)
        if value and value.strip():
            return clean(value.strip(), 12)
    try:
        settings = json.loads((Path.home() / ".claude" / "settings.json").read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 - label detail only, never block.
        return ""
    if settings.get("fastMode") is True:
        return "fast"
    effort = settings.get("effortLevel")
    if isinstance(effort, str) and effort.strip():
        return clean(effort.strip(), 12)
    return ""


def short_model(model: str, effort: str = "") -> str:
    """Compact a model id into e.g. claude-opus-4-8 + xhigh -> opus4.8-xhigh."""
    text = str(model or "").strip()
    if text.startswith("claude-"):
        text = text[len("claude-") :]
    label = text
    parts = text.split("-")
    if parts and parts[0]:
        family = parts[0]
        nums = [p for p in parts[1:] if p.isdigit()]
        if len(nums) >= 2:
            label = f"{family}{nums[0]}.{nums[1]}"
        elif len(nums) == 1:
            label = f"{family}{nums[0]}"
        else:
            label = family
    if effort:
        label = f"{label}-{effort}" if label else effort
    return clean(label, 24)


def short_session(data: dict[str, Any], info: dict[str, str]) -> str:
    title = (info.get("session") or "").strip()
    if title:
        return clean(title, 22)
    cwd = data.get("cwd")
    if cwd:
        return basename_label(cwd)
    return sanitize_id(data.get("session_id"))[:12]


def notify_setting(data: dict[str, Any]) -> str:
    value = data.get("skill_system_desktop_notify")
    if value is None:
        value = os.environ.get("CLAUDE_DESKTOP_NOTIFY") or os.environ.get("SKILL_SYSTEM_DESKTOP_NOTIFY", "")
    return str(value).strip().lower()


def enabled(data: dict[str, Any]) -> bool:
    return notify_setting(data) not in DISABLED


def dry_run(data: dict[str, Any], cli_dry_run: bool) -> bool:
    return cli_dry_run or notify_setting(data) in DRY_RUN


def state_root() -> Path:
    raw = os.environ.get("CLAUDE_NOTIFY_STATE_DIR")
    if raw:
        return Path(raw).expanduser()
    return Path.home() / ".claude" / "hook-state" / "skill-system-notify"


def state_path(data: dict[str, Any]) -> Path:
    return state_root() / f"{sanitize_id(data.get('session_id'))}.json"


def load_state(data: dict[str, Any]) -> dict[str, Any]:
    path = state_path(data)
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 - state is advisory only.
        return {}
    return value if isinstance(value, dict) else {}


def save_state(data: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    event = str(data.get("hook_event_name") or "")
    changed = False
    if isinstance(data.get("cwd"), str):
        state["cwd"] = clean(data["cwd"], 180)
        changed = True
    if isinstance(data.get("prompt"), str):
        state["latest_prompt"] = clean(data["prompt"], 180)
        changed = True
    if isinstance(data.get("task_subject"), str):
        state["task_subject"] = clean(data["task_subject"], 160)
        changed = True
    if isinstance(data.get("compact_summary"), str):
        state["compact_summary"] = clean(data["compact_summary"], 180)
        changed = True
    if isinstance(data.get("last_assistant_message"), str):
        state["last_assistant_message"] = clean(data["last_assistant_message"], 180)
        changed = True
    if isinstance(data.get("agent_type"), str):
        state["agent_type"] = clean(data["agent_type"], 80)
        changed = True
    if changed or event in STATE_EVENTS:
        path = state_path(data)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(state, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
            path.chmod(0o600)
        except OSError:
            pass
    return state


def basename_label(value: object) -> str:
    raw = str(value or "")
    if not raw:
        return ""
    name = Path(raw).name
    return clean(name or raw, 80)


def context_label(data: dict[str, Any], state: dict[str, Any]) -> str:
    # Session context carried in the message BODY (the title separately shows
    # [stat]-[model]-[session]); body context is what the notify tests assert.
    for key in ["task_subject", "compact_summary", "last_assistant_message", "latest_prompt"]:
        if isinstance(data.get(key), str) and data[key].strip():
            return clean(data[key], 120)
        if isinstance(state.get(key), str) and state[key].strip():
            return clean(state[key], 120)
    cwd = data.get("cwd") or state.get("cwd")
    if cwd:
        return basename_label(cwd)
    return sanitize_id(data.get("session_id"))


def task_label(data: dict[str, Any], state: dict[str, Any]) -> str:
    for key in ["task_subject", "compact_summary", "latest_prompt"]:
        if isinstance(data.get(key), str) and data[key].strip():
            return clean(data[key], 80)
        if isinstance(state.get(key), str) and state[key].strip():
            return clean(state[key], 80)
    cwd = data.get("cwd") or state.get("cwd")
    if cwd:
        return basename_label(cwd)
    return sanitize_id(data.get("session_id"))


def completion_label(data: dict[str, Any], state: dict[str, Any]) -> str:
    # Body carries the summary AND the task label; the title separately shows
    # [stat]-[model]-[session].
    summary = ""
    for source in (data.get("last_assistant_message"), state.get("last_assistant_message")):
        if isinstance(source, str) and source.strip():
            for line in source.splitlines():
                text = line.strip()
                if text and not text.startswith("```") and text != "---":
                    summary = clean(text, 150)
                    break
        if summary:
            break
    label = task_label(data, state)
    if summary and label and label not in summary:
        return clean(f"{summary} - {label}", 220)
    return summary or label


def tool_description(data: dict[str, Any]) -> str:
    tool_input = data.get("tool_input")
    if isinstance(tool_input, dict):
        description = tool_input.get("description")
        if isinstance(description, str) and description.strip():
            return clean(description, 120)
        command = tool_input.get("command")
        if isinstance(command, str) and command.strip():
            return f"{command.strip().split(maxsplit=1)[0]} command"
    return ""


def notification_payload(data: dict[str, Any], state: dict[str, Any]) -> tuple[str, str, str, str] | None:
    event = str(data.get("hook_event_name") or "")
    label = context_label(data, state)
    if event == "PermissionRequest":
        tool_name = clean(data.get("tool_name") or "Tool", 80)
        detail = tool_description(data)
        suffix = f" - {detail}" if detail else ""
        return "approval-requested", "Claude approval requested", f"{tool_name} permission needed for {label}{suffix}.", "approval"
    if event == "Notification":
        notification_type = str(data.get("notification_type") or "")
        if notification_type not in NOTIFICATION_TYPES:
            return None
        title = clean(data.get("title") or "Claude notification", 80)
        message = clean(data.get("message") or notification_type, 140)
        return f"claude-{notification_type}", title, f"{message} - {label}.", "input"
    if event == "StopFailure":
        error = clean(data.get("error") or "unknown", 80)
        details = clean(data.get("error_details") or "", 120)
        suffix = f": {details}" if details else ""
        return "claude-stop-failure", "Claude session error", f"{error}{suffix} - {label}.", "error"
    if event == "Elicitation":
        message = clean(data.get("message") or "Claude needs input", 140)
        return "claude-elicitation", "Claude input requested", f"{message} - {label}.", "input"
    if event == "Stop":
        return "turn-complete", "Claude task complete", completion_label(data, state), "done"
    return None


def run_notification(event: str, title: str, message: str, topic: str, model: str, session: str, dry: bool) -> dict[str, Any]:
    cmd = [
        sys.executable,
        str(ROOT / ".claude" / "tools" / "notify_desktop.py"),
        "--event",
        event,
        "--title",
        title,
        "--message",
        message,
        "--mode",
        "overlay",
        "--app",
        "claude",
    ]
    if topic:
        cmd += ["--topic", topic]
    if model:
        cmd.append(f"--model={model}")
    if session:
        cmd.append(f"--session={session}")
    if dry:
        cmd.append("--dry-run")
    try:
        completed = subprocess.run(
            cmd,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=5,
        )
    except Exception as exc:  # noqa: BLE001 - hook must stay non-blocking.
        return {"status": "error", "reason": clean(str(exc), 160)}
    if completed.returncode != 0:
        return {
            "status": "error",
            "returncode": completed.returncode,
            "reason": clean(completed.stderr or completed.stdout, 160),
        }
    try:
        report = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {"status": "error", "reason": "notify_desktop returned non-JSON output"}
    return report if isinstance(report, dict) else {"status": "error", "reason": "notify_desktop returned non-object JSON"}


def handle(args: argparse.Namespace) -> dict[str, Any]:
    data = read_input(args.input_file)
    info = extract_transcript_info(data)
    if info["summary"] and not (isinstance(data.get("last_assistant_message"), str) and data["last_assistant_message"].strip()):
        data["last_assistant_message"] = info["summary"]
    event = str(data.get("hook_event_name") or "")
    state = load_state(data)
    state = save_state(data, state)
    if event not in NOTIFY_EVENTS or not enabled(data):
        return {"status": "skipped", "event": event}
    payload = notification_payload(data, state)
    if payload is None:
        return {"status": "skipped", "event": event, "reason": "unmatched notification type"}
    notification_event, title, message, topic = payload
    model = short_model(info["model"], current_effort())
    session = short_session(data, info)
    report = run_notification(notification_event, title, message, topic, model, session, dry_run(data, args.dry_run))
    report["hook_event_name"] = event
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-file", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--print-report", action="store_true")
    args = parser.parse_args()
    try:
        report = handle(args)
    except Exception as exc:  # noqa: BLE001 - hook must not interrupt Claude.
        report = {"status": "error", "reason": clean(str(exc), 160)}
    if args.print_report:
        print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
