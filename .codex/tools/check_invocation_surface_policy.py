#!/usr/bin/env python3
"""Validate skill invocation-surface policy metadata."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _validation import load_yaml_file, read_text  # noqa: E402


VALID_SURFACES = {
    "explicit_procedure",
    "selective_router",
    "evidence_gate",
    "support_only",
}
SUPPORT_ROLES = {
    "support",
    "output_modifier",
    "execution_modifier",
    "surface_specialist_implementation_modifier",
}
EVIDENCE_GATE_ROLES = {
    "design_evidence_gate",
    "review_gate",
}
NON_OWNER_SURFACES = {"selective_router", "evidence_gate", "support_only"}
POLICY_COMPARE_KEYS = {
    "invocation_surface",
    "allow_implicit_invocation",
    "may_own_execution",
    "may_write",
    "may_block_completion",
}


def skill_dirs(root: Path, namespace: str) -> list[Path]:
    base = root / namespace / "skills"
    if not base.exists():
        return []
    return sorted(path for path in base.iterdir() if (path / "SKILL.md").is_file())


def routing_role(skill_md: Path) -> str | None:
    for line in read_text(skill_md).splitlines():
        stripped = line.strip()
        if stripped.startswith("- role:"):
            return stripped.split(":", 1)[1].strip()
    return None


def load_policy(skill_dir: Path) -> tuple[dict[str, Any] | None, Path]:
    agent_file = skill_dir / "agents" / "openai.yaml"
    if not agent_file.exists():
        return None, agent_file
    data = load_yaml_file(agent_file)
    if not isinstance(data, dict):
        return None, agent_file
    policy = data.get("policy")
    return policy if isinstance(policy, dict) else None, agent_file


def expected_surface(role: str) -> str:
    if role == "router":
        return "selective_router"
    if role in EVIDENCE_GATE_ROLES:
        return "evidence_gate"
    if role in SUPPORT_ROLES:
        return "support_only"
    return "explicit_procedure"


def false_value(policy: dict[str, Any], key: str) -> bool:
    return policy.get(key) is False


def true_value(policy: dict[str, Any], key: str) -> bool:
    return policy.get(key) is True


def validate_skill(skill_dir: Path, root: Path) -> list[str]:
    errors: list[str] = []
    label = skill_dir.relative_to(root).as_posix()
    role = routing_role(skill_dir / "SKILL.md")
    if role is None:
        return [f"{label}: missing Routing Card role"]
    policy, agent_file = load_policy(skill_dir)
    if policy is None:
        return [f"{agent_file.relative_to(root).as_posix()}: missing policy mapping"]
    surface = policy.get("invocation_surface")
    if surface not in VALID_SURFACES:
        errors.append(f"{label}: invalid invocation_surface {surface!r}")
    if surface != expected_surface(role):
        errors.append(f"{label}: invocation_surface {surface!r} does not match role {role!r}")
    allow_implicit = policy.get("allow_implicit_invocation")
    if not isinstance(allow_implicit, bool):
        errors.append(f"{label}: allow_implicit_invocation must be boolean")
    if allow_implicit is True and surface != "selective_router":
        errors.append(f"{label}: implicit invocation is only allowed for selective_router")
    if surface in NON_OWNER_SURFACES and not false_value(policy, "may_own_execution"):
        errors.append(f"{label}: {surface} must set may_own_execution: false")
    if surface == "explicit_procedure" and not true_value(policy, "may_own_execution"):
        errors.append(f"{label}: explicit_procedure must set may_own_execution: true")
    if surface in {"selective_router", "evidence_gate"} and not false_value(policy, "may_write"):
        errors.append(f"{label}: {surface} must set may_write: false")
    if surface == "evidence_gate" and not true_value(policy, "may_block_completion"):
        errors.append(f"{label}: evidence_gate must set may_block_completion: true")
    return errors


def policy_subset(policy: dict[str, Any]) -> dict[str, Any]:
    return {key: policy.get(key) for key in sorted(POLICY_COMPARE_KEYS) if key in policy}


def validate_mirror_parity(root: Path) -> list[str]:
    errors: list[str] = []
    codex = {path.name: path for path in skill_dirs(root, ".codex")}
    claude = {path.name: path for path in skill_dirs(root, ".claude")}
    for skill_id in sorted(set(codex) & set(claude)):
        codex_policy, _ = load_policy(codex[skill_id])
        claude_policy, _ = load_policy(claude[skill_id])
        if codex_policy is None or claude_policy is None:
            continue
        if policy_subset(codex_policy) != policy_subset(claude_policy):
            errors.append(f"{skill_id}: .codex/.claude invocation policy drift")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()
    errors: list[str] = []
    for namespace in [".codex", ".claude"]:
        for skill_dir in skill_dirs(root, namespace):
            errors.extend(validate_skill(skill_dir, root))
    errors.extend(validate_mirror_parity(root))
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
