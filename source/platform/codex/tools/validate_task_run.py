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
import hashlib
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from _validation import load_json_file, load_yaml_file, validate_schema

SCHEMA = Path(__file__).resolve().parent.parent / "schemas" / "task" / "task-run.schema.json"
WORK_CONTRACT_SCHEMA = (
    Path(__file__).resolve().parent.parent / "schemas" / "task" / "work-contract.schema.json"
)
OPTIONAL_WORK_KINDS = {
    "agent_validation",
    "test_authoring",
    "validation_artifact",
    "optional_quality",
    "meta",
}


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def contract_path(task_run_path: Path, ref: Any) -> Path | None:
    if not isinstance(ref, str) or not ref:
        return None
    relative = Path(ref)
    if relative.is_absolute():
        return None
    root = task_run_path.parent.resolve()
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate


def task_semantic_errors(data: dict[str, Any], contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    scope = contract.get("scope") if isinstance(contract.get("scope"), dict) else {}
    excluded = {
        item
        for item in scope.get("excluded_action_classes", [])
        if isinstance(item, str)
    }
    allowed = {
        item
        for item in scope.get("allowed_action_classes", [])
        if isinstance(item, str)
    }
    overlap = sorted(allowed & excluded)
    if overlap:
        errors.append("work contract action classes overlap: " + ", ".join(overlap))
    execution = contract.get("execution") if isinstance(contract.get("execution"), dict) else {}
    interaction = contract.get("interaction") if isinstance(contract.get("interaction"), dict) else {}
    verification = (
        contract.get("verification")
        if isinstance(contract.get("verification"), dict)
        else {}
    )
    if verification.get("owner") == "user":
        missing = sorted(
            {"agent_validation", "test_authoring", "validation_artifact"} - excluded
        )
        if missing:
            errors.append(
                "user-owned verification does not exclude agent verification work: "
                + ", ".join(missing)
            )
    unattended_no_interaction = (
        execution.get("mode") == "unattended_goal_loop"
        and interaction.get("mode") == "forbidden"
    )
    steps = [item for item in data.get("steps", []) if isinstance(item, dict)]
    completed = {item.get("id") for item in steps if item.get("status") == "complete"}
    deferred_intents: list[str] = []
    runnable_required: list[str] = []
    for step in steps:
        step_id = str(step.get("id", "<unknown>"))
        kind = step.get("kind")
        status = step.get("status")
        if kind in excluded and status != "deferred":
            errors.append(f"{step_id}: excluded work kind {kind!r} must remain deferred")
        if kind in excluded and kind in OPTIONAL_WORK_KINDS and step.get("required") is not False:
            errors.append(f"{step_id}: excluded auxiliary work cannot remain required")
        if (
            unattended_no_interaction
            and step.get("requires_interaction") is True
            and status in {"pending", "in_progress", "failed"}
        ):
            errors.append(f"{step_id}: unattended no-interaction work must defer the interaction")
        if status == "deferred" and isinstance(step.get("intent_key"), str):
            deferred_intents.append(step["intent_key"])
        if step.get("required", True) and status in {"pending", "in_progress", "failed"}:
            dependencies = step.get("depends_on", [])
            if isinstance(dependencies, list) and all(item in completed for item in dependencies):
                runnable_required.append(step_id)
    duplicate_intents = sorted(
        {
            intent
            for intent in deferred_intents
            if deferred_intents.count(intent) > 1
        }
    )
    if duplicate_intents:
        errors.append(
            "deferred steps repeat semantic intents: "
            + ", ".join(duplicate_intents)
        )
    if data.get("status") == "blocked" and runnable_required:
        errors.append(
            "blocked TaskRun still has required runnable steps: "
            + ", ".join(runnable_required)
        )
    if data.get("status") == "complete":
        incomplete = [
            str(step.get("id", "<unknown>"))
            for step in steps
            if step.get("required", True) and step.get("status") != "complete"
        ]
        if incomplete:
            errors.append("complete TaskRun has incomplete required steps: " + ", ".join(incomplete))
        open_findings = [
            str(item.get("id", "<unknown>"))
            for item in data.get("findings", [])
            if isinstance(item, dict) and item.get("status") == "open"
        ]
        if open_findings:
            errors.append("complete TaskRun has open findings: " + ", ".join(open_findings))
        final_status = (
            data.get("final_verification", {}).get("status")
            if isinstance(data.get("final_verification"), dict)
            else None
        )
        owner = (
            contract.get("verification", {}).get("owner")
            if isinstance(contract.get("verification"), dict)
            else None
        )
        handoff = (
            contract.get("verification", {}).get("handoff_on_unavailable")
            if isinstance(contract.get("verification"), dict)
            else None
        )
        expected = {
            "pass": "agent-verified",
            "user-verification-needed": "user-verification-needed",
            "unverified": "unverified",
        }.get(str(final_status))
        if data.get("result_label") != expected:
            errors.append(
                f"complete TaskRun result_label {data.get('result_label')!r} "
                f"does not match final_verification {final_status!r}"
            )
        if final_status == "user-verification-needed" and owner not in {"user", "shared"}:
            errors.append("user-verification-needed requires user/shared verification ownership")
        if final_status == "unverified" and handoff != "unverified":
            errors.append("unverified final status is not allowed by the work contract handoff")
    return errors


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
    if isinstance(data, dict) and data.get("schema_version") == 2:
        path = contract_path(args.task_run, data.get("work_contract_ref"))
        if path is None or not path.is_file():
            errors.append("work_contract_ref must resolve inside the TaskRun directory")
        else:
            contract = load_yaml_file(path)
            if not isinstance(contract, dict):
                errors.append("work contract must be a mapping")
            else:
                errors.extend(
                    f"work contract: {error}"
                    for error in validate_schema(
                        contract,
                        load_json_file(WORK_CONTRACT_SCHEMA),
                    )
                )
                if data.get("work_contract_hash") != file_sha256(path):
                    errors.append("work_contract_hash does not match the referenced contract")
                errors.extend(task_semantic_errors(data, contract))
    print("FAIL" if errors else "PASS")
    for error in errors:
        print(f"- {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
