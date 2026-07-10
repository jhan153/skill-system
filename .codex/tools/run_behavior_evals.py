#!/usr/bin/env python3
"""Validate replayed or host-assisted behavior-eval evidence."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from _validation import is_iso_datetime, load_json_file, load_yaml_file, resolve_bundle_path, validate_schema


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
PLACEHOLDER_METADATA = {"", "unknown", "unspecified", "none", "n/a", "na"}


def plugin_runtime(root: Path) -> bool:
    return (root / ".codex" / "plugins" / "cache").exists()


def artifact_available(root: Path, artifact: str) -> bool:
    if artifact.startswith("/"):
        return False
    if (root / artifact).exists() or resolve_bundle_path(root, artifact) is not None:
        return True
    return plugin_runtime(root) and not artifact.startswith(".codex/")


def strict_artifact_path(root: Path, artifact: str) -> Path | None:
    relative = Path(artifact)
    if relative.is_absolute() or ".." in relative.parts:
        return None
    resolved_root = root.resolve()
    candidate = (resolved_root / relative).resolve()
    try:
        candidate.relative_to(resolved_root)
    except ValueError:
        return None
    if candidate.is_file():
        return candidate
    resolved = resolve_bundle_path(root, artifact)
    if resolved is None or not resolved.is_file():
        return None
    resolved = resolved.resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError:
        return None
    return resolved


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def files_are_distinct(first: Path | None, second: Path | None) -> bool:
    if first is None or second is None:
        return False
    try:
        return not first.samefile(second)
    except OSError:
        return False


def parse_iso_datetime(value: object) -> dt.datetime | None:
    if not isinstance(value, str) or not is_iso_datetime(value):
        return None
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def timestamp_in_window(
    value: object,
    not_before: dt.datetime | None,
    not_after: dt.datetime | None,
) -> bool:
    parsed = parse_iso_datetime(value)
    if parsed is None:
        return False
    return (not_before is None or parsed >= not_before) and (
        not_after is None or parsed <= not_after
    )


def yaml_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(path.glob("*.yaml"))


def load_eval_cases(
    eval_path: Path,
    schema_path: Path | None = None,
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    errors: list[str] = []
    cases: dict[str, dict[str, Any]] = {}
    schema: dict[str, Any] | None = None
    if schema_path is not None:
        try:
            loaded_schema = load_json_file(schema_path)
        except Exception as exc:  # noqa: BLE001
            return {}, [f"{schema_path}: invalid eval schema: {exc}"]
        if not isinstance(loaded_schema, dict):
            return {}, [f"{schema_path}: expected schema mapping"]
        schema = loaded_schema
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
            if schema is not None:
                for error in validate_schema(case, schema):
                    errors.append(f"{path}: {case_id}: {error}")
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
        elif "expected" in required:
            expected = required["expected"]
            if not any(record.get("value") == expected for record in matches):
                errors.append(f"missing {evidence_type} evidence with value {expected!r}")
    return errors


def validate_run(
    path: Path,
    cases: dict[str, dict[str, Any]],
    root: Path,
    bundle_version: str,
    *,
    strict_host_assisted: bool = False,
    required_model: str | None = None,
    not_before: dt.datetime | None = None,
    not_after: dt.datetime | None = None,
) -> tuple[str, list[str]]:
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
    if strict_host_assisted and result != "pass":
        errors.append(f"host-assisted release evidence requires result 'pass', got {result!r}")
    if data.get("bundle_version") != bundle_version:
        errors.append(f"bundle_version {data.get('bundle_version')!r} != expected {bundle_version!r}")
    started_at = parse_iso_datetime(data.get("started_at"))
    if started_at is None:
        errors.append("started_at must be ISO datetime")
    elif not_before is not None and started_at < not_before:
        errors.append(
            f"started_at {data.get('started_at')!r} predates required evidence window {not_before.isoformat()!r}"
        )
    elif not_after is not None and started_at > not_after:
        errors.append(
            f"started_at {data.get('started_at')!r} exceeds required evidence window {not_after.isoformat()!r}"
        )
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
            available = (
                strict_artifact_path(root, artifact) is not None
                if strict_host_assisted
                else artifact_available(root, artifact)
            )
            if not available:
                errors.append(f"artifact not found or not repo-relative: {artifact}")
    if strict_host_assisted:
        for field in ("host", "host_version", "model", "model_version"):
            value = data.get(field)
            if not isinstance(value, str) or value.strip().lower() in PLACEHOLDER_METADATA:
                errors.append(f"host-assisted release evidence requires attested {field}")
        if not artifacts:
            errors.append("host-assisted release evidence requires at least one raw artifact")
        verification = data.get("verification")
        records = verification if isinstance(verification, list) else []
        checksum_records = [
            item for item in records if isinstance(item, dict) and item.get("type") == "artifact_sha256"
        ]
        for artifact in artifacts:
            path_match = strict_artifact_path(root, artifact)
            matching = [item for item in checksum_records if item.get("artifact") == artifact]
            if not matching:
                errors.append(f"host-assisted artifact lacks artifact_sha256 binding: {artifact}")
            elif path_match is not None:
                actual = sha256_file(path_match)
                if not any(item.get("sha256") == actual for item in matching):
                    errors.append(f"host-assisted artifact sha256 mismatch: {artifact}")
        qualitative_reviews = [
            item
            for item in records
            if isinstance(item, dict)
            and item.get("type") == "qualitative_review"
            and item.get("value") == "pass"
        ]
        valid_qualitative_review = False
        for item in qualitative_reviews:
            reviewed_artifact = item.get("artifact")
            review_artifact = item.get("review_artifact")
            reviewed_path = (
                strict_artifact_path(root, reviewed_artifact)
                if isinstance(reviewed_artifact, str)
                else None
            )
            review_path = (
                strict_artifact_path(root, review_artifact)
                if isinstance(review_artifact, str)
                else None
            )
            reviewed_digest = sha256_file(reviewed_path) if reviewed_path is not None else None
            checked_at = parse_iso_datetime(item.get("checked_at"))
            if (
                isinstance(item.get("reviewer"), str)
                and item.get("reviewer", "").strip().lower() not in PLACEHOLDER_METADATA
                and reviewed_artifact in artifacts
                and review_artifact in artifacts
                and review_artifact != reviewed_artifact
                and files_are_distinct(reviewed_path, review_path)
                and reviewed_digest is not None
                and item.get("reviewed_sha256") == reviewed_digest
                and checked_at is not None
                and started_at is not None
                and checked_at >= started_at
                and timestamp_in_window(item.get("checked_at"), not_before, not_after)
            ):
                valid_qualitative_review = True
                break
        if not valid_qualitative_review:
            errors.append(
                "host-assisted release evidence requires a fresh named review bound to the exact reviewed bytes and review artifact"
            )
        model_identity = [
            item
            for item in records
            if isinstance(item, dict) and item.get("type") == "model_identity"
        ]
        if not any(item.get("value") == data.get("model") for item in model_identity):
            errors.append("host-assisted model_identity must match run model")
    if required_model is not None and data.get("model") != required_model:
        errors.append(f"model {data.get('model')!r} != required model {required_model!r}")
    if result == "pass" and not observed_behaviors:
        errors.append("pass result requires observed_behaviors")
    if case is not None:
        expected_route = case.get("expected_primary_skill")
        expected_route_class = case.get("expected_route_class")
        observed_route = data.get("observed_route")
        if expected_route is None:
            if observed_route not in {None, "", "none", "null"}:
                errors.append(f"observed_route {observed_route!r} should be empty for no-primary-skill case")
        elif observed_route != expected_route:
            errors.append(f"observed_route {observed_route!r} != expected_primary_skill {expected_route!r}")
        if isinstance(expected_route_class, str) and expected_route_class:
            observed_route_class = data.get("observed_route_class")
            if observed_route_class != expected_route_class:
                errors.append(
                    f"observed_route_class {observed_route_class!r} != expected_route_class {expected_route_class!r}"
                )
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
    parser.add_argument("--eval-schema", type=Path)
    parser.add_argument("--observed-runs", type=Path, default=Path(".codex/eval/observed-runs"))
    parser.add_argument("--bundle-version", default="9.1.1")
    parser.add_argument("--required-model")
    parser.add_argument("--require-all-cases", action="store_true")
    parser.add_argument("--not-before", help="reject evidence recorded before this ISO datetime")
    parser.add_argument("--not-after", help="reject evidence recorded after this ISO datetime")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()
    not_before = parse_iso_datetime(args.not_before) if args.not_before else None
    not_after = parse_iso_datetime(args.not_after) if args.not_after else None
    if args.not_before and not_before is None:
        print(f"FAIL: --not-before must be an ISO datetime: {args.not_before!r}")
        return 2
    if args.not_after and not_after is None:
        print(f"FAIL: --not-after must be an ISO datetime: {args.not_after!r}")
        return 2
    if not_before is not None and not_after is not None and not_before > not_after:
        print("FAIL: --not-before must not be later than --not-after")
        return 2
    if args.mode == "host-assisted" and args.eval_schema is None:
        print("FAIL: host-assisted mode requires --eval-schema")
        return 2
    if args.mode == "live":
        print("SKIP: live execution is external to this evidence validator")
        return 0
    if not args.observed_runs.exists():
        if args.mode == "host-assisted":
            print(f"FAIL: observed runs path not found: {args.observed_runs}")
            return 1
        print(f"SKIP: observed runs path not found: {args.observed_runs}")
        return 0
    cases, case_errors = load_eval_cases(args.eval_path, args.eval_schema)
    paths = yaml_files(args.observed_runs)
    if not paths:
        if args.mode == "host-assisted":
            print("FAIL: no host-assisted observed runs")
            return 1
        print("SKIP: no observed runs")
        return 0
    checks = []
    failed = bool(case_errors)
    observed_case_ids: set[str] = set()
    root = Path(".").resolve()
    for path in paths:
        raw_run, _ = load_run(path)
        if isinstance(raw_run, dict) and isinstance(raw_run.get("case_id"), str):
            observed_case_ids.add(raw_run["case_id"])
        run_id, errors = validate_run(
            path,
            cases,
            root,
            args.bundle_version,
            strict_host_assisted=args.mode == "host-assisted",
            required_model=args.required_model,
            not_before=not_before,
            not_after=not_after,
        )
        status = "FAIL" if errors else "PASS"
        failed = failed or bool(errors)
        checks.append({"run_id": run_id, "path": path.as_posix(), "status": status, "errors": errors})
    coverage_errors: list[str] = []
    if args.require_all_cases:
        missing_case_ids = sorted(set(cases) - observed_case_ids)
        if missing_case_ids:
            coverage_errors.append("missing observed run for cases: " + ", ".join(missing_case_ids))
            failed = True
    report = {
        "mode": args.mode,
        "status": "FAIL" if failed else "PASS",
        "case_errors": case_errors,
        "coverage_errors": coverage_errors,
        "runs": checks,
    }
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(report["status"])
        for error in case_errors:
            print(f"- eval cases: {error}")
        for error in coverage_errors:
            print(f"- coverage: {error}")
        for check in checks:
            print(f"- {check['run_id']}: {check['status']}")
            for error in check["errors"]:
                print(f"  - {error}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
