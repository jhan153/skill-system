#!/usr/bin/env python3
"""Declared-subject receipt monitor for the opt-in 9.2.1 harness."""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

from hook_runtime import ZERO_HASH, event_hash


VERSION = "9.2.1"
CONTRACT_ENV = "SKILL_SYSTEM_VERIFIER_CONTRACT"
TRUSTED_VERIFIERS = {"user", "repository", "external"}
VERIFIER_ORIGINS = TRUSTED_VERIFIERS | {"agent_modified"}
MAX_SUBJECT_REFS = 32
MAX_SUBJECT_BYTES = 16 * 1024 * 1024
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")

def digest(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def configured_contract() -> tuple[dict[str, Any] | None, str | None]:
    raw = os.environ.get(CONTRACT_ENV, "")
    if not raw:
        return None, None
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return None, f"{CONTRACT_ENV} must be valid JSON"
    if not isinstance(value, dict):
        return None, f"{CONTRACT_ENV} must be a JSON object"
    allowed = {
        "contract_id", "verifier_command_hash", "negative_control_command_hash",
        "verifier_origin", "oracle_origin", "oracle_hash", "subject_refs",
    }
    if set(value) - allowed:
        return None, f"{CONTRACT_ENV} has unsupported fields"
    if not isinstance(value.get("contract_id"), str) or not 0 < len(value["contract_id"]) <= 80:
        return None, "verifier contract requires a short contract_id"
    if not isinstance(value.get("verifier_command_hash"), str) or not SHA256_RE.fullmatch(
        value["verifier_command_hash"]
    ):
        return None, "verifier contract requires verifier_command_hash"
    for legacy_field in ("negative_control_command_hash", "oracle_hash"):
        legacy_value = value.get(legacy_field)
        if legacy_value is not None and (
            not isinstance(legacy_value, str) or not SHA256_RE.fullmatch(legacy_value)
        ):
            return None, f"{legacy_field} must be sha256 when present"
    if value.get("verifier_origin") not in VERIFIER_ORIGINS:
        return None, "verifier contract has invalid verifier_origin"
    refs = value.get("subject_refs")
    if not isinstance(refs, list) or not 0 < len(refs) <= MAX_SUBJECT_REFS:
        return None, f"verifier contract requires 1..{MAX_SUBJECT_REFS} subject_refs"
    normalized: list[str] = []
    for ref in refs:
        if not isinstance(ref, str) or not ref or Path(ref).is_absolute() or ".." in Path(ref).parts:
            return None, "verifier contract subject_refs must be workspace-relative files"
        normalized.append(Path(ref).as_posix())
    if len(normalized) != len(set(normalized)):
        return None, "verifier contract subject_refs must be unique"
    contract = {
        "harness_version": VERSION,
        "contract_id": value["contract_id"],
        "verifier_command_hash": value["verifier_command_hash"],
        "verifier_origin": value["verifier_origin"],
        "subject_refs": normalized,
    }
    contract["contract_digest"] = digest(contract)
    return contract, None


def read_events(ledger: Path) -> tuple[list[dict[str, Any]], list[str]]:
    if not ledger.exists():
        return [], []
    events: list[dict[str, Any]] = []
    errors: list[str] = []
    previous_seq, previous_hash = 0, ZERO_HASH
    for line_no, line in enumerate(ledger.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            errors.append(f"ledger line {line_no} is not valid JSON")
            continue
        if not isinstance(event, dict):
            errors.append(f"ledger line {line_no} is not an object")
            continue
        if event.get("schema_version") != 2 or event.get("seq") != previous_seq + 1:
            errors.append(f"ledger line {line_no} has invalid schema or seq")
        if event.get("prev_event_hash") != previous_hash or event.get("event_hash") != event_hash(event):
            errors.append(f"ledger line {line_no} has a hash-chain mismatch")
        if isinstance(event.get("seq"), int):
            previous_seq = event["seq"]
        if isinstance(event.get("event_hash"), str):
            previous_hash = event["event_hash"]
        events.append(event)
    return events, errors


def bound_contract(
    events: list[dict[str, Any]],
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, str | None]:
    bindings = [
        (event.get("evidence", {}).get("verification_contract"), event)
        for event in events
        if event.get("neutral_event") == "request_received" and isinstance(event.get("evidence"), dict)
        and isinstance(event["evidence"].get("verification_contract"), dict)
    ]
    if not bindings:
        return None, None, None
    if len(bindings) != 1:
        return None, None, "ledger must contain exactly one pre-bound verifier contract"
    contract, binding_event = bindings[0]
    body = dict(contract)
    contract_digest = body.pop("contract_digest", None)
    if contract_digest != digest(body):
        return None, None, "pre-bound verifier contract digest mismatch"
    if body.get("harness_version") != VERSION:
        return None, None, "pre-bound verifier contract version mismatch"
    seq = int(binding_event.get("seq", 0))
    if any(
        event.get("neutral_event") in {"tool_preflight", "permission_requested", "tool_result"}
        and int(event.get("seq", 0)) < seq
        for event in events
    ):
        return None, None, "verifier contract was bound after tool execution began"
    return contract, binding_event, None


def run_binding(value: dict[str, Any]) -> tuple[str, str]:
    evidence = value.get("evidence") if isinstance(value.get("evidence"), dict) else {}
    session_id = value.get("session_id") or evidence.get("session_id")
    turn_id = value.get("turn_id") or evidence.get("turn_id")
    return str(session_id or ""), str(turn_id or "")


def same_run(event: dict[str, Any], data: dict[str, Any]) -> bool:
    expected = run_binding(data)
    return bool(expected[0] and expected[1] and run_binding(event) == expected)


def subject_snapshot(contract: dict[str, Any], cwd: object) -> tuple[str | None, int, str | None]:
    if not isinstance(cwd, str) or not cwd:
        return None, 0, "hook input lacks cwd for subject binding"
    root = Path(cwd).expanduser().resolve()
    if not root.is_dir():
        return None, 0, "hook cwd is not a directory"
    entries: list[dict[str, Any]] = []
    total = 0
    for ref in contract["subject_refs"]:
        try:
            path = (root / ref).resolve(strict=True)
        except OSError:
            return None, total, f"subject ref is missing: {ref}"
        if not path.is_relative_to(root) or not path.is_file():
            return None, total, f"subject ref is not a workspace file: {ref}"
        total += path.stat().st_size
        if total > MAX_SUBJECT_BYTES:
            return None, total, f"subject refs exceed {MAX_SUBJECT_BYTES} bytes"
        entries.append({"path": ref, "size": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    return digest(entries), total, None


def observe_receipt(
    ledger: Path,
    data: dict[str, Any],
    *,
    command_hash: object,
    exit_code: object,
    output_digest: object,
) -> dict[str, Any] | None:
    events, errors = read_events(ledger)
    contract, binding_event, contract_error = bound_contract(events)
    if (
        errors or contract is None or binding_event is None or contract_error is not None
        or not same_run(binding_event, data)
    ):
        return None
    if command_hash != contract.get("verifier_command_hash"):
        return None
    receipt: dict[str, Any] = {
        "harness_version": VERSION,
        "contract_digest": contract["contract_digest"],
        "kind": "positive",
        "command_hash": command_hash,
        "session_id": str(data.get("session_id") or ""),
        "turn_id": str(data.get("turn_id") or ""),
        "tool_use_id": str(data.get("tool_use_id") or ""),
        "exit_code": exit_code,
        "output_digest": output_digest,
        "observed_result": "pass" if exit_code == 0 else "fail" if isinstance(exit_code, int) else "unverified",
    }
    subject_digest, subject_bytes, error = subject_snapshot(contract, data.get("cwd"))
    receipt.update({"subject_digest": subject_digest, "subject_bytes": subject_bytes})
    if error is not None:
        receipt.update({"observed_result": "unverified", "subject_error": error})
    return receipt


def decide(ledger: Path, data: dict[str, Any]) -> dict[str, Any]:
    """Report receipt state without interpreting or controlling task completion."""
    base = {"harness_version": VERSION}

    def result(receipt_status: str, reason_code: str, **extra: Any) -> dict[str, Any]:
        return {**base, "receipt_status": receipt_status, "reason_code": reason_code, **extra}

    events, errors = read_events(ledger)
    if errors:
        return result("integrity_error", "ledger_integrity_error", integrity_errors=errors[:5])
    contract, binding_event, contract_error = bound_contract(events)
    if contract_error:
        return result("integrity_error", "contract_integrity_error")
    if contract is None or binding_event is None:
        return result("missing", "missing_prebound_contract")
    contract_fields = {
        "contract_id": contract["contract_id"],
        "contract_digest": contract["contract_digest"],
    }
    if not same_run(binding_event, data):
        return result("unavailable", "contract_run_mismatch", **contract_fields)
    contract_receipts = [
        (event["evidence"]["verifier_receipt"], int(event.get("seq", 0)), event)
        for event in events
        if isinstance(event.get("evidence"), dict)
        and isinstance(event["evidence"].get("verifier_receipt"), dict)
        and event["evidence"]["verifier_receipt"].get("contract_digest") == contract["contract_digest"]
    ]
    receipts = [entry for entry in contract_receipts if same_run(entry[2], data)]
    if contract_receipts and not receipts:
        return result("unavailable", "receipt_run_mismatch", **contract_fields)
    positives = [(receipt, seq) for receipt, seq, _event in receipts if receipt.get("kind") == "positive"]
    if not positives:
        return result("missing", "missing_positive_receipt", **contract_fields)
    positive, positive_seq = positives[-1]
    receipt_fields = {
        **contract_fields,
        "receipt_seq": positive_seq,
        "receipt_subject_digest": positive.get("subject_digest"),
        "receipt_subject_bytes": positive.get("subject_bytes"),
    }
    session_id, turn_id = run_binding(data)
    if positive.get("observed_result") == "fail":
        return result("failed", "verifier_failed", **receipt_fields)
    if (
        positive.get("observed_result") != "pass" or not positive.get("subject_digest")
        or not positive.get("tool_use_id") or not isinstance(positive.get("output_digest"), str)
        or not SHA256_RE.fullmatch(positive["output_digest"])
        or positive.get("session_id") != session_id or positive.get("turn_id") != turn_id
    ):
        return result("unavailable", "receipt_or_subject_unbound", **receipt_fields)
    current_digest, current_bytes, subject_error = subject_snapshot(contract, data.get("cwd"))
    if subject_error is not None:
        return result(
            "unavailable",
            "subject_unavailable_at_stop",
            **receipt_fields,
            subject_error=subject_error,
        )
    if current_digest != positive["subject_digest"]:
        return result(
            "stale",
            "subject_changed_after_verifier",
            **receipt_fields,
            current_subject_digest=current_digest,
            subject_bytes=current_bytes,
        )
    if contract.get("verifier_origin") == "agent_modified":
        return result(
            "supporting_only",
            "agent_modified_verifier",
            **receipt_fields,
            current_subject_digest=current_digest,
            subject_bytes=current_bytes,
        )
    if contract.get("verifier_origin") not in TRUSTED_VERIFIERS:
        return result(
            "untrusted_origin",
            "untrusted_verifier_origin",
            **receipt_fields,
            current_subject_digest=current_digest,
            subject_bytes=current_bytes,
        )
    return result(
        "current_for_declared_subjects",
        "trusted_receipt_matches_declared_subjects",
        **receipt_fields,
        current_subject_digest=current_digest,
        subject_bytes=current_bytes,
    )
