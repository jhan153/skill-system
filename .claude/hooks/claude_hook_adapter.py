#!/usr/bin/env python3
"""Claude Code lifecycle hook adapter for Skill-System execution assurance.

Claude-side counterpart of .codex/hooks/codex_hook_adapter.py. It records Claude
Code lifecycle events into the SAME hash-chained evidence ledger
(.codex/tools/hook_runtime.py) so observed-evidence parity holds across both
runtimes. The shared discipline contract lives in the byte-mirrored skills
(workflow-rigor, analysis-bug, ...); this adapter is only the Claude runtime
wiring.

Default behavior is OBSERVATIONAL (record + allow stop), matching the Codex
adapter's non-strict default. A strict blocking gate (observed-vs-claimed
contradiction) requires a per-run manifest (run.yaml) that the Claude runtime
does not yet emit, so strict mode degrades to observational here until that
producer exists (see .claude/hooks/README.md). Fail-open: any error exits 0 so
the host session is never broken.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CODEX_TOOLS = ROOT / ".codex" / "tools"

# Claude Code hook event -> neutral event (subset of the Codex EVENT_MAP).
EVENT_MAP = {
    "UserPromptSubmit": "request_received",
    "SessionStart": "context_loaded",
    "PreToolUse": "tool_preflight",
    "PostToolUse": "tool_result",
    "Stop": "turn_finalize",
    "SubagentStop": "turn_finalize",
    "PreCompact": "compact_before",
}


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


def main() -> int:
    data = read_input()
    neutral = EVENT_MAP.get(str(data.get("hook_event_name") or ""))
    if neutral is None:
        return 0  # event we do not record; allow it.
    # Reuse the shared, runtime-agnostic evidence ledger. If the Codex tools are
    # not co-deployed, degrade to a no-op rather than break the host session.
    try:
        if str(CODEX_TOOLS) not in sys.path:
            sys.path.insert(0, str(CODEX_TOOLS))
        from hook_runtime import default_ledger, utc_now, write_event  # noqa: PLC0415
    except Exception:
        return 0

    session_id = str(data.get("session_id") or "claude-session")
    payload = {
        "recorded_at": utc_now(),
        "neutral_event": neutral,
        "host": "claude",
        "host_event": str(data.get("hook_event_name") or ""),
        "support_level": "native",
        "tool_id": str(data.get("tool_name") or ""),
        "session_id": session_id,
        "status": classify_status(data),
        "evidence": {
            "session_id": data.get("session_id"),
            "cwd": data.get("cwd"),
            "permission_mode": data.get("permission_mode"),
            "tool_name": data.get("tool_name"),
            "transcript_present": bool(data.get("transcript_path")),
            "stop_hook_active": bool(data.get("stop_hook_active")),
        },
    }
    try:
        write_event(payload, default_ledger(), session_id)
    except Exception:
        return 0
    # Stop is observational by default: record and allow. The strict
    # observed-vs-claimed block needs a per-run manifest the Claude runtime does
    # not yet emit, so it intentionally does not fire here.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
