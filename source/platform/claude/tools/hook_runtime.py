#!/usr/bin/env python3
"""Claude-owned opt-in hook event recorder for execution-assurance evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True

try:
    import fcntl
except ModuleNotFoundError:  # pragma: no cover - non-POSIX fallback.
    fcntl = None


NEUTRAL_EVENTS = {
    "request_received",
    "context_loaded",
    "tool_preflight",
    "permission_requested",
    "tool_result",
    "tool_batch_completed",
    "turn_finalize_attempt",
    "turn_finalize",
    "compact_before",
    "compact_after",
}
SUPPORT_LEVELS = {"native", "approximate", "unsupported"}
STATUSES = {"pass", "warn", "fail", "skip"}
ZERO_HASH = "0" * 64
FALLBACK_LEDGER_NAME = "hook-events.jsonl"
STANDALONE_RUN_ID = "standalone"
CHAIN_TAIL_BYTES = 1024 * 1024
RECOVERY_GUARD_DISABLED = {"0", "false", "off", "no", "none", "disabled"}
RECOVERY_GUARD_AUDIT = {"audit", "strict", "block"}


def configured_ledger() -> Path | None:
    configured = os.environ.get("SKILL_SYSTEM_HOOK_LEDGER")
    if configured:
        return Path(configured)
    return None


def default_ledger_root() -> Path:
    codex_home = os.environ.get("CODEX_HOME") or str(Path.home() / ".codex")
    return Path(codex_home).expanduser() / "harness" / "hook-ledgers"


def stable_run_key(run_id: str) -> str:
    value = str(run_id or "") or STANDALONE_RUN_ID
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def default_ledger(run_id: str = "") -> Path:
    configured = configured_ledger()
    if configured is not None:
        return configured
    effective_run_id = run_id or os.environ.get("SKILL_SYSTEM_RUN_ID", "") or STANDALONE_RUN_ID
    return default_ledger_root() / stable_run_key(effective_run_id) / FALLBACK_LEDGER_NAME


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def agent_output_gate_mode() -> str:
    value = os.environ.get("SKILL_SYSTEM_AGENT_OUTPUT_GATE", "").strip().lower()
    return "strict" if value == "strict" else "observe"


def recovery_guard_mode() -> str:
    value = os.environ.get("SKILL_SYSTEM_RECOVERY_GUARD", "observe").strip().lower()
    if value in RECOVERY_GUARD_DISABLED:
        return "off"
    if value in RECOVERY_GUARD_AUDIT:
        return "audit"
    return "observe"


def parse_json_object(raw: str, label: str) -> dict[str, Any]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} must be a JSON object: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{label} must be a JSON object")
    return data


def event_hash(event: dict[str, Any]) -> str:
    body = dict(event)
    body.pop("event_hash", None)
    raw = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def run_id_for_ledger(ledger: Path, explicit_run_id: str = "") -> str:
    if explicit_run_id:
        return explicit_run_id
    configured = os.environ.get("SKILL_SYSTEM_RUN_ID", "")
    if configured:
        return configured
    return ledger.parent.name or "unknown-run"


def _latest_chain_state(lines: list[bytes]) -> tuple[int, str] | None:
    for raw_line in reversed(lines):
        if not raw_line.strip():
            continue
        try:
            event = json.loads(raw_line)
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(event, dict):
            continue
        seq = event.get("seq")
        event_hash_value = event.get("event_hash")
        if isinstance(seq, int) and isinstance(event_hash_value, str) and len(event_hash_value) == 64:
            return seq, event_hash_value
    return None


def last_chain_state(ledger: Path) -> tuple[int, str]:
    if not ledger.exists():
        return 0, ZERO_HASH
    with ledger.open("rb") as handle:
        handle.seek(0, os.SEEK_END)
        size = handle.tell()
        start = max(0, size - CHAIN_TAIL_BYTES)
        handle.seek(start)
        tail = handle.read()
    lines = tail.splitlines()
    if start and lines:
        lines = lines[1:]  # the first tail fragment may start inside a JSON record
    state = _latest_chain_state(lines)
    if state is not None:
        return state
    if start:
        state = _latest_chain_state(ledger.read_bytes().splitlines())
        if state is not None:
            return state
    return 0, ZERO_HASH


def add_chain_fields(payload: dict[str, Any], ledger: Path, run_id: str = "") -> dict[str, Any]:
    seq, previous = last_chain_state(ledger)
    payload["schema_version"] = 2
    payload["run_id"] = run_id_for_ledger(ledger, run_id)
    payload["seq"] = seq + 1
    payload["prev_event_hash"] = previous
    payload["event_hash"] = event_hash(payload)
    return payload


def lock_path_for(ledger: Path) -> Path:
    return ledger.with_suffix(ledger.suffix + ".lock")


def write_event_unlocked(payload: dict[str, Any], ledger: Path, run_id: str = "") -> dict[str, Any]:
    add_chain_fields(payload, ledger, run_id)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True, ensure_ascii=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    try:
        ledger.chmod(0o600)
    except OSError:
        pass
    return payload


def write_event(payload: dict[str, Any], ledger: Path, run_id: str = "") -> dict[str, Any]:
    ledger.parent.mkdir(parents=True, exist_ok=True)
    try:
        ledger.parent.chmod(0o700)
    except OSError:
        pass
    with lock_path_for(ledger).open("a", encoding="utf-8") as lock_handle:
        try:
            lock_path_for(ledger).chmod(0o600)
        except OSError:
            pass
        if fcntl is not None:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
        try:
            return write_event_unlocked(payload, ledger, run_id)
        finally:
            if fcntl is not None:
                fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)


def record(args: argparse.Namespace) -> int:
    if args.event not in NEUTRAL_EVENTS:
        print(f"FAIL: unsupported neutral event: {args.event}")
        return 2
    if args.support_level not in SUPPORT_LEVELS:
        print(f"FAIL: unsupported support level: {args.support_level}")
        return 2
    if args.status not in STATUSES:
        print(f"FAIL: unsupported status: {args.status}")
        return 2
    try:
        evidence = parse_json_object(args.evidence, "--evidence")
    except ValueError as exc:
        print(f"FAIL: {exc}")
        return 2
    payload = {
        "recorded_at": utc_now(),
        "neutral_event": args.event,
        "host": args.host,
        "host_event": args.host_event,
        "support_level": args.support_level,
        "tool_id": args.tool_id,
        "status": args.status,
        "evidence": evidence,
    }
    ledger = args.ledger if args.ledger is not None else default_ledger(args.run_id)
    write_event(payload, ledger, args.run_id)
    print(f"PASS: recorded {args.event} to {ledger}")
    return 0


def show(args: argparse.Namespace) -> int:
    if not args.ledger.exists():
        print(f"SKIP: hook ledger not found: {args.ledger}")
        return 0
    count = 0
    with args.ledger.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                count += 1
    print(f"PASS: hook ledger entries={count}")
    return 0


def status(_args: argparse.Namespace) -> int:
    print(json.dumps({
        "agent_output_gate_mode": agent_output_gate_mode(),
        "recovery_guard_mode": recovery_guard_mode(),
    }, sort_keys=True))
    return 0


def verify(args: argparse.Namespace) -> int:
    if not args.ledger.exists():
        print(f"FAIL: hook ledger not found: {args.ledger}")
        return 2
    errors: list[str] = []
    count = 0
    previous_seq = 0
    previous_hash = ZERO_HASH
    run_id = ""
    for line_no, line in enumerate(
        args.ledger.read_text(encoding="utf-8", errors="replace").splitlines(), start=1
    ):
        if not line.strip():
            continue
        count += 1
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"line {line_no}: invalid JSON: {exc}")
            continue
        if not isinstance(event, dict):
            errors.append(f"line {line_no}: expected JSON object")
            continue
        if event.get("event_hash") != event_hash(event):
            errors.append(f"line {line_no}: event_hash mismatch")
        if event.get("schema_version") == 2:
            seq = event.get("seq")
            current_run_id = event.get("run_id")
            if not isinstance(seq, int) or seq != previous_seq + 1:
                errors.append(f"line {line_no}: seq must increment from {previous_seq}")
            if event.get("prev_event_hash") != previous_hash:
                errors.append(f"line {line_no}: prev_event_hash mismatch")
            if not isinstance(current_run_id, str) or not current_run_id:
                errors.append(f"line {line_no}: schema v2 requires run_id")
            elif run_id and current_run_id != run_id:
                errors.append(f"line {line_no}: run_id changed within ledger")
            else:
                run_id = current_run_id
            if isinstance(seq, int):
                previous_seq = seq
            if isinstance(event.get("event_hash"), str):
                previous_hash = event["event_hash"]
    if not count:
        errors.append("ledger has no events")
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"PASS: hook ledger entries={count} hash_chain=valid")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    record_parser = sub.add_parser("record")
    record_parser.add_argument("--event", required=True)
    record_parser.add_argument("--host", required=True)
    record_parser.add_argument("--host-event", required=True)
    record_parser.add_argument("--support-level", required=True)
    record_parser.add_argument("--tool-id", default="")
    record_parser.add_argument("--status", default="pass")
    record_parser.add_argument("--evidence", default="{}")
    record_parser.add_argument("--ledger", type=Path, default=None)
    record_parser.add_argument("--run-id", default="")
    record_parser.set_defaults(func=record)
    show_parser = sub.add_parser("show")
    show_parser.add_argument("--ledger", type=Path, default=default_ledger())
    show_parser.set_defaults(func=show)
    status_parser = sub.add_parser("status")
    status_parser.set_defaults(func=status)
    verify_parser = sub.add_parser("verify")
    verify_parser.add_argument("--ledger", type=Path, default=default_ledger())
    verify_parser.set_defaults(func=verify)
    args = parser.parse_args()
    try:
        return args.func(args)
    except BrokenPipeError:
        return 1
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
