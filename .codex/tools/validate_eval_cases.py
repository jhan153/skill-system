#!/usr/bin/env python3
"""Validate skill-system eval YAML files against the eval-case schema."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from _validation import load_json_file, load_yaml_file, validate_schema


def candidate_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    return sorted(path for path in root.glob("*.yaml") if path.name != "usage_quality_report.template.md")


def load_cases(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    errors: list[str] = []
    try:
        data = load_yaml_file(path)
    except Exception as exc:  # noqa: BLE001 - validator CLI reports parse failures.
        return [], [f"{path}: invalid YAML: {exc}"]
    if not isinstance(data, dict):
        return [], [f"{path}: expected top-level mapping"]
    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        return [], [f"{path}: missing non-empty cases list"]
    valid_cases: list[dict[str, Any]] = []
    for idx, case in enumerate(cases):
        if not isinstance(case, dict):
            errors.append(f"{path}: cases[{idx}] expected mapping")
            continue
        valid_cases.append(case)
    return valid_cases, errors


def validate_file(path: Path, schema: dict[str, Any]) -> tuple[list[str], int]:
    errors: list[str] = []
    cases, load_errors = load_cases(path)
    errors.extend(load_errors)
    seen: set[str] = set()
    v2_count = 0
    for idx, case in enumerate(cases):
        case_id = case.get("case_id", f"cases[{idx}]")
        if isinstance(case_id, str):
            if case_id in seen:
                errors.append(f"{path}: duplicate case_id {case_id!r}")
            seen.add(case_id)
        else:
            errors.append(f"{path}: cases[{idx}].case_id must be string")
        for error in validate_schema(case, schema):
            errors.append(f"{path}: {case_id}: {error}")
        if case.get("schema_version") == 2:
            v2_count += 1
    return errors, v2_count


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("eval_path", type=Path)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--min-v2-cases", type=int, default=0)
    args = parser.parse_args()
    if not args.eval_path.exists():
        print(f"FAIL: eval path not found: {args.eval_path}")
        return 2
    if not args.schema.exists():
        print(f"FAIL: schema path not found: {args.schema}")
        return 2
    try:
        schema = load_json_file(args.schema)
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: invalid schema file: {args.schema}: {exc}")
        return 2
    errors: list[str] = []
    total_v2 = 0
    for path in candidate_files(args.eval_path):
        file_errors, file_v2 = validate_file(path, schema)
        errors.extend(file_errors)
        total_v2 += file_v2
    if args.min_v2_cases and total_v2 < args.min_v2_cases:
        errors.append(f"{args.eval_path}: expected at least {args.min_v2_cases} schema_version 2 cases, found {total_v2}")
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
