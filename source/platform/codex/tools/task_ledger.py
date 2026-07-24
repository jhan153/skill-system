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
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import yaml

sys.dont_write_bytecode = True

from _validation import load_json_file, validate_schema

SCHEMA_ROOT = Path(__file__).resolve().parent.parent / "schemas" / "task"

STEP_STATUSES = {"pending", "in_progress", "complete", "failed", "blocked", "deferred"}
FINDING_SEVERITIES = {"low", "medium", "high", "critical"}
WORK_KINDS = {
    "core",
    "required_prerequisite",
    "agent_validation",
    "test_authoring",
    "validation_artifact",
    "optional_quality",
    "meta",
}
OPTIONAL_WORK_KINDS = {
    "agent_validation",
    "test_authoring",
    "validation_artifact",
    "optional_quality",
    "meta",
}


def ledger_path(run_dir: Path) -> Path:
    return run_dir / "task-run.yaml"


def work_contract_path(run_dir: Path) -> Path:
    return run_dir / "work-contract.yaml"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def semantic_intent_key(kind: str, title: str) -> str:
    normalized = " ".join(title.lower().split())
    if kind in {"agent_validation", "test_authoring", "validation_artifact", "optional_quality"}:
        basis = "validation"
    elif kind == "meta":
        basis = "meta"
    else:
        basis = f"{kind}:{normalized}"
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()


def safe_contract_component(value: str) -> str:
    cleaned = "".join(
        character
        if character.isascii() and (character.isalnum() or character in "._-")
        else "-"
        for character in value
    ).strip("._-")
    return cleaned[:96] or "task-run"


def schema_errors(value: dict[str, Any], name: str) -> list[str]:
    path = SCHEMA_ROOT / name
    if not path.is_file():
        return []
    return validate_schema(value, load_json_file(path))


def work_contract_semantic_errors(contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    scope = contract.get("scope") if isinstance(contract.get("scope"), dict) else {}
    allowed = {
        item
        for item in scope.get("allowed_action_classes", [])
        if isinstance(item, str)
    }
    excluded = {
        item
        for item in scope.get("excluded_action_classes", [])
        if isinstance(item, str)
    }
    overlap = sorted(allowed & excluded)
    if overlap:
        errors.append("action classes cannot be both allowed and excluded: " + ", ".join(overlap))
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
                "user-owned verification must exclude agent verification work: "
                + ", ".join(missing)
            )
    return errors


def default_work_contract(args: argparse.Namespace, task_run_id: str) -> dict[str, Any]:
    verification_owner = args.verification_owner
    interaction_mode = args.interaction_mode
    execution_mode = args.execution_mode
    excluded = list(dict.fromkeys(args.exclude_action or []))
    if verification_owner == "user":
        for item in ("agent_validation", "test_authoring", "validation_artifact"):
            if item not in excluded:
                excluded.append(item)
    handoff = "user-verification-needed" if verification_owner == "user" else "unverified"
    unattended_no_interaction = (
        execution_mode == "unattended_goal_loop" and interaction_mode == "forbidden"
    )
    allowed = sorted(WORK_KINDS - set(excluded))
    return {
        "schema_version": 1,
        "contract_id": f"WC-{safe_contract_component(task_run_id)}",
        "source": {"kind": "natural_language"},
        "execution": {"mode": execution_mode},
        "scope": {
            "core_deliverables": args.core_deliverable or [args.objective],
            "allowed_action_classes": allowed,
            "excluded_action_classes": sorted(excluded),
            "non_goals": args.non_goal or [],
        },
        "verification": {
            "owner": verification_owner,
            "handoff_on_unavailable": handoff,
        },
        "interaction": {
            "mode": interaction_mode,
            "approval_behavior": "defer" if unattended_no_interaction else "normal",
            "question_behavior": "defer" if unattended_no_interaction else "normal",
        },
        "continuation": {
            "on_local_block": "reevaluate_remaining_work",
            "on_optional_failure": "continue",
            "duplicate_intent_behavior": "defer_same_intent",
            "global_block_condition": "no_required_runnable_work",
        },
        "termination": {
            "time_budget_seconds": args.time_budget_seconds,
            "stop_condition": args.stop_condition
            or "All required runnable work is complete or genuinely blocked.",
        },
    }


def load_work_contract(run_dir: Path, data: dict[str, Any] | None = None) -> dict[str, Any]:
    data = data or load(run_dir)
    ref = data.get("work_contract_ref")
    if not isinstance(ref, str) or not ref:
        return {
            "scope": {"excluded_action_classes": []},
            "verification": {"owner": "agent", "handoff_on_unavailable": "blocked"},
            "interaction": {"mode": "allowed", "approval_behavior": "normal"},
            "execution": {"mode": "attended"},
        }
    relative = Path(ref)
    if relative.is_absolute():
        raise SystemExit("FAIL: work_contract_ref must be relative to the TaskRun directory")
    root = run_dir.resolve()
    path = (root / relative).resolve()
    try:
        path.relative_to(root)
    except ValueError:
        raise SystemExit("FAIL: work_contract_ref escapes the TaskRun directory") from None
    if not path.is_file():
        raise SystemExit("FAIL: work_contract_ref does not resolve to a file")
    contract = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(contract, dict):
        raise SystemExit("FAIL: work contract is not a mapping")
    expected = data.get("work_contract_hash")
    if isinstance(expected, str) and expected and expected != file_sha256(path):
        raise SystemExit("FAIL: work_contract_hash does not match work-contract.yaml")
    errors = schema_errors(contract, "work-contract.schema.json")
    errors.extend(work_contract_semantic_errors(contract))
    if errors:
        raise SystemExit("FAIL: invalid work contract\n- " + "\n- ".join(errors))
    return contract


def excluded_action_classes(contract: dict[str, Any]) -> set[str]:
    scope = contract.get("scope") if isinstance(contract.get("scope"), dict) else {}
    raw = scope.get("excluded_action_classes", [])
    return {item for item in raw if isinstance(item, str)}


def load(run_dir: Path) -> dict[str, Any]:
    data = yaml.safe_load(ledger_path(run_dir).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("FAIL: task-run.yaml is not a mapping")
    return data


def save(run_dir: Path, data: dict[str, Any]) -> None:
    errors = schema_errors(data, "task-run.schema.json")
    if errors:
        raise SystemExit("FAIL: invalid TaskRun state\n- " + "\n- ".join(errors))
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
    task_run_id = args.task_run_id or run_dir.name or "task-run"
    contract = default_work_contract(args, task_run_id)
    contract_errors = schema_errors(contract, "work-contract.schema.json")
    contract_errors.extend(work_contract_semantic_errors(contract))
    if contract_errors:
        raise SystemExit("FAIL: invalid work contract\n- " + "\n- ".join(contract_errors))
    run_dir.mkdir(parents=True, exist_ok=True)
    work_contract_path(run_dir).write_text(
        yaml.safe_dump(contract, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    data = {
        "schema_version": 2,
        "task_run_id": task_run_id,
        "work_item_ref": args.work_item_ref or None,
        "objective": args.objective,
        "work_contract_ref": "work-contract.yaml",
        "work_contract_hash": file_sha256(work_contract_path(run_dir)),
        "workspace": {"root": args.workspace_root or "", "revision": args.revision or ""},
        "status": "active",
        "result_label": "pending",
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
    if args.kind not in WORK_KINDS:
        raise SystemExit(f"FAIL: kind must be one of {sorted(WORK_KINDS)}")
    unknown_dependencies = [item for item in args.depends_on if not find(data["steps"], "id", item)]
    if unknown_dependencies:
        raise SystemExit(f"FAIL: unknown dependencies: {', '.join(unknown_dependencies)}")
    contract = load_work_contract(args.dir, data)
    required = args.required or (not args.optional and args.kind not in OPTIONAL_WORK_KINDS)
    intent_key = args.intent_key or semantic_intent_key(args.kind, args.title or args.id)
    status = "pending"
    deferred_reason = ""
    existing_intent = next(
        (
            step
            for step in data["steps"]
            if step.get("intent_key") == intent_key and step.get("status") in {"deferred", "blocked"}
        ),
        None,
    )
    if existing_intent is not None:
        print(
            f"PASS: step {args.id} not added; semantic intent is already "
            f"{existing_intent.get('status')} as {existing_intent.get('id')}"
        )
        return 0
    if args.kind in excluded_action_classes(contract):
        status = "deferred"
        deferred_reason = "action class is excluded by the user work contract"
        if args.kind in OPTIONAL_WORK_KINDS:
            required = False
    elif args.requires_interaction and contract.get("execution", {}).get("mode") == "unattended_goal_loop" and contract.get("interaction", {}).get("mode") == "forbidden":
        status = "deferred"
        deferred_reason = "unattended Goal/Loop contract forbids additional interaction"
    step = {
        "id": args.id,
        "title": args.title,
        "kind": args.kind,
        "required": required,
        "depends_on": args.depends_on,
        "intent_key": intent_key,
        "requires_interaction": args.requires_interaction,
        "status": status,
        "evidence_refs": [],
    }
    if deferred_reason:
        step["deferred_reason"] = deferred_reason
    data["steps"].append(step)
    refresh_execution_state(data)
    save(args.dir, data)
    print(f"PASS: added step {args.id} ({status})")
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
    if args.status == "deferred" and not args.reason:
        raise SystemExit(f"FAIL: step {args.step} cannot be deferred without --reason")
    if args.status == "deferred":
        step["deferred_reason"] = args.reason
    elif args.status != "blocked":
        step.pop("deferred_reason", None)
    step["status"] = args.status
    data["active_step_id"] = args.step if args.status == "in_progress" else data.get("active_step_id")
    refresh_execution_state(data)
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
    incomplete = [
        s["id"]
        for s in data["steps"]
        if s.get("required", True) and s.get("status") != "complete"
    ]
    if incomplete:
        reasons.append(f"required steps not complete: {', '.join(incomplete)}")
    final_status = data["final_verification"].get("status")
    if final_status == "pending":
        reasons.append("final_verification is pending")
    open_findings = [f["id"] for f in data["findings"] if f.get("status") == "open"]
    if open_findings:
        reasons.append(f"open findings: {', '.join(open_findings)}")
    return reasons


def cmd_close(args: argparse.Namespace) -> int:
    data = load(args.dir)
    contract = load_work_contract(args.dir, data)
    reasons = gate_reasons(data)
    if reasons:
        print("FAIL: task run cannot close")
        for reason in reasons:
            print(f"- {reason}")
        return 1
    final_status = data["final_verification"].get("status")
    owner = contract.get("verification", {}).get("owner")
    expected_handoff = contract.get("verification", {}).get("handoff_on_unavailable")
    if final_status == "pass":
        result_label = "agent-verified"
    elif final_status == "user-verification-needed" and owner in {"user", "shared"}:
        result_label = "user-verification-needed"
    elif final_status == "unverified" and expected_handoff == "unverified":
        result_label = "unverified"
    else:
        print("FAIL: task run cannot close")
        print(
            f"- final_verification={final_status!r} is incompatible with "
            f"verification owner={owner!r} handoff={expected_handoff!r}"
        )
        return 1
    data["status"] = "complete"
    data["result_label"] = result_label
    save(args.dir, data)
    print(f"PASS: task run closed (complete, {result_label})")
    return 0


def runnable_steps(data: dict[str, Any]) -> list[dict[str, Any]]:
    completed = {step["id"] for step in data["steps"] if step.get("status") == "complete"}
    candidates = []
    for index, step in enumerate(data["steps"]):
        if step.get("status") not in {"pending", "in_progress", "failed"}:
            continue
        dependencies = step.get("depends_on", [])
        if any(item not in completed for item in dependencies):
            continue
        candidates.append((0 if step.get("required", True) else 1, index, step))
    return [item[2] for item in sorted(candidates, key=lambda item: (item[0], item[1]))]


def refresh_execution_state(data: dict[str, Any]) -> None:
    if data.get("status") in {"complete", "cancelled"}:
        return
    incomplete_required = [
        step
        for step in data["steps"]
        if step.get("required", True) and step.get("status") != "complete"
    ]
    if incomplete_required and not runnable_steps(data):
        data["status"] = "blocked"
        data["result_label"] = "blocked"
    else:
        data["status"] = "active"
        data["result_label"] = "pending"


def cmd_next_action(args: argparse.Namespace) -> int:
    data = load(args.dir)
    refresh_execution_state(data)
    save(args.dir, data)
    runnable = runnable_steps(data)
    if runnable:
        step = runnable[0]
        result = {
            "status": "runnable",
            "step_id": step["id"],
            "kind": step.get("kind", "core"),
            "required": step.get("required", True),
            "intent_key": step.get("intent_key"),
        }
    else:
        incomplete_required = [
            step
            for step in data["steps"]
            if step.get("required", True) and step.get("status") != "complete"
        ]
        result = {
            "status": "blocked" if incomplete_required else "complete",
            "blocked_step_ids": [step["id"] for step in incomplete_required],
        }
    if args.format == "json":
        print(json.dumps(result, sort_keys=True))
    else:
        print(result["status"])
        if result.get("step_id"):
            print(f"- step_id: {result['step_id']}")
        if result.get("blocked_step_ids"):
            print(f"- blocked_step_ids: {', '.join(result['blocked_step_ids'])}")
    return 1 if result["status"] == "blocked" else 0


def cmd_status(args: argparse.Namespace) -> int:
    data = load(args.dir)
    steps = data["steps"]
    done = sum(1 for s in steps if s.get("status") == "complete")
    open_f = sum(1 for f in data["findings"] if f.get("status") == "open")
    print(
        f"task_run_id={data.get('task_run_id')} status={data.get('status')} "
        f"result_label={data.get('result_label', 'pending')}"
    )
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
    p.add_argument("--execution-mode", choices=["attended", "unattended_goal_loop"], default="attended")
    p.add_argument("--verification-owner", choices=["agent", "user", "shared", "external"], default="agent")
    p.add_argument("--interaction-mode", choices=["allowed", "forbidden"], default="allowed")
    p.add_argument("--exclude-action", action="append", choices=sorted(WORK_KINDS), default=[])
    p.add_argument("--core-deliverable", action="append", default=[])
    p.add_argument("--non-goal", action="append", default=[])
    p.add_argument("--time-budget-seconds", type=int, default=None)
    p.add_argument("--stop-condition", default="")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("add-step"); add_dir(p)
    p.add_argument("--id", required=True)
    p.add_argument("--title", default="")
    p.add_argument("--kind", choices=sorted(WORK_KINDS), default="core")
    requiredness = p.add_mutually_exclusive_group()
    requiredness.add_argument("--required", action="store_true")
    requiredness.add_argument("--optional", action="store_true")
    p.add_argument("--depends-on", action="append", default=[])
    p.add_argument("--intent-key", default="")
    p.add_argument("--requires-interaction", action="store_true")
    p.set_defaults(func=cmd_add_step)

    p = sub.add_parser("checkpoint"); add_dir(p)
    p.add_argument("--step", required=True)
    p.add_argument("--status", required=True)
    p.add_argument("--reason", default="")
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
    p.add_argument(
        "--status",
        required=True,
        choices=["pending", "pass", "user-verification-needed", "unverified"],
    )
    p.add_argument("--evidence", action="append", default=[])
    p.set_defaults(func=cmd_final_verify)

    p = sub.add_parser("close"); add_dir(p); p.set_defaults(func=cmd_close)
    p = sub.add_parser("next-action"); add_dir(p)
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.set_defaults(func=cmd_next_action)
    p = sub.add_parser("status"); add_dir(p); p.set_defaults(func=cmd_status)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
