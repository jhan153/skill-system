#!/usr/bin/env python3
"""Validate a workflow-task-ledger task-run.yaml against its schema.

Enforces the conditional invariants the schema expresses (complete step needs
observed evidence, accepted_risk needs accepted_by/reason/review_at, resolved
needs a resolution + evidence, final pass needs evidence) on a concrete ledger
file. The task_ledger CLI enforces these at write time; this validator enforces
them on any persisted ledger (e.g. a resumed or hand-edited one).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from _validation import load_json_file, load_yaml_file, validate_schema

SCHEMA = Path(__file__).resolve().parent.parent / "schemas" / "task" / "task-run.schema.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("task_run", type=Path)
    args = parser.parse_args()
    if not args.task_run.exists():
        print(f"FAIL: task-run not found: {args.task_run}")
        return 2
    schema = load_json_file(SCHEMA)
    data = load_yaml_file(args.task_run)
    errors = validate_schema(data, schema)
    print("FAIL" if errors else "PASS")
    for error in errors:
        print(f"- {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
