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
    body = json.dumps(event, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


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
        "schema_version": 1,
        "recorded_at": utc_now(),
        "neutral_event": args.event,
        "host": args.host,
        "host_event": args.host_event,
        "support_level": args.support_level,
        "tool_id": args.tool_id,
        "status": args.status,
        "evidence": evidence,
    }
    payload["event_hash"] = event_hash(payload)
    args.ledger.parent.mkdir(parents=True, exist_ok=True)
    with args.ledger.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True, ensure_ascii=True) + "\n")
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
