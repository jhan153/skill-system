#!/usr/bin/env python3
"""Release a session's LoopRun activation pointer (terminal/abandoned loops).

Marks the session pointer inactive so the Stop hook stops driving continuations.
The pointer file is kept (status: inactive) for audit rather than deleted.
"""

from __future__ import annotations

import argparse
import json
import sys

sys.dont_write_bytecode = True

from loop_policy import session_pointer_path, utc_now


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--session-id", required=True)
    args = parser.parse_args()

    pointer = session_pointer_path(args.session_id)
    if not pointer.is_file():
        print(json.dumps({"status": "PASS", "note": "no active pointer", "session_id": args.session_id}, sort_keys=True))
        return 0
    try:
        info = json.loads(pointer.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        info = {"session_id": args.session_id}
    if not isinstance(info, dict):
        info = {"session_id": args.session_id}
    info["status"] = "inactive"
    info["deactivated_at"] = utc_now()
    pointer.write_text(json.dumps(info, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "pointer": str(pointer), "loop_status": "inactive"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
