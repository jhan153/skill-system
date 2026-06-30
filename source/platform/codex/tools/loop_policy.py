#!/usr/bin/env python3
"""Shared helpers for bounded verification loop state."""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import subprocess
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

try:
    import fcntl
except ImportError:  # pragma: no cover - non-POSIX fallback.
    fcntl = None  # type: ignore[assignment]


LOOP_STATUSES = {"active", "success", "blocked", "budget_exhausted", "unsafe", "fatal", "stalled"}
CONDITION_STATUSES = {"pass", "fail", "unverified", "blocked"}
DECISION_ACTIONS = {"success", "continue", "recover", "pause", "blocked", "budget_exhausted", "unsafe", "fatal"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def elapsed_seconds(started_at: str, now: str) -> int:
    """Whole seconds between two ISO-8601 timestamps (0 on parse failure)."""
    try:
        start = datetime.fromisoformat(str(started_at).replace("Z", "+00:00"))
        end = datetime.fromisoformat(str(now).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return 0
    return max(0, int((end - start).total_seconds()))


def canonical_hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_id(value: str, fallback: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in "._-" else "-" for ch in value).strip(".-")
    return cleaned[:96] or fallback


def active_loops_dir() -> Path:
    """Host-stable directory holding session->LoopRun activation pointers.

    Lives under CODEX_HOME (default ~/.codex) so the activation tool (run from a
    project cwd) and the Stop hook (whose ROOT differs) agree on one location.
    The Stop hook mirrors this resolution inline to avoid importing yaml.
    """
    base = os.environ.get("CODEX_HOME") or str(Path.home() / ".codex")
    return Path(base).expanduser() / "harness" / "active-loops"


def session_pointer_path(session_id: str) -> Path:
    return active_loops_dir() / f"{safe_id(str(session_id), 'unknown-session')}.json"


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def write_yaml(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value, sort_keys=False, allow_unicode=False), encoding="utf-8")


def git_revision(root: Path) -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=5,
        )
    except Exception:  # noqa: BLE001 - revision is metadata only.
        return "unversioned"
    revision = completed.stdout.strip()
    return revision if completed.returncode == 0 and revision else "unversioned"


def workspace_id(root: Path) -> str:
    return hashlib.sha256(str(root.resolve()).encode("utf-8", errors="replace")).hexdigest()[:16]


def success_conditions(contract: dict[str, Any]) -> list[dict[str, Any]]:
    goal = contract.get("goal") if isinstance(contract.get("goal"), dict) else {}
    raw_conditions = goal.get("success_conditions", [])
    return [item for item in raw_conditions if isinstance(item, dict) and isinstance(item.get("id"), str)]


def required_condition_ids(contract: dict[str, Any]) -> list[str]:
    return [condition["id"] for condition in success_conditions(contract) if condition.get("required", True) is not False]


def control_value(contract: dict[str, Any], key: str, default: int) -> int:
    control = contract.get("control") if isinstance(contract.get("control"), dict) else {}
    value = control.get(key, default)
    return value if isinstance(value, int) and value >= 0 else default


def condition_map(state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    results = state.get("condition_results", [])
    return {
        item["condition_id"]: item
        for item in results
        if isinstance(item, dict) and isinstance(item.get("condition_id"), str)
    }


def passed_required_count(contract: dict[str, Any], state: dict[str, Any]) -> int:
    results = condition_map(state)
    return sum(1 for condition_id in required_condition_ids(contract) if results.get(condition_id, {}).get("status") == "pass")


def state_fingerprint(contract: dict[str, Any], state: dict[str, Any]) -> str:
    results = condition_map(state)
    body = {
        "required": [
            {
                "id": condition_id,
                "status": results.get(condition_id, {}).get("status", "unverified"),
                "failure_fingerprint": results.get(condition_id, {}).get("failure_fingerprint"),
            }
            for condition_id in required_condition_ids(contract)
        ],
        "iteration": state.get("iteration"),
    }
    return canonical_hash(body)


def append_jsonl(path: Path, event: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True, ensure_ascii=True) + "\n")


@contextlib.contextmanager
def loop_lock(loop_dir: Path) -> Iterator[None]:
    """Exclusive advisory lock guarding a LoopRun's read-modify-write cycle.

    Prevents two concurrent Stop-hook evaluations from corrupting the same
    LoopRun state. Degrades to a no-op lock on platforms without fcntl.
    """
    loop_dir = Path(loop_dir)
    loop_dir.mkdir(parents=True, exist_ok=True)
    handle = (loop_dir / ".lock").open("w", encoding="utf-8")
    try:
        if fcntl is not None:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        yield
    finally:
        try:
            if fcntl is not None:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        finally:
            handle.close()
