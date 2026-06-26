#!/usr/bin/env python3
"""Claude Code lifecycle hook adapter for Skill-System execution assurance.

Claude-side counterpart of .codex/hooks/codex_hook_adapter.py. It records Claude
Code lifecycle events into the SAME hash-chained evidence ledger
(.codex/tools/hook_runtime.py) so observed-evidence parity holds across both
runtimes. The shared discipline contract lives in the byte-mirrored skills
(workflow-rigor, analysis-bug, ...); this adapter is only the Claude runtime
wiring.

Default is OBSERVATIONAL (record + allow stop). A STRICT observed-vs-claimed
gate (decision 6 opt-in via SKILL_SYSTEM_AGENT_OUTPUT_GATE=strict) blocks a stop
when the final assistant message claims `agent-verified` but the transcript
shows a failed tool result with no later success. The Codex side enforces the
same intent through a pre-declared run.yaml manifest; the Claude runtime does
not emit that manifest, so this adapter derives the contradiction from the
transcript instead (same intent, runtime-specific mechanism). Fail-open: any
error exits 0 so the host session is never broken.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CODEX_TOOLS = ROOT / ".codex" / "tools"

EVENT_MAP = {
    "UserPromptSubmit": "request_received",
    "SessionStart": "context_loaded",
    "PreToolUse": "tool_preflight",
    "PostToolUse": "tool_result",
    "Stop": "turn_finalize",
    "SubagentStop": "turn_finalize",
    "PreCompact": "compact_before",
}

STRICT_GATE = "strict"
# Result label claimed in the final message that asserts full agent verification.
VERIFIED_LABEL = "agent-verified"


def read_input() -> dict:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def classify_status(data: dict) -> str:
    if str(data.get("hook_event_name") or "") != "PostToolUse":
        return "pass"
    response = data.get("tool_response")
    if isinstance(response, dict):
        if response.get("success") is False or response.get("error"):
            return "fail"
        if response.get("success") is True:
            return "pass"
    return "warn"


def strict_gate_enabled(data: dict) -> bool:
    configured = data.get("skill_system_agent_output_gate") or os.environ.get(
        "SKILL_SYSTEM_AGENT_OUTPUT_GATE", ""
    )
    return str(configured).lower() == STRICT_GATE


def measurement_enabled(data: dict) -> bool:
    """Out-of-band holdout measurement (opt-in). When on, off-arm sessions record
    would_fire but do not block (gate-off baseline) so the harness paradox can be
    measured. Default off, so it never changes baseline behavior."""
    configured = data.get("skill_system_harness_measurement") or os.environ.get(
        "SKILL_SYSTEM_HARNESS_MEASUREMENT", ""
    )
    return str(configured).lower() in {"1", "true", "on", "yes"}


# --- pure decision logic (unit-testable, no I/O) ---------------------------

def claims_verified(last_assistant_text: str) -> bool:
    """Whether the final assistant message asserts the `agent-verified` label."""
    return VERIFIED_LABEL in (last_assistant_text or "").lower()


def has_unresolved_tool_failure(tool_results: list[dict[str, Any]]) -> bool:
    """A tool result errored and no later tool result succeeded after it.

    `tool_results` is the ordered list of observed tool results, each a dict with
    a boolean `is_error`. Returns True when the last error is not followed by any
    success, i.e. the failure was not visibly recovered before finalizing.
    """
    last_error_idx = -1
    last_success_idx = -1
    for idx, result in enumerate(tool_results):
        if not isinstance(result, dict):
            continue
        if result.get("is_error") is True:
            last_error_idx = idx
        elif result.get("is_error") is False:
            last_success_idx = idx
    return last_error_idx >= 0 and last_error_idx > last_success_idx


def strict_block(last_assistant_text: str, tool_results: list[dict[str, Any]]) -> tuple[bool, str]:
    """Observed-vs-claimed contradiction: claims agent-verified but a tool failed."""
    if claims_verified(last_assistant_text) and has_unresolved_tool_failure(tool_results):
        return True, (
            "fablize/strict gate: the final message claims agent-verified, but the "
            "transcript shows a failed tool result with no later success. Re-verify "
            "the changed behavior or correct the result label before finalizing."
        )
    return False, ""


# --- transcript parsing (best-effort, fail-open) ---------------------------

def parse_transcript(path_value: Any) -> tuple[str, list[dict[str, Any]]]:
    """Return (last_assistant_text, ordered tool_results) from a Claude transcript.

    Never raises; returns ("", []) on any problem so strict mode degrades to
    observational rather than blocking on a parse error.
    """
    last_text = ""
    tool_results: list[dict[str, Any]] = []
    try:
        path = Path(str(path_value)).expanduser()
        if not path.is_file():
            return "", []
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(event, dict):
                continue
            message = event.get("message")
            if not isinstance(message, dict):
                continue
            role = message.get("role")
            content = message.get("content")
            if role == "assistant":
                texts = [
                    block.get("text", "")
                    for block in content
                    if isinstance(block, dict) and block.get("type") == "text"
                ] if isinstance(content, list) else ([content] if isinstance(content, str) else [])
                joined = " ".join(t for t in texts if t).strip()
                if joined:
                    last_text = joined
            elif role == "user" and isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_result":
                        tool_results.append({"is_error": bool(block.get("is_error"))})
    except Exception:
        return "", []
    return last_text, tool_results


def main() -> int:
    data = read_input()
    event = str(data.get("hook_event_name") or "")
    neutral = EVENT_MAP.get(event)
    if neutral is None:
        return 0
    try:
        if str(CODEX_TOOLS) not in sys.path:
            sys.path.insert(0, str(CODEX_TOOLS))
        from hook_runtime import default_ledger, utc_now, write_event  # noqa: PLC0415
    except Exception:
        return 0

    session_id = str(data.get("session_id") or "claude-session")
    decision: dict[str, Any] | None = None
    extra: dict[str, Any] = {}

    if event == "Stop" and strict_gate_enabled(data) and not data.get("stop_hook_active"):
        text, tool_results = parse_transcript(data.get("transcript_path"))
        would_fire, reason = strict_block(text, tool_results)
        measure = measurement_enabled(data)
        arm = "on"
        if measure:
            try:
                from analyze_harness_measurement import holdout_arm  # noqa: PLC0415
                arm = holdout_arm(session_id)
            except Exception:
                arm = "on"
        do_block = would_fire and arm == "on"  # off arm = gate-off baseline
        extra["strict_gate"] = "block" if do_block else ("would_fire_baseline" if would_fire else "observed")
        if measure:
            extra.update({"holdout_arm": arm, "would_fire": would_fire, "did_block": do_block})
        if do_block:
            decision = {"decision": "block", "reason": reason}

    payload = {
        "recorded_at": utc_now(),
        "neutral_event": neutral,
        "host": "claude",
        "host_event": event,
        "support_level": "native",
        "tool_id": str(data.get("tool_name") or ""),
        "session_id": session_id,
        "status": "fail" if decision else classify_status(data),
        "evidence": {
            "session_id": data.get("session_id"),
            "cwd": data.get("cwd"),
            "permission_mode": data.get("permission_mode"),
            "tool_name": data.get("tool_name"),
            "transcript_present": bool(data.get("transcript_path")),
            "stop_hook_active": bool(data.get("stop_hook_active")),
            **extra,
        },
    }
    try:
        write_event(payload, default_ledger(), session_id)
    except Exception:
        return 0

    if decision is not None:
        # Strict observed-vs-claimed contradiction: block the stop (Claude reads
        # the decision JSON). Default/observational path prints nothing and allows.
        print(json.dumps(decision))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
