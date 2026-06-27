#!/usr/bin/env python3
"""Bootstrap a live Codex agent-run manifest.

This creates the run-local files that the hook adapter can append to and that
`validate_agent_run_artifact.py` can later validate. It deliberately defaults to
`unverified`; it does not turn a final assistant claim into proof.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_ROOT = ROOT / ".codex" / "harness" / "agent-runs"
DEFAULT_BUNDLE_VERSION = "8.5.1"
RESULT_LABELS = {"agent-verified", "user-verification-needed", "unverified", "blocked"}
CLAIM_LINE = re.compile(r"(?m)^\s*(?:[-*]\s*)?(C-[0-9]{3})\s*:\s*(.+?)\s*$")
RESULT_LABEL_LINE = re.compile(r"(?m)^\s*result_label:\s*([A-Za-z0-9_-]+)\s*$")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def today_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d")


def sanitize_id(value: object, fallback: str) -> str:
    raw = str(value or fallback)
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "-", raw).strip(".-")
    return safe[:80] or fallback


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(data: dict[str, Any]) -> str:
    raw = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def parse_result_label(text: str) -> str | None:
    match = RESULT_LABEL_LINE.search(text)
    if not match:
        return None
    value = match.group(1)
    return value if value in RESULT_LABELS else None


def parse_report_claims(text: str) -> list[tuple[str, str]]:
    claims: list[tuple[str, str]] = []
    seen: set[str] = set()
    for match in CLAIM_LINE.finditer(text):
        claim_id = match.group(1)
        claim_text = match.group(2).strip()
        if claim_id in seen or not claim_text:
            continue
        seen.add(claim_id)
        claims.append((claim_id, claim_text))
    return claims


def claim_records_from_report(manifest: dict[str, Any], parsed_claims: list[tuple[str, str]]) -> list[dict[str, Any]]:
    outputs = manifest.get("outputs") if isinstance(manifest.get("outputs"), dict) else {}
    existing_claims = outputs.get("claims", []) if isinstance(outputs.get("claims"), list) else []
    existing_by_id = {
        claim.get("claim_id"): claim
        for claim in existing_claims
        if isinstance(claim, dict) and isinstance(claim.get("claim_id"), str)
    }
    records: list[dict[str, Any]] = []
    for claim_id, text in parsed_claims:
        previous = existing_by_id.get(claim_id)
        previous_text = previous.get("text") if isinstance(previous, dict) else None
        if isinstance(previous, dict) and previous_text == text:
            records.append(dict(previous))
            continue
        records.append({
            "claim_id": claim_id,
            "text": text,
            "claim_class": "execution_result",
            "support": {
                "type": "manual_check",
                "evidence_ref": "final-report.md",
            },
        })
    return records


def next_run_id(output_root: Path, date_id: str) -> str:
    pattern = re.compile(rf"^AR-{re.escape(date_id)}-([0-9]{{3}})$")
    seen: list[int] = []
    if output_root.exists():
        for run_file in output_root.rglob("run.yaml"):
            try:
                data = yaml.safe_load(run_file.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001 - best-effort id allocation.
                continue
            if not isinstance(data, dict):
                continue
            run_id = data.get("run_id")
            if isinstance(run_id, str):
                match = pattern.fullmatch(run_id)
                if match:
                    seen.append(int(match.group(1)))
    return f"AR-{date_id}-{(max(seen) + 1 if seen else 1):03d}"


def default_run_dir(output_root: Path, session_id: str, turn_id: str) -> Path:
    return output_root / sanitize_id(session_id, "unknown-session") / sanitize_id(turn_id, "unknown-turn")


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def placeholder_report(result_label: str) -> str:
    return (
        "# Agent Run Final Report\n\n"
        f"result_label: {result_label}\n\n"
        "## Claims\n\n"
        "- C-001: live agent-run manifest bootstrap initialized current run evidence capture.\n\n"
        "## Evidence\n\n"
        "- artifacts/bootstrap.txt\n\n"
        "## Verification\n\n"
        "- Live run manifest bootstrap is present; task outcome remains unverified until final evidence is supplied.\n"
    )


def build_context_pack(date_id: str, sequence: str, task: str, primary_skill: str) -> dict[str, Any]:
    source_id = f"SRC-{date_id}-{sequence}"
    claim_id = f"KC-{date_id}-{sequence}"
    pack = {
        "schema_version": 2,
        "pack_id": f"CP-{date_id}-{sequence}",
        "task": task,
        "primary_skill": primary_skill,
        "anchors": {
            "files": [],
            "components": [],
            "topics": ["agent-run-bootstrap", "run-trace-integrity"],
            "decisions": [],
            "kanboard_cards": [],
        },
        "admitted_claims": [
            {
                "claim_id": claim_id,
                "statement": "Live agent-run bootstrap captures the current session and turn before Stop validation.",
                "authority_class": "operational",
                "verification_state": "unverified",
                "freshness": "current",
                "operational_effect": "Hook events can attach to a run-local manifest instead of falling back to a temp ledger.",
                "evidence_refs": [source_id],
            }
        ],
        "relation_paths": [],
        "raw_source_handles": [
            {
                "source_id": source_id,
                "locator": "hook://current-session/current-turn",
                "revision": "live",
                "load_when": "agent-run bootstrap evidence needs manual inspection",
            }
        ],
        "expansion_handles": [
            {
                "handle_id": f"EH-{date_id}-{sequence}",
                "claim_id": claim_id,
                "source_ids": [source_id],
                "expand_when": "Need bootstrap source context for the current live run.",
            }
        ],
        "retrieval_trace": {
            "query_type": "live-bootstrap",
            "lexical_hits": [claim_id],
            "vector_hits": [],
            "graph_expansions": [],
            "reranked": [claim_id],
        },
        "compilation": {
            "knowledge_graph_version": "live-bootstrap",
            "index_version": "live-bootstrap",
            "source_snapshot": [source_id],
            "max_hops": 0,
            "token_budget": 512,
            "generated_at": utc_now(),
            "compiler_version": "init-agent-run-v1",
        },
    }
    pack["pack_hash"] = {"algorithm": "sha256", "value": canonical_hash(pack)}
    return pack


def init_run(args: argparse.Namespace) -> int:
    if args.result_label not in RESULT_LABELS:
        raise SystemExit(f"FAIL: result label must be one of {sorted(RESULT_LABELS)}")
    run_dir = args.run_dir or default_run_dir(args.output_root, args.session_id, args.turn_id)
    manifest_path = run_dir / "run.yaml"
    if manifest_path.exists() and not args.force:
        print(json.dumps({"status": "exists", "run_dir": str(run_dir), "manifest": str(manifest_path)}, sort_keys=True))
        return 0
    date_id = args.date_id or today_id()
    run_id = args.run_id or next_run_id(args.output_root, date_id)
    sequence = run_id.rsplit("-", 1)[-1]
    task = args.user_request_summary.strip() or "Live Codex agent run."
    primary_skill = args.primary_skill.strip() or "unknown"
    report = placeholder_report(args.result_label)

    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "artifacts").mkdir(exist_ok=True)
    (run_dir / "context").mkdir(exist_ok=True)
    (run_dir / "final-report.md").write_text(report, encoding="utf-8")
    (run_dir / "artifacts" / "bootstrap.txt").write_text(
        "PASS: live agent-run manifest bootstrap initialized.\n",
        encoding="utf-8",
    )
    context_pack = build_context_pack(date_id, sequence, task, primary_skill)
    context_path = run_dir / "context" / "context-pack.yaml"
    write_yaml(context_path, context_pack)
    manifest = {
        "schema_version": 2,
        "run_id": run_id,
        "bundle_version": args.bundle_version,
        "task": {
            "user_request_summary": task,
            "result_label": args.result_label,
        },
        "routing": {
            "primary_skill": primary_skill,
            "modifiers": [],
            "review_gate": None,
            "output_modifier": None,
            "memory_operation": None,
            "knowledge_context_mode": "optional",
        },
        "context": {
            "context_pack_id": context_pack["pack_id"],
            "context_pack_ref": "context/context-pack.yaml",
            "context_pack_hash": file_sha256(context_path),
            "admitted_claim_ids": [claim["claim_id"] for claim in context_pack["admitted_claims"]],
            "source_snapshot_refs": context_pack["compilation"]["source_snapshot"],
        },
        "assistant_message": {
            "sha256": sha256_text(report),
            "result_label": args.result_label,
            "claim_ids": ["C-001"],
        },
        "outputs": {
            "final_report": "final-report.md",
            "artifact_refs": ["artifacts/bootstrap.txt"],
            "claims": [
                {
                    "claim_id": "C-001",
                    "text": "live agent-run manifest bootstrap initialized current run evidence capture",
                    "claim_class": "limitation",
                    "support": {
                        "type": "artifact_exists",
                        "evidence_ref": "artifacts/bootstrap.txt",
                    },
                    "context_support": {
                        "claim_ids": [claim["claim_id"] for claim in context_pack["admitted_claims"]],
                        "relation_path_ids": [],
                    },
                    "source_support": {
                        "source_refs": context_pack["compilation"]["source_snapshot"],
                    },
                }
            ],
        },
        "validations": [
            {
                "type": "manual_check",
                "evidence_ref": "artifacts/bootstrap.txt",
            }
        ],
        "hook_events": "hook-events.jsonl",
    }
    write_yaml(manifest_path, manifest)
    print(json.dumps({"status": "initialized", "run_id": run_id, "run_dir": str(run_dir)}, sort_keys=True))
    return 0


def finalize_run(args: argparse.Namespace) -> int:
    run_dir = args.run_dir
    manifest_path = run_dir / "run.yaml"
    if not manifest_path.exists():
        print(json.dumps({"status": "missing", "manifest": str(manifest_path)}, sort_keys=True))
        return 0
    bootstrap_artifact = run_dir / "artifacts" / "bootstrap.txt"
    if not bootstrap_artifact.exists() and not args.force:
        print(json.dumps({"status": "skipped_non_bootstrap", "manifest": str(manifest_path)}, sort_keys=True))
        return 0
    message = args.last_assistant_message or ""
    if not message and args.input_file:
        data = json.loads(args.input_file.read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("last_assistant_message"), str):
            message = data["last_assistant_message"]
    if not message:
        print(json.dumps({"status": "no_message", "manifest": str(manifest_path)}, sort_keys=True))
        return 0
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise SystemExit("FAIL: run.yaml is not a mapping")
    (run_dir / "final-report.md").write_text(message, encoding="utf-8")
    parsed_label = parse_result_label(message)
    parsed_claims = parse_report_claims(message)
    if parsed_label is not None:
        task = manifest.get("task")
        if isinstance(task, dict):
            task["result_label"] = parsed_label
    assistant = manifest.get("assistant_message")
    if not isinstance(assistant, dict):
        assistant = {}
        manifest["assistant_message"] = assistant
    assistant["sha256"] = sha256_text(message)
    if parsed_label is not None:
        assistant["result_label"] = parsed_label
    if parsed_claims:
        claim_ids = [claim_id for claim_id, _ in parsed_claims]
        assistant["claim_ids"] = claim_ids
        outputs = manifest.get("outputs")
        if not isinstance(outputs, dict):
            outputs = {}
            manifest["outputs"] = outputs
        outputs["claims"] = claim_records_from_report(manifest, parsed_claims)
        validations = manifest.get("validations")
        if not isinstance(validations, list):
            validations = []
            manifest["validations"] = validations
        if not any(isinstance(item, dict) and item.get("type") == "manual_check" and item.get("evidence_ref") == "final-report.md" for item in validations):
            validations.append({"type": "manual_check", "evidence_ref": "final-report.md"})
    write_yaml(manifest_path, manifest)
    print(json.dumps({
        "status": "finalized",
        "manifest": str(manifest_path),
        "parsed_claim_ids": [claim_id for claim_id, _ in parsed_claims],
        "parsed_result_label": parsed_label or "",
    }, sort_keys=True))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize or finalize a live agent-run manifest")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init")
    init.add_argument("--session-id", required=True)
    init.add_argument("--turn-id", required=True)
    init.add_argument("--user-request-summary", default="")
    init.add_argument("--primary-skill", default="unknown")
    init.add_argument("--result-label", default="unverified")
    init.add_argument("--bundle-version", default=DEFAULT_BUNDLE_VERSION)
    init.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    init.add_argument("--run-dir", type=Path)
    init.add_argument("--run-id", default="")
    init.add_argument("--date-id", default="")
    init.add_argument("--force", action="store_true")
    init.set_defaults(func=init_run)

    finalize = sub.add_parser("finalize")
    finalize.add_argument("run_dir", type=Path)
    finalize.add_argument("--last-assistant-message", default="")
    finalize.add_argument("--input-file", type=Path)
    finalize.add_argument("--force", action="store_true")
    finalize.set_defaults(func=finalize_run)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
