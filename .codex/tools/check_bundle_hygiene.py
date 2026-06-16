#!/usr/bin/env python3
"""Read-only sanity checks for the 7.2.0 manual drop-in skill bundle."""

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
        path = root / name
        if not path.exists():
            continue
        if name == "docs":
            # Planning artifacts under docs/plan/ are allowed; any other root docs/ content
            # is still a forbidden runtime dependency.
            stray = [
                p
                for p in path.rglob("*")
                if p.is_file() and not p.relative_to(root).as_posix().startswith("docs/plan/")
            ]
            if stray:
                errors.append(
                    f"root runtime dependency not allowed: docs (only docs/plan/ is allowed; stray: {stray[0].relative_to(root)})"
                )
            continue
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
    section: list[str] = []
    in_registry = False
    for line in read_text(registry).splitlines():
        if line.startswith("## Registry"):
            in_registry = True
            continue
        if in_registry and line.startswith("## "):
            break
        if in_registry:
            section.append(line)
    text = "\n".join(section)
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


MIRROR_DIR_PAIRS = [
    (".codex/docs", ".claude/docs"),
    (".codex/eval", ".claude/eval"),
    (".codex/skills", ".claude/skills"),
]
MIRROR_FILE_PAIRS = [
    (".codex/context-routing.md", ".claude/context-routing.md"),
]
SKILL_REF_FIELDS = ("expected_primary_skill", "expected_supporting_skills", "should_not_trigger")
SKILL_REF_IGNORE = {"", "null", "none", "~", "[]"}


def relative_files(base: Path) -> set:
    return {path.relative_to(base) for path in base.rglob("*") if path.is_file()}


def check_mirror_parity(root: Path, errors: list[str]) -> None:
    for codex_rel, claude_rel in MIRROR_DIR_PAIRS:
        codex_dir = root / codex_rel
        claude_dir = root / claude_rel
        if not codex_dir.exists() or not claude_dir.exists():
            errors.append(f"mirror dir missing: {codex_rel} or {claude_rel}")
            continue
        codex_files = relative_files(codex_dir)
        claude_files = relative_files(claude_dir)
        for rel in sorted(str(p) for p in codex_files - claude_files):
            errors.append(f"mirror parity: {claude_rel}/{rel} missing (present in {codex_rel})")
        for rel in sorted(str(p) for p in claude_files - codex_files):
            errors.append(f"mirror parity: {codex_rel}/{rel} missing (present in {claude_rel})")
        for shared in sorted(codex_files & claude_files, key=str):
            if (codex_dir / shared).read_bytes() != (claude_dir / shared).read_bytes():
                errors.append(f"mirror parity: content differs for {shared} between {codex_rel} and {claude_rel}")
    for codex_rel, claude_rel in MIRROR_FILE_PAIRS:
        codex_file = root / codex_rel
        claude_file = root / claude_rel
        if not codex_file.exists() or not claude_file.exists():
            errors.append(f"mirror file missing: {codex_rel} or {claude_rel}")
        elif codex_file.read_bytes() != claude_file.read_bytes():
            errors.append(f"mirror parity: content differs between {codex_rel} and {claude_rel}")


def check_eval_referential_integrity(root: Path, errors: list[str]) -> None:
    actual = {p.parent.name for p in (root / ".codex" / "skills").glob("*/SKILL.md")}
    for rel in EVALS:
        path = root / rel
        if path.suffix not in {".yaml", ".yml"}:
            continue
        for line in read_text(path).splitlines():
            stripped = line.strip()
            for field in SKILL_REF_FIELDS:
                if not stripped.startswith(field + ":"):
                    continue
                value = stripped[len(field) + 1:].strip().strip("[]")
                for raw in value.split(","):
                    token = raw.strip().strip("'\"").strip()
                    if token.lower() in SKILL_REF_IGNORE or not token:
                        continue
                    if token not in actual:
                        errors.append(f"{rel}: unknown skill reference '{token}' in {field}")


def check_agent_metadata(root: Path, errors: list[str]) -> None:
    yamls = sorted((root / ".codex" / "skills").glob("*/agents/openai.yaml"))
    if not yamls:
        errors.append("no codex agent metadata found")
    for path in yamls:
        if not re.search(r"(?m)^\s*allow_implicit_invocation:\s*(true|false)\s*$", read_text(path)):
            errors.append(f"missing allow_implicit_invocation: {path.relative_to(root)}")


CANONICAL_RC_ORDER = [
    "role",
    "intent_signature",
    "use_when",
    "do_not_use_when",
    "expected_inputs",
    "expected_outputs",
    "context_targets",
    "risk_profile",
    "entry_scene",
]
STALE_VERSION_LABELS = [
    "7.1 Terms",
    "7.1.1 Terms",
    "7.1 core",
    "7.1.1 core",
    "7.1 Bundle Policy",
    "7.1.1 Bundle Policy",
    "7.1 manual drop-in",
    "7.1.1 manual drop-in",
    "7.1 is a manual drop-in",
    "7.1.1 is a manual drop-in",
]
VERSION_LABEL_DOCS = ["README.md", "CHANGELOG.md", "TERMS.md", ".codex/AGENTS.md", ".claude/CLAUDE.md"]


def routing_card_role(text: str):
    match = re.search(r"(?m)^- role:\s*(\S+)", text)
    return match.group(1) if match else None


def routing_card_writes(text: str) -> list[str]:
    items: list[str] = []
    in_writes = False
    for line in text.splitlines():
        if re.match(r"^\s{2}writes:\s*$", line):
            in_writes = True
            continue
        if in_writes:
            if re.match(r"^\s{4}- ", line):
                items.append(line.strip()[2:].strip())
            elif line.strip():
                break
    return items


def routing_card_field_order(text: str) -> list[str]:
    fields: list[str] = []
    in_card = False
    for line in text.splitlines():
        if line.startswith("## Routing Card"):
            in_card = True
            continue
        if in_card and line.startswith("## "):
            break
        if in_card:
            match = re.match(r"^- ([a-z_]+):", line)
            if match:
                fields.append(match.group(1))
    return fields


def check_role_risk_consistency(root: Path, errors: list[str]) -> None:
    for skill_file in sorted((root / ".codex" / "skills").glob("*/SKILL.md")):
        name = skill_file.parent.name
        text = read_text(skill_file)
        role = routing_card_role(text)
        if role == "router":
            for item in routing_card_writes(text):
                if "WRITE_" in item:
                    errors.append(f"router {name} declares a write capability: {item}")
        if role == "heavy_artifact_generator":
            meta = skill_file.parent / "agents" / "openai.yaml"
            if not meta.exists() or not re.search(
                r"(?m)^\s*allow_implicit_invocation:\s*false\s*$", read_text(meta)
            ):
                errors.append(f"heavy artifact generator {name} must keep allow_implicit_invocation: false")


def check_routing_card_order(root: Path, errors: list[str]) -> None:
    for skill_file in sorted((root / ".codex" / "skills").glob("*/SKILL.md")):
        present = [f for f in routing_card_field_order(read_text(skill_file)) if f in CANONICAL_RC_ORDER]
        if present != CANONICAL_RC_ORDER:
            errors.append(f"routing card field order/presence off in {skill_file.parent.name}: {present}")


ALLOWED_FAMILIES = {
    "search",
    "design",
    "report",
    "research",
    "analysis",
    "workflow",
    "coordination",
    "planning",
    "memory",
    "evaluation",
    "skill_system",
}


def check_family_consistency(root: Path, errors: list[str]) -> None:
    registry = root / ".codex" / "docs" / "skill_registry.md"
    if not registry.exists():
        return
    in_registry = False
    header_has_family = False
    for line in read_text(registry).splitlines():
        if line.startswith("## Registry"):
            in_registry = True
            continue
        if in_registry and line.startswith("## "):
            break
        if not in_registry:
            continue
        if line.startswith("| skill | cluster | maturity"):
            header_has_family = line.rstrip().rstrip("|").rstrip().endswith("family")
            continue
        if not line.startswith("| `"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        skill = cells[0].strip("`")
        family = cells[-1].strip("`").strip() if cells else ""
        if not family:
            errors.append(f"registry skill {skill} has no family")
        elif family not in ALLOWED_FAMILIES:
            errors.append(f"registry skill {skill} has unknown family: {family}")
    if not header_has_family:
        errors.append("registry table is missing a trailing family column")


def check_version_labels(root: Path, errors: list[str]) -> None:
    for rel in VERSION_LABEL_DOCS:
        path = root / rel
        if not path.exists():
            continue
        text = read_text(path)
        for label in STALE_VERSION_LABELS:
            if label in text:
                errors.append(f"stale version label '{label}' in {rel}; use 7.2.0")


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
    check_mirror_parity(root, errors)
    check_eval_referential_integrity(root, errors)
    check_agent_metadata(root, errors)
    check_role_risk_consistency(root, errors)
    check_routing_card_order(root, errors)
    check_version_labels(root, errors)
    check_family_consistency(root, errors)
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
