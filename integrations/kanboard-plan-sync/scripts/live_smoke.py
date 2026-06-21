#!/usr/bin/env python3
"""Guarded live smoke test against a running Kanboard.

This is NOT a unit test and is never run by the test suite. It performs real
JSON-RPC writes, so it is double-gated:

1. a Kanboard API token must be present in the env var named by the workspace
   config (`token_env`, default ``KANBOARD_API_TOKEN``);
2. ``--confirm`` must be passed to actually write.

Without ``--confirm`` it prints the dry-run plan and exits without writing.

Usage:
    python scripts/live_smoke.py <workspace> <plan_path> [--confirm]

Prereq: start Kanboard first (``~/.ai/infra/kanboard-local/serve.sh``)
and export the token (``export KANBOARD_API_TOKEN=...``).
"""

from __future__ import annotations

import argparse
import json
import sys

# Allow running from the repo without installing the package.
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from kanboard_plan_sync_mcp.tools import run_tool  # noqa: E402


def _print(title, obj):
    print(f"\n=== {title} ===")
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Guarded live Kanboard smoke test.")
    parser.add_argument("workspace")
    parser.add_argument("plan_path")
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="actually write to Kanboard (otherwise dry-run only)",
    )
    args = parser.parse_args(argv)

    # Resolve a relative plan path against the workspace root.
    plan_path = Path(args.plan_path)
    if not plan_path.is_file():
        candidate = Path(args.workspace) / args.plan_path
        if candidate.is_file():
            plan_path = candidate
    common = {"workspace": args.workspace, "plan_path": str(plan_path)}

    # Always show the dry-run projection first.
    _print("sync (dry-run)", run_tool("sync_plan_to_board", {**common, "dry_run": True}))

    if not args.confirm:
        print(
            "\n[guarded] pass --confirm to apply to a live Kanboard. "
            "Ensure serve.sh is running and the API token env var is set."
        )
        return 0

    _print("create_board (live)", run_tool("create_board_from_plan", {**common, "dry_run": False}))
    sync = run_tool("sync_plan_to_board", {**common, "dry_run": False})
    _print("sync (live)", sync)
    _print("pull (live snapshot)", run_tool("pull_board_status", common))

    status = sync.get("status")
    if status == "needs_live_kanboard":
        print("\n[blocked] no live connection — is Kanboard running and the token set?")
        return 2
    return 0 if status == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
