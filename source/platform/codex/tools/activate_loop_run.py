#!/usr/bin/env python3
"""Bind a LoopRun to the current session so the Stop hook finds it by session_id.

This is the activation bridge: init_loop_run.py creates a LoopRun on disk, but the
Stop hook cannot guess its path. Running this writes a session-scoped pointer the
hook resolves via session_id (no custom Stop payload field or parent env var).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from loop_policy import session_pointer_path, utc_now


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--loop-run-dir", required=True, type=Path)
    args = parser.parse_args()

    loop_dir = args.loop_run_dir.expanduser().resolve()
    if not (loop_dir / "state.yaml").is_file():
        print(f"FAIL: not a LoopRun dir (no state.yaml): {loop_dir}")
        return 2

    pointer = session_pointer_path(args.session_id)
    pointer.parent.mkdir(parents=True, exist_ok=True)
    pointer.write_text(
        json.dumps(
            {
                "session_id": args.session_id,
                "loop_run_dir": str(loop_dir),
                "status": "active",
                "activated_at": utc_now(),
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    pointer.chmod(0o600)
    print(json.dumps({"status": "PASS", "pointer": str(pointer), "loop_run_dir": str(loop_dir)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
