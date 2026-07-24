#!/usr/bin/env python3
"""Shared helpers for bounded verification loop state."""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import subprocess
from collections.abc import Iterator
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import yaml

try:
    import fcntl
except ImportError:  # pragma: no cover - non-POSIX fallback.
    fcntl = None  # type: ignore[assignment]


LOOP_STATUSES = {
    "active", "success", "user_verification_needed", "blocked",
    "budget_exhausted", "unsafe", "fatal", "stalled",
}
CONDITION_STATUSES = {"pass", "fail", "unverified", "blocked", "deferred"}
DECISION_ACTIONS = {
    "success", "user_verification_needed", "continue", "recover", "pause",
    "blocked", "budget_exhausted", "unsafe", "fatal",
}
VERIFIER_RECEIPT_KINDS = {
    "command_exit": "command_exit",
    "artifact_exists": "artifact_exists",
    "manual_check": "manual_acceptance",
    "diff_scope": "diff_scope",
}
EVIDENCE_FUTURE_TOLERANCE_SECONDS = 300


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def elapsed_seconds(started_at: str, now: str) -> int:
    """Whole seconds between two ISO-8601 timestamps (0 on parse failure)."""
    try:
        start = datetime.fromisoformat(str(started_at).replace("Z", "+00:00"))
        end = datetime.fromisoformat(str(now).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return 0
    return max(0, int((end - start).total_seconds()))


def canonical_hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_id(value: str, fallback: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in "._-" else "-" for ch in value).strip(".-")
    return cleaned[:96] or fallback


def contained_path(base: Path, ref: str) -> Path | None:
    """Resolve a relative ref without allowing absolute paths or directory escape."""
    relative = Path(ref)
    if relative.is_absolute():
        return None
    root = base.resolve()
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate


def active_loops_dir() -> Path:
    """Host-stable directory holding session->LoopRun activation pointers.

    Lives under CODEX_HOME (default ~/.codex) so the activation tool (run from a
    project cwd) and the Stop hook (whose ROOT differs) agree on one location.
    The Stop hook mirrors this resolution inline to avoid importing yaml.
    """
    base = os.environ.get("CODEX_HOME") or str(Path.home() / ".codex")
    return Path(base).expanduser() / "harness" / "active-loops"


def session_pointer_path(session_id: str) -> Path:
    return active_loops_dir() / f"{safe_id(str(session_id), 'unknown-session')}.json"


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def write_yaml(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value, sort_keys=False, allow_unicode=False), encoding="utf-8")


def git_revision(root: Path) -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=5,
        )
    except Exception:  # noqa: BLE001 - revision is metadata only.
        return "unversioned"
    revision = completed.stdout.strip()
    return revision if completed.returncode == 0 and revision else "unversioned"


def workspace_id(root: Path) -> str:
    return hashlib.sha256(str(root.resolve()).encode("utf-8", errors="replace")).hexdigest()[:16]


def success_conditions(contract: dict[str, Any]) -> list[dict[str, Any]]:
    goal = contract.get("goal") if isinstance(contract.get("goal"), dict) else {}
    raw_conditions = goal.get("success_conditions", [])
    return [item for item in raw_conditions if isinstance(item, dict) and isinstance(item.get("id"), str)]


def success_condition_map(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {condition["id"]: condition for condition in success_conditions(contract)}


def contract_runtime_errors(contract: dict[str, Any]) -> list[str]:
    """Return fail-closed runtime-contract errors before any state mutation."""
    errors: list[str] = []
    version = contract.get("schema_version")
    if version not in {2, 3}:
        errors.append("schema_version 1 is legacy read-only; create or migrate to a v2/v3 contract")
    conditions = success_conditions(contract)
    ids = [condition["id"] for condition in conditions]
    duplicates = sorted({condition_id for condition_id in ids if ids.count(condition_id) > 1})
    if duplicates:
        errors.append(f"duplicate success condition ids: {', '.join(duplicates)}")
    if not any(condition.get("required", True) is not False for condition in conditions):
        errors.append("at least one success condition must be required")
    goal = contract.get("goal") if isinstance(contract.get("goal"), dict) else {}
    if goal.get("invariants"):
        errors.append("goal.invariants are not runtime-bound in v2; promote them to required success conditions")
    for condition in conditions:
        verifier = condition.get("verifier") if isinstance(condition.get("verifier"), dict) else {}
        owner = verifier.get("owner")
        if not isinstance(owner, str) or not owner.strip():
            errors.append(f"{condition['id']}: verifier.owner is required for v2 runtime use")
        if verifier.get("type") == "manual_check" and not verifier.get("acceptance_scope"):
            errors.append(f"{condition['id']}: manual_check requires acceptance_scope")
        if verifier.get("type") == "diff_scope" and not verifier.get("path"):
            errors.append(f"{condition['id']}: diff_scope requires path")
    if version == 3:
        work_contract = contract.get("work_contract")
        if not isinstance(work_contract, dict):
            errors.append("schema_version 3 requires work_contract")
            return errors
        wc_scope = work_contract.get("scope") if isinstance(work_contract.get("scope"), dict) else {}
        excluded = {
            item
            for item in wc_scope.get("excluded_action_classes", [])
            if isinstance(item, str)
        }
        allowed = {
            item
            for item in wc_scope.get("allowed_action_classes", [])
            if isinstance(item, str)
        }
        overlap = sorted(allowed & excluded)
        if overlap:
            errors.append(
                "work contract action classes cannot be both allowed and excluded: "
                + ", ".join(overlap)
            )
        verification = (
            work_contract.get("verification")
            if isinstance(work_contract.get("verification"), dict)
            else {}
        )
        interaction = (
            work_contract.get("interaction")
            if isinstance(work_contract.get("interaction"), dict)
            else {}
        )
        execution = (
            work_contract.get("execution")
            if isinstance(work_contract.get("execution"), dict)
            else {}
        )
        if verification.get("owner") == "user" and not any(
            isinstance(condition.get("verifier"), dict)
            and condition["verifier"].get("type") == "manual_check"
            and condition.get("required", True) is not False
            for condition in conditions
        ):
            errors.append("user-owned verification requires one required manual_check handoff condition")
        if verification.get("owner") == "user":
            missing_exclusions = sorted(
                {"agent_validation", "test_authoring", "validation_artifact"} - excluded
            )
            if missing_exclusions:
                errors.append(
                    "user-owned verification must exclude agent verification work: "
                    + ", ".join(missing_exclusions)
                )
        if (
            verification.get("owner") == "user"
            and verification.get("handoff_on_unavailable") != "user-verification-needed"
        ):
            errors.append(
                "user-owned verification requires handoff_on_unavailable=user-verification-needed"
            )
        termination = (
            contract.get("termination")
            if isinstance(contract.get("termination"), dict)
            else {}
        )
        precedence = termination.get("precedence", [])
        if (
            verification.get("owner") == "user"
            and (
                not isinstance(precedence, list)
                or "user_verification_needed" not in precedence
            )
        ):
            errors.append(
                "user-owned verification requires user_verification_needed in termination.precedence"
            )
        if execution.get("mode") == "unattended_goal_loop" and interaction.get("mode") == "forbidden":
            if interaction.get("approval_behavior") != "defer" or interaction.get("question_behavior") != "defer":
                errors.append("unattended no-interaction work must defer approvals and questions")
        condition_ids = set(ids)
        required_ids = {
            condition["id"]
            for condition in conditions
            if condition.get("required", True) is not False
        }
        dependency_graph: dict[str, list[str]] = {}
        seen_intents: set[str] = set()
        for condition in conditions:
            condition_id = condition["id"]
            kind = condition.get("work_kind")
            intent_key = condition.get("intent_key")
            if not isinstance(kind, str):
                errors.append(f"{condition_id}: work_kind is required for v3 runtime use")
            if not isinstance(intent_key, str) or not intent_key.strip():
                errors.append(f"{condition_id}: intent_key is required for v3 runtime use")
            elif intent_key in seen_intents:
                errors.append(f"{condition_id}: duplicate semantic intent_key {intent_key!r}")
            else:
                seen_intents.add(intent_key)
            if kind in excluded and condition.get("required", True) is not False:
                errors.append(f"{condition_id}: excluded work_kind {kind!r} cannot be a required condition")
            dependencies = condition.get("depends_on", [])
            if not isinstance(dependencies, list):
                continue
            dependency_graph[condition_id] = [
                dependency
                for dependency in dependencies
                if isinstance(dependency, str) and dependency in condition_ids
            ]
            for dependency in dependencies:
                if dependency == condition_id:
                    errors.append(f"{condition_id}: condition cannot depend on itself")
                elif dependency not in condition_ids:
                    errors.append(f"{condition_id}: unknown dependency {dependency!r}")
                elif condition_id in required_ids and dependency not in required_ids:
                    errors.append(
                        f"{condition_id}: required condition cannot depend on optional condition {dependency!r}"
                    )
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(condition_id: str, path: list[str]) -> None:
            if condition_id in visited:
                return
            if condition_id in visiting:
                start = path.index(condition_id) if condition_id in path else 0
                cycle = path[start:] + [condition_id]
                errors.append(f"dependency cycle: {' -> '.join(cycle)}")
                return
            visiting.add(condition_id)
            for dependency in dependency_graph.get(condition_id, []):
                visit(dependency, path + [condition_id])
            visiting.remove(condition_id)
            visited.add(condition_id)

        for condition_id in ids:
            visit(condition_id, [])
    return errors


def work_contract(contract: dict[str, Any]) -> dict[str, Any]:
    value = contract.get("work_contract")
    return value if isinstance(value, dict) else {}


def work_contract_value(contract: dict[str, Any], section: str, key: str, default: Any = None) -> Any:
    value = work_contract(contract).get(section)
    if not isinstance(value, dict):
        return default
    return value.get(key, default)


def success_condition(contract: dict[str, Any], condition_id: str) -> dict[str, Any]:
    return success_condition_map(contract).get(condition_id, {})


def is_user_verification_condition(contract: dict[str, Any], condition_id: str) -> bool:
    if work_contract_value(contract, "verification", "owner") != "user":
        return False
    verifier = success_condition(contract, condition_id).get("verifier")
    return isinstance(verifier, dict) and verifier.get("type") == "manual_check"


def condition_dependencies(contract: dict[str, Any], condition_id: str) -> list[str]:
    raw = success_condition(contract, condition_id).get("depends_on", [])
    return [item for item in raw if isinstance(item, str)] if isinstance(raw, list) else []


def condition_intent_key(contract: dict[str, Any], condition_id: str) -> str:
    condition = success_condition(contract, condition_id)
    value = condition.get("intent_key")
    return value if isinstance(value, str) and value else condition_id


def contract_excluded_action_classes(contract: dict[str, Any]) -> set[str]:
    raw = work_contract_value(contract, "scope", "excluded_action_classes", [])
    return {item for item in raw if isinstance(item, str)} if isinstance(raw, list) else set()


def condition_defer_reason(contract: dict[str, Any], condition_id: str) -> str | None:
    condition = success_condition(contract, condition_id)
    kind = condition.get("work_kind")
    if isinstance(kind, str) and kind in contract_excluded_action_classes(contract):
        return f"work_kind {kind} is excluded by the user work contract"
    unattended = work_contract_value(contract, "execution", "mode") == "unattended_goal_loop"
    no_interaction = work_contract_value(contract, "interaction", "mode") == "forbidden"
    if unattended and no_interaction and condition.get("interaction_required") is True:
        return "unattended Goal/Loop contract forbids required human interaction"
    return None


def _receipt_artifact_path(
    loop_dir: Path,
    state: dict[str, Any],
    receipt: dict[str, Any],
) -> tuple[Path | None, str | None]:
    ref = receipt.get("artifact_ref")
    scope = receipt.get("artifact_scope")
    if not isinstance(ref, str) or not ref:
        return None, "artifact_ref must be a non-empty relative path"
    relative = Path(ref)
    if relative.is_absolute():
        return None, "artifact_ref must be relative"
    if scope == "loop_run":
        base = loop_dir.resolve()
    elif scope == "workspace":
        workspace = state.get("workspace") if isinstance(state.get("workspace"), dict) else {}
        root = workspace.get("root")
        if not isinstance(root, str) or not root:
            return None, "workspace.root is unavailable for workspace evidence"
        base = Path(root).expanduser().resolve()
    else:
        return None, "artifact_scope must be loop_run or workspace"
    candidate = (base / relative).resolve()
    try:
        candidate.relative_to(base)
    except ValueError:
        return None, "artifact_ref escapes its declared scope"
    return candidate, None


def _parse_aware_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed


def _manual_acceptance_payload_errors(
    artifact_path: Path,
    contract: dict[str, Any],
    state: dict[str, Any],
    condition_id: str,
    receipt: dict[str, Any],
) -> list[str]:
    """Validate a durable manual event under procedural, not cryptographic, trust.

    The event binds the receipt to one actual user-input decision. File integrity
    and field consistency are checked, but the host does not cryptographically
    authenticate the actor; without this event manual verification is unavailable.
    """
    try:
        event = load_yaml(artifact_path)
    except Exception as exc:  # noqa: BLE001 - malformed evidence is a validation error.
        return [f"user acceptance event cannot be read: {exc}"]
    if not isinstance(event, dict):
        return ["user acceptance event must be a mapping"]
    expected = {
        "schema_version": 1,
        "event_type": "user_acceptance",
        "contract_id": contract.get("contract_id"),
        "loop_run_id": state.get("loop_run_id"),
        "condition_id": condition_id,
        "actor": receipt.get("actor"),
        "scope": receipt.get("accepted_scope"),
        "accepted": True,
        "observed_at": receipt.get("observed_at"),
        "source": "user_input",
    }
    errors: list[str] = []
    for key, value in expected.items():
        if event.get(key) != value:
            errors.append(f"user acceptance event {key} must equal {value!r}")
    unexpected = sorted(set(event) - set(expected))
    if unexpected:
        errors.append(f"user acceptance event has unexpected fields: {', '.join(unexpected)}")
    return errors


def structured_evidence_errors(
    contract: dict[str, Any],
    state: dict[str, Any],
    results: Any,
    loop_dir: Path,
) -> list[str]:
    """Validate durable verifier receipts against their contract and files.

    ``evidence_refs`` remains compatibility metadata. It never makes a condition
    pass; only a matching, outcome=pass structured receipt can do that.
    """
    conditions = success_condition_map(contract)
    if not isinstance(results, list):
        return ["condition_results must be an array"]
    errors: list[str] = []
    seen: set[str] = set()
    for index, result in enumerate(results):
        if not isinstance(result, dict):
            errors.append(f"condition_results[{index}] must be a mapping")
            continue
        condition_id = result.get("condition_id")
        prefix = str(condition_id) if isinstance(condition_id, str) else f"condition_results[{index}]"
        if not isinstance(condition_id, str) or condition_id not in conditions:
            errors.append(f"{prefix}: condition is not declared by the contract")
            continue
        if condition_id in seen:
            errors.append(f"{prefix}: duplicate condition result")
            continue
        seen.add(condition_id)
        condition = conditions[condition_id]
        verifier = condition.get("verifier") if isinstance(condition.get("verifier"), dict) else {}
        verifier_type = verifier.get("type")
        contract_owner = verifier.get("owner")
        expected_kind = VERIFIER_RECEIPT_KINDS.get(str(verifier_type))
        receipts = result.get("evidence", [])
        if not isinstance(receipts, list):
            errors.append(f"{prefix}: evidence must be an array")
            receipts = []
        status = result.get("status")
        if status == "pass" and (not isinstance(contract_owner, str) or not contract_owner.strip()):
            errors.append(f"{prefix}: pass requires verifier.owner in the contract")
        valid_pass_receipts = 0
        for receipt_index, receipt in enumerate(receipts):
            receipt_prefix = f"{prefix}.evidence[{receipt_index}]"
            receipt_errors: list[str] = []
            if not isinstance(receipt, dict):
                errors.append(f"{receipt_prefix}: receipt must be a mapping")
                continue
            kind = receipt.get("kind")
            outcome = receipt.get("outcome")
            owner = receipt.get("verifier_owner")
            observed_at = receipt.get("observed_at")
            if kind != expected_kind:
                receipt_errors.append(
                    f"kind {kind!r} does not match contract verifier {verifier_type!r} (expected {expected_kind!r})"
                )
            if not isinstance(owner, str) or not owner.strip():
                receipt_errors.append("verifier_owner must be non-empty")
            if owner != contract_owner:
                receipt_errors.append("verifier_owner does not match the contract verifier owner")
            observed_timestamp = _parse_aware_timestamp(observed_at)
            if observed_timestamp is None:
                receipt_errors.append("observed_at must be an ISO date-time with a timezone")
            else:
                started_timestamp = _parse_aware_timestamp(state.get("started_at"))
                if started_timestamp is not None and observed_timestamp < started_timestamp:
                    receipt_errors.append("observed_at predates the LoopRun started_at")
                future_limit = datetime.now(timezone.utc) + timedelta(seconds=EVIDENCE_FUTURE_TOLERANCE_SECONDS)
                if observed_timestamp > future_limit:
                    receipt_errors.append(
                        f"observed_at exceeds the {EVIDENCE_FUTURE_TOLERANCE_SECONDS}-second future tolerance"
                    )
            allowed_outcomes = {status}
            if status == "unverified":
                allowed_outcomes.add("user-verification-needed")
            if outcome not in allowed_outcomes:
                receipt_errors.append(f"outcome {outcome!r} does not match condition status {status!r}")

            artifact_path, path_error = _receipt_artifact_path(loop_dir, state, receipt)
            artifact_valid = False
            if path_error:
                receipt_errors.append(path_error)
            elif artifact_path is not None:
                if not artifact_path.is_file():
                    receipt_errors.append(f"referenced artifact does not exist: {receipt.get('artifact_ref')}")
                else:
                    declared_digest = receipt.get("artifact_sha256")
                    if not isinstance(declared_digest, str) or file_sha256(artifact_path) != declared_digest:
                        receipt_errors.append(f"artifact_sha256 does not match {receipt.get('artifact_ref')}")
                    else:
                        artifact_valid = True

            if kind == "command_exit":
                if receipt.get("artifact_scope") != "loop_run":
                    receipt_errors.append("command_exit evidence must use artifact_scope=loop_run")
                if receipt.get("command") != verifier.get("command"):
                    receipt_errors.append("command does not match the contract verifier")
                expected_exit = verifier.get("expected_exit_code", 0)
                if outcome == "pass" and receipt.get("exit_code") != expected_exit:
                    receipt_errors.append(f"exit_code does not match expected_exit_code {expected_exit!r}")
                if outcome == "fail" and receipt.get("exit_code") == expected_exit:
                    receipt_errors.append("a failed command receipt cannot record the expected exit code")
                if outcome == "pass":
                    receipt_errors.append(
                        "command_exit auto-pass is unavailable: claimed logs are not runtime-authenticated attestations"
                    )
            elif kind == "artifact_exists":
                if receipt.get("artifact_scope") != "workspace":
                    receipt_errors.append("artifact_exists evidence must use artifact_scope=workspace")
                if receipt.get("artifact_ref") != verifier.get("path"):
                    receipt_errors.append("artifact_ref does not match the contract verifier path")
            elif kind == "diff_scope":
                if receipt.get("artifact_scope") != "loop_run":
                    receipt_errors.append("diff_scope evidence must use artifact_scope=loop_run")
                verifier_path = verifier.get("path")
                if isinstance(verifier_path, str) and receipt.get("checked_path") != verifier_path:
                    receipt_errors.append("checked_path does not match the contract verifier path")
                workspace = state.get("workspace") if isinstance(state.get("workspace"), dict) else {}
                workspace_root = workspace.get("root")
                if isinstance(verifier_path, str) and isinstance(workspace_root, str):
                    base = Path(workspace_root).expanduser().resolve()
                    checked = (base / verifier_path).resolve()
                    try:
                        checked.relative_to(base)
                    except ValueError:
                        receipt_errors.append("diff_scope verifier path escapes workspace.root")
                    else:
                        if not checked.exists():
                            receipt_errors.append("diff_scope checked_path does not exist in the workspace")
                if outcome == "pass":
                    receipt_errors.append(
                        "diff_scope auto-pass is unavailable: claimed scope logs are not runtime-authenticated attestations"
                    )
            elif kind == "manual_acceptance":
                if receipt.get("artifact_scope") != "loop_run":
                    receipt_errors.append("manual acceptance evidence must use artifact_scope=loop_run")
                if receipt.get("actor_type") != "user" or receipt.get("accepted") is not True:
                    receipt_errors.append("manual acceptance requires actor_type=user and accepted=true")
                actor = receipt.get("actor")
                if not isinstance(actor, str) or not actor.strip():
                    receipt_errors.append("manual acceptance requires an explicit actor")
                accepted_scope = receipt.get("accepted_scope")
                if not isinstance(accepted_scope, str) or not accepted_scope.strip():
                    receipt_errors.append("manual acceptance requires accepted_scope")
                elif accepted_scope != verifier.get("acceptance_scope"):
                    receipt_errors.append("accepted_scope does not match the contract verifier acceptance_scope")
                if outcome != "pass":
                    receipt_errors.append("manual acceptance is valid only with outcome=pass")
                if artifact_valid and artifact_path is not None:
                    receipt_errors.extend(
                        _manual_acceptance_payload_errors(
                            artifact_path,
                            contract,
                            state,
                            condition_id,
                            receipt,
                        )
                    )
                if outcome == "pass":
                    receipt_errors.append(
                        "manual_check auto-pass is unavailable without host-authenticated user provenance"
                    )

            if receipt_errors:
                errors.extend(f"{receipt_prefix}: {error}" for error in receipt_errors)
            elif status == "pass" and outcome == "pass":
                valid_pass_receipts += 1
        if status == "pass" and valid_pass_receipts == 0:
            errors.append(
                f"{prefix}: pass requires a valid structured evidence receipt; evidence_refs do not satisfy verification"
            )
    return errors


def required_condition_ids(contract: dict[str, Any]) -> list[str]:
    return [condition["id"] for condition in success_conditions(contract) if condition.get("required", True) is not False]


def control_value(contract: dict[str, Any], key: str, default: int) -> int:
    control = contract.get("control") if isinstance(contract.get("control"), dict) else {}
    value = control.get(key, default)
    return value if isinstance(value, int) and value >= 0 else default


def condition_map(state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    results = state.get("condition_results", [])
    return {
        item["condition_id"]: item
        for item in results
        if isinstance(item, dict) and isinstance(item.get("condition_id"), str)
    }


def passed_required_count(contract: dict[str, Any], state: dict[str, Any]) -> int:
    results = condition_map(state)
    return sum(1 for condition_id in required_condition_ids(contract) if results.get(condition_id, {}).get("status") == "pass")


def state_fingerprint(contract: dict[str, Any], state: dict[str, Any]) -> str:
    results = condition_map(state)
    body = {
        "required": [
            {
                "id": condition_id,
                "status": results.get(condition_id, {}).get("status", "unverified"),
                "failure_fingerprint": results.get(condition_id, {}).get("failure_fingerprint"),
            }
            for condition_id in required_condition_ids(contract)
        ],
        "iteration": state.get("iteration"),
    }
    return canonical_hash(body)


def append_jsonl(path: Path, event: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True, ensure_ascii=True) + "\n")


@contextlib.contextmanager
def loop_lock(loop_dir: Path) -> Iterator[None]:
    """Exclusive advisory lock guarding a LoopRun's read-modify-write cycle.

    Prevents two concurrent Stop-hook evaluations from corrupting the same
    LoopRun state. Degrades to a no-op lock on platforms without fcntl.
    """
    loop_dir = Path(loop_dir)
    loop_dir.mkdir(parents=True, exist_ok=True)
    handle = (loop_dir / ".lock").open("w", encoding="utf-8")
    try:
        if fcntl is not None:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        yield
    finally:
        try:
            if fcntl is not None:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        finally:
            handle.close()
