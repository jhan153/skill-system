#!/usr/bin/env python3
"""Check 8.3.1 execution assurance artifacts."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from _validation import load_json_file, load_yaml_file, read_text, validate_schema


REQUIRED_FILES = [
    ".codex/docs/harness_lifecycle_hooks.md",
    ".claude/docs/harness_lifecycle_hooks.md",
    ".codex/docs/tool_hardening_profile.md",
    ".claude/docs/tool_hardening_profile.md",
    ".codex/docs/work_item_lifecycle.md",
    ".claude/docs/work_item_lifecycle.md",
    ".codex/schemas/harness/lifecycle-event.schema.json",
    ".codex/schemas/tools/tool-policy.schema.json",
    ".codex/schemas/harness/examples/lifecycle-event.codex-tool-preflight.yaml",
    ".codex/schemas/tools/examples/tool-policy.exec-command.yaml",
    ".codex/hooks/codex-pretooluse.example.sh",
    ".codex/hooks/codex_hook_adapter.py",
    ".codex/hooks.json",
    ".claude/tools/claude_notify_adapter.py",
    ".claude/tools/notify_desktop.py",
    ".codex/tools/hook_runtime.py",
    ".codex/tools/notify_desktop.py",
    ".codex/tools/run_behavior_evals.py",
    ".codex/tools/run_validator_unit_tests.py",
    ".codex/tools/run_verification_pipeline.py",
    ".codex/tools/validate_agent_run_artifact.py",
    ".codex/schemas/harness/agent-run.schema.json",
    ".codex/tools/tests/fixtures/agent-runs/current-run/run.yaml",
    ".codex/tools/tests/fixtures/agent-runs/permission-no-tool-id/run.yaml",
    ".codex/tools/tests/fixtures/agent-runs/repeated-tools/run.yaml",
    ".codex/schemas/loop/loop-contract.schema.json",
    ".codex/schemas/loop/loop-run.schema.json",
    ".codex/schemas/loop/iteration-result.schema.json",
    ".codex/schemas/loop/examples/loop-contract.example.yaml",
    ".codex/schemas/loop/examples/loop-run.example.yaml",
    ".codex/schemas/loop/examples/iteration-result.example.yaml",
    ".codex/tools/init_loop_run.py",
    ".codex/tools/evaluate_loop_run.py",
    ".codex/tools/validate_loop_run.py",
    ".codex/tools/loop_policy.py",
    ".codex/tools/emit_loop_feedback.py",
    ".codex/tools/check_evidence_ledger.py",
    ".codex/tools/activate_loop_run.py",
    ".codex/tools/deactivate_loop_run.py",
    ".codex/tools/resume_loop_run.py",
    ".codex/tools/tests/test_loop_engineering.py",
    ".codex/tools/tests/fixtures/loop-runs/valid/contract.yaml",
    ".codex/tools/tests/fixtures/loop-runs/valid/state.yaml",
    ".codex/tools/tests/fixtures/loop-runs/valid/checkpoints/0000.yaml",
    ".codex/skills/workflow-task-ledger/SKILL.md",
    ".codex/schemas/task/task-run.schema.json",
    ".codex/schemas/task/examples/task-run.example.yaml",
    ".codex/schemas/workitem/work-item.schema.json",
    ".codex/schemas/workitem/examples/work-item.example.yaml",
    ".codex/tools/task_ledger.py",
    ".codex/tools/validate_task_run.py",
    ".codex/tools/validate_work_item.py",
    ".codex/tools/tests/test_task_ledger.py",
    ".codex/tools/tests/test_work_item_lifecycle.py",
    ".codex/tools/analyze_harness_measurement.py",
    ".codex/tools/tests/test_harness_measurement.py",
]
SCHEMA_CONTRACTS = {
    ".codex/schemas/harness/lifecycle-event.schema.json": {
        "top_property": "mapping",
        "example": ".codex/schemas/harness/examples/lifecycle-event.codex-tool-preflight.yaml",
        "invalid": {"mapping": {"neutral_event": "not-real", "host": "codex", "host_event": "PreToolUse", "support_level": "native"}},
    },
    ".codex/schemas/tools/tool-policy.schema.json": {
        "top_property": "tool_policy",
        "example": ".codex/schemas/tools/examples/tool-policy.exec-command.yaml",
        "invalid": {"tool_policy": {"tool_id": "x", "capabilities": ["made_up"], "decision": {"default": "maybe"}}},
    },
    ".codex/schemas/harness/agent-run.schema.json": {
        "top_property": "outputs",
        "example": ".codex/tools/tests/fixtures/agent-runs/current-run/run.yaml",
        "invalid": {
            "schema_version": 1,
            "run_id": "AR-20260620-999",
            "bundle_version": "7.3.1",
            "task": {"user_request_summary": "invalid", "result_label": "done"},
            "assistant_message": {"sha256": "x", "result_label": "done", "claim_ids": []},
            "outputs": {"final_report": "final-report.md", "artifact_refs": [], "claims": []},
            "validations": [],
            "hook_events": "hook-events.jsonl",
        },
    },
    ".codex/schemas/loop/loop-contract.schema.json": {
        "top_property": "goal",
        "example": ".codex/schemas/loop/examples/loop-contract.example.yaml",
        "invalid": {
            "schema_version": 1,
            "contract_id": "LC-1",
            "activation": "implicit",
            "goal": {"statement": "x"},
            "control": {},
            "termination": {},
        },
    },
    ".codex/schemas/loop/loop-run.schema.json": {
        "top_property": "progress",
        "example": ".codex/schemas/loop/examples/loop-run.example.yaml",
        "invalid": {
            "schema_version": 1,
            "loop_run_id": "LR-1",
            "contract_ref": "contract.yaml",
            "contract_hash": "nothex",
            "workspace": {},
            "status": "running",
            "iteration": -1,
            "started_at": "x",
            "updated_at": "x",
            "budgets": {},
            "condition_results": [],
            "progress": {},
            "agent_run_refs": [],
            "last_decision": {},
            "side_effect_journal": [],
        },
    },
    ".codex/schemas/loop/iteration-result.schema.json": {
        "top_property": "condition_results",
        "example": ".codex/schemas/loop/examples/iteration-result.example.yaml",
        "invalid": {
            "schema_version": 2,
            "loop_run_id": "LR-1",
            "iteration": 0,
            "condition_results": [],
        },
    },
    ".codex/schemas/task/task-run.schema.json": {
        "top_property": "steps",
        "example": ".codex/schemas/task/examples/task-run.example.yaml",
        "invalid": {
            "schema_version": 1,
            "task_run_id": "TR-x",
            "objective": "x",
            "status": "active",
            "steps": [{"id": "S1", "title": "t", "status": "complete", "evidence_refs": []}],
            "findings": [],
            "final_verification": {"status": "pending", "evidence_refs": []},
        },
    },
    ".codex/schemas/workitem/work-item.schema.json": {
        "top_property": "history",
        "example": ".codex/schemas/workitem/examples/work-item.example.yaml",
        "invalid": {
            "schema_version": 1,
            "work_item_id": "WI-20260627-999",
            "title": "invalid",
            "source": {"type": "user_request", "ref": "demo"},
            "state": "closed",
            "owner": "agent",
            "primary_skill": "workflow-task-ledger",
            "runtime_boundary": {
                "mode": "state_model",
                "queue_runtime": True,
                "scheduler_runtime": False,
                "kanboard_source_of_truth": False,
                "looprun_replacement": False,
            },
            "history": [{"state": "closed", "at": "2026-06-27T00:00:00Z", "actor": "agent", "evidence_refs": []}],
            "evidence_refs": [],
            "open_findings": [],
            "next_action": "",
        },
    },
}


def validate_schema_contract(path: Path, contract: dict[str, Any], root: Path) -> list[str]:
    errors: list[str] = []
    try:
        schema = load_json_file(path)
    except Exception as exc:  # noqa: BLE001
        return [f"invalid json: {path.relative_to(root)}: {exc}"]
    for key in ["$schema", "type", "required", "properties"]:
        if key not in schema:
            errors.append(f"{path.relative_to(root)}: schema missing {key}")
    if schema.get("type") != "object":
        errors.append(f"{path.relative_to(root)}: schema top-level type must be object")
    top_property = contract["top_property"]
    if top_property not in schema.get("required", []):
        errors.append(f"{path.relative_to(root)}: schema must require {top_property}")
    if top_property not in schema.get("properties", {}):
        errors.append(f"{path.relative_to(root)}: schema must define {top_property}")
    example_path = root / contract["example"]
    try:
        example = load_yaml_file(example_path)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"{example_path.relative_to(root)}: invalid YAML: {exc}")
        example = None
    if example is not None:
        for error in validate_schema(example, schema):
            errors.append(f"{example_path.relative_to(root)}: {error}")
    invalid_errors = validate_schema(contract["invalid"], schema)
    if not invalid_errors:
        errors.append(f"{path.relative_to(root)}: schema accepted invalid sentinel instance")
    return errors


def main() -> int:
    root = Path(".").resolve()
    errors: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            errors.append(f"missing: {rel}")
    lifecycle = root / ".codex/docs/harness_lifecycle_hooks.md"
    if lifecycle.exists():
        text = read_text(lifecycle)
        for term in ["support_level", "native", "approximate", "unsupported", "do not replace", "approval policy"]:
            if term not in text:
                errors.append(f"harness lifecycle doc missing term: {term}")
    tool_doc = root / ".codex/docs/tool_hardening_profile.md"
    if tool_doc.exists():
        text = read_text(tool_doc)
        for term in ["tool_policy", "capabilities", "invocation_scope", "postconditions"]:
            if term not in text:
                errors.append(f"tool hardening doc missing term: {term}")
    for rel, contract in SCHEMA_CONTRACTS.items():
        path = root / rel
        if path.exists():
            errors.extend(validate_schema_contract(path, contract, root))
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
