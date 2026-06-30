#!/usr/bin/env python3
"""Validate a bounded verification LoopRun directory."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from _validation import load_json_file, load_yaml_file, validate_schema
from loop_policy import file_sha256, required_condition_ids


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("loop_run_dir", type=Path)
    args = parser.parse_args()

    loop_dir = args.loop_run_dir
    state_path = loop_dir / "state.yaml"
    if not state_path.exists():
        print(f"FAIL: state file not found: {state_path}")
        return 2
    state_schema = load_json_file(ROOT / ".codex" / "schemas" / "loop" / "loop-run.schema.json")
    contract_schema = load_json_file(ROOT / ".codex" / "schemas" / "loop" / "loop-contract.schema.json")
    state = load_yaml_file(state_path)
    if not isinstance(state, dict):
        print("FAIL: state must be a mapping")
        return 2
    contract_path = loop_dir / str(state.get("contract_ref", "contract.yaml"))
    if not contract_path.exists():
        print(f"FAIL: contract file not found: {contract_path}")
        return 2
    contract = load_yaml_file(contract_path)
    if not isinstance(contract, dict):
        print("FAIL: contract must be a mapping")
        return 2

    errors: list[str] = []
    errors.extend(f"state: {error}" for error in validate_schema(state, state_schema))
    errors.extend(f"contract: {error}" for error in validate_schema(contract, contract_schema))
    if state.get("contract_hash") != file_sha256(contract_path):
        errors.append("state: contract_hash does not match contract.yaml")
    contract_ids = set(required_condition_ids(contract))
    state_ids = {
        item.get("condition_id")
        for item in state.get("condition_results", [])
        if isinstance(item, dict)
    }
    missing = sorted(contract_ids - state_ids)
    if missing:
        errors.append(f"state: missing required condition results: {', '.join(missing)}")
    if state.get("progress", {}).get("required_total") != len(contract_ids):
        errors.append("state: progress.required_total does not match contract required conditions")
    iteration = int(state.get("iteration", 0))
    checkpoint = loop_dir / "checkpoints" / f"{iteration:04d}.yaml"
    if not checkpoint.exists():
        errors.append(f"state: checkpoint not found for current iteration: {checkpoint.relative_to(loop_dir)}")

    # Audit integrity: iteration only advances via an applied iteration result, so
    # every iteration 1..N must have input + decision records, and the counters and
    # applied_results map must line up with N.
    budgets = state.get("budgets", {}) if isinstance(state.get("budgets"), dict) else {}
    iters_used = int(budgets.get("iterations_used", 0))
    if iters_used != iteration:
        errors.append(f"state: budgets.iterations_used ({iters_used}) != iteration ({iteration})")
    for index in range(1, iteration + 1):
        for kind in ("input", "decision"):
            audit = loop_dir / "iterations" / f"{index:04d}.{kind}.yaml"
            if not audit.exists():
                errors.append(f"state: missing iteration audit record: {audit.relative_to(loop_dir)}")
    applied = state.get("applied_results")
    if isinstance(applied, dict):
        seen_iters: dict[int, str] = {}
        for rid, entry in applied.items():
            raw_iter = entry.get("iteration") if isinstance(entry, dict) else entry
            try:
                applied_iter = int(raw_iter)
            except (TypeError, ValueError):
                errors.append(f"state: applied_results[{rid}] has no valid iteration")
                continue
            if applied_iter < 1 or applied_iter > iteration:
                errors.append(f"state: applied_results[{rid}] iteration {applied_iter} outside 1..{iteration}")
            if applied_iter in seen_iters:
                errors.append(
                    f"state: applied_results iteration {applied_iter} mapped by multiple result ids "
                    f"({seen_iters[applied_iter]}, {rid})"
                )
            else:
                seen_iters[applied_iter] = rid

    print("FAIL" if errors else "PASS")
    for error in errors:
        print(f"- {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
