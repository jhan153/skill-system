#!/usr/bin/env python3
"""Validate skill invocation-surface policy metadata."""

from __future__ import annotations

import argparse
import json
import re
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
IMPLICIT_SKILL_SURFACES = {
    "design-frontend": "explicit_procedure",
    "knowledge-base-read": "support_only",
    "memory-bank-harness": "support_only",
    "project-context-checkpoint": "explicit_procedure",
}
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


def validate_skill(skill_dir: Path, root: Path, automatic_handoff_targets: set[str]) -> list[str]:
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
    narrow_implicit_allowed = (
        IMPLICIT_SKILL_SURFACES.get(skill_dir.name) == surface
        or skill_dir.name in automatic_handoff_targets
    )
    if allow_implicit is True and surface != "selective_router" and not narrow_implicit_allowed:
        errors.append(
            f"{label}: implicit invocation is only allowed for selective_router "
            "or an approved narrow skill surface"
        )
    if surface in NON_OWNER_SURFACES and not false_value(policy, "may_own_execution"):
        errors.append(f"{label}: {surface} must set may_own_execution: false")
    if surface == "explicit_procedure" and not true_value(policy, "may_own_execution"):
        errors.append(f"{label}: explicit_procedure must set may_own_execution: true")
    if surface in {"selective_router", "evidence_gate"} and not false_value(policy, "may_write"):
        errors.append(f"{label}: {surface} must set may_write: false")
    if surface == "evidence_gate" and not true_value(policy, "may_block_completion"):
        errors.append(f"{label}: evidence_gate must set may_block_completion: true")
    return errors


def invocation_contract(skill_md: Path) -> tuple[set[str] | None, set[str] | None]:
    text = read_text(skill_md)

    def values(field: str) -> set[str] | None:
        match = re.search(rf"(?m)^- {field}:\s*(.*)$", text)
        if match is None:
            return None
        return set(re.findall(r"`([a-z0-9][a-z0-9-]*)`", match.group(1)))

    return values("automatic_handoff_targets"), values("explicit_recommendation_targets")


def validate_handoff_contracts(root: Path, namespace: str) -> tuple[list[str], set[str]]:
    errors: list[str] = []
    skills = {path.name: path for path in skill_dirs(root, namespace)}
    automatic_union: set[str] = set()
    for router_id, router_dir in skills.items():
        if routing_role(router_dir / "SKILL.md") != "router":
            continue
        policy, _ = load_policy(router_dir)
        if policy is None or policy.get("allow_implicit_invocation") is not True:
            continue
        label = router_dir.relative_to(root).as_posix()
        automatic, explicit = invocation_contract(router_dir / "SKILL.md")
        if automatic is None or explicit is None:
            errors.append(
                f"{label}: implicit router must declare automatic_handoff_targets "
                "and explicit_recommendation_targets"
            )
            continue
        if not automatic:
            errors.append(f"{label}: automatic_handoff_targets must not be empty")
        overlap = automatic & explicit
        if overlap:
            errors.append(f"{label}: targets classified as both automatic and explicit: {sorted(overlap)}")

        referenced = {
            token
            for token in re.findall(r"`([a-z0-9][a-z0-9-]*)`", read_text(router_dir / "SKILL.md"))
            if token in skills and token != router_id
        }
        unclassified = referenced - automatic - explicit
        if unclassified:
            errors.append(f"{label}: referenced skill targets lack invocation classification: {sorted(unclassified)}")

        for target in sorted(automatic):
            target_dir = skills.get(target)
            if target_dir is None:
                errors.append(f"{label}: automatic handoff target does not exist: {target}")
                continue
            target_policy, _ = load_policy(target_dir)
            if target_policy is None or target_policy.get("allow_implicit_invocation") is not True:
                errors.append(f"{label}: automatic handoff target is not implicitly invocable: {target}")
        for target in sorted(explicit):
            target_dir = skills.get(target)
            if target_dir is None:
                errors.append(f"{label}: explicit recommendation target does not exist: {target}")
                continue
            target_policy, _ = load_policy(target_dir)
            if target_policy is None or target_policy.get("allow_implicit_invocation") is not False:
                errors.append(f"{label}: explicit recommendation target must remain explicit-only: {target}")
        automatic_union.update(automatic)
    return errors, automatic_union


def policy_subset(policy: dict[str, Any]) -> dict[str, Any]:
    return {key: policy.get(key) for key in sorted(POLICY_COMPARE_KEYS) if key in policy}


def frontmatter_scalar(skill_md: Path, key: str) -> tuple[str | None, list[str]]:
    errors: list[str] = []
    lines = read_text(skill_md).splitlines()
    if not lines or lines[0] != "---":
        return None, [f"{skill_md}: missing YAML frontmatter"]
    try:
        closing = lines.index("---", 1)
    except ValueError:
        return None, [f"{skill_md}: unclosed YAML frontmatter"]
    matches = []
    prefix = f"{key}:"
    for line in lines[1:closing]:
        if line.startswith(prefix):
            matches.append(line.split(":", 1)[1].strip())
    if len(matches) > 1:
        errors.append(f"{skill_md}: duplicate {key}")
    return (matches[0] if matches else None), errors


def validate_invocation_projection(skill_dir: Path, root: Path, *, claude: bool) -> list[str]:
    errors: list[str] = []
    label = skill_dir.relative_to(root).as_posix()
    value, frontmatter_errors = frontmatter_scalar(skill_dir / "SKILL.md", "disable-model-invocation")
    errors.extend(frontmatter_errors)
    policy, _ = load_policy(skill_dir)
    if policy is None or not isinstance(policy.get("allow_implicit_invocation"), bool):
        return errors
    allow_implicit = policy["allow_implicit_invocation"]
    if not claude:
        if value is not None:
            errors.append(f"{label}: Codex SKILL.md must not contain Claude disable-model-invocation")
        return errors
    expected = None if allow_implicit else "true"
    if value != expected:
        rendered = "absent" if expected is None else expected
        errors.append(
            f"{label}: Claude disable-model-invocation must be {rendered} "
            f"when allow_implicit_invocation is {str(allow_implicit).lower()}"
        )
    return errors


def validate_runtime_projection(root: Path) -> list[str]:
    errors: list[str] = []
    codex = {path.name: path for path in skill_dirs(root, ".codex")}
    claude = {path.name: path for path in skill_dirs(root, ".claude")}
    if codex and claude and set(codex) != set(claude):
        errors.append(".codex/.claude skill inventory drift")
    for skill_id in sorted(set(codex) & set(claude)):
        codex_policy, _ = load_policy(codex[skill_id])
        claude_policy, _ = load_policy(claude[skill_id])
        if codex_policy is None or claude_policy is None:
            continue
        if policy_subset(codex_policy) != policy_subset(claude_policy):
            errors.append(f"{skill_id}: .codex/.claude invocation policy drift")
        errors.extend(validate_invocation_projection(codex[skill_id], root, claude=False))
        errors.extend(validate_invocation_projection(claude[skill_id], root, claude=True))
    return errors


def validate_plugin_projection(root: Path) -> list[str]:
    errors: list[str] = []
    plugins_root = root / "plugins"
    if not plugins_root.is_dir():
        return errors
    claude_root = plugins_root / "claude"
    codex_plugins = {
        path.name: path
        for path in plugins_root.iterdir()
        if path.is_dir() and (path / ".codex-plugin" / "plugin.json").is_file()
    }
    claude_plugins = {
        path.name: path
        for path in claude_root.iterdir()
        if path.is_dir() and (path / ".claude-plugin" / "plugin.json").is_file()
    } if claude_root.is_dir() else {}
    if set(codex_plugins) != set(claude_plugins):
        errors.append("plugins: Codex/Claude package inventory drift")
    for plugin in [codex_plugins[name] for name in sorted(codex_plugins)]:
        codex_manifest = plugin / ".codex-plugin" / "plugin.json"
        claude_plugin = claude_root / plugin.name
        claude_manifest = claude_plugin / ".claude-plugin" / "plugin.json"
        label = plugin.relative_to(root).as_posix()
        if not claude_manifest.is_file():
            errors.append(f"{label}: missing paired Claude plugin manifest")
            continue
        codex_data = json.loads(read_text(codex_manifest))
        claude_data = json.loads(read_text(claude_manifest))
        if codex_data.get("skills") != "./skills/":
            errors.append(f"{label}: Codex manifest skills must be ./skills/")
        if claude_data.get("skills") != "./skills/":
            errors.append(f"{label}: Claude manifest skills must be ./skills/")
        codex_skills = {
            path.name: path
            for path in (plugin / "skills").iterdir()
            if path.is_dir() and (path / "SKILL.md").is_file()
        } if (plugin / "skills").is_dir() else {}
        claude_skills = {
            path.name: path
            for path in (claude_plugin / "skills").iterdir()
            if path.is_dir() and (path / "SKILL.md").is_file()
        } if (claude_plugin / "skills").is_dir() else {}
        if set(codex_skills) != set(claude_skills):
            errors.append(f"{label}: Codex/Claude plugin skill inventory drift")
        for skill_id in sorted(set(codex_skills) & set(claude_skills)):
            codex_policy, _ = load_policy(codex_skills[skill_id])
            claude_policy, _ = load_policy(claude_skills[skill_id])
            if codex_policy is None or claude_policy is None:
                errors.append(f"{label}/{skill_id}: missing projected invocation policy")
                continue
            if codex_policy.get("allow_implicit_invocation") != claude_policy.get("allow_implicit_invocation"):
                errors.append(f"{label}/{skill_id}: plugin invocation policy drift")
            errors.extend(validate_invocation_projection(codex_skills[skill_id], root, claude=False))
            errors.extend(validate_invocation_projection(claude_skills[skill_id], root, claude=True))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()
    errors: list[str] = []
    for namespace in [".codex", ".claude"]:
        contract_errors, automatic_handoff_targets = validate_handoff_contracts(root, namespace)
        errors.extend(contract_errors)
        for skill_dir in skill_dirs(root, namespace):
            errors.extend(validate_skill(skill_dir, root, automatic_handoff_targets))
    errors.extend(validate_runtime_projection(root))
    errors.extend(validate_plugin_projection(root))
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
