#!/usr/bin/env python3
"""Evaluate bounded verification LoopRun progress and continuation decisions."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from _validation import load_json_file, load_yaml_file, validate_schema
from loop_policy import (
    append_jsonl,
    canonical_hash,
    condition_map,
    control_value,
    elapsed_seconds,
    file_sha256,
    load_yaml,
    loop_lock,
    passed_required_count,
    required_condition_ids,
    state_fingerprint,
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


def continuation_prompt(action: str, reason_code: str, contract: dict[str, Any], state: dict[str, Any], target: str | None) -> str:
    max_iterations = control_value(contract, "max_iterations", 1)
    prefix = f"Loop iteration {int(state.get('iteration', 0)) + 1}/{max_iterations}."
    if action == "recover":
        if reason_code == "oscillation_limit_reached":
            target_text = f" Regressed condition: {target}." if target else ""
            return (
                f"{prefix} Oscillation detected: a previously passing required condition regressed to fail.{target_text} "
                "Switch to workflow-recovery: find what reverted the condition and fix that root cause; "
                "do not re-break conditions that were already passing or weaken tests. "
                "Record new verifier evidence before finalizing again."
            )
        return (
            f"{prefix} Repeated verifier failure reached the recovery threshold. "
            "Switch to workflow-recovery: use one hypothesis, one diagnostic, and one fix. "
            "Do not weaken tests or expand write scope. Record new verifier evidence before finalizing again."
        )
    target_text = f" Target condition: {target}." if target else ""
    return (
        f"{prefix}{target_text} Continue only with the smallest action that can change verifier evidence. "
        "Do not weaken success conditions. Record verifier evidence before finalizing again."
    )


def evidenceless_passes(contract: dict[str, Any], state: dict[str, Any]) -> list[str]:
    """Required conditions reported as pass but lacking any verifier evidence.

    A pass with no evidence is a reward-hacking / premature-completion signal: it
    must not be counted toward loop success.
    """
    results = condition_map(state)
    violations: list[str] = []
    for condition_id in required_condition_ids(contract):
        result = results.get(condition_id, {})
        if result.get("status") == "pass" and not result.get("evidence_refs"):
            violations.append(condition_id)
    return violations


# Default ordering when (or where) the contract's termination.precedence is silent.
# Reserved states (unsafe/fatal/approval_required/stalled) have no auto-emit path
# yet; they stay in the vocabulary so a future verifier signal resolves correctly.
DEFAULT_PRECEDENCE = [
    "unsafe", "fatal", "blocked", "success", "approval_required", "stalled", "budget_exhausted", "recover", "continue",
]


def termination_precedence(contract: dict[str, Any]) -> list[str]:
    termination = contract.get("termination") if isinstance(contract.get("termination"), dict) else {}
    raw = termination.get("precedence")
    return [item for item in raw if isinstance(item, str)] if isinstance(raw, list) else []


def decide(contract: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    failed = failed_required_conditions(contract, state)
    progress = state.get("progress", {}) if isinstance(state.get("progress"), dict) else {}
    budgets = state.get("budgets", {}) if isinstance(state.get("budgets"), dict) else {}
    target = failed[0]["condition_id"] if failed else None

    # Hard governance guards win regardless of contract precedence: an evidence-less
    # required pass, or an explicitly blocked condition, is never overridden.
    evidence_violations = evidenceless_passes(contract, state)
    if evidence_violations:
        return {"action": "blocked", "reason_code": "pass_without_evidence", "target_condition": evidence_violations[0]}
    if any(item.get("status") == "blocked" for item in failed):
        return {"action": "blocked", "reason_code": "required_condition_blocked", "target_condition": target}

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
    contract_path = loop_dir / str(state.get("contract_ref", "contract.yaml"))
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

    recorded_iteration: int | None = None
    if args.iteration_result:
        schema = load_json_file(ROOT / ".codex" / "schemas" / "loop" / "iteration-result.schema.json")
        result = load_yaml_file(args.iteration_result)
        if not isinstance(result, dict):
            print("FAIL: iteration result must be a mapping")
            return 2
        errors = validate_schema(result, schema)
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
            report = {"status": "PASS", "loop_run_id": state["loop_run_id"], "decision": prior, "replay": True}
            if args.format == "json":
                print(json.dumps(report, sort_keys=True))
            else:
                print("PASS")
                print(f"- action: {prior.get('action')}")
                print(f"- reason_code: {prior.get('reason_code')}")
                print("- replay: true")
            return 0

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

    decision = decide(contract, state)
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
    elif decision["action"] == "success":
        state["status"] = "success"
        decision["continuation_prompt"] = None
    elif decision["action"] == "budget_exhausted":
        state["status"] = "budget_exhausted"
        decision["continuation_prompt"] = None
    elif decision["action"] == "blocked":
        state["status"] = "blocked"
        decision["continuation_prompt"] = None
    else:
        state["status"] = str(decision["action"])
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
    report = {"status": "PASS", "loop_run_id": state["loop_run_id"], "decision": decision}
    if args.format == "json":
        print(json.dumps(report, sort_keys=True))
    else:
        print("PASS")
        print(f"- action: {decision['action']}")
        print(f"- reason_code: {decision['reason_code']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
