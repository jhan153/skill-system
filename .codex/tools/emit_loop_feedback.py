#!/usr/bin/env python3
"""Emit a knowledge feedback packet from a bounded verification LoopRun.

Loop output is a *feedback candidate*, never accepted knowledge: the packet is
always written with review_state=proposed and must pass human review before
knowledge-base-maintenance can act on it. Provenance is enforced — the packet's
source_run_id is taken from the LoopRun's recorded agent-run refs, so a packet
can only be produced for a loop that actually ran an attributable agent run.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from _validation import load_json_file, validate_schema
from loop_policy import load_yaml, utc_now, write_yaml


ROOT = Path(__file__).resolve().parents[2]
AGENT_RUN_PATTERN = re.compile(r"^AR-[0-9]{8}-[0-9]{3}$")


def source_run_id_for(state: dict[str, Any]) -> str | None:
    refs = state.get("agent_run_refs") or []
    for ref in reversed(refs):
        run_id = ref.get("run_id") if isinstance(ref, dict) else None
        if isinstance(run_id, str) and AGENT_RUN_PATTERN.match(run_id):
            return run_id
    return None


def build_proposals(state: dict[str, Any]) -> list[dict[str, Any]]:
    last_decision = state.get("last_decision", {}) if isinstance(state.get("last_decision"), dict) else {}
    reason_code = last_decision.get("reason_code", "unknown")
    proposals: list[dict[str, Any]] = []
    for index, result in enumerate(state.get("condition_results", []), start=1):
        if not isinstance(result, dict):
            continue
        condition_id = result.get("condition_id", "SC-???")
        status = result.get("status", "unverified")
        evidence_refs = [ref for ref in result.get("evidence_refs", []) if isinstance(ref, str)]
        proposal_type = "add_claim" if status == "pass" else "note_conflict"
        proposals.append(
            {
                "proposal_id": f"KFP-{index:03d}",
                "proposal_type": proposal_type,
                "rationale": (
                    f"LoopRun {state.get('loop_run_id')} condition {condition_id} ended with "
                    f"status '{status}' under final decision '{reason_code}'."
                ),
                "evidence_refs": evidence_refs,
            }
        )
    return proposals


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("loop_run_dir", type=Path)
    parser.add_argument("--output", type=Path, help="write packet YAML here; otherwise print to stdout")
    args = parser.parse_args()

    state_path = args.loop_run_dir / "state.yaml"
    if not state_path.exists():
        print(f"FAIL: state file not found: {state_path}")
        return 2
    state = load_yaml(state_path)
    if not isinstance(state, dict):
        print("FAIL: state must be a mapping")
        return 2

    source_run_id = source_run_id_for(state)
    if source_run_id is None:
        print("FAIL: no attributable agent run (agent_run_refs) — cannot establish feedback provenance")
        return 1

    loop_run_id = str(state.get("loop_run_id", ""))
    packet_id = "FP-" + loop_run_id[3:] if loop_run_id.startswith("LR-") else loop_run_id
    packet = {
        "schema_version": 1,
        "packet_id": packet_id,
        "source_run_id": source_run_id,
        "created_at": utc_now(),
        "review_state": "proposed",
        "proposals": build_proposals(state),
    }

    schema = load_json_file(ROOT / ".codex" / "schemas" / "knowledge" / "feedback-packet.schema.json")
    errors = validate_schema(packet, schema)
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- feedback_packet: {error}")
        return 1

    if args.output:
        write_yaml(args.output, packet)
        print(f"PASS: wrote {packet_id} -> {args.output}")
    else:
        print(f"PASS: {packet_id} (source_run_id={source_run_id}, review_state=proposed)")
        sys.stdout.write(_dump(packet))
    return 0


def _dump(packet: dict[str, Any]) -> str:
    import yaml

    return yaml.safe_dump(packet, sort_keys=False, allow_unicode=False)


if __name__ == "__main__":
    raise SystemExit(main())
