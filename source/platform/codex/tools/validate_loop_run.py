#!/usr/bin/env python3
"""Validate a bounded verification LoopRun directory."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from _validation import load_json_file, load_yaml_file, validate_schema
from loop_policy import (
    canonical_hash,
    condition_map,
    contained_path,
    contract_runtime_errors,
    file_sha256,
    required_condition_ids,
    state_fingerprint,
    structured_evidence_errors,
)


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
    contract_path = contained_path(loop_dir, str(state.get("contract_ref", "contract.yaml")))
    if contract_path is None or not contract_path.is_file():
        print("FAIL: contract_ref must resolve to a file contained by the LoopRun directory")
        return 2
    contract = load_yaml_file(contract_path)
    if not isinstance(contract, dict):
        print("FAIL: contract must be a mapping")
        return 2

    errors: list[str] = []
    errors.extend(f"state: {error}" for error in validate_schema(state, state_schema))
    errors.extend(f"contract: {error}" for error in validate_schema(contract, contract_schema))
    errors.extend(f"contract: {error}" for error in contract_runtime_errors(contract))
    if state.get("schema_version") != 2:
        errors.append("state: schema_version 1 is legacy read-only")
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
    errors.extend(
        f"state: {error}"
        for error in structured_evidence_errors(
            contract,
            state,
            state.get("condition_results", []),
            loop_dir,
        )
    )
    iteration = int(state.get("iteration", 0))
    if iteration == 0 and (
        state.get("status") == "success"
        or any(
            item.get("status") == "pass"
            for item in state.get("condition_results", [])
            if isinstance(item, dict) and item.get("condition_id") in contract_ids
        )
    ):
        errors.append("state: iteration 0 cannot contain a required pass or success status")
    checkpoint = loop_dir / "checkpoints" / f"{iteration:04d}.yaml"
    if not checkpoint.exists():
        errors.append(f"state: checkpoint not found for current iteration: {checkpoint.relative_to(loop_dir)}")
    else:
        checkpoint_state = load_yaml_file(checkpoint)
        if not isinstance(checkpoint_state, dict) or canonical_hash(checkpoint_state) != canonical_hash(state):
            errors.append("state: current checkpoint does not exactly match state.yaml")
    expected_state_hash = state_fingerprint(contract, state)
    if state.get("progress", {}).get("state_hash") != expected_state_hash:
        errors.append("state: progress.state_hash does not match current condition state")

    # Audit integrity: iteration only advances via an applied iteration result, so
    # every iteration 1..N must have input + decision records, and the counters and
    # applied_results map must line up with N.
    budgets = state.get("budgets", {}) if isinstance(state.get("budgets"), dict) else {}
    iters_used = int(budgets.get("iterations_used", 0))
    if iters_used != iteration:
        errors.append(f"state: budgets.iterations_used ({iters_used}) != iteration ({iteration})")
    applied = state.get("applied_results")
    iteration_schema = load_json_file(ROOT / ".codex" / "schemas" / "loop" / "iteration-result.schema.json")
    if isinstance(applied, dict):
        if len(applied) != iteration:
            errors.append(f"state: applied_results count ({len(applied)}) != iteration ({iteration})")
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
        last_audit_checkpoint: dict | None = None
        for index in range(1, iteration + 1):
            input_path = loop_dir / "iterations" / f"{index:04d}.input.yaml"
            decision_path = loop_dir / "iterations" / f"{index:04d}.decision.yaml"
            checkpoint_path = loop_dir / "iterations" / f"{index:04d}.checkpoint.yaml"
            if not input_path.is_file() or not decision_path.is_file() or not checkpoint_path.is_file():
                errors.append(f"state: iteration {index} is missing input, decision, or checkpoint audit data")
                continue
            audit_input = load_yaml_file(input_path)
            audit_decision = load_yaml_file(decision_path)
            audit_checkpoint = load_yaml_file(checkpoint_path)
            if not isinstance(audit_input, dict):
                errors.append(f"state: iteration {index} input audit is not a mapping")
                continue
            errors.extend(
                f"state: iteration {index} input: {error}"
                for error in validate_schema(audit_input, iteration_schema)
            )
            if (
                audit_input.get("schema_version") != 2
                or audit_input.get("iteration") != index
                or audit_input.get("loop_run_id") != state.get("loop_run_id")
            ):
                errors.append(f"state: iteration {index} input identity/version does not match the LoopRun")
            body = {key: value for key, value in audit_input.items() if key != "payload_hash"}
            digest = canonical_hash(body)
            rid = audit_input.get("iteration_result_id") or digest
            entry = applied.get(rid)
            if not isinstance(entry, dict) or entry.get("iteration") != index or entry.get("payload_hash") != digest:
                errors.append(f"state: iteration {index} input is not exactly bound by applied_results")
            if not isinstance(audit_checkpoint, dict) or audit_checkpoint.get("iteration") != index:
                errors.append(f"state: iteration {index} checkpoint has the wrong iteration")
                continue
            last_audit_checkpoint = audit_checkpoint
            if audit_checkpoint.get("progress", {}).get("state_hash") != state_fingerprint(contract, audit_checkpoint):
                errors.append(f"state: iteration {index} checkpoint state_hash is invalid")
            checkpoint_results = condition_map(audit_checkpoint)
            for result in audit_input.get("condition_results", []):
                if not isinstance(result, dict) or not isinstance(result.get("condition_id"), str):
                    continue
                normalized_result = {
                    "condition_id": result["condition_id"],
                    "status": result.get("status", "unverified"),
                    "evidence_refs": result.get("evidence_refs", [])
                    if isinstance(result.get("evidence_refs"), list)
                    else [],
                    "evidence": result.get("evidence", [])
                    if isinstance(result.get("evidence"), list)
                    else [],
                    **(
                        {"failure_fingerprint": result["failure_fingerprint"]}
                        if isinstance(result.get("failure_fingerprint"), str)
                        else {}
                    ),
                }
                if canonical_hash(checkpoint_results.get(result["condition_id"], {})) != canonical_hash(normalized_result):
                    errors.append(
                        f"state: iteration {index} input result {result['condition_id']} is not reflected in checkpoint"
                    )
            if not isinstance(audit_decision, dict) or canonical_hash(audit_checkpoint.get("last_decision")) != canonical_hash(audit_decision):
                errors.append(f"state: iteration {index} decision is not bound to its checkpoint")
        if last_audit_checkpoint is not None:
            for field in ("condition_results", "agent_run_refs", "side_effect_journal", "applied_results"):
                if canonical_hash(state.get(field)) != canonical_hash(last_audit_checkpoint.get(field)):
                    errors.append(f"state: current {field} does not match the latest immutable iteration checkpoint")
    elif iteration:
        errors.append("state: applied_results must be present for an iterated LoopRun")

    print("FAIL" if errors else "PASS")
    for error in errors:
        print(f"- {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
