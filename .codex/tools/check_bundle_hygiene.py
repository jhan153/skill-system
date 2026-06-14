#!/usr/bin/env python3
"""Read-only sanity checks for the 7.1 manual drop-in skill bundle."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT_DOCS = ["README.md", "TERMS.md", "CHANGELOG.md", "FIELD_FEEDBACK.md"]
CODEX_DIRS = [".codex/docs", ".codex/eval", ".codex/tools", ".codex/skills", ".codex/rules"]
CODEX_FILES = [".codex/AGENTS.md", ".codex/context-routing.md", ".codex/research-routing.md"]
CLAUDE_DIRS = [".claude/docs", ".claude/eval", ".claude/skills"]
CLAUDE_FILES = [".claude/CLAUDE.md"]
DOCS = [
    ".codex/docs/runtime_terms.md",
    ".codex/docs/skill_registry.md",
    ".codex/docs/skill_maturity.md",
    ".codex/docs/team_patterns.md",
    ".codex/docs/context_pack_guidelines.md",
    ".codex/docs/memory_usage_guidelines.md",
    ".codex/docs/design_cluster_roadmap.md",
    ".codex/docs/field_feedback_guidelines.md",
    ".codex/docs/improvement_tracks.md",
]
EVALS = [
    ".codex/eval/runtime_usage_cases.yaml",
    ".codex/eval/routing_cases.yaml",
    ".codex/eval/negative_routing_cases.yaml",
    ".codex/eval/memory_usage_cases.yaml",
    ".codex/eval/handoff_cases.yaml",
    ".codex/eval/design_usage_cases.yaml",
    ".codex/eval/research_regression_cases.yaml",
    ".codex/eval/usage_quality_report.template.md",
]
SENSITIVE_NAMES = {
    "auth.json",
    "sessions",
    "archived_sessions",
    ".env",
    ".netrc",
    "id_rsa",
    "id_ed25519",
}
SENSITIVE_SUFFIXES = {".sqlite", ".db", ".pem", ".key"}
EXCLUDED_CORE_DIRS = {"harness", ".agent-workflow", "docs", "eval", "tools", "shared"}
ALLOWED_MATURITY = {"skeleton", "usable", "field_tuned", "experimental", "deprecated"}
POLICY_DOCS = ["README.md", "TERMS.md", ".codex/AGENTS.md"]


def add_missing_path_errors(root: Path, paths: list[str], errors: list[str]) -> None:
    for item in paths:
        if not (root / item).exists():
            errors.append(f"missing: {item}")


def check_root_shape(root: Path, errors: list[str]) -> None:
    add_missing_path_errors(root, ROOT_DOCS + CODEX_FILES + CLAUDE_FILES + DOCS + EVALS, errors)
    add_missing_path_errors(root, CODEX_DIRS + CLAUDE_DIRS, errors)
    for name in EXCLUDED_CORE_DIRS:
        if (root / name).exists():
            errors.append(f"root runtime dependency not allowed: {name}")


def check_sensitive_files(root: Path, errors: list[str]) -> None:
    for path in root.rglob("*"):
        name = path.name.lower()
        if name in SENSITIVE_NAMES or any(name.endswith(suffix) for suffix in SENSITIVE_SUFFIXES):
            errors.append(f"sensitive-looking file: {path.relative_to(root)}")
        if "secret" in name or "api_key" in name or "private_key" in name:
            errors.append(f"sensitive-looking name: {path.relative_to(root)}")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def check_skill_frontmatter(root: Path, errors: list[str]) -> None:
    skills_root = root / ".codex" / "skills"
    skill_files = sorted(skills_root.glob("*/SKILL.md"))
    if not skill_files:
        errors.append("no codex skills found")
        return
    for skill_file in skill_files:
        text = read_text(skill_file)
        if not text.startswith("---\n"):
            errors.append(f"missing frontmatter: {skill_file.relative_to(root)}")
            continue
        head = text.split("---", 2)[1]
        if not re.search(r"(?m)^name:\s*\S+", head):
            errors.append(f"missing name: {skill_file.relative_to(root)}")
        if not re.search(r"(?m)^description:\s*.+", head):
            errors.append(f"missing description: {skill_file.relative_to(root)}")


def check_registry(root: Path, errors: list[str]) -> None:
    registry = root / ".codex" / "docs" / "skill_registry.md"
    text = read_text(registry)
    listed = set()
    for line in text.splitlines():
        if not line.startswith("| `"):
            continue
        first_cell = line.strip("|").split("|", 1)[0].strip()
        match = re.fullmatch(r"`([^`]+)`", first_cell)
        if match:
            listed.add(match.group(1))
    actual = {p.parent.name for p in (root / ".codex" / "skills").glob("*/SKILL.md")}
    missing = sorted(actual - listed)
    extra = sorted(listed - actual - {"skill"})
    for skill in missing:
        errors.append(f"registry missing skill: {skill}")
    for skill in extra:
        errors.append(f"registry unknown skill: {skill}")
    for line in text.splitlines():
        if line.startswith("| `") and " | `" in line:
            parts = [part.strip() for part in line.strip("|").split("|")]
            if len(parts) >= 3:
                value = parts[2].strip("`")
                if value not in ALLOWED_MATURITY:
                    errors.append(f"invalid maturity for {parts[0]}: {value}")


def check_eval_shape(root: Path, errors: list[str]) -> None:
    required = [
        "case_id:",
        "user_request:",
        "expected_primary_skill:",
        "expected_supporting_skills:",
        "should_not_trigger:",
        "expected_context:",
        "expected_output_shape:",
        "quality_notes:",
        "friction_risk:",
    ]
    for rel in EVALS:
        path = root / rel
        if path.suffix not in {".yaml", ".yml"}:
            continue
        text = read_text(path)
        for field in required:
            if field not in text:
                errors.append(f"{rel} missing field {field}")


def policy_text(root: Path) -> str:
    return "\n".join(read_text(root / rel) for rel in POLICY_DOCS if (root / rel).exists())


def check_bundle_policy(root: Path, errors: list[str], warnings: list[str]) -> None:
    if (root / ".codex" / "config.toml").exists():
        errors.append(".codex/config.toml should not be in the default bundle")
    if (root / ".codex" / "automations").exists():
        errors.append(".codex/automations should not be in the default bundle")
    docs = policy_text(root)
    for term in [".codex/config.toml", "automations", ".system"]:
        if term not in docs:
            errors.append(f"policy docs do not mention {term}")
    if (root / ".codex" / "skills" / ".system").exists():
        errors.append("core .codex/skills/.system is not allowed")
    if (root / ".claude" / "skills" / ".system").exists():
        errors.append("core .claude/skills/.system is not allowed")
    optional = root / "optional-system-skills-snapshot" / ".codex" / "skills" / ".system"
    if optional.exists():
        warnings.append("optional system skills snapshot present; do not copy by default")
    rules = root / ".codex" / "rules" / "default.rules"
    if rules.exists():
        risky = ["curl", "rebase", '"branch", "-d"', "fetch", "pkill", "kill", "lldb", "/users/", "/private/tmp", ".codex", '"checkout", "--ours"']
        for block in re.findall(r"prefix_rule\((.*?)\)", read_text(rules), flags=re.S):
            lower = block.lower()
            if 'decision="allow"' in lower and any(item in lower for item in risky):
                errors.append(f"risky allow in rules/default.rules: {block.splitlines()[0].strip()}")


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    errors: list[str] = []
    warnings: list[str] = []
    if not root.exists():
        print(f"FAIL: root not found: {root}")
        return 2
    check_root_shape(root, errors)
    check_sensitive_files(root, errors)
    check_skill_frontmatter(root, errors)
    check_registry(root, errors)
    check_eval_shape(root, errors)
    check_bundle_policy(root, errors, warnings)
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS")
    for warning in warnings:
        print(f"WARN: {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
