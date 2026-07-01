#!/usr/bin/env python3
"""Replay-first behavior eval runner for 8.3.1 execution assurance."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from _validation import is_iso_datetime, load_yaml_file, resolve_bundle_path


REQUIRED_RUN_FIELDS = {
    "run_id",
    "case_id",
    "host",
    "host_version",
    "model",
    "model_version",
    "bundle_version",
    "started_at",
    "observed_route",
    "observed_behaviors",
    "artifacts",
    "verification",
    "result",
}
RESULTS = {"pass", "partial", "fail"}


def plugin_runtime(root: Path) -> bool:
    return (root / ".codex" / "plugins" / "cache").exists()


def artifact_available(root: Path, artifact: str) -> bool:
    if artifact.startswith("/"):
        return False
    if (root / artifact).exists() or resolve_bundle_path(root, artifact) is not None:
        return True
    return plugin_runtime(root) and not artifact.startswith(".codex/")


def yaml_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(path.glob("*.yaml"))


def load_eval_cases(eval_path: Path) -> tuple[dict[str, dict[str, Any]], list[str]]:
    errors: list[str] = []
    cases: dict[str, dict[str, Any]] = {}
    for path in yaml_files(eval_path):
        try:
            data = load_yaml_file(path)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{path}: invalid YAML: {exc}")
            continue
        if not isinstance(data, dict):
            continue
        raw_cases = data.get("cases")
        if not isinstance(raw_cases, list):
            continue
        for idx, case in enumerate(raw_cases):
            if not isinstance(case, dict):
                errors.append(f"{path}: cases[{idx}] is not a mapping")
                continue
            case_id = case.get("case_id")
            if not isinstance(case_id, str) or not case_id:
                errors.append(f"{path}: cases[{idx}] missing case_id")
                continue
            if case_id in cases:
                errors.append(f"{path}: duplicate case_id {case_id}")
                continue
            cases[case_id] = case
    if not cases:
        errors.append(f"{eval_path}: no eval cases found")
    return cases, errors


def load_run(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        data = load_yaml_file(path)
    except Exception as exc:  # noqa: BLE001
        return None, [f"invalid YAML: {exc}"]
    if not isinstance(data, dict):
        return None, ["expected top-level mapping"]
    return data, []


def validate_verification(run: dict[str, Any], case: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    verification = run.get("verification")
    if not isinstance(verification, list) or not verification:
        return ["verification must be a non-empty list of structured evidence records"]
    for idx, record in enumerate(verification):
        if not isinstance(record, dict):
            errors.append(f"verification[{idx}] must be a mapping")
            continue
        if not isinstance(record.get("type"), str) or not record.get("type"):
            errors.append(f"verification[{idx}] missing type")
        if record.get("type") == "command_exit":
            if not isinstance(record.get("command"), str) or not record.get("command"):
                errors.append(f"verification[{idx}] command_exit missing command")
            if not isinstance(record.get("exit_code"), int):
                errors.append(f"verification[{idx}] command_exit missing integer exit_code")
        checked_at = record.get("checked_at")
        if checked_at is not None and not is_iso_datetime(checked_at):
            errors.append(f"verification[{idx}] checked_at must be ISO datetime")
    for required in case.get("required_evidence", []) or []:
        if not isinstance(required, dict):
            errors.append("required_evidence item must be a mapping")
            continue
        evidence_type = required.get("type")
        matches = [record for record in verification if isinstance(record, dict) and record.get("type") == evidence_type]
        if not matches:
            errors.append(f"missing required evidence type {evidence_type!r}")
            continue
        if evidence_type == "command_exit" and "expected" in required:
            expected = required["expected"]
            if not any(record.get("exit_code") == expected for record in matches):
                errors.append(f"missing command_exit evidence with exit_code {expected!r}")
    return errors


def validate_run(path: Path, cases: dict[str, dict[str, Any]], root: Path, bundle_version: str) -> tuple[str, list[str]]:
    errors: list[str] = []
    data, load_errors = load_run(path)
    errors.extend(load_errors)
    if data is None:
        return path.name, errors
    missing = sorted(REQUIRED_RUN_FIELDS - set(data))
    for field in missing:
        errors.append(f"missing {field}")
    run_id = data.get("run_id", path.name)
    case_id = data.get("case_id")
    case = cases.get(case_id) if isinstance(case_id, str) else None
    if case is None:
        errors.append(f"case_id does not resolve to eval case: {case_id!r}")
    result = data.get("result")
    if result not in RESULTS:
        errors.append(f"invalid result {result!r}")
    if data.get("bundle_version") != bundle_version:
        errors.append(f"bundle_version {data.get('bundle_version')!r} != expected {bundle_version!r}")
    if not is_iso_datetime(data.get("started_at")):
        errors.append("started_at must be ISO datetime")
    observed_behaviors = data.get("observed_behaviors")
    if not isinstance(observed_behaviors, list) or not all(isinstance(item, str) for item in observed_behaviors):
        errors.append("observed_behaviors must be a list of strings")
        observed_behaviors = []
    artifacts = data.get("artifacts")
    if not isinstance(artifacts, list) or not all(isinstance(item, str) for item in artifacts):
        errors.append("artifacts must be a list of repo-relative strings")
        artifacts = []
    else:
        for artifact in artifacts:
            if not artifact_available(root, artifact):
                errors.append(f"artifact not found or not repo-relative: {artifact}")
    if result == "pass" and not observed_behaviors:
        errors.append("pass result requires observed_behaviors")
    if case is not None:
        expected_route = case.get("expected_primary_skill")
        observed_route = data.get("observed_route")
        if expected_route is None:
            if observed_route not in {None, "", "none", "null"}:
                errors.append(f"observed_route {observed_route!r} should be empty for no-primary-skill case")
        elif observed_route != expected_route:
            errors.append(f"observed_route {observed_route!r} != expected_primary_skill {expected_route!r}")
        expected_behaviors = case.get("expected_behaviors", []) or []
        forbidden_behaviors = case.get("forbidden_behaviors", []) or []
        for behavior in expected_behaviors:
            if behavior not in observed_behaviors:
                errors.append(f"missing expected behavior {behavior!r}")
        for behavior in forbidden_behaviors:
            if behavior in observed_behaviors:
                errors.append(f"observed forbidden behavior {behavior!r}")
        errors.extend(validate_verification(data, case))
    return str(run_id), errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["replay", "host-assisted", "live"], default="replay")
    parser.add_argument("--eval-path", type=Path, default=Path(".codex/eval"))
    parser.add_argument("--observed-runs", type=Path, default=Path(".codex/eval/observed-runs"))
    parser.add_argument("--bundle-version", default="8.3.1")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()
    if args.mode != "replay":
        print(f"SKIP: mode {args.mode!r} is not implemented in 8.3.1 replay pilot")
        return 0
    if not args.observed_runs.exists():
        print(f"SKIP: observed runs path not found: {args.observed_runs}")
        return 0
    cases, case_errors = load_eval_cases(args.eval_path)
    paths = yaml_files(args.observed_runs)
    if not paths:
        print("SKIP: no observed runs")
        return 0
    checks = []
    failed = bool(case_errors)
    root = Path(".").resolve()
    for path in paths:
        run_id, errors = validate_run(path, cases, root, args.bundle_version)
        status = "FAIL" if errors else "PASS"
        failed = failed or bool(errors)
        checks.append({"run_id": run_id, "path": path.as_posix(), "status": status, "errors": errors})
    report = {"mode": args.mode, "status": "FAIL" if failed else "PASS", "case_errors": case_errors, "runs": checks}
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(report["status"])
        for error in case_errors:
            print(f"- eval cases: {error}")
        for check in checks:
            print(f"- {check['run_id']}: {check['status']}")
            for error in check["errors"]:
                print(f"  - {error}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
