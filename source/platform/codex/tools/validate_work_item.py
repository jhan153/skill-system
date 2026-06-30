#!/usr/bin/env python3
"""Validate a WorkItem lifecycle artifact against schema and lifecycle gates."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from _validation import load_json_file, load_yaml_file, validate_schema

SCHEMA = Path(__file__).resolve().parent.parent / "schemas" / "workitem" / "work-item.schema.json"
STATES = ["triage", "explore", "ready", "implement", "verify", "review", "closed"]
ALLOWED_TRANSITIONS = {
    "triage": {"triage", "explore", "blocked"},
    "explore": {"explore", "triage", "ready", "blocked"},
    "ready": {"ready", "explore", "implement", "blocked"},
    "implement": {"implement", "ready", "verify", "blocked"},
    "verify": {"verify", "implement", "review", "blocked"},
    "review": {"review", "implement", "verify", "closed", "blocked"},
    "blocked": {"triage", "explore", "ready", "implement", "verify", "review", "closed", "blocked"},
    "closed": {"closed"},
}


def lifecycle_errors(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    history = data.get("history")
    if isinstance(history, list) and history:
        last = history[-1].get("state") if isinstance(history[-1], dict) else None
        if last != data.get("state"):
            errors.append(f"history[-1].state {last!r} must match state {data.get('state')!r}")
        previous = None
        for idx, item in enumerate(history):
            if not isinstance(item, dict):
                continue
            current = item.get("state")
            if previous is not None and current not in ALLOWED_TRANSITIONS.get(previous, set()):
                errors.append(f"invalid transition history[{idx - 1}].state {previous!r} -> history[{idx}].state {current!r}")
            previous = current
    if data.get("state") == "closed":
        unresolved = [
            item.get("id", "<unknown>")
            for item in data.get("open_findings", [])
            if isinstance(item, dict) and item.get("status") in {"open", "blocked"}
        ]
        if unresolved:
            errors.append(f"closed WorkItem has unresolved findings: {', '.join(unresolved)}")
        if data.get("next_action"):
            errors.append("closed WorkItem must leave next_action empty")
    if data.get("state") in {"ready", "implement", "verify", "review", "closed"} and not data.get("primary_skill"):
        errors.append(f"{data.get('state')} WorkItem must set primary_skill")
    runtime = data.get("runtime_boundary") if isinstance(data.get("runtime_boundary"), dict) else {}
    for key in ["queue_runtime", "scheduler_runtime", "kanboard_source_of_truth", "looprun_replacement"]:
        if runtime.get(key) is not False:
            errors.append(f"runtime_boundary.{key} must be false in the 8.5.0 state model")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("work_item", type=Path)
    args = parser.parse_args()
    if not args.work_item.exists():
        print(f"FAIL: WorkItem not found: {args.work_item}")
        return 2
    schema = load_json_file(SCHEMA)
    data = load_yaml_file(args.work_item)
    errors = validate_schema(data, schema)
    if isinstance(data, dict):
        errors.extend(lifecycle_errors(data))
    print("FAIL" if errors else "PASS")
    for error in errors:
        print(f"- {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
