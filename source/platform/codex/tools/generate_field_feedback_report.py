#!/usr/bin/env python3
"""Generate FIELD_FEEDBACK.md from machine-readable field feedback entries."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from _validation import load_yaml_file


def load_entries(source: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for path in sorted(source.glob("FF-*.yaml")):
        data = load_yaml_file(path)
        if isinstance(data, dict):
            entries.append(data)
    return entries


def load_gate(source: Path) -> dict[str, Any]:
    gate = source / "gate.yaml"
    if not gate.exists():
        return {}
    data = load_yaml_file(gate)
    return data if isinstance(data, dict) else {}


def list_value(value: object) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    if value is None:
        return ""
    return str(value)


def render(entries: list[dict[str, Any]], gate: dict[str, Any]) -> str:
    lines = [
        "# Field Feedback",
        "",
        "Generated human-readable view. Machine-readable source lives in `.codex/field-feedback/*.yaml`.",
        "",
        "## Status",
        "",
    ]
    if not entries:
        release_gate = "waived" if gate.get("field_feedback_gate") == "user-accepted" else "not-waived"
        waived_by = gate.get("accepted_by", "") if release_gate == "waived" else ""
        lines.extend(
            [
                "- measured_entries: 0",
                "- field_evidence_status: unmeasured",
                f"- release_gate: {release_gate}",
                f"- waived_by: {waived_by}",
                "- positive_field_signal: unmeasured",
                "",
                "No measured field feedback entries have been recorded. The release gate is waived by user decision, not by measured field evidence.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                f"- measured_entries: {len(entries)}",
                "- field_evidence_status: measured",
                f"- release_gate: {gate.get('field_feedback_gate', 'not-recorded')}",
                "",
            ]
        )
        for entry in entries:
            lines.extend(
                [
                    f"## {entry.get('feedback_id', 'unknown')}",
                    "",
                    f"- date: {entry.get('date', '')}",
                    f"- bundle_version: {entry.get('bundle_version', '')}",
                    f"- host: {entry.get('host', '')}",
                    f"- request_class: {entry.get('request_class', '')}",
                    f"- expected_primary_skill: {entry.get('expected_primary_skill', '')}",
                    f"- actual_primary_skill: {entry.get('actual_primary_skill', '')}",
                    f"- outcome: {entry.get('outcome', '')}",
                    f"- friction: {entry.get('friction', '')}",
                    f"- artifact_refs: {list_value(entry.get('artifact_refs'))}",
                    f"- validation_evidence: {list_value(entry.get('validation_evidence'))}",
                    "",
                ]
            )
    lines.extend(
        [
            "## Guidance",
            "",
            "- Record observed behavior, not guesses.",
            "- Prefer one request per entry.",
            "- Mark uncertain conclusions as `user-verification-needed` or keep the entry out of release evidence.",
            "- Do not paste secrets, credentials, session data, private chat logs, or unrelated project content.",
            "",
            "## Examples",
            "",
            "Examples are intentionally kept out of this generated view so they cannot be mistaken for measured field results.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path(".codex/field-feedback"))
    parser.add_argument("--output", type=Path, default=Path("FIELD_FEEDBACK.md"))
    args = parser.parse_args()
    entries = load_entries(args.source)
    gate = load_gate(args.source)
    args.output.write_text(render(entries, gate), encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
