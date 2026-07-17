#!/usr/bin/env python3
"""Run the bundle verification profiles in a repeatable order."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


DEFAULT_PROFILES = ["core", "execution", "research", "integrations", "loop"]
CHECK_STATUSES = {"PASS", "SKIP", "FAIL", "ERROR"}
RELEASE_REQUIRED_CHECK_IDS = {
    "core": {
        "doc_freshness",
        "tool_requirements",
        "reference_targets",
        "eval_cases",
        "source_registry",
        "invocation_surface_policy",
        "work_horizon_policy",
        "work_item_lifecycle",
        "release_identity",
        "generated_mirrors",
        "validator_unit_tests",
    },
    "execution": {
        "execution_assurance_artifacts",
    },
    "research": {"research_ledger"},
    "integrations": {"kanboard_integration"},
    "loop": {
        "loop_run_fixture",
        "loop_init_smoke",
        "loop_evidence_ledger",
        "loop_engineering_invariants",
    },
}


def validate_profile_report(report: object, profile: str, *, release: bool) -> str | None:
    if not isinstance(report, dict):
        return "profile report is not a JSON object"
    if report.get("profile") != profile:
        return f"profile identity {report.get('profile')!r} != expected {profile!r}"
    checks = report.get("checks")
    if not isinstance(checks, list) or not checks:
        return "profile report requires a non-empty checks list"
    statuses: list[str] = []
    required_statuses: list[str] = []
    check_ids: set[str] = set()
    for index, check in enumerate(checks):
        if not isinstance(check, dict):
            return f"checks[{index}] is not an object"
        if not isinstance(check.get("id"), str) or not check.get("id"):
            return f"checks[{index}] missing id"
        if check["id"] in check_ids:
            return f"duplicate check id {check['id']!r}"
        check_ids.add(check["id"])
        if not isinstance(check.get("required"), bool):
            return f"checks[{index}] missing boolean required"
        status = check.get("status")
        if status not in CHECK_STATUSES:
            return f"checks[{index}] has invalid status {status!r}"
        statuses.append(status)
        if check["required"]:
            required_statuses.append(status)
    expected_status = (
        "ERROR"
        if "ERROR" in required_statuses
        else "FAIL"
        if "FAIL" in required_statuses
        else "PASS_WITH_SKIPS"
        if "SKIP" in statuses
        else "PASS"
    )
    if report.get("status") != expected_status:
        return f"profile status {report.get('status')!r} != derived status {expected_status!r}"
    if release:
        missing = sorted(RELEASE_REQUIRED_CHECK_IDS[profile] - check_ids)
        if missing:
            return "release profile missing required checks: " + ", ".join(missing)
        nonpassing = [
            check["id"]
            for check in checks
            if isinstance(check, dict) and check.get("status") != "PASS"
        ]
        if nonpassing:
            return "release profile has non-PASS checks: " + ", ".join(nonpassing)
    return None


def run_profile(profile: str, root: Path, release: bool) -> dict[str, object]:
    cmd = [sys.executable, ".codex/tools/verify_bundle.py", "--profile", profile, "--format", "json", "--root", str(root)]
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
    validation_error = validate_profile_report(report, profile, release=release)
    if validation_error is not None:
        report = {
            "profile": profile,
            "status": "ERROR",
            "checks": [],
            "validation_error": validation_error,
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
    if args.release:
        missing_profiles = [profile for profile in DEFAULT_PROFILES if profile not in args.profiles]
        if missing_profiles:
            print("FAIL")
            print("- release requires profiles: " + ", ".join(missing_profiles))
            return 2
    reports = [run_profile(profile, root, args.release) for profile in args.profiles]
    allowed_statuses = {"PASS"} if args.release else {"PASS", "PASS_WITH_SKIPS"}
    failed = any(
        report.get("exit_code") not in {0, None}
        or report.get("status") not in allowed_statuses
        for report in reports
    )
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
