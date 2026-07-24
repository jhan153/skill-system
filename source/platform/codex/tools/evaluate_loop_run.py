#!/usr/bin/env python3
"""Evaluate bounded verification LoopRun progress and continuation decisions."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from _validation import load_json_file, load_yaml_file, validate_schema
from loop_policy import (
    append_jsonl,
    canonical_hash,
    contained_path,
    contract_runtime_errors,
    condition_defer_reason,
    condition_dependencies,
    condition_intent_key,
    condition_map,
    control_value,
    elapsed_seconds,
    file_sha256,
    is_user_verification_condition,
    load_yaml,
    loop_lock,
    passed_required_count,
    required_condition_ids,
    state_fingerprint,
    structured_evidence_errors,
    success_conditions,
    utc_now,
    write_yaml,
)


ROOT = Path(__file__).resolve().parents[2]


def merge_iteration_result(contract: dict[str, Any], state: dict[str, Any], result: dict[str, Any]) -> None:
    old_results = condition_map(state)
    old_passed = passed_required_count(contract, state)
    old_failures = {
        condition_id: item.get("failure_fingerprint")
        for condition_id, item in old_results.items()
        if item.get("status") == "fail"
    }

    old_status = {condition_id: item.get("status") for condition_id, item in old_results.items()}

    merged = dict(old_results)
    for item in result.get("condition_results", []):
        if not isinstance(item, dict) or not isinstance(item.get("condition_id"), str):
            continue
        merged[item["condition_id"]] = {
            "condition_id": item["condition_id"],
            "status": item.get("status", "unverified"),
            "evidence_refs": item.get("evidence_refs", []) if isinstance(item.get("evidence_refs"), list) else [],
            "evidence": item.get("evidence", []) if isinstance(item.get("evidence"), list) else [],
            **({"failure_fingerprint": item["failure_fingerprint"]} if isinstance(item.get("failure_fingerprint"), str) else {}),
        }
    state["condition_results"] = list(merged.values())
    # Iteration advances strictly by one. _evaluate's monotonicity guard has
    # already verified result.iteration == state.iteration + 1 before this merge,
    # so we assign (not max()) — max() is what allowed skip/replay/rewind.
    state["iteration"] = int(result.get("iteration", int(state.get("iteration", 0)) + 1))
    state["budgets"]["iterations_used"] = max(int(state["budgets"].get("iterations_used", 0)), int(state["iteration"]))
    if isinstance(result.get("agent_run_id"), str) and result["agent_run_id"]:
        ref = {"iteration": int(result["iteration"]), "run_id": result["agent_run_id"]}
        if ref not in state["agent_run_refs"]:
            state["agent_run_refs"].append(ref)
    if isinstance(result.get("side_effects"), list):
        state["side_effect_journal"].extend(result["side_effects"])

    new_passed = passed_required_count(contract, state)
    new_failures = {
        condition_id: item.get("failure_fingerprint")
        for condition_id, item in condition_map(state).items()
        if item.get("status") == "fail"
    }
    new_status = {condition_id: item.get("status") for condition_id, item in condition_map(state).items()}
    regressed = any(
        old_status.get(condition_id) == "pass" and new_status.get(condition_id) == "fail"
        for condition_id in required_condition_ids(contract)
    )

    progress = state["progress"]
    if new_passed > old_passed:
        progress["no_progress_count"] = 0
        progress["repeated_failure_count"] = 0
    elif new_failures and new_failures == old_failures:
        progress["no_progress_count"] = int(progress.get("no_progress_count", 0)) + 1
        progress["repeated_failure_count"] = int(progress.get("repeated_failure_count", 0)) + 1
    elif new_failures != old_failures:
        progress["no_progress_count"] = 0
        progress["repeated_failure_count"] = 0
    else:
        progress["no_progress_count"] = int(progress.get("no_progress_count", 0)) + 1
    if regressed:
        progress["oscillation_count"] = int(progress.get("oscillation_count", 0)) + 1
    progress["required_passed"] = new_passed
    progress["required_total"] = len(required_condition_ids(contract))
    progress["state_hash"] = state_fingerprint(contract, state)


def failed_required_conditions(contract: dict[str, Any], state: dict[str, Any]) -> list[dict[str, Any]]:
    results = condition_map(state)
    failed: list[dict[str, Any]] = []
    for condition_id in required_condition_ids(contract):
        result = results.get(condition_id, {"condition_id": condition_id, "status": "unverified", "evidence_refs": []})
        if result.get("status") != "pass":
            failed.append(result)
    return failed


def remaining_work(
    contract: dict[str, Any],
    state: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Classify non-passing required conditions without globalizing a local block.

    Returns runnable work, locally deferred work, and dependency-waiting work.
    User-owned manual verification is a terminal handoff and is classified by
    ``decide`` before this helper is used.
    """
    results = condition_map(state)
    passed = {
        condition_id
        for condition_id, result in results.items()
        if result.get("status") == "pass"
    }
    runnable: list[dict[str, Any]] = []
    deferred: list[dict[str, Any]] = []
    waiting: list[dict[str, Any]] = []
    for condition_id in required_condition_ids(contract):
        result = results.get(
            condition_id,
            {"condition_id": condition_id, "status": "unverified", "evidence_refs": []},
        )
        if result.get("status") == "pass" or is_user_verification_condition(contract, condition_id):
            continue
        reason = condition_defer_reason(contract, condition_id)
        status = result.get("status")
        if reason is None and status == "blocked":
            reason = "condition is locally blocked"
        elif reason is None and status == "deferred":
            reason = "condition was locally deferred"
        if reason is not None:
            deferred.append(
                {
                    "condition_id": condition_id,
                    "intent_key": condition_intent_key(contract, condition_id),
                    "reason": reason,
                }
            )
            continue
        dependencies = condition_dependencies(contract, condition_id)
        if all(dependency in passed for dependency in dependencies):
            runnable.append(result)
        else:
            waiting.append(result)
    for condition in success_conditions(contract):
        if condition.get("required", True) is not False:
            continue
        condition_id = condition["id"]
        result = results.get(
            condition_id,
            {"condition_id": condition_id, "status": "unverified", "evidence_refs": []},
        )
        if result.get("status") == "pass":
            continue
        reason = condition_defer_reason(contract, condition_id)
        if reason is None and result.get("status") == "blocked":
            reason = "optional condition is locally blocked"
        elif reason is None and result.get("status") == "deferred":
            reason = "optional condition was locally deferred"
        if reason is not None:
            deferred.append(
                {
                    "condition_id": condition_id,
                    "intent_key": condition_intent_key(contract, condition_id),
                    "reason": reason,
                }
            )
    return runnable, deferred, waiting


def record_deferred_actions(state: dict[str, Any], deferred: list[dict[str, Any]]) -> None:
    state["deferred_actions"] = deferred


def continuation_prompt(action: str, reason_code: str, contract: dict[str, Any], state: dict[str, Any], target: str | None) -> str:
    max_iterations = control_value(contract, "max_iterations", 1)
    prefix = f"Loop iteration {int(state.get('iteration', 0)) + 1}/{max_iterations}."
    work_contract_active = bool(contract.get("work_contract"))
    if action == "recover":
        if reason_code == "oscillation_limit_reached":
            target_text = f" Regressed condition: {target}." if target else ""
            return (
                f"{prefix} Oscillation detected: a previously passing required condition regressed to fail.{target_text} "
                "Switch to workflow-recovery: find what reverted the condition and fix that root cause; "
                "do not re-break conditions that were already passing or weaken success conditions. "
                "Record only evidence already required by the accepted contract."
            )
        return (
            f"{prefix} Repeated verifier failure reached the recovery threshold. "
            "Switch to workflow-recovery: use one hypothesis, one diagnostic, and one fix. "
            "Do not weaken success conditions or expand write scope. "
            "Record only evidence already required by the accepted contract."
        )
    target_text = f" Target condition: {target}." if target else ""
    if work_contract_active:
        return (
            f"{prefix}{target_text} Continue the smallest in-contract action that advances this required condition. "
            "Keep locally deferred purposes deferred, reevaluate independent required work after each local block, "
            "and do not create optional validation or management work. "
            "Record only evidence already required by the accepted contract."
        )
    return (
        f"{prefix}{target_text} Continue only with the smallest action that can change verifier evidence. "
        "Do not weaken success conditions. Record verifier evidence before finalizing again."
    )


# Default ordering when (or where) the contract's termination.precedence is silent.
# Reserved states (unsafe/fatal/approval_required/stalled) have no auto-emit path
# yet; they stay in the vocabulary so a future verifier signal resolves correctly.
DEFAULT_PRECEDENCE = [
    "unsafe", "fatal", "blocked", "success", "user_verification_needed",
    "approval_required", "stalled", "budget_exhausted", "recover", "continue",
]


def termination_precedence(contract: dict[str, Any]) -> list[str]:
    termination = contract.get("termination") if isinstance(contract.get("termination"), dict) else {}
    raw = termination.get("precedence")
    return [item for item in raw if isinstance(item, str)] if isinstance(raw, list) else []


def decide(
    contract: dict[str, Any],
    state: dict[str, Any],
    evidence_errors: list[str] | None = None,
) -> dict[str, Any]:
    failed = failed_required_conditions(contract, state)
    progress = state.get("progress", {}) if isinstance(state.get("progress"), dict) else {}
    budgets = state.get("budgets", {}) if isinstance(state.get("budgets"), dict) else {}

    # Hard governance guards win regardless of contract precedence: malformed,
    # mismatched, missing, or stale verifier receipts can never be overridden.
    if evidence_errors:
        target_condition = evidence_errors[0].split(":", 1)[0]
        return {"action": "blocked", "reason_code": "invalid_verifier_evidence", "target_condition": target_condition}

    user_pending = [
        item
        for item in failed
        if is_user_verification_condition(contract, str(item.get("condition_id", "")))
    ]
    non_user_failed = [
        item
        for item in failed
        if not is_user_verification_condition(contract, str(item.get("condition_id", "")))
    ]
    if user_pending and not non_user_failed:
        record_deferred_actions(state, [])
        return {
            "action": "user_verification_needed",
            "reason_code": "user_owned_verification_pending",
            "target_condition": user_pending[0].get("condition_id"),
        }

    runnable, deferred, waiting = remaining_work(contract, state)
    record_deferred_actions(state, deferred)
    target = runnable[0].get("condition_id") if runnable else None

    # A local block is terminal only after the remaining dependency graph has no
    # independent required condition that can still run.
    if failed and not runnable:
        blocked_target = (
            deferred[0]["condition_id"]
            if deferred
            else waiting[0].get("condition_id")
            if waiting
            else failed[0].get("condition_id")
        )
        return {
            "action": "blocked",
            "reason_code": "no_required_runnable_work",
            "target_condition": blocked_target,
        }

    # Terminal (stop) candidates are resolved by the contract's termination.precedence.
    # These are mutually bounded: success only when nothing failed; budget only when
    # a ceiling is hit. Precedence orders them and any future reserved terminal states.
    terminal: dict[str, dict[str, Any]] = {}
    if not failed:
        terminal["success"] = {"reason_code": "all_required_conditions_passed", "target_condition": None}
    else:
        if int(budgets.get("iterations_used", 0)) >= control_value(contract, "max_iterations", 1):
            terminal["budget_exhausted"] = {"reason_code": "max_iterations_exhausted", "target_condition": target}
        max_wall = control_value(contract, "max_wall_time_seconds", 0)
        if max_wall and int(budgets.get("wall_time_seconds", 0)) >= max_wall:
            terminal.setdefault("budget_exhausted", {"reason_code": "wall_time_exhausted", "target_condition": target})
    if terminal:
        contract_order = termination_precedence(contract)
        order = contract_order + [action for action in DEFAULT_PRECEDENCE if action not in contract_order]
        resolved = next((action for action in order if action in terminal), None)
        if resolved is not None:
            return {"action": resolved, **terminal[resolved]}

    # Not terminating: choose the continuation strategy from progress thresholds.
    # recover-vs-continue is a strategy decision, not a termination ordering.
    target_status = runnable[0].get("status") if runnable else None
    if deferred and target_status == "unverified":
        return {
            "action": "continue",
            "reason_code": "local_block_deferred_independent_work_remaining",
            "target_condition": target,
        }
    if int(progress.get("repeated_failure_count", 0)) >= control_value(contract, "same_failure_limit", 1):
        return {"action": "recover", "reason_code": "same_failure_limit_reached", "target_condition": target}
    if int(progress.get("oscillation_count", 0)) >= control_value(contract, "oscillation_limit", 2):
        return {"action": "recover", "reason_code": "oscillation_limit_reached", "target_condition": target}
    if int(progress.get("no_progress_count", 0)) >= control_value(contract, "no_progress_limit", 1):
        return {"action": "recover", "reason_code": "no_progress_limit_reached", "target_condition": target}
    return {"action": "continue", "reason_code": "required_condition_not_passed", "target_condition": target}


def read_recorded_decision(loop_dir: Path, iteration: int) -> dict[str, Any]:
    """Return the decision recorded when an iteration was first applied (for replay)."""
    path = loop_dir / "iterations" / f"{iteration:04d}.decision.yaml"
    if path.is_file():
        data = load_yaml(path)
        if isinstance(data, dict):
            return data
    return {"action": "noop", "reason_code": "idempotent_replay", "target_condition": None, "continuation_prompt": None}


def load_state_and_contract(loop_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    state = load_yaml(loop_dir / "state.yaml")
    if not isinstance(state, dict):
        raise ValueError("state.yaml must be a mapping")
    contract_path = contained_path(loop_dir, str(state.get("contract_ref", "contract.yaml")))
    if contract_path is None or not contract_path.is_file():
        raise ValueError("contract_ref must resolve to a file contained by the LoopRun directory")
    contract = load_yaml(contract_path)
    if not isinstance(contract, dict):
        raise ValueError("contract must be a mapping")
    if state.get("contract_hash") != file_sha256(contract_path):
        raise ValueError("state contract_hash does not match contract file")
    return state, contract


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("loop_run_dir", type=Path)
    parser.add_argument("--iteration-result", type=Path)
    parser.add_argument("--record-stop-continuation", action="store_true")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()
    with loop_lock(args.loop_run_dir):
        return _evaluate(args)


def _evaluate(args: argparse.Namespace) -> int:
    try:
        state, contract = load_state_and_contract(args.loop_run_dir)
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: {exc}")
        return 2

    preflight_errors: list[str] = []
    state_schema = load_json_file(ROOT / ".codex" / "schemas" / "loop" / "loop-run.schema.json")
    contract_schema = load_json_file(ROOT / ".codex" / "schemas" / "loop" / "loop-contract.schema.json")
    preflight_errors.extend(f"state: {error}" for error in validate_schema(state, state_schema))
    preflight_errors.extend(f"contract: {error}" for error in validate_schema(contract, contract_schema))
    preflight_errors.extend(f"contract: {error}" for error in contract_runtime_errors(contract))
    if state.get("schema_version") != 2:
        preflight_errors.append("state: schema_version 1 is legacy read-only and cannot be evaluated")
    checkpoint = args.loop_run_dir / "checkpoints" / f"{int(state.get('iteration', 0)):04d}.yaml"
    if not checkpoint.is_file():
        preflight_errors.append("state: current checkpoint is missing")
    else:
        checkpoint_state = load_yaml(checkpoint)
        if not isinstance(checkpoint_state, dict) or canonical_hash(checkpoint_state) != canonical_hash(state):
            preflight_errors.append("state: current checkpoint does not exactly match state.yaml")
    if state.get("progress", {}).get("state_hash") != state_fingerprint(contract, state):
        preflight_errors.append("state: progress.state_hash does not match current condition state")
    if preflight_errors:
        print("FAIL")
        for error in preflight_errors:
            print(f"- preflight: {error}")
        return 3
    integrity = subprocess.run(
        [sys.executable, str(Path(__file__).with_name("validate_loop_run.py")), str(args.loop_run_dir)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if integrity.returncode != 0:
        print("FAIL: LoopRun integrity validation failed before evaluation")
        print(integrity.stdout.rstrip())
        return 3
    persisted_evidence_errors = structured_evidence_errors(
        contract,
        state,
        state.get("condition_results", []),
        args.loop_run_dir,
    )
    if persisted_evidence_errors:
        print("FAIL")
        for error in persisted_evidence_errors:
            print(f"- persisted_evidence: {error}")
        return 3

    recorded_iteration: int | None = None
    if args.iteration_result:
        schema = load_json_file(ROOT / ".codex" / "schemas" / "loop" / "iteration-result.schema.json")
        result = load_yaml_file(args.iteration_result)
        if not isinstance(result, dict):
            print("FAIL: iteration result must be a mapping")
            return 2
        errors = validate_schema(result, schema)
        if result.get("schema_version") != 2:
            errors.append("iteration result schema_version 1 is legacy read-only")
        if result.get("schema_version") != state.get("schema_version"):
            errors.append("iteration result schema_version does not match state")
        if result.get("loop_run_id") != state.get("loop_run_id"):
            errors.append("iteration result loop_run_id does not match state")
        if errors:
            print("FAIL")
            for error in errors:
                print(f"- iteration_result: {error}")
            return 1

        body = {key: value for key, value in result.items() if key != "payload_hash"}
        digest = canonical_hash(body)
        rid = result.get("iteration_result_id") or digest
        applied = state.setdefault("applied_results", {})

        # Idempotency vs conflict: a result id already applied with the SAME payload
        # is an idempotent replay (return the prior decision, no re-mutation). The
        # same id with a DIFFERENT payload is a conflict, not a replay — reject it.
        if rid in applied:
            entry = applied[rid]
            prior_iteration = entry.get("iteration") if isinstance(entry, dict) else entry
            prior_hash = entry.get("payload_hash") if isinstance(entry, dict) else None
            if prior_hash is not None and prior_hash != digest:
                print(f"FAIL: iteration_result_id {rid!r} reused with a different payload (conflict, not replay)")
                return 3
            prior = read_recorded_decision(args.loop_run_dir, int(prior_iteration))
            report = {
                "status": "PASS",
                "loop_run_id": state["loop_run_id"],
                "result_label": state.get("result_label", "pending"),
                "decision": prior,
                "replay": True,
            }
            if args.format == "json":
                print(json.dumps(report, sort_keys=True))
            else:
                print("PASS")
                print(f"- action: {prior.get('action')}")
                print(f"- reason_code: {prior.get('reason_code')}")
                print("- replay: true")
            return 0

        evidence_errors = structured_evidence_errors(
            contract,
            state,
            result.get("condition_results", []),
            args.loop_run_dir,
        )
        if evidence_errors:
            print("FAIL")
            for error in evidence_errors:
                print(f"- iteration_result: {error}")
            return 1

        # Terminal immutability: terminal LoopRuns reject new results.
        if state.get("status") != "active":
            print(f"FAIL: loop is terminal (status={state.get('status')}); use resume_loop_run.py to reopen")
            return 3

        # Monotonic sequencing: only iteration N+1 is accepted (no skip/rewind/replay-as-new).
        expected = int(state.get("iteration", 0)) + 1
        if int(result.get("iteration", 0)) != expected:
            print(f"FAIL: iteration sequence conflict (expected {expected}, received {result.get('iteration')})")
            return 3

        # Optional integrity check binding the payload to its declared hash.
        declared = result.get("payload_hash")
        if isinstance(declared, str) and declared and declared != digest:
            print("FAIL: payload_hash does not match iteration result body")
            return 3

        # Audit: persist the input that drives this transition before mutating state.
        write_yaml(args.loop_run_dir / "iterations" / f"{expected:04d}.input.yaml", result)
        merge_iteration_result(contract, state, result)
        applied[rid] = {"iteration": expected, "payload_hash": digest}
        recorded_iteration = expected

    # Wall-time is a real bound: measure elapsed since started_at so decide() can
    # enforce control.max_wall_time_seconds.
    state.setdefault("budgets", {})["wall_time_seconds"] = elapsed_seconds(state.get("started_at", ""), utc_now())

    state_evidence_errors = structured_evidence_errors(
        contract,
        state,
        state.get("condition_results", []),
        args.loop_run_dir,
    )
    decision = decide(contract, state, state_evidence_errors)
    if decision["action"] in {"continue", "recover"}:
        budgets = state["budgets"]
        if int(budgets.get("stop_continuations_used", 0)) >= int(budgets.get("max_stop_continuations", 0)):
            decision = {
                "action": "budget_exhausted",
                "reason_code": "max_stop_continuations_exhausted",
                "target_condition": decision.get("target_condition"),
            }
        elif args.record_stop_continuation:
            budgets["stop_continuations_used"] = int(budgets.get("stop_continuations_used", 0)) + 1

    if decision["action"] in {"continue", "recover"}:
        decision["continuation_prompt"] = continuation_prompt(
            str(decision["action"]),
            str(decision.get("reason_code", "")),
            contract,
            state,
            decision.get("target_condition") if isinstance(decision.get("target_condition"), str) else None,
        )
        state["status"] = "active"
        state["result_label"] = "pending"
    elif decision["action"] == "success":
        state["status"] = "success"
        state["result_label"] = "agent-verified"
        decision["continuation_prompt"] = None
    elif decision["action"] == "user_verification_needed":
        state["status"] = "user_verification_needed"
        state["result_label"] = "user-verification-needed"
        decision["continuation_prompt"] = None
    elif decision["action"] == "budget_exhausted":
        state["status"] = "budget_exhausted"
        state["result_label"] = "unverified"
        decision["continuation_prompt"] = None
    elif decision["action"] == "blocked":
        state["status"] = "blocked"
        state["result_label"] = "blocked"
        decision["continuation_prompt"] = None
    else:
        state["status"] = str(decision["action"])
        state["result_label"] = "blocked" if decision["action"] in {"unsafe", "fatal"} else "unverified"
        decision["continuation_prompt"] = None

    now = utc_now()
    state["updated_at"] = now
    state["progress"]["required_passed"] = passed_required_count(contract, state)
    state["progress"]["required_total"] = len(required_condition_ids(contract))
    state["progress"]["state_hash"] = state_fingerprint(contract, state)
    state["last_decision"] = decision
    if recorded_iteration is not None:
        write_yaml(args.loop_run_dir / "iterations" / f"{recorded_iteration:04d}.decision.yaml", decision)
    write_yaml(args.loop_run_dir / "state.yaml", state)
    write_yaml(args.loop_run_dir / "checkpoints" / f"{int(state.get('iteration', 0)):04d}.yaml", state)
    if recorded_iteration is not None:
        write_yaml(
            args.loop_run_dir / "iterations" / f"{recorded_iteration:04d}.checkpoint.yaml",
            state,
        )
    append_jsonl(
        args.loop_run_dir / "loop-events.jsonl",
        {
            "recorded_at": now,
            "event": "loop_evaluated",
            "loop_run_id": state["loop_run_id"],
            "iteration": state["iteration"],
            "decision": decision,
            "state_hash": state["progress"]["state_hash"],
        },
    )
    report = {
        "status": "PASS",
        "loop_run_id": state["loop_run_id"],
        "result_label": state["result_label"],
        "decision": decision,
    }
    if args.format == "json":
        print(json.dumps(report, sort_keys=True))
    else:
        print("PASS")
        print(f"- action: {decision['action']}")
        print(f"- reason_code: {decision['reason_code']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
