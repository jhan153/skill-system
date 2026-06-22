#!/usr/bin/env python3
"""Opt-in hook event recorder for execution-assurance evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
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


def default_ledger() -> Path:
    configured = os.environ.get("SKILL_SYSTEM_HOOK_LEDGER")
    if configured:
        return Path(configured)
    return Path(tempfile.gettempdir()) / "skill-system-hook-events.jsonl"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def last_chain_state(ledger: Path) -> tuple[int, str]:
    if not ledger.exists():
        return 0, ZERO_HASH
    seq = 0
    previous = ZERO_HASH
    for line in ledger.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        event_hash_value = event.get("event_hash")
        if isinstance(event.get("seq"), int):
            seq = max(seq, int(event["seq"]))
        else:
            seq += 1
        if isinstance(event_hash_value, str) and len(event_hash_value) == 64:
            previous = event_hash_value
    return seq, previous


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
    return payload


def write_event(payload: dict[str, Any], ledger: Path, run_id: str = "") -> dict[str, Any]:
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with lock_path_for(ledger).open("a", encoding="utf-8") as lock_handle:
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
    write_event(payload, args.ledger, args.run_id)
    print(f"PASS: recorded {args.event} to {args.ledger}")
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
    record_parser.add_argument("--ledger", type=Path, default=default_ledger())
    record_parser.add_argument("--run-id", default="")
    record_parser.set_defaults(func=record)
    show_parser = sub.add_parser("show")
    show_parser.add_argument("--ledger", type=Path, default=default_ledger())
    show_parser.set_defaults(func=show)
    args = parser.parse_args()
    try:
        return args.func(args)
    except BrokenPipeError:
        return 1
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
