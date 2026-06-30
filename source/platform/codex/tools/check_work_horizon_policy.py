#!/usr/bin/env python3
"""Validate plan/workflow work-horizon metadata."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _validation import load_yaml_file  # noqa: E402


EXPECTED: dict[str, dict[str, str]] = {
    "plan-long-term-package": {"work_horizon": "long_plan", "planning_altitude": "strategic_package"},
    "plan-short-term-docs": {"work_horizon": "short_plan", "planning_altitude": "tactical_design"},
    "plan-loop-term": {"work_horizon": "loop_overlay", "planning_altitude": "loop_contract"},
    "plan-spec-curator": {"work_horizon": "cross_horizon", "planning_altitude": "lifecycle_curation"},
    "workflow-plan-runner": {"work_horizon": "cross_horizon", "execution_mode": "plan_batch_execution"},
    "workflow-loop-runner": {"work_horizon": "loop_overlay", "execution_mode": "loop_convergence_execution"},
    "workflow-task-ledger": {"work_horizon": "task_ticket", "execution_mode": "checkpoint_ledger"},
    "workflow-rigor": {"work_horizon": "cross_horizon", "execution_mode": "rigor_modifier"},
    "workflow-recovery": {"work_horizon": "cross_horizon", "execution_mode": "recovery_intervention"},
    "workflow-validation": {"work_horizon": "cross_horizon", "execution_mode": "validation_lane"},
    "workflow-minimal-implementation": {"work_horizon": "cross_horizon", "execution_mode": "minimality_constraint"},
}

VALID_HORIZONS = {"task_ticket", "short_plan", "long_plan", "loop_overlay", "cross_horizon"}
VALID_ALTITUDES = {"strategic_package", "tactical_design", "loop_contract", "lifecycle_curation"}
VALID_EXECUTION_MODES = {
    "plan_batch_execution",
    "loop_convergence_execution",
    "checkpoint_ledger",
    "rigor_modifier",
    "recovery_intervention",
    "validation_lane",
    "minimality_constraint",
}
COMPARE_KEYS = {"work_horizon", "planning_altitude", "execution_mode"}


def skill_dirs(root: Path, namespace: str) -> dict[str, Path]:
    base = root / namespace / "skills"
    if not base.exists():
        return {}
    return {path.name: path for path in sorted(base.iterdir()) if (path / "SKILL.md").is_file()}


def load_agent(skill_dir: Path) -> dict[str, Any]:
    path = skill_dir / "agents" / "openai.yaml"
    data = load_yaml_file(path)
    return data if isinstance(data, dict) else {}


def mapping_key(data: dict[str, Any], name: str, key: str) -> str | None:
    value = data.get(name)
    if not isinstance(value, dict):
        return None
    raw = value.get(key)
    return raw if isinstance(raw, str) else None


def validate_agent(skill_id: str, data: dict[str, Any], label: str) -> list[str]:
    errors: list[str] = []
    expected = EXPECTED[skill_id]
    horizon = mapping_key(data, "work_horizon", "level")
    if horizon not in VALID_HORIZONS:
        errors.append(f"{label}: work_horizon.level must be one of {sorted(VALID_HORIZONS)}, got {horizon!r}")
    elif horizon != expected["work_horizon"]:
        errors.append(f"{label}: work_horizon.level {horizon!r} != expected {expected['work_horizon']!r}")

    if "planning_altitude" in expected:
        altitude = mapping_key(data, "planning_altitude", "kind")
        if altitude not in VALID_ALTITUDES:
            errors.append(f"{label}: planning_altitude.kind must be one of {sorted(VALID_ALTITUDES)}, got {altitude!r}")
        elif altitude != expected["planning_altitude"]:
            errors.append(f"{label}: planning_altitude.kind {altitude!r} != expected {expected['planning_altitude']!r}")

    if "execution_mode" in expected:
        mode = mapping_key(data, "execution_mode", "kind")
        if mode not in VALID_EXECUTION_MODES:
            errors.append(f"{label}: execution_mode.kind must be one of {sorted(VALID_EXECUTION_MODES)}, got {mode!r}")
        elif mode != expected["execution_mode"]:
            errors.append(f"{label}: execution_mode.kind {mode!r} != expected {expected['execution_mode']!r}")
    return errors


def metadata_subset(data: dict[str, Any]) -> dict[str, Any]:
    return {key: data.get(key) for key in sorted(COMPARE_KEYS) if key in data}


def validate_namespace(root: Path, namespace: str, allow_partial: bool) -> list[str]:
    errors: list[str] = []
    skills = skill_dirs(root, namespace)
    for skill_id in sorted(EXPECTED):
        skill_dir = skills.get(skill_id)
        if skill_dir is None:
            if not allow_partial:
                errors.append(f"{namespace}/skills/{skill_id}: missing expected work-horizon skill")
            continue
        errors.extend(validate_agent(skill_id, load_agent(skill_dir), f"{namespace}/skills/{skill_id}"))
    return errors


def validate_mirror_parity(root: Path, allow_partial: bool) -> list[str]:
    errors: list[str] = []
    codex = skill_dirs(root, ".codex")
    claude = skill_dirs(root, ".claude")
    for skill_id in sorted(EXPECTED):
        if skill_id not in codex or skill_id not in claude:
            if not allow_partial:
                errors.append(f"{skill_id}: missing .codex or .claude mirror for work-horizon parity")
            continue
        if metadata_subset(load_agent(codex[skill_id])) != metadata_subset(load_agent(claude[skill_id])):
            errors.append(f"{skill_id}: .codex/.claude work-horizon metadata drift")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--allow-partial", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    errors: list[str] = []
    for namespace in [".codex", ".claude"]:
        errors.extend(validate_namespace(root, namespace, args.allow_partial))
    errors.extend(validate_mirror_parity(root, args.allow_partial))
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
