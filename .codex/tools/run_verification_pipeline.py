#!/usr/bin/env python3
"""Run the bundle verification profiles in a repeatable order."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


DEFAULT_PROFILES = ["core", "execution", "agent-output", "research", "integrations"]


def run_profile(profile: str, root: Path, release: bool) -> dict[str, object]:
    cmd = [sys.executable, ".codex/tools/verify_bundle.py", "--profile", profile, "--format", "json", "--root", str(root)]
    if release:
        cmd.append("--release")
    started = time.monotonic()
    completed = subprocess.run(
        cmd,
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=120,
    )
    try:
        report = json.loads(completed.stdout)
    except json.JSONDecodeError:
        report = {
            "profile": profile,
            "status": "ERROR",
            "checks": [],
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    report["exit_code"] = completed.returncode
    report["duration_ms"] = int((time.monotonic() - started) * 1000)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--profiles", nargs="+", default=DEFAULT_PROFILES)
    parser.add_argument("--release", action="store_true")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()
    root = args.root.resolve()
    reports = [run_profile(profile, root, args.release) for profile in args.profiles]
    failed = any(report.get("exit_code") not in {0, None} for report in reports)
    status = "FAIL" if failed else "PASS"
    pipeline = {"status": status, "profiles": reports}
    if args.format == "json":
        print(json.dumps(pipeline, indent=2))
    else:
        print(status)
        for report in reports:
            print(f"- {report.get('profile')}: {report.get('status')} ({report.get('duration_ms')} ms)")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
