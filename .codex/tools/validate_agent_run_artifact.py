#!/usr/bin/env python3
"""Validate Codex agent run output artifacts against recorded evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from _validation import is_iso_datetime, load_json_file, load_yaml_file, validate_schema


EVENT_ORDER = {
    "request_received": 0,
    "context_loaded": 1,
    "tool_preflight": 2,
    "permission_requested": 3,
    "tool_result": 4,
    "tool_batch_completed": 5,
    "turn_finalize_attempt": 6,
    "turn_finalize": 7,
    "compact_before": 8,
    "compact_after": 9,
}
EVENT_STATUSES = {"pass", "warn", "fail", "skip"}
SUPPORT_LEVELS = {"native", "approximate", "unsupported"}
HOSTS = {"codex", "claude"}
TOOL_START = "tool_preflight"
TOOL_PERMISSION = "permission_requested"
TOOL_END = "tool_result"
TURN_END = "turn_finalize"
ZERO_HASH = "0" * 64
HASH_RE = re.compile(r"^[a-f0-9]{64}$")


def run_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if (path / "run.yaml").exists():
        return [path / "run.yaml"]
    return sorted(path.rglob("run.yaml"))


def repo_relative(path: str) -> bool:
    return bool(path) and not path.startswith("/") and ".." not in Path(path).parts


def evidence_text(run_dir: Path, rel: str) -> tuple[str | None, str | None]:
    if not repo_relative(rel):
        return None, f"evidence path is not run-relative: {rel}"
    path = run_dir / rel
    if not path.exists():
        return None, f"evidence file not found: {rel}"
    return path.read_text(encoding="utf-8", errors="replace"), None


def expected_event_hash(event: dict[str, Any]) -> str:
    body = dict(event)
    body.pop("event_hash", None)
    raw = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(data: dict[str, Any]) -> str:
    raw = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def load_hook_events(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    errors: list[str] = []
    events: list[dict[str, Any]] = []
    if not path.exists():
        return events, [f"hook events file not found: {path.name}"]
    for line_no, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{path.name}:{line_no}: invalid JSON: {exc}")
            continue
        if not isinstance(event, dict):
            errors.append(f"{path.name}:{line_no}: expected JSON object")
            continue
        events.append(event)
    if not events:
        errors.append(f"{path.name}: no hook events recorded")
    return events, errors


def validate_hook_events(
    run_dir: Path,
    rel: str,
    phase: str = "post-finalize",
    candidate_final_event: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    if not repo_relative(rel):
        return [f"hook_events path is not run-relative: {rel}"]
    events, load_errors = load_hook_events(run_dir / rel)
    errors.extend(load_errors)
    if candidate_final_event is not None:
        events.append(candidate_final_event)
    tool_states: dict[str, str] = {}
    compact_started = False
    turn_finalized = False
    expected_session_id = ""
    expected_turn_id = ""
    previous_hash = ZERO_HASH
    previous_seq = 0
    previous_run_id = ""
    saw_v2_event = False
    saw_request_received = False
    saw_context_loaded = False
    saw_passing_turn_finalize = False
    passing_turn_finalize_count = 0
    for idx, event in enumerate(events):
        label = f"hook_events[{idx}]"
        neutral_event = event.get("neutral_event")
        if turn_finalized:
            errors.append(f"{label}: lifecycle event after turn_finalize")
        for field in ["schema_version", "recorded_at", "neutral_event", "host", "host_event", "support_level", "status", "evidence"]:
            if field not in event:
                errors.append(f"{label}: missing {field}")
        schema_version = event.get("schema_version")
        if schema_version not in {1, 2}:
            errors.append(f"{label}: schema_version must be 1 or 2")
        if schema_version == 2:
            saw_v2_event = True
            seq = event.get("seq")
            run_id = event.get("run_id")
            prev_event_hash = event.get("prev_event_hash")
            if not isinstance(seq, int) or seq <= 0:
                errors.append(f"{label}: schema_version 2 requires positive integer seq")
            elif seq != previous_seq + 1:
                errors.append(f"{label}: seq must increment from previous event")
            if not isinstance(run_id, str) or not run_id:
                errors.append(f"{label}: schema_version 2 requires run_id")
            elif previous_run_id and run_id != previous_run_id:
                errors.append(f"{label}: run_id differs from earlier hook events")
            if not isinstance(prev_event_hash, str) or not HASH_RE.fullmatch(prev_event_hash):
                errors.append(f"{label}: schema_version 2 requires prev_event_hash")
            elif prev_event_hash != previous_hash:
                errors.append(f"{label}: prev_event_hash does not match previous event_hash")
        if not is_iso_datetime(event.get("recorded_at")):
            errors.append(f"{label}: recorded_at must be ISO datetime")
        if neutral_event == "request_received":
            saw_request_received = True
        if neutral_event == "context_loaded":
            saw_context_loaded = True
        if neutral_event == TURN_END and event.get("status") == "pass":
            saw_passing_turn_finalize = True
            passing_turn_finalize_count += 1
            if passing_turn_finalize_count > 1:
                errors.append(f"{label}: duplicate passing turn_finalize")
        order = EVENT_ORDER.get(neutral_event)
        if order is None:
            errors.append(f"{label}: unknown neutral_event {neutral_event!r}")
        if event.get("host") not in HOSTS:
            errors.append(f"{label}: unknown host {event.get('host')!r}")
        if event.get("support_level") not in SUPPORT_LEVELS:
            errors.append(f"{label}: unknown support_level {event.get('support_level')!r}")
        if event.get("status") not in EVENT_STATUSES:
            errors.append(f"{label}: unknown status {event.get('status')!r}")
        evidence = event.get("evidence")
        if not isinstance(evidence, dict):
            errors.append(f"{label}: evidence must be an object")
            evidence = {}
        session_id = event.get("session_id") or evidence.get("session_id")
        turn_id = event.get("turn_id") or evidence.get("turn_id")
        if isinstance(session_id, str) and session_id:
            if not expected_session_id:
                expected_session_id = session_id
            elif session_id != expected_session_id:
                errors.append(f"{label}: session_id differs from earlier hook events")
        if isinstance(turn_id, str) and turn_id:
            if not expected_turn_id:
                expected_turn_id = turn_id
            elif turn_id != expected_turn_id:
                errors.append(f"{label}: turn_id differs from earlier hook events")
        tool_use_id = event.get("tool_use_id") or evidence.get("tool_use_id")
        if neutral_event in {TOOL_START, TOOL_END}:
            if not isinstance(tool_use_id, str) or not tool_use_id:
                errors.append(f"{label}: tool lifecycle event requires tool_use_id")
            elif neutral_event == TOOL_START:
                if tool_states.get(tool_use_id) in {"started", "permission_requested"}:
                    errors.append(f"{label}: duplicate tool_preflight before tool_result for {tool_use_id}")
                elif tool_states.get(tool_use_id) == "ended":
                    errors.append(f"{label}: tool_preflight after tool_result for {tool_use_id}")
                else:
                    tool_states[tool_use_id] = "started"
            elif neutral_event == TOOL_END:
                if tool_states.get(tool_use_id) not in {"started", "permission_requested"}:
                    errors.append(f"{label}: tool_result without prior tool_preflight for {tool_use_id}")
                else:
                    tool_states[tool_use_id] = "ended"
        if neutral_event == TOOL_PERMISSION:
            if isinstance(tool_use_id, str) and tool_use_id:
                if tool_states.get(tool_use_id) not in {"started", "permission_requested"}:
                    errors.append(f"{label}: permission_requested without prior tool_preflight for {tool_use_id}")
                else:
                    tool_states[tool_use_id] = "permission_requested"
            elif event.get("support_level") != "approximate":
                errors.append(f"{label}: permission_requested without tool_use_id must use support_level approximate")
        if neutral_event == TURN_END and event.get("status") == "pass":
            unfinished = sorted(tool_id for tool_id, state in tool_states.items() if state != "ended")
            for tool_id in unfinished:
                errors.append(f"{label}: turn finalized with unfinished tool call {tool_id}")
            turn_finalized = True
        if neutral_event == "compact_before":
            compact_started = True
        if neutral_event == "compact_after" and not compact_started:
            errors.append(f"{label}: compact_after without compact_before")
        if neutral_event in {TOOL_START, TOOL_PERMISSION, TOOL_END} and turn_finalized:
            errors.append(f"{label}: tool lifecycle event after turn_finalize")
        event_hash = event.get("event_hash")
        if not isinstance(event_hash, str) or event_hash != expected_event_hash(event):
            errors.append(f"{label}: event_hash mismatch")
        if schema_version == 2:
            if isinstance(event.get("seq"), int):
                previous_seq = event["seq"]
            if isinstance(event.get("run_id"), str):
                previous_run_id = event["run_id"]
            if isinstance(event_hash, str) and HASH_RE.fullmatch(event_hash):
                previous_hash = event_hash
    unfinished = sorted(tool_id for tool_id, state in tool_states.items() if state != "ended")
    for tool_id in unfinished:
        errors.append(f"hook_events: unfinished tool call at end of ledger {tool_id}")
    if saw_v2_event:
        if not saw_request_received:
            errors.append("hook_events: schema_version 2 ledger missing request_received")
        if not saw_context_loaded:
            errors.append("hook_events: schema_version 2 ledger missing context_loaded")
        if phase == "post-finalize" and not saw_passing_turn_finalize:
            errors.append("hook_events: schema_version 2 ledger missing passing turn_finalize")
    return errors


def validation_key(record: dict[str, Any]) -> tuple[object, object, object]:
    return (record.get("type"), record.get("command"), record.get("exit_code"))


def validate_command_record(run_dir: Path, record: dict[str, Any], label: str) -> list[str]:
    errors: list[str] = []
    evidence_ref = record.get("evidence_ref")
    if not isinstance(evidence_ref, str):
        return [f"{label}: evidence_ref must be string"]
    text, error = evidence_text(run_dir, evidence_ref)
    if error:
        errors.append(f"{label}: {error}")
        return errors
    command = record.get("command")
    if record.get("type") == "command_exit":
        if not isinstance(command, str) or not command:
            errors.append(f"{label}: command_exit requires command")
        elif command not in text:
            errors.append(f"{label}: evidence file does not contain command")
        exit_code = record.get("exit_code")
        if not isinstance(exit_code, int):
            errors.append(f"{label}: command_exit requires integer exit_code")
        elif exit_code == 0 and "PASS" not in text:
            errors.append(f"{label}: exit_code 0 evidence must contain PASS")
        elif exit_code != 0 and "FAIL" not in text:
            errors.append(f"{label}: nonzero exit evidence must contain FAIL")
    return errors


def validate_support_record(
    run_dir: Path,
    record: dict[str, Any],
    label: str,
    pack_claim_ids: set[str],
    pack_source_ids: set[str],
) -> list[str]:
    errors = validate_command_record(run_dir, record, label)
    support_type = record.get("type")
    if support_type == "retrieved_claim":
        claim_id = record.get("claim_id")
        source_id = record.get("source_id")
        if not isinstance(claim_id, str) or claim_id not in pack_claim_ids:
            errors.append(f"{label}: retrieved_claim references claim outside context pack {claim_id!r}")
        if isinstance(source_id, str) and source_id not in pack_source_ids:
            errors.append(f"{label}: retrieved_claim references source outside context pack {source_id!r}")
    return errors


def validate_pack_hash(pack: dict[str, Any], label: str) -> list[str]:
    pack_hash = pack.get("pack_hash")
    if not isinstance(pack_hash, dict) or pack_hash.get("algorithm") != "sha256" or not isinstance(pack_hash.get("value"), str):
        return [f"{label}: context pack missing sha256 pack_hash"]
    body = dict(pack)
    body.pop("pack_hash", None)
    if pack_hash["value"] != canonical_hash(body):
        return [f"{label}: context pack pack_hash does not match canonical pack body"]
    return []


def context_pack_claim_ids(pack: dict[str, Any]) -> set[str]:
    return {
        claim["claim_id"]
        for claim in pack.get("admitted_claims", []) or []
        if isinstance(claim, dict) and isinstance(claim.get("claim_id"), str)
    }


def context_pack_source_ids(pack: dict[str, Any]) -> set[str]:
    ids: set[str] = set()
    for claim in pack.get("admitted_claims", []) or []:
        if isinstance(claim, dict):
            ids.update(ref for ref in claim.get("evidence_refs", []) or [] if isinstance(ref, str))
    for handle in pack.get("raw_source_handles", []) or []:
        if isinstance(handle, dict) and isinstance(handle.get("source_id"), str):
            ids.add(handle["source_id"])
    compilation = pack.get("compilation") if isinstance(pack.get("compilation"), dict) else {}
    ids.update(source_id for source_id in compilation.get("source_snapshot", []) or [] if isinstance(source_id, str))
    return ids


def context_pack_relation_path_ids(pack: dict[str, Any]) -> set[str]:
    return {
        path_record["path_id"]
        for path_record in pack.get("relation_paths", []) or []
        if isinstance(path_record, dict) and isinstance(path_record.get("path_id"), str)
    }


def validate_context_record(
    run_dir: Path,
    data: dict[str, Any],
    run_id: str,
    context_pack_schema: dict[str, Any] | None = None,
) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    context = data.get("context")
    if data.get("schema_version") == 2 and not isinstance(context, dict):
        return None, [f"{run_id}: schema_version 2 requires context"]
    if not isinstance(context, dict):
        return None, errors
    pack_ref = context.get("context_pack_ref")
    if not isinstance(pack_ref, str) or not repo_relative(pack_ref):
        errors.append(f"{run_id}: context.context_pack_ref must be run-relative string")
        return None, errors
    pack_path = run_dir / pack_ref
    if not pack_path.exists():
        errors.append(f"{run_id}: context pack not found: {pack_ref}")
        return None, errors
    pack_hash = context.get("context_pack_hash")
    if isinstance(pack_hash, str) and pack_hash != file_sha256(pack_path):
        errors.append(f"{run_id}: context.context_pack_hash does not match context pack content")
    try:
        pack = load_yaml_file(pack_path)
    except Exception as exc:  # noqa: BLE001
        return None, errors + [f"{run_id}: context pack is not readable YAML: {exc}"]
    if not isinstance(pack, dict):
        return None, errors + [f"{run_id}: context pack must be a mapping"]
    if context_pack_schema is not None:
        errors.extend(f"{run_id}: context pack: {error}" for error in validate_schema(pack, context_pack_schema))
    errors.extend(f"{run_id}: {error}" for error in validate_pack_hash(pack, "context pack"))
    pack_id = context.get("context_pack_id")
    if isinstance(pack_id, str) and pack_id != pack.get("pack_id"):
        errors.append(f"{run_id}: context.context_pack_id does not match context pack pack_id")
    routing = data.get("routing") if isinstance(data.get("routing"), dict) else {}
    if isinstance(routing.get("primary_skill"), str) and routing.get("primary_skill") != pack.get("primary_skill"):
        errors.append(f"{run_id}: routing.primary_skill does not match context pack primary_skill")
    task = data.get("task") if isinstance(data.get("task"), dict) else {}
    if isinstance(task.get("user_request_summary"), str) and task.get("user_request_summary") != pack.get("task"):
        errors.append(f"{run_id}: task.user_request_summary does not match context pack task")

    manifest_claim_ids = set(context.get("admitted_claim_ids", []) if isinstance(context.get("admitted_claim_ids"), list) else [])
    pack_claim_ids = context_pack_claim_ids(pack)
    if manifest_claim_ids != pack_claim_ids:
        errors.append(f"{run_id}: context.admitted_claim_ids do not match context pack admitted claims")
    manifest_source_ids = set(context.get("source_snapshot_refs", []) if isinstance(context.get("source_snapshot_refs"), list) else [])
    compilation = pack.get("compilation") if isinstance(pack.get("compilation"), dict) else {}
    pack_snapshot_ids = set(compilation.get("source_snapshot", []) if isinstance(compilation.get("source_snapshot"), list) else [])
    if manifest_source_ids != pack_snapshot_ids:
        errors.append(f"{run_id}: context.source_snapshot_refs do not match context pack source_snapshot")
    return pack, errors


def validate_run_file(
    path: Path,
    schema: dict[str, Any],
    context_pack_schema: dict[str, Any] | None,
    phase: str,
    candidate_final_event: dict[str, Any] | None,
) -> tuple[str, list[str]]:
    run_dir = path.parent
    errors: list[str] = []
    try:
        data = load_yaml_file(path)
    except Exception as exc:  # noqa: BLE001
        return path.as_posix(), [f"{path}: invalid YAML: {exc}"]
    if not isinstance(data, dict):
        return path.as_posix(), [f"{path}: expected top-level mapping"]
    run_id = str(data.get("run_id", path.parent.name))
    errors.extend(f"{run_id}: {error}" for error in validate_schema(data, schema))
    context_pack, context_errors = validate_context_record(run_dir, data, run_id, context_pack_schema)
    errors.extend(context_errors)
    outputs = data.get("outputs", {}) if isinstance(data.get("outputs"), dict) else {}
    task = data.get("task", {}) if isinstance(data.get("task"), dict) else {}
    context = data.get("context", {}) if isinstance(data.get("context"), dict) else {}
    admitted_claim_ids = set(context.get("admitted_claim_ids", []) if isinstance(context.get("admitted_claim_ids"), list) else [])
    source_snapshot_refs = set(context.get("source_snapshot_refs", []) if isinstance(context.get("source_snapshot_refs"), list) else [])
    pack_claim_ids = context_pack_claim_ids(context_pack or {}) if context_pack is not None else set()
    pack_source_ids = context_pack_source_ids(context_pack or {}) if context_pack is not None else set()
    pack_relation_path_ids = context_pack_relation_path_ids(context_pack or {}) if context_pack is not None else set()
    final_report_rel = outputs.get("final_report")
    final_report_text = ""
    if not isinstance(final_report_rel, str) or not repo_relative(final_report_rel):
        errors.append(f"{run_id}: final_report must be run-relative string")
    elif not (run_dir / final_report_rel).exists():
        errors.append(f"{run_id}: final_report not found: {final_report_rel}")
    else:
        final_report_text = (run_dir / final_report_rel).read_text(encoding="utf-8", errors="replace")
    result_label = task.get("result_label")
    if isinstance(result_label, str) and final_report_text and result_label not in final_report_text:
        errors.append(f"{run_id}: final_report does not mention result_label {result_label!r}")
    for rel in outputs.get("artifact_refs", []) or []:
        if not isinstance(rel, str) or not repo_relative(rel) or not (run_dir / rel).exists():
            errors.append(f"{run_id}: artifact_ref not found or not run-relative: {rel!r}")
    validations = data.get("validations", []) if isinstance(data.get("validations"), list) else []
    validation_keys = {validation_key(record) for record in validations if isinstance(record, dict)}
    for idx, record in enumerate(validations):
        if isinstance(record, dict):
            errors.extend(validate_command_record(run_dir, record, f"{run_id}: validations[{idx}]"))
    for idx, claim in enumerate(outputs.get("claims", []) or []):
        if not isinstance(claim, dict):
            continue
        claim_id = claim.get("claim_id", f"claims[{idx}]")
        support = claim.get("support")
        if final_report_text and isinstance(claim_id, str) and claim_id not in final_report_text:
            errors.append(f"{run_id}: final_report does not mention claim_id {claim_id}")
        if isinstance(support, dict):
            errors.extend(validate_support_record(run_dir, support, f"{run_id}: {claim_id}.support", pack_claim_ids, pack_source_ids))
            if support.get("type") == "command_exit" and validation_key(support) not in validation_keys:
                errors.append(f"{run_id}: {claim_id}.support has no matching validation record")
        context_support = claim.get("context_support")
        if isinstance(context_support, dict):
            for context_claim_id in context_support.get("claim_ids", []) or []:
                if context_claim_id not in admitted_claim_ids:
                    errors.append(f"{run_id}: {claim_id}.context_support references non-admitted claim {context_claim_id}")
                if context_pack is not None and context_claim_id not in pack_claim_ids:
                    errors.append(f"{run_id}: {claim_id}.context_support references claim outside context pack {context_claim_id}")
            for relation_path_id in context_support.get("relation_path_ids", []) or []:
                if context_pack is not None and relation_path_id not in pack_relation_path_ids:
                    errors.append(f"{run_id}: {claim_id}.context_support references relation path outside context pack {relation_path_id}")
        source_support = claim.get("source_support")
        if isinstance(source_support, dict):
            for source_ref in source_support.get("source_refs", []) or []:
                if source_ref not in source_snapshot_refs:
                    errors.append(f"{run_id}: {claim_id}.source_support references unknown source snapshot {source_ref}")
                if context_pack is not None and source_ref not in pack_source_ids:
                    errors.append(f"{run_id}: {claim_id}.source_support references source outside context pack {source_ref}")
    hook_events_rel = data.get("hook_events")
    if isinstance(hook_events_rel, str):
        errors.extend(
            f"{run_id}: {error}"
            for error in validate_hook_events(run_dir, hook_events_rel, phase, candidate_final_event)
        )
    if result_label == "agent-verified":
        nonzero = [record for record in validations if isinstance(record, dict) and record.get("type") == "command_exit" and record.get("exit_code") != 0]
        if nonzero:
            errors.append(f"{run_id}: agent-verified result has nonzero command validation")
        hook_events, _ = load_hook_events(run_dir / str(hook_events_rel)) if isinstance(hook_events_rel, str) else ([], [])
        if any(event.get("status") == "fail" and event.get("neutral_event") != "turn_finalize_attempt" for event in hook_events):
            errors.append(f"{run_id}: agent-verified result has failed hook event")
    assistant_message = data.get("assistant_message")
    if isinstance(assistant_message, dict):
        if assistant_message.get("result_label") != result_label:
            errors.append(f"{run_id}: assistant_message.result_label must match task.result_label")
        claim_ids = assistant_message.get("claim_ids")
        expected_claim_ids = [claim.get("claim_id") for claim in outputs.get("claims", []) if isinstance(claim, dict)]
        if isinstance(claim_ids, list) and sorted(claim_ids) != sorted(expected_claim_ids):
            errors.append(f"{run_id}: assistant_message.claim_ids must match outputs.claims claim_id values")
        digest = assistant_message.get("sha256")
        if isinstance(digest, str) and final_report_text:
            actual_digest = hashlib.sha256(final_report_text.encode("utf-8", errors="replace")).hexdigest()
            if digest != actual_digest:
                errors.append(f"{run_id}: assistant_message.sha256 does not match final_report content")
    return run_id, errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--schema", type=Path, default=Path(".codex/schemas/harness/agent-run.schema.json"))
    parser.add_argument("--context-pack-schema", type=Path, default=Path(".codex/schemas/knowledge/context-pack.schema.json"))
    parser.add_argument("--phase", choices=["pre-finalize", "post-finalize"], default="post-finalize")
    parser.add_argument("--candidate-final-event")
    args = parser.parse_args()
    if not args.path.exists():
        print(f"FAIL: agent run path not found: {args.path}")
        return 2
    if not args.schema.exists():
        print(f"FAIL: agent run schema not found: {args.schema}")
        return 2
    try:
        schema = load_json_file(args.schema)
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: invalid agent run schema: {exc}")
        return 2
    context_pack_schema = None
    if args.context_pack_schema.exists():
        try:
            context_pack_schema = load_json_file(args.context_pack_schema)
        except Exception as exc:  # noqa: BLE001
            print(f"FAIL: invalid context pack schema: {exc}")
            return 2
    candidate_final_event = None
    if args.candidate_final_event:
        try:
            candidate_final_event = json.loads(args.candidate_final_event)
        except json.JSONDecodeError as exc:
            print(f"FAIL: invalid candidate final event JSON: {exc}")
            return 2
        if not isinstance(candidate_final_event, dict):
            print("FAIL: candidate final event must be a JSON object")
            return 2
    paths = run_files(args.path)
    if not paths:
        print(f"SKIP: no agent run artifacts under {args.path}")
        return 0
    failed = False
    checks: list[tuple[str, list[str]]] = []
    for run_file in paths:
        run_id, errors = validate_run_file(run_file, schema, context_pack_schema, args.phase, candidate_final_event)
        failed = failed or bool(errors)
        checks.append((run_id, errors))
    print("FAIL" if failed else "PASS")
    for run_id, errors in checks:
        print(f"- {run_id}: {'FAIL' if errors else 'PASS'}")
        for error in errors:
            print(f"  - {error}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
