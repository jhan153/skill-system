#!/usr/bin/env python3
"""Low-context recovery guard state reducer.

The reducer observes lifecycle payloads without retaining prompt, assistant, or
tool output text.  It emits a single audit request for a correction episode only
after the session has accumulated context pressure.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


try:
    import fcntl
except ModuleNotFoundError:  # pragma: no cover - non-POSIX fallback.
    fcntl = None


SCHEMA_VERSION = 1
SUPPORTED_EVENTS = {
    "UserPromptSubmit",
    "SessionStart",
    "PreToolUse",
    "PermissionRequest",
    "PostToolUse",
    "PreCompact",
    "PostCompact",
    "Stop",
}
AUDIT_FIELDS = (
    "goal_anchor",
    "latest_user_delta",
    "observed_changes",
    "verified_progress",
    "open_gap_and_next_action",
)
MAX_RECENT_EVENTS = 64
MAX_AUDIT_BLOCKS_PER_SESSION = 3
PHASES = {"passive", "armed", "correction_pending", "audit_requested", "awaiting_user"}
STATE_FIELDS = frozenset(
    {
        "schema_version",
        "session_hash",
        "user_turns",
        "tool_events",
        "permission_requests",
        "stop_events",
        "correction_episodes",
        "successful_progress_events",
        "pre_compact_seen",
        "post_compact_seen",
        "armed",
        "episode",
        "correction_pending",
        "progress_since_correction",
        "audit_issued_for_episode",
        "audit_blocked_for_episode",
        "audit_responses",
        "audit_blocks",
        "audit_packet_valid",
        "phase",
        "last_stop_recovery_rhetoric",
        "last_stop_substantive",
        "last_event_hash",
        "recent_events",
    }
)

_KOREAN_CORRECTION = re.compile(
    r"(?:^\s*(?:아니(?:요)?)(?!면)[\s,.!?:]|"
    r"그게\s+아니(?:야|에요|예요|잖아|잖아요)|"
    r"그\s+뜻이\s+아니|"
    r"(?:내가|제가)\s+(?:말|요청)한.+아니|"
    r"말한\s*(?:게|건|것(?:이)?)\s+아니|"
    r"(?:(?:내가|제가)\s+)?(?:원한|보고\s+싶은)\s*(?:게|건|것(?:이)?)\s+아니|"
    r"(?:내가|제가)\s+원한\s+건.+(?:아니라|아니고)|"
    r"(?:원래\s+)?요청(?:한\s+것)?과\s+다르|"
    r"잘못\s+(?:이해|고쳤|수정|했)|"
    r"^\s*(?:틀렸|잘못됐))",
    re.IGNORECASE,
)
_ENGLISH_CORRECTION = re.compile(
    r"(?:^\s*(?:no[,.:!\s]|that's\s+(?:not\s+what|wrong)|this\s+is\s+wrong)|"
    r"not\s+what\s+i\s+(?:asked|meant)|"
    r"you\s+(?:misunderstood|missed\s+the\s+point)|"
    r"please\s+(?:correct|fix)\s+(?:that|this))",
    re.IGNORECASE,
)
_CORRECTION_OVERRIDE = re.compile(
    r"(?:그게\s+아니|말한\s*(?:게|건|것(?:이)?)\s+아니|원한\s+건.+(?:아니라|아니고)|"
    r"not\s+what\s+i\s+(?:asked|meant)|that's\s+not\s+what|this\s+is\s+wrong|you\s+misunderstood)",
    re.IGNORECASE,
)
_EXPLICIT_STOP = re.compile(
    r"^\s*(?:"
    r"(?:아니(?:요)?[,!?.\s]*)?(?:이제\s+)?(?:"
    r"그만(?:해|하세요|해주세요)?|멈춰(?:줘|주세요)?|중단(?:해|하세요|해주세요)?|"
    r"됐(?:어|습니다)|괜찮(?:아|아요|습니다)?|감사(?:합니다|해요)?|하지\s*마(?:세요)?|"
    r"(?:추가|더\s+이상)\s*(?:작업|조치|설명)?(?:은|는|이|가)?\s*"
    r"(?:필요\s*없(?:어|습니다)?|안\s+해도\s+돼|하지\s*마(?:세요)?))|"
    r"no[,.!]?\s*(?:thanks(?:[.!]\s*that\s+is\s+all)?|thank\s+you|stop(?:\s+here)?|"
    r"that(?:'s|\s+is)\s+all|"
    r"(?:do\s+not|don't)\s+(?:do|start|continue)\s+(?:anything|more|additional|anything\s+else))|"
    r"stop(?:\s+here)?|(?:do\s+not|don't)\s+continue|"
    r"no\s+(?:need\s+(?:to\s+continue|for\s+(?:more|additional)\s+work|for\s+anything\s+else)|"
    r"(?:further|additional)\s+work\s+is\s+needed)"
    r")\s*[.!]?\s*$",
    re.IGNORECASE,
)
_RECOVERY_OPENER = re.compile(
    r"^\s*(?:"
    r"맞습니다|그렇습니다|제가\s+잘못|죄송합니다|죄송해요|"
    r"you're\s+right|you\s+are\s+right|i(?:'m|\s+am)\s+sorry|apologies|my\s+mistake"
    r")[\s,.!?:]",
    re.IGNORECASE,
)
_RECOVERY_PROMISE = re.compile(
    r"(?:"
    r"(?:이제|바로|앞으로(?:는)?)\b.{0,80}(?:하겠습니다|고치겠습니다|수정하겠습니다|진행하겠습니다|마무리하겠습니다)|"
    r"(?:다시는|새로\s+계획|다시\s+시작)|"
    r"(?:i\s+will|i'll|from\s+now\s+on|going\s+forward)\b|"
    r"let\s+me\s+(?:fix|redo|restart|start\s+over|try\s+again|correct|rework)\b"
    r")",
    re.IGNORECASE | re.DOTALL,
)
_SUBSTANTIVE_MARKER = re.compile(
    r"(?:차이|결과|결론|이유|원인|조건|규칙|입력|출력|데이터|구조|흐름|화면|사용자|성능|복잡도|"
    r"오류|예외|상태|호출|전파|반환|저장|계약|런타임|실제\s+동작|"
    r"difference|result|conclusion|reason|cause|condition|rule|input|output|data|structure|flow|screen|user|"
    r"performance|complexity|behavior|error|exception|state|call(?:er)?|propagat|return|persist|contract|runtime|"
    r"`[^`]+`|(?:^|\s)[A-Za-z0-9_.-]+\.(?:py|ts|js|cs|cpp|h|md|yaml|json)(?::\d+)?)",
    re.IGNORECASE | re.MULTILINE,
)
_SUBSTANTIVE_ASSERTION = re.compile(
    r"(?:반면|하지만|따라서|때문|그러므로|결론적으로|그\s+결과|즉\s|"
    r"던지(?:지만|고)?|반환(?:하지만|하고|값)?|"
    r"because|whereas|however|therefore|thus|"
    r"\b(?:returns?|throws?|propagates?|persists?|differs?)\b|"
    r"`[^`]+`|(?:^|\s)[A-Za-z0-9_.-]+\.(?:py|ts|js|cs|cpp|h|md|yaml|json)(?::\d+)?)",
    re.IGNORECASE | re.MULTILINE,
)
_DIRECT_CONCLUSION_ASSERTION = re.compile(
    r"(?:"
    r"(?:핵심|주요|실제|결정적)?\s*(?:차이|원인|결론|답|문제|조건)(?:점)?(?:은|는|이|가)\s+"
    r"[^.!?\n]{1,120}(?:입니다|이다|예요|에요|입니다만)|"
    r"\b(?:the\s+)?(?:key\s+|main\s+|actual\s+)?"
    r"(?:difference|cause|conclusion|answer|issue|condition)\s+is\s+[^.!?\n]{1,160}"
    r")",
    re.IGNORECASE | re.MULTILINE,
)
_FUTURE_ONLY_ASSERTION = re.compile(
    r"(?:예정|계획|(?:확인|검토|수정|구현|검증|조사)하겠|"
    r"\b(?:will|shall|going\s+to|plan\s+to|need\s+to\s+(?:check|verify|investigate))\b)",
    re.IGNORECASE,
)


def default_state_dir() -> Path:
    configured = os.environ.get("SKILL_SYSTEM_RECOVERY_GUARD_STATE_DIR")
    if configured:
        return Path(configured).expanduser()
    codex_home = os.environ.get("CODEX_HOME") or str(Path.home() / ".codex")
    return Path(codex_home).expanduser() / "harness" / "recovery-guard" / "sessions"


def state_path_for_session(session_id: object, state_dir: Path | None = None) -> Path:
    """Return a non-identifying, session-stable state path."""

    if not str(session_id or "").strip():
        raise ValueError("recovery guard requires session_id")
    return (state_dir or default_state_dir()) / f"{hash_text(session_id)}.json"


@dataclass(frozen=True)
class GuardThresholds:
    """Context-pressure thresholds; any one threshold arms the guard."""

    user_turns: int = 6
    tool_events: int = 20
    correction_episodes: int = 2

    def __post_init__(self) -> None:
        for name in ("user_turns", "tool_events", "correction_episodes"):
            if getattr(self, name) < 1:
                raise ValueError(f"{name} threshold must be at least 1")

    @classmethod
    def from_mapping(cls, values: Mapping[str, object] | None) -> "GuardThresholds":
        if not values:
            return cls()
        kwargs: dict[str, int] = {}
        for name in ("user_turns", "tool_events", "correction_episodes"):
            if name in values:
                value = values[name]
                if isinstance(value, bool) or not isinstance(value, int):
                    raise ValueError(f"{name} threshold must be an integer")
                kwargs[name] = value
        return cls(**kwargs)


def hash_text(value: object) -> str:
    return hashlib.sha256(str(value or "").encode("utf-8", errors="replace")).hexdigest()


def detect_correction(text: object) -> bool:
    """Return true only for explicit user-correction phrases, not generic questions."""

    if not isinstance(text, str) or not text.strip():
        return False
    sample = text[:1200]
    if detect_explicit_stop(sample):
        return False
    return bool(_KOREAN_CORRECTION.search(sample) or _ENGLISH_CORRECTION.search(sample))


def detect_explicit_stop(text: object) -> bool:
    """Recognize a user instruction that ends work, not a correction."""

    if not isinstance(text, str) or not text.strip():
        return False
    sample = text[:400]
    return bool(_EXPLICIT_STOP.search(sample) and not _CORRECTION_OVERRIDE.search(sample))


def detect_recovery_rhetoric(text: object) -> bool:
    """Detect apology/agreement openers coupled to a future-facing repair promise."""

    if not isinstance(text, str) or not text.strip():
        return False
    sample = text[:1200]
    return bool(_RECOVERY_OPENER.search(sample[:240]) and _RECOVERY_PROMISE.search(sample))


def detect_substantive_response(text: object) -> bool:
    """Distinguish a concrete correction from rhetoric-only recovery prose."""

    if not isinstance(text, str) or not text.strip():
        return False
    sample = text[:2400]
    residual = _RECOVERY_OPENER.sub("", sample, count=1)
    # Remove only the recovery opener's first promise. Later future-facing
    # language belongs to the claimed result and must remain available to the
    # future-only guard below.
    residual = _RECOVERY_PROMISE.sub("", residual, count=1)
    compact = re.sub(r"\s+", " ", residual).strip()
    direct_match = _DIRECT_CONCLUSION_ASSERTION.search(compact)
    direct_conclusion = bool(
        direct_match is not None and not _FUTURE_ONLY_ASSERTION.search(direct_match.group(0))
    )
    assertion = direct_conclusion or _SUBSTANTIVE_ASSERTION.search(compact) is not None
    # A short, concrete contrast is still substantive; long future-facing
    # plans remain rhetoric because they lack a present/past assertion.
    return bool(
        len(compact) >= (12 if direct_conclusion else 20 if assertion else 60)
        and _SUBSTANTIVE_MARKER.search(compact) is not None
        and assertion
    )


def detect_recovery_audit_packet(text: object) -> bool:
    """Recognize the compact recovery handoff shape without retaining its values."""

    if not isinstance(text, str) or not text.strip() or "recovery_audit" not in text:
        return False
    lines = [line.rstrip() for line in text[:6000].strip().splitlines() if line.strip()]
    if len(lines) >= 2 and lines[0].strip().startswith("```") and lines[-1].strip() == "```":
        lines = lines[1:-1]
    if not lines or lines[0].strip() != "recovery_audit:":
        return False
    values: dict[str, str] = {}
    for line in lines[1:]:
        match = re.fullmatch(r"\s{2,}([a-z_]+):\s*(.*?)\s*", line)
        if match is None or match.group(1) not in AUDIT_FIELDS or match.group(1) in values:
            return False
        value = match.group(2).strip()
        if not value or re.fullmatch(r"<[^>]+>", value):
            return False
        values[match.group(1)] = value
    if tuple(values) != AUDIT_FIELDS:
        return False
    for field in ("observed_changes", "verified_progress"):
        if not (values[field].startswith("[") and values[field].endswith("]")):
            return False
    return all(len(value) <= 1000 for value in values.values())


def _session_hash(event: Mapping[str, Any]) -> str:
    return hash_text(event.get("session_id", ""))


def new_state(session_id: object = "") -> dict[str, Any]:
    """Create the compact persisted schema for one session."""

    return {
        "schema_version": SCHEMA_VERSION,
        "session_hash": hash_text(session_id),
        "user_turns": 0,
        "tool_events": 0,
        "permission_requests": 0,
        "stop_events": 0,
        "correction_episodes": 0,
        "successful_progress_events": 0,
        "pre_compact_seen": False,
        "post_compact_seen": False,
        "armed": False,
        "episode": 0,
        "correction_pending": False,
        "progress_since_correction": False,
        "audit_issued_for_episode": False,
        "audit_blocked_for_episode": False,
        "audit_responses": 0,
        "audit_blocks": 0,
        "audit_packet_valid": False,
        "phase": "passive",
        "last_stop_recovery_rhetoric": False,
        "last_stop_substantive": False,
        "last_event_hash": "",
        "recent_events": [],
    }


def _validate_state(state: Mapping[str, Any]) -> None:
    missing = sorted(STATE_FIELDS.difference(state))
    if missing:
        raise ValueError(f"recovery guard state missing fields: {', '.join(missing)}")
    unexpected = sorted(set(state).difference(STATE_FIELDS))
    if unexpected:
        raise ValueError(f"recovery guard state has unexpected fields: {', '.join(unexpected)}")
    if state.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported recovery guard state schema")
    if not isinstance(state.get("session_hash"), str) or len(state["session_hash"]) != 64:
        raise ValueError("recovery guard state has invalid session_hash")
    for name in (
        "user_turns",
        "tool_events",
        "permission_requests",
        "stop_events",
        "correction_episodes",
        "successful_progress_events",
        "episode",
        "audit_responses",
        "audit_blocks",
    ):
        value = state.get(name)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"recovery guard state has invalid {name}")
    for name in (
        "pre_compact_seen",
        "post_compact_seen",
        "armed",
        "correction_pending",
        "progress_since_correction",
        "audit_issued_for_episode",
        "audit_blocked_for_episode",
        "audit_packet_valid",
        "last_stop_recovery_rhetoric",
        "last_stop_substantive",
    ):
        if not isinstance(state.get(name), bool):
            raise ValueError(f"recovery guard state has invalid {name}")
    last_event_hash = state.get("last_event_hash")
    if not isinstance(last_event_hash, str) or (last_event_hash and len(last_event_hash) != 64):
        raise ValueError("recovery guard state has invalid last_event_hash")
    if state.get("phase") not in PHASES:
        raise ValueError("recovery guard state has invalid phase")
    recent_events = state.get("recent_events")
    if not isinstance(recent_events, list) or len(recent_events) > MAX_RECENT_EVENTS:
        raise ValueError("recovery guard state has invalid recent_events")
    for item in recent_events:
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("event_hash"), str)
            or len(item["event_hash"]) != 64
            or item.get("action") not in {"allow", "audit", "handoff"}
            or not isinstance(item.get("audit_blocked"), bool)
        ):
            raise ValueError("recovery guard state has invalid recent event receipt")


def _event_text(event: Mapping[str, Any], *names: str) -> str:
    for name in names:
        value = event.get(name)
        if isinstance(value, str):
            return value
    return ""


def _event_hash(event: Mapping[str, Any]) -> str:
    """Hash an event for replay suppression without persisting its raw payload."""

    try:
        raw = json.dumps(event, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)
    except (TypeError, ValueError):
        raw = repr(sorted((str(key), str(value)) for key, value in event.items()))
    return hash_text(raw)


def _has_successful_progress(event: Mapping[str, Any]) -> bool:
    """Require explicit progress evidence; a generic zero exit is not enough."""

    explicit_success = False
    for container in (event, event.get("evidence"), event.get("tool_response")):
        if not isinstance(container, Mapping):
            continue
        if container.get("successful_progress") is True or container.get("progress_evidence") is True:
            return True
        exit_code = container.get("exit_code")
        changed_files = container.get("changed_files")
        validation_passed = container.get("validation_passed") is True
        succeeded = exit_code == 0 or container.get("success") is True
        explicit_success = explicit_success or succeeded
        if succeeded and (validation_passed or (isinstance(changed_files, list) and bool(changed_files))):
            return True
    tool_name = str(event.get("tool_name") or "").lower()
    return explicit_success and tool_name in {"apply_patch", "edit", "write"}


def _is_armed(state: Mapping[str, Any], thresholds: GuardThresholds) -> bool:
    return bool(
        state["post_compact_seen"]
        or state["user_turns"] >= thresholds.user_turns
        or state["tool_events"] >= thresholds.tool_events
        or state["correction_episodes"] >= thresholds.correction_episodes
    )


def _arm_reasons(state: Mapping[str, Any], thresholds: GuardThresholds) -> list[str]:
    reasons: list[str] = []
    if state["post_compact_seen"]:
        reasons.append("post_compact")
    if state["user_turns"] >= thresholds.user_turns:
        reasons.append("user_turn_threshold")
    if state["tool_events"] >= thresholds.tool_events:
        reasons.append("tool_event_threshold")
    if state["correction_episodes"] >= thresholds.correction_episodes:
        reasons.append("correction_episode_threshold")
    return reasons


def _remember_event(state: dict[str, Any], fingerprint: str, action: str, *, audit_blocked: bool = False) -> None:
    state["last_event_hash"] = fingerprint
    state["recent_events"] = [
        *state["recent_events"][-(MAX_RECENT_EVENTS - 1):],
        {"event_hash": fingerprint, "action": action, "audit_blocked": audit_blocked},
    ]


def _duplicate_decision(state: Mapping[str, Any], fingerprint: str) -> dict[str, Any] | None:
    for receipt in reversed(state["recent_events"]):
        if receipt["event_hash"] != fingerprint:
            continue
        if receipt["action"] == "audit" and not state["audit_issued_for_episode"]:
            return None
        decision: dict[str, Any] = {
            "action": "duplicate",
            "replayed_action": receipt["action"],
            "replayed_blocked": bool(receipt.get("audit_blocked")),
            "reason_codes": ["duplicate_event"],
            "armed": state["armed"],
            "arm_reasons": [],
            "episode": state["episode"],
            "phase": state["phase"],
        }
        return decision
    return None


def reduce_event(
    state: Mapping[str, Any] | None,
    event: Mapping[str, Any],
    thresholds: GuardThresholds | Mapping[str, object] | None = None,
    *,
    block_audit: bool = True,
    consume_audit: bool = True,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Purely reduce one hook event into state and an allow/audit decision.

    ``action == 'audit'`` means the caller may block this Stop once and request
    ``AUDIT_FIELDS``. ``handoff`` releases the next Stop without declaring task
    completion. All other events are observational and return ``allow``.
    """

    event_name = event.get("hook_event_name")
    if event_name not in SUPPORTED_EVENTS:
        raise ValueError(f"unsupported recovery guard event: {event_name}")
    config = thresholds if isinstance(thresholds, GuardThresholds) else GuardThresholds.from_mapping(thresholds)
    current = dict(state) if state is not None else new_state(event.get("session_id", ""))
    _validate_state(current)
    incoming_session_hash = _session_hash(event)
    if event.get("session_id") and current["session_hash"] != incoming_session_hash:
        raise ValueError("recovery guard state belongs to a different session")

    fingerprint = _event_hash(event)
    is_clear = event_name == "SessionStart" and str(event.get("source") or "").lower() == "clear"
    if not is_clear:
        duplicate = _duplicate_decision(current, fingerprint)
        if duplicate is not None:
            return current, duplicate

    reason_codes: list[str] = []
    if event_name == "UserPromptSubmit":
        if current["phase"] in {"audit_requested", "awaiting_user"}:
            current["correction_pending"] = False
            current["progress_since_correction"] = False
            current["audit_issued_for_episode"] = False
            current["audit_blocked_for_episode"] = False
            current["audit_packet_valid"] = False
        current["user_turns"] += 1
        prompt = _event_text(event, "prompt", "user_prompt", "message")
        explicit_stop = detect_explicit_stop(prompt) and not _CORRECTION_OVERRIDE.search(str(prompt)[:400])
        if explicit_stop:
            current["correction_pending"] = False
            current["progress_since_correction"] = False
            current["audit_issued_for_episode"] = False
            current["audit_blocked_for_episode"] = False
            current["audit_packet_valid"] = False
            reason_codes.append("explicit_stop")
        is_correction = event.get("correction_detected") is True or detect_correction(prompt)
        if is_correction and not explicit_stop:
            current["correction_episodes"] += 1
            current["episode"] += 1
            current["correction_pending"] = True
            current["progress_since_correction"] = False
            current["audit_issued_for_episode"] = False
            current["audit_blocked_for_episode"] = False
            current["audit_packet_valid"] = False
            reason_codes.append("correction_detected")
    elif event_name == "SessionStart":
        source = str(event.get("source") or "").lower()
        if source == "clear":
            current = new_state(event.get("session_id", ""))
            reason_codes.append("session_cleared")
        elif source == "compact":
            current["post_compact_seen"] = True
            reason_codes.append("compact_resume")
    elif event_name == "PreToolUse":
        current["tool_events"] += 1
    elif event_name == "PermissionRequest":
        current["permission_requests"] += 1
    elif event_name == "PostToolUse":
        if current["correction_pending"] and _has_successful_progress(event):
            current["successful_progress_events"] += 1
            current["progress_since_correction"] = True
            reason_codes.append("progress_evidence")
    elif event_name == "PreCompact":
        current["pre_compact_seen"] = True
    elif event_name == "PostCompact":
        current["post_compact_seen"] = True

    current["armed"] = _is_armed(current, config)
    arm_reasons = _arm_reasons(current, config)
    action = "allow"
    if event_name == "Stop":
        current["stop_events"] += 1
        assistant_text = _event_text(event, "last_assistant_message", "assistant_message", "draft", "output")
        rhetoric = event.get("recovery_rhetoric_detected") is True or detect_recovery_rhetoric(assistant_text)
        substantive = event.get("substantive_response_detected") is True or detect_substantive_response(assistant_text)
        current["last_stop_recovery_rhetoric"] = rhetoric
        current["last_stop_substantive"] = substantive
        should_audit = bool(
            current["armed"]
            and current["correction_pending"]
            and rhetoric
            and not substantive
            and not current["progress_since_correction"]
            and not current["audit_issued_for_episode"]
        )
        if (
            current["audit_blocked_for_episode"]
            and current["correction_pending"]
            and event.get("stop_hook_active") is True
        ):
            packet_valid = detect_recovery_audit_packet(assistant_text)
            current["audit_responses"] += 1
            current["audit_packet_valid"] = packet_valid
            current["correction_pending"] = False
            current["phase"] = "awaiting_user"
            action = "handoff"
            reason_codes.append("audit_packet_valid" if packet_valid else "audit_packet_unstructured")
        elif current["audit_blocked_for_episode"] and current["correction_pending"]:
            # Only the host-marked continuation can consume an audit request.
            # A near-duplicate inactive Stop may differ in incidental payload
            # fields, so preserve and replay the existing audit instead of
            # misclassifying the original response as the audit packet.
            current["phase"] = "audit_requested"
            action = "audit"
            reason_codes.append("awaiting_active_audit_response")
        elif should_audit and block_audit and current["audit_blocks"] >= MAX_AUDIT_BLOCKS_PER_SESSION:
            reason_codes.append("session_audit_limit_reached")
        elif should_audit:
            current["audit_issued_for_episode"] = consume_audit
            current["audit_blocked_for_episode"] = bool(consume_audit and block_audit)
            if current["audit_blocked_for_episode"]:
                current["audit_blocks"] += 1
            current["phase"] = "audit_requested" if current["audit_blocked_for_episode"] else "correction_pending"
            action = "audit"
            reason_codes.extend(
                ["context_pressure", "correction_pending", "recovery_rhetoric", "progress_evidence_missing"]
            )
        elif current["correction_pending"] and (
            current["progress_since_correction"]
            or substantive
            or (bool(assistant_text.strip()) and not rhetoric)
        ):
            current["correction_pending"] = False
            reason_codes.append("correction_resolved")
    sticky_phase = current["phase"] in {"audit_requested", "awaiting_user"} and event_name != "UserPromptSubmit"
    if action == "allow" and not sticky_phase:
        if current["correction_pending"]:
            current["phase"] = "correction_pending"
        elif current["armed"]:
            current["phase"] = "armed"
        else:
            current["phase"] = "passive"

    _remember_event(
        current,
        fingerprint,
        action,
        audit_blocked=bool(action == "audit" and current["audit_blocked_for_episode"]),
    )
    decision: dict[str, Any] = {
        "action": action,
        "reason_codes": reason_codes,
        "armed": current["armed"],
        "arm_reasons": arm_reasons,
        "episode": current["episode"],
        "phase": current["phase"],
    }
    if action == "audit":
        decision["required_fields"] = list(AUDIT_FIELDS)
    return current, decision


def load_state(path: Path, session_id: object = "") -> dict[str, Any]:
    """Load and validate state, or initialize it when no file exists."""

    if not path.exists():
        return new_state(session_id)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid recovery guard state: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("invalid recovery guard state: expected JSON object")
    _validate_state(value)
    expected_hash = hash_text(session_id)
    if session_id and value["session_hash"] != expected_hash:
        raise ValueError("recovery guard state belongs to a different session")
    return value


def save_state_atomic(path: Path, state: Mapping[str, Any]) -> None:
    """Atomically replace a state file with a validated, fsynced JSON object."""

    _validate_state(state)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.parent.chmod(0o700)
    except OSError:
        pass
    fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(dict(state), handle, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        try:
            path.chmod(0o600)
        except OSError:
            pass
        try:
            directory_fd = os.open(path.parent, os.O_RDONLY)
        except OSError:  # pragma: no cover - filesystem-specific.
            directory_fd = -1
        if directory_fd >= 0:
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
    finally:
        if temporary.exists():
            temporary.unlink()


def update_state_atomic(
    path: Path,
    event: Mapping[str, Any],
    thresholds: GuardThresholds | Mapping[str, object] | None = None,
    *,
    block_audit: bool = True,
    consume_audit: bool = True,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Lock, reduce, and atomically persist one session event."""

    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.parent.chmod(0o700)
    except OSError:
        pass
    lock_path = path.with_suffix(path.suffix + ".lock")
    with lock_path.open("a", encoding="utf-8") as lock_handle:
        try:
            lock_path.chmod(0o600)
        except OSError:
            pass
        if fcntl is not None:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
        try:
            try:
                state = load_state(path, event.get("session_id", ""))
            except ValueError:
                if event.get("hook_event_name") != "SessionStart" or str(event.get("source") or "").lower() != "clear":
                    raise
                state = new_state(event.get("session_id", ""))
            next_state, decision = reduce_event(
                state,
                event,
                thresholds,
                block_audit=block_audit,
                consume_audit=consume_audit,
            )
            save_state_atomic(path, next_state)
            return next_state, decision
        finally:
            if fcntl is not None:
                fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
