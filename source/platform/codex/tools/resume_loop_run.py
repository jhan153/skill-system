#!/usr/bin/env python3
"""Explicitly reopen a terminal LoopRun.

Terminal LoopRun states (success / blocked / budget_exhausted / unsafe / fatal /
stalled) are immutable to evaluate_loop_run.py. Reopening one is a deliberate act
that must go through this command, which records an audit event and resets the run
to active. This keeps "the loop succeeded" from being silently overwritten by a
late or stray iteration result.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from loop_policy import append_jsonl, load_yaml, loop_lock, utc_now, write_yaml

TERMINAL_STATUSES = {"success", "blocked", "budget_exhausted", "unsafe", "fatal", "stalled"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("loop_run_dir", type=Path)
    parser.add_argument("--reason", required=True)
    args = parser.parse_args()

    with loop_lock(args.loop_run_dir):
        state_path = args.loop_run_dir / "state.yaml"
        if not state_path.is_file():
            print(f"FAIL: no state.yaml: {state_path}")
            return 2
        state = load_yaml(state_path)
        if not isinstance(state, dict):
            print("FAIL: state.yaml must be a mapping")
            return 2
        status = state.get("status")
        if status == "active":
            print("FAIL: loop is already active; resume only reopens terminal loops")
            return 1
        if status not in TERMINAL_STATUSES:
            print(f"FAIL: unexpected status {status!r}; not a terminal loop")
            return 1

        now = utc_now()
        state["status"] = "active"
        state["updated_at"] = now
        state.setdefault("resumes", []).append({"from": str(status), "reason": args.reason, "resumed_at": now})
        write_yaml(state_path, state)
        append_jsonl(
            args.loop_run_dir / "loop-events.jsonl",
            {
                "recorded_at": now,
                "event": "loop_resumed",
                "loop_run_id": state.get("loop_run_id"),
                "from_status": str(status),
                "reason": args.reason,
            },
        )
        print(json.dumps({"status": "PASS", "loop_run_id": state.get("loop_run_id"), "reopened_from": status}, sort_keys=True))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
