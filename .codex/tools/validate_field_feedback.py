#!/usr/bin/env python3
"""Validate machine-readable field feedback entries."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from _validation import load_json_file, load_yaml_file, validate_schema


GATE_FILE = "gate.yaml"
GATE_VALUES = {"user-accepted", "measured"}


def feedback_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    return sorted(path for path in root.glob("FF-*.yaml") if path.is_file())


def validate_entry(path: Path, schema: dict[str, Any]) -> list[str]:
    try:
        data = load_yaml_file(path)
    except Exception as exc:  # noqa: BLE001
        return [f"{path}: invalid YAML: {exc}"]
    if not isinstance(data, dict):
        return [f"{path}: expected top-level mapping"]
    return [f"{path}: {error}" for error in validate_schema(data, schema)]


def validate_gate(root: Path, entry_count: int) -> tuple[str | None, list[str]]:
    gate = root / GATE_FILE
    if not gate.exists():
        return None, []
    errors: list[str] = []
    try:
        data = load_yaml_file(gate)
    except Exception as exc:  # noqa: BLE001
        return None, [f"{gate}: invalid YAML: {exc}"]
    if not isinstance(data, dict):
        return None, [f"{gate}: expected top-level mapping"]
    status = data.get("field_feedback_gate")
    if status not in GATE_VALUES:
        errors.append(f"{gate}: invalid field_feedback_gate {status!r}")
    if data.get("measured_entries_count") != entry_count:
        errors.append(f"{gate}: measured_entries_count {data.get('measured_entries_count')!r} != actual {entry_count}")
    if status == "user-accepted" and data.get("measured_entries_required") is not False:
        errors.append(f"{gate}: user-accepted gate must set measured_entries_required: false")
    return str(status) if isinstance(status, str) else None, errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("feedback_path", type=Path)
    parser.add_argument("--schema", type=Path)
    args = parser.parse_args()
    if not args.feedback_path.exists():
        print(f"FAIL: feedback path not found: {args.feedback_path}")
        return 2
    schema = args.schema or (args.feedback_path / "field-feedback.schema.json" if args.feedback_path.is_dir() else None)
    if schema is None or not schema.exists():
        print(f"FAIL: field feedback schema not found under {args.feedback_path}")
        return 2
    try:
        schema_data = load_json_file(schema)
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: invalid field feedback schema: {exc}")
        return 2
    entries = feedback_files(args.feedback_path)
    errors: list[str] = []
    for entry in entries:
        errors.extend(validate_entry(entry, schema_data))
    gate_status, gate_errors = validate_gate(args.feedback_path, len(entries)) if args.feedback_path.is_dir() else (None, [])
    errors.extend(gate_errors)
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    if not entries:
        if gate_status == "user-accepted":
            print("PASS: field evidence unmeasured; release gate waived by user")
            return 0
        print("SKIP: no measured field feedback entries")
        return 0
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
