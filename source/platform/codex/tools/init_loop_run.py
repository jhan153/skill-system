#!/usr/bin/env python3
"""Initialize a bounded verification LoopRun from an accepted contract."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from _validation import load_json_file, load_yaml_file, validate_schema
from loop_policy import (
    append_jsonl,
    control_value,
    file_sha256,
    git_revision,
    required_condition_ids,
    safe_id,
    state_fingerprint,
    success_conditions,
    utc_now,
    workspace_id,
    write_yaml,
)


ROOT = Path(__file__).resolve().parents[2]


def default_loop_run_id(contract_id: str) -> str:
    return safe_id(contract_id.replace("LC-", "LR-", 1), "LR-00000000-001")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("contract", type=Path)
    parser.add_argument("--workspace-root", type=Path, default=Path("."))
    parser.add_argument("--output-root", type=Path, default=Path(".codex/harness/loop-runs"))
    parser.add_argument("--loop-run-id")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if not args.contract.exists():
        print(f"FAIL: loop contract not found: {args.contract}")
        return 2
    schema_path = ROOT / ".codex" / "schemas" / "loop" / "loop-contract.schema.json"
    schema = load_json_file(schema_path)
    contract = load_yaml_file(args.contract)
    if not isinstance(contract, dict):
        print("FAIL: loop contract must be a mapping")
        return 2
    errors = validate_schema(contract, schema)
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- contract: {error}")
        return 1

    workspace_root = args.workspace_root.resolve()
    ws_id = workspace_id(workspace_root)
    loop_run_id = safe_id(args.loop_run_id or default_loop_run_id(str(contract["contract_id"])), "LR-00000000-001")
    loop_dir = args.output_root / ws_id / loop_run_id
    if loop_dir.exists():
        if not args.force:
            print(f"FAIL: loop run already exists: {loop_dir}")
            return 1
        # --force re-initializes from scratch: drop the old run entirely so stale
        # iterations/checkpoints/artifacts cannot mix with the new audit trail.
        shutil.rmtree(loop_dir)
    loop_dir.mkdir(parents=True, exist_ok=True)
    for rel in ["iterations", "checkpoints", "artifacts"]:
        (loop_dir / rel).mkdir(exist_ok=True)
    shutil.copy2(args.contract, loop_dir / "contract.yaml")

    required_ids = required_condition_ids(contract)
    now = utc_now()
    state = {
        "schema_version": 1,
        "loop_run_id": loop_run_id,
        "contract_ref": "contract.yaml",
        "contract_hash": file_sha256(loop_dir / "contract.yaml"),
        "workspace": {
            "root": str(workspace_root),
            "revision": git_revision(workspace_root),
            "workspace_id": ws_id,
        },
        "status": "active",
        "iteration": 0,
        "started_at": now,
        "updated_at": now,
        "budgets": {
            "iterations_used": 0,
            "max_iterations": control_value(contract, "max_iterations", 1),
            "stop_continuations_used": 0,
            "max_stop_continuations": control_value(contract, "max_stop_continuations", 0),
            "wall_time_seconds": 0,
        },
        "condition_results": [
            {
                "condition_id": condition["id"],
                "status": "unverified",
                "evidence_refs": [],
            }
            for condition in success_conditions(contract)
        ],
        "progress": {
            "required_passed": 0,
            "required_total": len(required_ids),
            "no_progress_count": 0,
            "repeated_failure_count": 0,
            "oscillation_count": 0,
            "state_hash": "0" * 64,
        },
        "agent_run_refs": [],
        "last_decision": {
            "action": "continue",
            "reason_code": "initialized",
            "target_condition": required_ids[0] if required_ids else None,
            "continuation_prompt": None,
        },
        "side_effect_journal": [],
    }
    state["progress"]["state_hash"] = state_fingerprint(contract, state)
    write_yaml(loop_dir / "state.yaml", state)
    write_yaml(loop_dir / "checkpoints" / "0000.yaml", state)
    append_jsonl(
        loop_dir / "loop-events.jsonl",
        {
            "recorded_at": now,
            "event": "loop_initialized",
            "loop_run_id": loop_run_id,
            "contract_hash": state["contract_hash"],
        },
    )
    print(json.dumps({"status": "PASS", "loop_run_id": loop_run_id, "loop_run_dir": str(loop_dir)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
