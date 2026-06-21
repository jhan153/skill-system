#!/usr/bin/env python3
"""Check 7.3.1 execution assurance artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from _validation import load_json_file, load_yaml_file, read_text, validate_schema


REQUIRED_FILES = [
    ".codex/docs/harness_lifecycle_hooks.md",
    ".claude/docs/harness_lifecycle_hooks.md",
    ".codex/docs/tool_hardening_profile.md",
    ".claude/docs/tool_hardening_profile.md",
    ".codex/schemas/harness/lifecycle-event.schema.json",
    ".codex/schemas/tools/tool-policy.schema.json",
    ".codex/schemas/harness/examples/lifecycle-event.codex-tool-preflight.yaml",
    ".codex/schemas/tools/examples/tool-policy.exec-command.yaml",
    ".codex/hooks/codex-pretooluse.example.sh",
    ".codex/hooks/codex_hook_adapter.py",
    ".codex/hooks.json",
    ".codex/tools/hook_runtime.py",
    ".codex/tools/run_behavior_evals.py",
    ".codex/tools/run_verification_pipeline.py",
    ".codex/tools/validate_agent_run_artifact.py",
    ".codex/schemas/harness/agent-run.schema.json",
    ".codex/tools/tests/fixtures/agent-runs/current-run/run.yaml",
    ".codex/tools/tests/fixtures/agent-runs/permission-no-tool-id/run.yaml",
    ".codex/tools/tests/fixtures/agent-runs/repeated-tools/run.yaml",
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
