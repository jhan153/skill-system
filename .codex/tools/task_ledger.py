#!/usr/bin/env python3
"""Checkpointed-execution task ledger (workflow-task-ledger).

Resume-safe step/finding state for multi-turn tasks that sit between one-shot
work and a full LoopRun. NOT a LoopRun: no verifier-feedback convergence, Stop
continuation, or budget/idempotency governance. Completion is gated on observed
evidence and open findings, never on free-text claims.

State lives in <dir>/task-run.yaml. The caller chooses <dir> (runtime picks a
path under the harness; tests use a tempdir), so the bundle ships no runtime
state. Each evidence ref is a JSON object (observed: command exit, verifier
result, file/artifact/readback, user approval).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

sys.dont_write_bytecode = True

STEP_STATUSES = {"pending", "in_progress", "complete", "failed", "blocked"}
FINDING_SEVERITIES = {"low", "medium", "high", "critical"}


def ledger_path(run_dir: Path) -> Path:
    return run_dir / "task-run.yaml"


def load(run_dir: Path) -> dict[str, Any]:
    data = yaml.safe_load(ledger_path(run_dir).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("FAIL: task-run.yaml is not a mapping")
    return data


def save(run_dir: Path, data: dict[str, Any]) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    ledger_path(run_dir).write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def parse_evidence(values: list[str]) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    for raw in values or []:
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"FAIL: --evidence must be a JSON object: {exc}")
        if not isinstance(obj, dict):
            raise SystemExit("FAIL: --evidence must be a JSON object")
        refs.append(obj)
    return refs


def find(items: list[dict[str, Any]], key: str, value: str) -> dict[str, Any] | None:
    return next((it for it in items if it.get(key) == value), None)


def cmd_init(args: argparse.Namespace) -> int:
    run_dir = args.dir
    if ledger_path(run_dir).exists():
        raise SystemExit("FAIL: task-run.yaml already exists")
    data = {
        "schema_version": 1,
        "task_run_id": args.task_run_id or run_dir.name or "task-run",
        "work_item_ref": args.work_item_ref or None,
        "objective": args.objective,
        "workspace": {"root": args.workspace_root or "", "revision": args.revision or ""},
        "status": "active",
        "active_step_id": None,
        "steps": [],
        "findings": [],
        "final_verification": {"status": "pending", "evidence_refs": []},
    }
    save(run_dir, data)
    print(f"PASS: initialized {ledger_path(run_dir)}")
    return 0


def cmd_add_step(args: argparse.Namespace) -> int:
    data = load(args.dir)
    if find(data["steps"], "id", args.id):
        raise SystemExit(f"FAIL: step {args.id} already exists")
    data["steps"].append({"id": args.id, "title": args.title, "status": "pending", "evidence_refs": []})
    save(args.dir, data)
    print(f"PASS: added step {args.id}")
    return 0


def cmd_checkpoint(args: argparse.Namespace) -> int:
    if args.status not in STEP_STATUSES:
        raise SystemExit(f"FAIL: status must be one of {sorted(STEP_STATUSES)}")
    data = load(args.dir)
    step = find(data["steps"], "id", args.step)
    if step is None:
        raise SystemExit(f"FAIL: unknown step {args.step}")
    refs = parse_evidence(args.evidence)
    if refs:
        step["evidence_refs"].extend(refs)
    if args.status == "complete" and not step["evidence_refs"]:
        raise SystemExit(f"FAIL: step {args.step} cannot be complete without observed evidence_refs")
    step["status"] = args.status
    data["active_step_id"] = args.step if args.status == "in_progress" else data.get("active_step_id")
    save(args.dir, data)
    print(f"PASS: step {args.step} -> {args.status}")
    return 0


def cmd_finding_add(args: argparse.Namespace) -> int:
    if args.severity not in FINDING_SEVERITIES:
        raise SystemExit(f"FAIL: severity must be one of {sorted(FINDING_SEVERITIES)}")
    data = load(args.dir)
    if find(data["findings"], "id", args.id):
        raise SystemExit(f"FAIL: finding {args.id} already exists")
    data["findings"].append({
        "id": args.id,
        "title": args.title,
        "step_id": args.step,
        "severity": args.severity,
        "status": "open",
        "evidence_refs": parse_evidence(args.evidence),
    })
    save(args.dir, data)
    print(f"PASS: added finding {args.id} (open)")
    return 0


def cmd_finding_resolve(args: argparse.Namespace) -> int:
    data = load(args.dir)
    finding = find(data["findings"], "id", args.id)
    if finding is None:
        raise SystemExit(f"FAIL: unknown finding {args.id}")
    refs = parse_evidence(args.evidence)
    if not args.resolution:
        raise SystemExit("FAIL: resolve requires a non-empty --resolution")
    if not refs:
        raise SystemExit(
            "FAIL: resolve requires verification evidence (new --evidence distinct from the "
            "admission/discovery evidence; mark it with kind=verification)"
        )
    finding["evidence_refs"].extend(refs)
    finding["status"] = "resolved"
    finding["resolution"] = args.resolution
    save(args.dir, data)
    print(f"PASS: finding {args.id} -> resolved")
    return 0


def cmd_finding_accept_risk(args: argparse.Namespace) -> int:
    data = load(args.dir)
    finding = find(data["findings"], "id", args.id)
    if finding is None:
        raise SystemExit(f"FAIL: unknown finding {args.id}")
    finding.update({
        "status": "accepted_risk",
        "accepted_by": args.accepted_by,
        "reason": args.reason,
        "review_at": args.review_at,
    })
    save(args.dir, data)
    print(f"PASS: finding {args.id} -> accepted_risk")
    return 0


def cmd_final_verify(args: argparse.Namespace) -> int:
    data = load(args.dir)
    refs = parse_evidence(args.evidence)
    if args.status == "pass" and not refs and not data["final_verification"].get("evidence_refs"):
        raise SystemExit("FAIL: final-verify pass requires observed evidence_refs")
    data["final_verification"]["evidence_refs"].extend(refs)
    data["final_verification"]["status"] = args.status
    save(args.dir, data)
    print(f"PASS: final_verification -> {args.status}")
    return 0


def gate_reasons(data: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    incomplete = [s["id"] for s in data["steps"] if s.get("status") != "complete"]
    if incomplete:
        reasons.append(f"steps not complete: {', '.join(incomplete)}")
    if data["final_verification"].get("status") != "pass":
        reasons.append("final_verification is not pass")
    open_findings = [f["id"] for f in data["findings"] if f.get("status") == "open"]
    if open_findings:
        reasons.append(f"open findings: {', '.join(open_findings)}")
    return reasons


def cmd_close(args: argparse.Namespace) -> int:
    data = load(args.dir)
    reasons = gate_reasons(data)
    if reasons:
        print("FAIL: task run cannot close")
        for reason in reasons:
            print(f"- {reason}")
        return 1
    data["status"] = "complete"
    save(args.dir, data)
    print("PASS: task run closed (complete)")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    data = load(args.dir)
    steps = data["steps"]
    done = sum(1 for s in steps if s.get("status") == "complete")
    open_f = sum(1 for f in data["findings"] if f.get("status") == "open")
    print(f"task_run_id={data.get('task_run_id')} status={data.get('status')}")
    print(f"steps={done}/{len(steps)} complete; open_findings={open_f}; final_verification={data['final_verification'].get('status')}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Checkpointed-execution task ledger")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_dir(p: argparse.ArgumentParser) -> None:
        p.add_argument("dir", type=Path)

    p = sub.add_parser("init"); add_dir(p)
    p.add_argument("--objective", required=True)
    p.add_argument("--workspace-root", default="")
    p.add_argument("--revision", default="")
    p.add_argument("--task-run-id", default="")
    p.add_argument("--work-item-ref", default="")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("add-step"); add_dir(p)
    p.add_argument("--id", required=True)
    p.add_argument("--title", default="")
    p.set_defaults(func=cmd_add_step)

    p = sub.add_parser("checkpoint"); add_dir(p)
    p.add_argument("--step", required=True)
    p.add_argument("--status", required=True)
    p.add_argument("--evidence", action="append", default=[])
    p.set_defaults(func=cmd_checkpoint)

    p = sub.add_parser("finding-add"); add_dir(p)
    p.add_argument("--id", required=True)
    p.add_argument("--title", default="")
    p.add_argument("--severity", required=True)
    p.add_argument("--step", default=None)
    p.add_argument("--evidence", action="append", default=[])
    p.set_defaults(func=cmd_finding_add)

    p = sub.add_parser("finding-resolve"); add_dir(p)
    p.add_argument("--id", required=True)
    p.add_argument("--resolution", default="")
    p.add_argument("--evidence", action="append", default=[])
    p.set_defaults(func=cmd_finding_resolve)

    p = sub.add_parser("finding-accept-risk"); add_dir(p)
    p.add_argument("--id", required=True)
    p.add_argument("--accepted-by", required=True, choices=["user", "project_policy"])
    p.add_argument("--reason", required=True)
    p.add_argument("--review-at", required=True)
    p.set_defaults(func=cmd_finding_accept_risk)

    p = sub.add_parser("final-verify"); add_dir(p)
    p.add_argument("--status", required=True, choices=["pending", "pass"])
    p.add_argument("--evidence", action="append", default=[])
    p.set_defaults(func=cmd_final_verify)

    p = sub.add_parser("close"); add_dir(p); p.set_defaults(func=cmd_close)
    p = sub.add_parser("status"); add_dir(p); p.set_defaults(func=cmd_status)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
