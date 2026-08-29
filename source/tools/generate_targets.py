#!/usr/bin/env python3
"""Generate provider runtimes and plugins from canonical source/.

Portable skills and data contracts are shared. Harness entry files, routing, hooks,
permissions, and platform tools are owned by source/platform/<provider> and can be generated
independently. ``runtime`` generates all declared runtime companions in one command.

Platform entries that overlap shared output are merged. Platform-only entries are replaced from
source so deleted tools and hook files cannot survive in generated targets.

Idempotency: verbatim trees copy unchanged bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

# (source_rel, target_rel) copied unchanged into either requested target.
NEUTRAL_VERBATIM: list[tuple[str, str]] = [
    ("shared/docs", "docs"),
    ("shared/schemas", "schemas"),  # Phase 1b: schema definitions are platform-neutral data contracts
]
NEUTRAL_TARGET_ROOTS = {target_rel.split("/", 1)[0] for _, target_rel in NEUTRAL_VERBATIM}
REPORT_CANVAS_SOURCE = Path("shared/report-canvas")
REPORT_CANVAS_CONTRACT_SOURCE = Path("shared/docs/report_canvas_contract.md")
REPORT_CANVAS_PLUGIN_TARGET = Path("shared/report-canvas")
REPORT_CANVAS_REFERENCE_TARGET = Path("references/report_canvas_contract.md")
REPORT_DELIVERY_CONTRACT_SOURCE = Path("shared/docs/report_delivery_contract.md")
REPORT_DELIVERY_CONTRACT_TARGET = Path("references/report_delivery_contract.md")
REPORT_VISUAL_AUTHORING_SOURCE = Path("shared/docs/report_visual_authoring.md")
REPORT_VISUAL_AUTHORING_TARGET = Path("references/report_visual_authoring.md")
VISUAL_DECISION_SOURCE = Path("shared/docs/visual_decision_contract.md")
VISUAL_DECISION_TARGET = Path("references/visual_decision_contract.md")
EXECUTION_ITEM_CONTRACT_SOURCE = Path("shared/docs/execution_item_contract.md")
EXECUTION_ITEM_CONTRACT_TARGET = Path("references/execution_item_contract.md")
EXECUTION_ITEM_VIEW_TARGET = Path("references/execution_item_view.md")
EXECUTION_ITEM_SCHEMA_SOURCE = Path("shared/schemas/execution/execution-item.schema.json")
EXECUTION_ITEM_SCHEMA_TARGET = Path("references/execution-item.schema.json")
EXECUTION_CARD_SOURCE_ROOT = Path("shared/contracts/core-execution-items-v1/cards")
EXECUTION_CARD_REFERENCE_RE = re.compile(
    r"references/core-execution-items-v1/cards/[A-Za-z0-9][A-Za-z0-9_.-]*\.md"
)
DELIVERY_SLICE_CONTRACT_SOURCE = Path("shared/docs/delivery_slice_contract.md")
DELIVERY_SLICE_CONTRACT_TARGET = Path("references/delivery_slice_contract.md")
EXECUTION_HANDOFF_INPUT_CONTRACT_SOURCE = Path(
    "shared/docs/execution_handoff_input_contract.md"
)
EXECUTION_HANDOFF_INPUT_CONTRACT_TARGET = Path(
    "references/execution_handoff_input_contract.md"
)
EXECUTION_ASSURANCE_CONTRACT_SOURCE = Path("shared/docs/execution_assurance_contract.md")
EXECUTION_ASSURANCE_CONTRACT_TARGET = Path("references/execution_assurance_contract.md")
BOUNDARY_DECISION_CONTRACT_SOURCE = Path("shared/docs/boundary_decision_contract.md")
BOUNDARY_DECISION_CONTRACT_TARGET = Path("references/boundary_decision_contract.md")
RESEARCH_STAGE_CONTRACT_SOURCE = Path("shared/docs/research_stage_contract.md")
RESEARCH_STAGE_CONTRACT_TARGET = Path("references/research_stage_contract.md")
DESIGN_SHARED_REFERENCE_PROJECTIONS = (
    (Path("shared/docs/design_stage_contract.md"), Path("references/design_stage_contract.md")),
    (Path("shared/docs/design_evidence_contract.md"), Path("references/design_evidence_contract.md")),
    (
        Path("shared/docs/product_family_design_contract.md"),
        Path("references/product_family_design_contract.md"),
    ),
    (
        Path("shared/docs/layout_constraint_contract.md"),
        Path("references/layout_constraint_contract.md"),
    ),
)
TESTING_SHARED_REFERENCE_PROJECTIONS = (
    (
        Path("shared/docs/testing_strategy_contract.md"),
        Path("references/testing_strategy_contract.md"),
    ),
    (
        Path("shared/docs/testing_stage_contract.md"),
        Path("references/testing_stage_contract.md"),
    ),
)
MANAGEMENT_SHARED_REFERENCE_PROJECTIONS = (
    (
        Path("shared/docs/project_context_manifest.md"),
        Path("references/project_context_manifest.md"),
    ),
    (
        Path("shared/docs/memory_mutation_contract.md"),
        Path("references/memory_mutation_contract.md"),
    ),
    (
        Path("shared/docs/knowledge_record_contract.md"),
        Path("references/knowledge_record_contract.md"),
    ),
)
MAINTAINABLE_CODE_PRINCIPLES_SOURCE = Path(
    "shared/docs/maintainable_code_principles.md"
)
MAINTAINABLE_CODE_PRINCIPLES_TARGET = Path(
    "references/maintainable_code_principles.md"
)
IDENTIFIER_READABILITY_PRINCIPLE_SOURCE = Path(
    "shared/docs/identifier_readability_principle.md"
)
IDENTIFIER_READABILITY_PRINCIPLE_TARGET = Path(
    "references/identifier_readability_principle.md"
)
DATABASE_PERSISTENCE_TRANSPARENCY_CONTRACT_SOURCE = Path(
    "shared/docs/database_persistence_transparency_contract.md"
)
DATABASE_PERSISTENCE_TRANSPARENCY_CONTRACT_TARGET = Path(
    "references/database_persistence_transparency_contract.md"
)

# Platform-native trees: every top-level entry under source/platform/<p> is copied verbatim
# into that one target only. AGENTS.md / CLAUDE.md live here as platform-native for Phase 1a;
# factoring them into a shared body + overlay (platform-template) is a Phase 1b refinement.
PLATFORM_CODEX_ROOT = "platform/codex"
PLATFORM_CLAUDE_ROOT = "platform/claude"
PLATFORM_GROK_ROOT = "platform/grok"
PLATFORM_ANTIGRAVITY_ROOT = "platform/antigravity"
REMOVED_CODEX_TARGET_ROOTS = ("research", "tools")
REMOVED_CODEX_TARGET_FILES = (
    "research-routing.md",
)
REMOVED_SHARED_TARGET_ROOTS = ("eval", "skills", "report-canvas")
REMOVED_VERIFIER_BINARIES = (
    "skill-system-verify",
    "skill-system-verify.exe",
    "skill-system-verify-linux-amd64",
)

BINARY_BUILD_MANIFEST = ".build-manifest.json"

# Portable skill bodies use Codex runtime paths as their canonical host spelling. Claude
# packages must project only namespaces that have a Claude-owned equivalent; tool-dependent
# instructions use host-neutral tool names in the canonical skill text instead.
CLAUDE_SKILL_PATH_PROJECTIONS: tuple[tuple[str, str], ...] = (
    (".codex/docs/", ".claude/docs/"),
    (".codex/schemas/", ".claude/schemas/"),
    (".codex/skills/.system", ".claude/skills/.system"),
)

_CACHE_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}

PLUGIN_DISPLAY = {
    "skill-system-core": ("Skill System Core", "Shared planning, management, evidence, and report delivery skills."),
    "skill-system-dev": ("Skill System Dev", "Engineering analysis, implementation, bounded bug repair, code review, behavior discovery, and refactoring skills."),
    "skill-system-design": ("Skill System Design", "Frontend, UI, layout, component, token, and visual validation skills."),
    "skill-system-research": ("Skill System Research", "Explicit Research node execution, scientific synthesis, experiment, analysis, manuscript, and review skills."),
    "skill-system-testing": ("Skill System Testing", "Human-in-loop test decisions, test design, test-only implementation, and evidence specialists."),
}


def _is_junk(name: str) -> bool:
    return (
        name == ".DS_Store"
        or name.startswith("._")
        or name in _CACHE_DIRS
        or name == "Thumbs.db"
        or name.endswith((".pyc", ".pyo"))
    )


def _ignore(_dir: str, names: list[str]) -> set[str]:
    return {n for n in names if _is_junk(n)}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tree_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and not any(_is_junk(part) for part in path.relative_to(root).parts)
    )


def _go_command_build_digest(module: Path, command: str) -> str:
    digest = hashlib.sha256()
    for path in _tree_files(module):
        if path.name.endswith("_test.go"):
            continue
        rel = path.relative_to(module).as_posix()
        if rel not in {"go.mod", "go.sum"}:
            if rel.startswith("cmd/") and not rel.startswith(f"cmd/{command}/"):
                continue
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(_sha256(path).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def _copy(src: Path, dst: Path) -> None:
    if src.is_dir():
        if dst.exists():
            shutil.rmtree(dst)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, dst, ignore=_ignore)
    elif src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
    else:
        raise SystemExit(f"missing source path: {src}")


def _top_level_key(line: str) -> str | None:
    if not line.strip() or line.startswith((" ", "\t")) or ":" not in line:
        return None
    return line.split(":", 1)[0].strip()


def _filter_policy_block(block: list[str]) -> list[str]:
    kept = [block[0]]
    for line in block[1:]:
        stripped = line.lstrip()
        if stripped.startswith("allow_implicit_invocation:"):
            kept.append(line)
    return kept if len(kept) > 1 else []


def _sanitize_plugin_agent_manifest(path: Path) -> None:
    """Project bundle-only agent metadata to the stricter Codex plugin schema."""
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if _top_level_key(line) is not None:
            if current:
                blocks.append(current)
            current = [line]
        elif current:
            current.append(line)
    if current:
        blocks.append(current)

    output: list[str] = []
    for block in blocks:
        key = _top_level_key(block[0])
        if key in {"interface", "dependencies"}:
            output.extend(block)
        elif key == "policy":
            output.extend(_filter_policy_block(block))

    while output and not output[-1].strip():
        output.pop()
    path.write_text("\n".join(output) + "\n", encoding="utf-8")


def _allow_implicit_invocation(skill_dir: Path) -> bool:
    """Read the one portable invocation bit from canonical Codex agent metadata."""
    agent_manifest = skill_dir / "agents" / "openai.yaml"
    if not agent_manifest.is_file():
        raise SystemExit(f"missing skill agent manifest: {agent_manifest}")
    matches: list[bool] = []
    for line in agent_manifest.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("allow_implicit_invocation:"):
            continue
        value = stripped.split(":", 1)[1].strip().lower()
        if value not in {"true", "false"}:
            raise SystemExit(f"invalid allow_implicit_invocation in {agent_manifest}: {value!r}")
        matches.append(value == "true")
    if len(matches) != 1:
        raise SystemExit(
            f"expected exactly one allow_implicit_invocation in {agent_manifest}, found {len(matches)}"
        )
    return matches[0]


def _project_claude_invocation(skill_dir: Path, target_dir: Path) -> None:
    """Project portable skill paths and invocation metadata into Claude's SKILL.md."""
    skill_md = target_dir / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    for source_path, claude_path in CLAUDE_SKILL_PATH_PROJECTIONS:
        text = text.replace(source_path, claude_path)
    if ".codex/" in text:
        raise SystemExit(f"unprojected Codex runtime path in Claude skill: {skill_md}")
    if "disable-model-invocation:" in text:
        raise SystemExit(f"canonical skill must not contain Claude invocation metadata: {skill_md}")
    if _allow_implicit_invocation(skill_dir):
        skill_md.write_text(text, encoding="utf-8")
        return
    if not text.startswith("---\n"):
        raise SystemExit(f"skill frontmatter must start on the first line: {skill_md}")
    closing = text.find("\n---\n", 4)
    if closing < 0:
        raise SystemExit(f"skill frontmatter is not closed: {skill_md}")
    text = text[:closing] + "\ndisable-model-invocation: true" + text[closing:]
    skill_md.write_text(text, encoding="utf-8")


def _copy_plugin_skill(src: Path, dst: Path, *, claude: bool = False) -> None:
    _copy(src, dst)
    agent_manifest = dst / "agents" / "openai.yaml"
    if agent_manifest.is_file():
        _sanitize_plugin_agent_manifest(agent_manifest)
    if claude:
        _project_claude_invocation(src, dst)


def _is_report_skill(skill_dir: Path) -> bool:
    return skill_dir.name.startswith("report-") and (skill_dir / "SKILL.md").is_file()


def _attach_report_canvas_payload(source: Path, skill_dir: Path) -> None:
    """Project small report contracts into one report skill; renderer is plugin-shared."""
    if not _is_report_skill(skill_dir):
        return
    skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    if "references/report_canvas_contract.md" not in skill_text:
        raise SystemExit(
            f"report skill does not reference its local Canvas contract: {skill_dir}"
        )
    if "references/report_delivery_contract.md" not in skill_text:
        raise SystemExit(
            f"report skill does not reference its local delivery contract: {skill_dir}"
        )
    _copy(
        source / REPORT_DELIVERY_CONTRACT_SOURCE,
        skill_dir / REPORT_DELIVERY_CONTRACT_TARGET,
    )
    _copy(
        source / REPORT_CANVAS_CONTRACT_SOURCE,
        skill_dir / REPORT_CANVAS_REFERENCE_TARGET,
    )
    _copy(
        source / REPORT_VISUAL_AUTHORING_SOURCE,
        skill_dir / REPORT_VISUAL_AUTHORING_TARGET,
    )


def _wants_visual_decision(skill_dir: Path) -> bool:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return False
    if _is_report_skill(skill_dir):
        return True
    return "references/visual_decision_contract.md" in skill_md.read_text(
        encoding="utf-8"
    )


def _attach_visual_decision_payload(source: Path, skill_dir: Path) -> None:
    """Project the shared visual-decision rule into report and opted-in design skills."""
    if not _wants_visual_decision(skill_dir):
        return
    _copy(source / VISUAL_DECISION_SOURCE, skill_dir / VISUAL_DECISION_TARGET)


def _wants_execution_item_contract(skill_dir: Path) -> bool:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return False
    text = skill_md.read_text(encoding="utf-8")
    return (
        "references/execution_item_contract.md" in text
        or "references/execution_item_view.md" in text
        or bool(EXECUTION_CARD_REFERENCE_RE.search(text))
    )


def _markdown_sections(text: str, level: int) -> dict[str, str]:
    marker = "#" * level + " "
    sections: dict[str, str] = {}
    title: str | None = None
    lines: list[str] = []
    for line in text.splitlines():
        if line.startswith(marker):
            if title is not None:
                sections[title] = "\n".join(lines).strip()
            title = line[len(marker) :].strip()
            lines = [line]
        elif title is not None:
            lines.append(line)
    if title is not None:
        sections[title] = "\n".join(lines).strip()
    return sections


def _render_execution_item_view(source: Path, skill_dir: Path, skill_text: str) -> None:
    """Generate one role view from the canonical contract and declared Core Cards."""
    contract_text = (source / EXECUTION_ITEM_CONTRACT_SOURCE).read_text(encoding="utf-8")
    contract_sections = _markdown_sections(contract_text, 2)
    skill_sections = _markdown_sections(skill_text, 2)
    required_sections = (
        "Authority",
        "Common Envelope",
        "Core Markdown Cards",
        "Item Kinds",
        "Worker-Done Body",
    )
    missing_sections = [name for name in required_sections if name not in contract_sections]
    if missing_sections or "Core Cards" not in skill_sections:
        raise SystemExit(
            f"cannot project execution-item role view for {skill_dir}: "
            f"missing contract sections {missing_sections} or skill Core Cards"
        )

    selected_kinds = {
        Path(reference).stem
        for reference in EXECUTION_CARD_REFERENCE_RE.findall(skill_sections["Core Cards"])
    }
    if not selected_kinds:
        raise SystemExit(f"execution-item role view for {skill_dir} selects no Core Cards")
    item_sections = _markdown_sections(contract_sections["Item Kinds"], 3)
    selected_sections = [
        section
        for title, section in item_sections.items()
        if title.strip("`") in selected_kinds
    ]
    projected_kinds = {
        title.strip("`") for title in item_sections if title.strip("`") in selected_kinds
    }
    if projected_kinds != selected_kinds:
        raise SystemExit(
            f"execution-item role view for {skill_dir} has no canonical item section for "
            f"{sorted(selected_kinds - projected_kinds)}"
        )

    preamble = contract_text.split("\n## ", 1)[0].splitlines()
    canonical_metadata = "\n".join(preamble[2:]).strip()
    role_cards = skill_sections["Core Cards"].replace("## Core Cards", "## Role Cards", 1)
    parts = [
        "# Core Execution Item Role View",
        (
            f"Generated from the canonical Core execution-item contract for `{skill_dir.name}`. "
            "Do not edit this projection."
        ),
        canonical_metadata,
        contract_sections["Authority"],
        contract_sections["Common Envelope"],
        contract_sections["Core Markdown Cards"],
        role_cards,
        "## Selected Item Kinds\n\n" + "\n\n".join(selected_sections),
        contract_sections["Worker-Done Body"],
    ]
    target = skill_dir / EXECUTION_ITEM_VIEW_TARGET
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n\n".join(part.strip() for part in parts if part.strip()) + "\n",
        encoding="utf-8",
    )


def _attach_execution_item_contract(source: Path, skill_dir: Path) -> None:
    """Project the Core execution-item contract or a generated role view."""
    if not _wants_execution_item_contract(skill_dir):
        return
    skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    wants_view = "references/execution_item_view.md" in skill_text
    wants_full_contract = "references/execution_item_contract.md" in skill_text or not wants_view
    if wants_full_contract:
        _copy(
            source / EXECUTION_ITEM_CONTRACT_SOURCE,
            skill_dir / EXECUTION_ITEM_CONTRACT_TARGET,
        )
    if wants_view:
        _render_execution_item_view(source, skill_dir, skill_text)
    _copy(
        source / EXECUTION_ITEM_SCHEMA_SOURCE,
        skill_dir / EXECUTION_ITEM_SCHEMA_TARGET,
    )
    for target_text in sorted(set(EXECUTION_CARD_REFERENCE_RE.findall(skill_text))):
        target = Path(target_text)
        canonical = source / EXECUTION_CARD_SOURCE_ROOT / target.name
        if not canonical.is_file():
            raise SystemExit(
                f"missing Core execution card {canonical} referenced by {skill_dir / 'SKILL.md'}"
            )
        _copy(canonical, skill_dir / target)


def _wants_delivery_slice_contract(skill_dir: Path) -> bool:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return False
    return "references/delivery_slice_contract.md" in skill_md.read_text(encoding="utf-8")


def _attach_delivery_slice_contract(source: Path, skill_dir: Path) -> None:
    """Project the shared delivery-slice contract into each opted-in skill package."""
    if not _wants_delivery_slice_contract(skill_dir):
        return
    _copy(
        source / DELIVERY_SLICE_CONTRACT_SOURCE,
        skill_dir / DELIVERY_SLICE_CONTRACT_TARGET,
    )


def _wants_execution_handoff_input_contract(skill_dir: Path) -> bool:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return False
    return "references/execution_handoff_input_contract.md" in skill_md.read_text(
        encoding="utf-8"
    )


def _attach_execution_handoff_input_contract(source: Path, skill_dir: Path) -> None:
    """Project the shared Planning-input contract into each opted-in skill package."""
    if not _wants_execution_handoff_input_contract(skill_dir):
        return
    _copy(
        source / EXECUTION_HANDOFF_INPUT_CONTRACT_SOURCE,
        skill_dir / EXECUTION_HANDOFF_INPUT_CONTRACT_TARGET,
    )


def _wants_execution_assurance_contract(skill_dir: Path) -> bool:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return False
    return "references/execution_assurance_contract.md" in skill_md.read_text(
        encoding="utf-8"
    )


def _attach_execution_assurance_contract(source: Path, skill_dir: Path) -> None:
    """Project the shared execution-assurance contract into each opted-in skill package."""
    if not _wants_execution_assurance_contract(skill_dir):
        return
    _copy(
        source / EXECUTION_ASSURANCE_CONTRACT_SOURCE,
        skill_dir / EXECUTION_ASSURANCE_CONTRACT_TARGET,
    )


def _wants_boundary_decision_contract(skill_dir: Path) -> bool:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return False
    return "references/boundary_decision_contract.md" in skill_md.read_text(
        encoding="utf-8"
    )


def _attach_boundary_decision_contract(source: Path, skill_dir: Path) -> None:
    """Project the shared boundary-decision rule into each opted-in skill package."""
    if not _wants_boundary_decision_contract(skill_dir):
        return
    _copy(
        source / BOUNDARY_DECISION_CONTRACT_SOURCE,
        skill_dir / BOUNDARY_DECISION_CONTRACT_TARGET,
    )


def _wants_research_stage_contract(skill_dir: Path) -> bool:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return False
    return "references/research_stage_contract.md" in skill_md.read_text(
        encoding="utf-8"
    )


def _attach_research_stage_contract(source: Path, skill_dir: Path) -> None:
    """Project the shared Research stage rule into each opted-in skill package."""
    if not _wants_research_stage_contract(skill_dir):
        return
    _copy(
        source / RESEARCH_STAGE_CONTRACT_SOURCE,
        skill_dir / RESEARCH_STAGE_CONTRACT_TARGET,
    )


def _attach_design_shared_references(source: Path, skill_dir: Path) -> None:
    """Project only the shared Design references explicitly named by a skill."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return
    text = skill_md.read_text(encoding="utf-8")
    for source_path, target_path in DESIGN_SHARED_REFERENCE_PROJECTIONS:
        if target_path.as_posix() in text:
            _copy(source / source_path, skill_dir / target_path)


def _attach_testing_shared_references(source: Path, skill_dir: Path) -> None:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return
    text = skill_md.read_text(encoding="utf-8")
    for source_path, target_path in TESTING_SHARED_REFERENCE_PROJECTIONS:
        if target_path.as_posix() in text:
            _copy(source / source_path, skill_dir / target_path)


def _attach_management_shared_references(source: Path, skill_dir: Path) -> None:
    """Project only the shared Management references explicitly named by a skill."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return
    text = skill_md.read_text(encoding="utf-8")
    for source_path, target_path in MANAGEMENT_SHARED_REFERENCE_PROJECTIONS:
        if target_path.as_posix() in text:
            _copy(source / source_path, skill_dir / target_path)


def _wants_maintainable_code_principles(skill_dir: Path) -> bool:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return False
    return "references/maintainable_code_principles.md" in skill_md.read_text(
        encoding="utf-8"
    )


def _attach_maintainable_code_principles(source: Path, skill_dir: Path) -> None:
    """Project the maintainable-code principles into opted-in skill packages."""
    if not _wants_maintainable_code_principles(skill_dir):
        return
    _copy(
        source / MAINTAINABLE_CODE_PRINCIPLES_SOURCE,
        skill_dir / MAINTAINABLE_CODE_PRINCIPLES_TARGET,
    )


def _wants_identifier_readability_principle(skill_dir: Path) -> bool:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return False
    return "references/identifier_readability_principle.md" in skill_md.read_text(
        encoding="utf-8"
    )


def _attach_identifier_readability_principle(
    source: Path, skill_dir: Path
) -> None:
    """Project the identifier-readability principle into opted-in skill packages."""
    if not _wants_identifier_readability_principle(skill_dir):
        return
    _copy(
        source / IDENTIFIER_READABILITY_PRINCIPLE_SOURCE,
        skill_dir / IDENTIFIER_READABILITY_PRINCIPLE_TARGET,
    )


def _wants_database_persistence_transparency_contract(skill_dir: Path) -> bool:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return False
    return "references/database_persistence_transparency_contract.md" in skill_md.read_text(
        encoding="utf-8"
    )


def _attach_database_persistence_transparency_contract(
    source: Path, skill_dir: Path
) -> None:
    """Project the database-persistence contract into opted-in skill packages."""
    if not _wants_database_persistence_transparency_contract(skill_dir):
        return
    _copy(
        source / DATABASE_PERSISTENCE_TRANSPARENCY_CONTRACT_SOURCE,
        skill_dir / DATABASE_PERSISTENCE_TRANSPARENCY_CONTRACT_TARGET,
    )


def _attach_plugin_skill_payloads(source: Path, skill_dir: Path) -> None:
    """Project every shared payload selected by one generated skill package."""
    _attach_report_canvas_payload(source, skill_dir)
    _attach_visual_decision_payload(source, skill_dir)
    _attach_execution_item_contract(source, skill_dir)
    _attach_delivery_slice_contract(source, skill_dir)
    _attach_execution_handoff_input_contract(source, skill_dir)
    _attach_execution_assurance_contract(source, skill_dir)
    _attach_boundary_decision_contract(source, skill_dir)
    _attach_research_stage_contract(source, skill_dir)
    _attach_design_shared_references(source, skill_dir)
    _attach_testing_shared_references(source, skill_dir)
    _attach_management_shared_references(source, skill_dir)
    _attach_maintainable_code_principles(source, skill_dir)
    _attach_identifier_readability_principle(source, skill_dir)
    _attach_database_persistence_transparency_contract(source, skill_dir)


def _merge_copy(src: Path, dst: Path) -> None:
    """Overlay src onto dst, copying files without removing pre-existing target content.

    Used for platform overlay so a platform tree can supplement a shared tree
    (for example, Codex-only tool metadata on top of shared schema definitions).
    """
    if src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
    elif src.is_dir():
        for child in src.rglob("*"):
            if not child.is_file():
                continue
            rel = child.relative_to(src)
            if any(_is_junk(part) for part in rel.parts):
                continue
            out = dst / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(child, out)
    else:
        raise SystemExit(f"missing source path: {src}")


def _copy_platform(platform_root: Path, target: Path, written: list[str]) -> None:
    if not platform_root.is_dir():
        raise SystemExit(f"missing platform root: {platform_root}")
    for child in sorted(platform_root.iterdir()):
        if _is_junk(child.name):
            continue
        if child.name in NEUTRAL_TARGET_ROOTS:
            _merge_copy(child, target / child.name)
        else:
            _copy(child, target / child.name)
        written.append((target / child.name).as_posix())


def _copy_neutral(source: Path, target: Path, written: list[str]) -> None:
    for src_rel, dst_rel in NEUTRAL_VERBATIM:
        _copy(source / src_rel, target / dst_rel)
        written.append((target / dst_rel).as_posix())


def _go_executable() -> str:
    configured = os.environ.get("SKILL_SYSTEM_GO", "").strip()
    if configured:
        path = Path(configured).expanduser()
        if not path.is_file():
            raise SystemExit(f"SKILL_SYSTEM_GO is not a file: {path}")
        return str(path)
    discovered = shutil.which("go")
    if discovered:
        return discovered
    raise SystemExit("Go is required to generate the Codex runtime; set SKILL_SYSTEM_GO or install Go")


def _load_binary_build_manifest(output_root: Path) -> dict:
    path = output_root / BINARY_BUILD_MANIFEST
    if not path.is_file():
        return {"manifest_version": 1, "groups": {}}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"manifest_version": 1, "groups": {}}
    if value.get("manifest_version") != 1 or not isinstance(value.get("groups"), dict):
        return {"manifest_version": 1, "groups": {}}
    return value


def _cached_binary_group(
    output_root: Path,
    group: str,
    build_key: str,
    filenames: list[str],
    written: list[str],
) -> bool:
    manifest = _load_binary_build_manifest(output_root)
    entry = manifest["groups"].get(group)
    if not isinstance(entry, dict) or entry.get("build_key") != build_key:
        return False
    outputs = entry.get("outputs")
    if not isinstance(outputs, dict):
        return False
    for filename in filenames:
        path = output_root / filename
        if not path.is_file() or outputs.get(filename) != _sha256(path):
            return False
    written.extend((output_root / filename).as_posix() for filename in filenames)
    return True


def _record_binary_group(output_root: Path, group: str, build_key: str, filenames: list[str]) -> None:
    manifest = _load_binary_build_manifest(output_root)
    manifest["groups"][group] = {
        "build_key": build_key,
        "outputs": {filename: _sha256(output_root / filename) for filename in filenames},
    }
    (output_root / BINARY_BUILD_MANIFEST).write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _remove_path(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def _prune_retired_evaluation_payload(runtime: Path) -> None:
    for root_name in REMOVED_SHARED_TARGET_ROOTS:
        _remove_path(runtime / root_name)
    _remove_path(runtime / ".generated-manifest.json")

    output_root = runtime / "bin"
    for filename in REMOVED_VERIFIER_BINARIES:
        _remove_path(output_root / filename)
    manifest_path = output_root / BINARY_BUILD_MANIFEST
    if manifest_path.is_file():
        manifest = _load_binary_build_manifest(output_root)
        manifest["groups"].pop("go:skill-system-verify", None)
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


def _swiftc_executable() -> str:
    configured = os.environ.get("SKILL_SYSTEM_SWIFTC", "").strip()
    if configured:
        path = Path(configured).expanduser()
        if not path.is_file():
            raise SystemExit(f"SKILL_SYSTEM_SWIFTC is not a file: {path}")
        return str(path)
    discovered = shutil.which("swiftc")
    if discovered:
        return discovered
    raise SystemExit("swiftc is required to build the macOS notification overlay; set SKILL_SYSTEM_SWIFTC")


def _build_go_dispatchers(
    source: Path,
    module_name: str,
    output_root: Path,
    command: str,
    targets: tuple[tuple[str, str, str], ...],
    written: list[str],
) -> None:
    module = source / "runtime" / "go" / module_name
    if not (module / "go.mod").is_file():
        raise SystemExit(f"missing Go harness module: {module}")
    version = str(_load_manifest(source / "plugins" / "core.yaml")["version"])
    filenames = [filename for _, _, filename in targets]
    key_source = json.dumps(
        {
            "module_digest": _go_command_build_digest(module, command),
            "command": command,
            "targets": targets,
            "version": version,
        },
        sort_keys=True,
    ).encode("utf-8")
    build_key = hashlib.sha256(key_source).hexdigest()
    if _cached_binary_group(output_root, "go:" + command, build_key, filenames, written):
        return
    go = _go_executable()
    for goos, goarch, filename in targets:
        output = output_root / filename
        env = os.environ.copy()
        env.update({"CGO_ENABLED": "0", "GOOS": goos, "GOARCH": goarch})
        subprocess.run(
            [
                go,
                "build",
                "-buildvcs=false",
                "-trimpath",
                "-ldflags",
                f"-s -w -X main.version={version}",
                "-o",
                str(output.resolve()),
                f"./cmd/{command}",
            ],
            cwd=module,
            env=env,
            check=True,
        )
        written.append(output.as_posix())
    _record_binary_group(output_root, "go:" + command, build_key, filenames)


def _build_notification_overlay(source: Path, output_root: Path, written: list[str]) -> None:
    overlay_source = source / "runtime" / "swift" / "notification_overlay.swift"
    if not overlay_source.is_file():
        raise SystemExit(f"missing Swift notification overlay source: {overlay_source}")
    overlay = output_root / "skill-system-notify-overlay"
    build_key = hashlib.sha256(
        ("swift:arm64-apple-macosx13.0:" + _sha256(overlay_source)).encode("utf-8")
    ).hexdigest()
    if _cached_binary_group(
        output_root,
        "swift:notification-overlay",
        build_key,
        [overlay.name],
        written,
    ):
        return
    with tempfile.TemporaryDirectory(prefix="skill-system-swift-cache-") as module_cache:
        subprocess.run(
            [
                _swiftc_executable(),
                "-O",
                "-target",
                "arm64-apple-macosx13.0",
                "-module-cache-path",
                module_cache,
                str(overlay_source.resolve()),
                "-o",
                str(overlay.resolve()),
            ],
            check=True,
        )
    overlay.chmod(0o755)
    written.append(overlay.as_posix())
    _record_binary_group(
        output_root,
        "swift:notification-overlay",
        build_key,
        [overlay.name],
    )


def _build_codex_harness(source: Path, codex: Path, written: list[str]) -> None:
    """Build the Codex Go dispatchers and packaged macOS notification overlay."""
    output_root = codex / "bin"
    output_root.mkdir(parents=True, exist_ok=True)
    _build_go_dispatchers(
        source,
        "codex",
        output_root,
        "skill-system-harness",
        (
            ("darwin", "arm64", "skill-system-harness"),
            ("windows", "amd64", "skill-system-harness.exe"),
        ),
        written,
    )
    _build_notification_overlay(source, output_root, written)


def _build_claude_harness(source: Path, claude: Path, written: list[str]) -> None:
    """Build Claude-native dispatchers plus the packaged macOS notification overlay."""
    output_root = claude / "bin"
    output_root.mkdir(parents=True, exist_ok=True)
    _build_go_dispatchers(
        source,
        "claude",
        output_root,
        "skill-system-claude-harness",
        (
            ("darwin", "arm64", "skill-system-claude-harness"),
            ("windows", "amd64", "skill-system-claude-harness.exe"),
            ("linux", "amd64", "skill-system-claude-harness-linux-amd64"),
        ),
        written,
    )
    _build_notification_overlay(source, output_root, written)


def _build_grok_harness(source: Path, grok: Path, written: list[str]) -> None:
    """Build the Grok-owned common Go harness; Orca retains lifecycle ownership."""
    output_root = grok / "bin"
    output_root.mkdir(parents=True, exist_ok=True)
    _build_go_dispatchers(
        source,
        "grok",
        output_root,
        "skill-system-grok-harness",
        (
            ("darwin", "arm64", "skill-system-grok-harness"),
            ("windows", "amd64", "skill-system-grok-harness.exe"),
            ("linux", "amd64", "skill-system-grok-harness-linux-amd64"),
        ),
        written,
    )
    _build_notification_overlay(source, output_root, written)


def _build_antigravity_harness(source: Path, antigravity: Path, written: list[str]) -> None:
    """Build the Antigravity-owned common Go harness; Orca retains lifecycle ownership."""
    output_root = antigravity / "bin"
    output_root.mkdir(parents=True, exist_ok=True)
    _build_go_dispatchers(
        source,
        "antigravity",
        output_root,
        "skill-system-antigravity-harness",
        (
            ("darwin", "arm64", "skill-system-antigravity-harness"),
            ("windows", "amd64", "skill-system-antigravity-harness.exe"),
            ("linux", "amd64", "skill-system-antigravity-harness-linux-amd64"),
        ),
        written,
    )
    _build_notification_overlay(source, output_root, written)


def generate_codex_runtime(source: Path, codex: Path) -> list[str]:
    written: list[str] = []
    _copy_neutral(source, codex, written)
    _copy_platform(source / PLATFORM_CODEX_ROOT, codex, written)
    # Retired Codex-only Research/Python-tool roots have no current owner. Remove them so an
    # upgrade cannot retain historical validators, ledgers, or lifecycle payload.
    for root_name in REMOVED_CODEX_TARGET_ROOTS:
        stale = codex / root_name
        if stale.is_dir():
            shutil.rmtree(stale)
        elif stale.exists():
            stale.unlink()
    for file_name in REMOVED_CODEX_TARGET_FILES:
        stale = codex / file_name
        if stale.is_dir():
            shutil.rmtree(stale)
        elif stale.exists():
            stale.unlink()
    _build_codex_harness(source, codex, written)
    _prune_retired_evaluation_payload(codex)
    return written


def generate_claude_runtime(source: Path, claude: Path) -> list[str]:
    written: list[str] = []
    _copy_neutral(source, claude, written)
    _copy_platform(source / PLATFORM_CLAUDE_ROOT, claude, written)
    # 9.3.4 removes the Python-only Claude runtime. Prune the now-absent
    # platform-owned root so stale adapters cannot survive regeneration.
    if not (source / PLATFORM_CLAUDE_ROOT / "tools").exists() and (claude / "tools").exists():
        shutil.rmtree(claude / "tools")
    _build_claude_harness(source, claude, written)
    _prune_retired_evaluation_payload(claude)
    return written


def generate_orca_runtime(source: Path, platform_root: str, target: Path) -> list[str]:
    """Generate a common Go companion while Orca retains provider lifecycle ownership."""
    written: list[str] = []
    _copy_neutral(source, target, written)
    _copy_platform(source / platform_root, target, written)
    _prune_retired_evaluation_payload(target)
    return written


def generate_grok_runtime(source: Path, grok: Path) -> list[str]:
    written = generate_orca_runtime(source, PLATFORM_GROK_ROOT, grok)
    _build_grok_harness(source, grok, written)
    return written


def generate_antigravity_runtime(source: Path, antigravity: Path) -> list[str]:
    written = generate_orca_runtime(source, PLATFORM_ANTIGRAVITY_ROOT, antigravity)
    _build_antigravity_harness(source, antigravity, written)
    return written


def generate_runtime(
    source: Path,
    codex: Path,
    claude: Path,
    grok: Path,
    antigravity: Path,
) -> list[str]:
    """Generate all provider runtime companions."""
    return (
        generate_codex_runtime(source, codex)
        + generate_claude_runtime(source, claude)
        + generate_grok_runtime(source, grok)
        + generate_antigravity_runtime(source, antigravity)
    )


def _load_manifest(path: Path) -> dict:
    """Minimal YAML manifest reader (name/version/description/skills) without a yaml dep."""
    spec: dict = {"skills": []}
    in_skills = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if in_skills and raw.lstrip().startswith("- "):
            spec["skills"].append(raw.split("- ", 1)[1].strip())
            continue
        in_skills = False
        if raw.startswith("skills:"):
            in_skills = True
        elif ":" in raw:
            key, val = raw.split(":", 1)
            spec[key.strip()] = val.strip().strip('"').strip("'")
    return spec


def generate_plugins(source: Path, plugins_root: Path) -> list[str]:
    written: list[str] = []
    manifests = sorted((source / "plugins").glob("*.yaml"))
    if not manifests:
        raise SystemExit(f"no plugin manifests under {source / 'plugins'}")
    manifest_names = {_load_manifest(path)["name"] for path in manifests}
    for path in plugins_root.glob("skill-system-*"):
        if path.is_dir() and path.name not in manifest_names:
            shutil.rmtree(path)
    src_skills = {p.name for p in (source / "skills").iterdir() if p.is_dir()}
    seen: dict[str, str] = {}
    marketplace_plugins: list[dict] = []
    claude_packages_root = plugins_root / "claude"
    if claude_packages_root.exists():
        shutil.rmtree(claude_packages_root)
    for mf in manifests:
        spec = _load_manifest(mf)
        name = spec["name"]
        codex_pkg = plugins_root / name
        claude_pkg = claude_packages_root / name
        if codex_pkg.exists():
            shutil.rmtree(codex_pkg)
        display_name, short_description = PLUGIN_DISPLAY.get(
            name,
            (name.replace("-", " ").title(), spec["description"]),
        )
        manifest = {
            "name": name,
            "version": str(spec["version"]),
            "description": spec["description"],
            "author": {"name": "Skill System Maintainers"},
            "license": "MIT",
            "keywords": ["skill-system", "codex", name.removeprefix("skill-system-")],
            "skills": "./skills/",
            "interface": {
                "displayName": display_name,
                "shortDescription": short_description,
                "longDescription": spec["description"],
                "developerName": "Skill System Maintainers",
                "category": "Developer Tools",
                "capabilities": ["Interactive", "Read", "Write"],
                "defaultPrompt": [f"Use {display_name} skills for this task."],
                "brandColor": "#2563EB",
                "screenshots": [],
            },
        }
        plugin_json = codex_pkg / ".codex-plugin" / "plugin.json"
        plugin_json.parent.mkdir(parents=True, exist_ok=True)
        plugin_json.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        written.append(plugin_json.as_posix())
        # Claude Code plugin manifest (accurate Claude schema): no Codex `interface`/`policy`/
        # `capabilities` blocks; components are directory-discovered, skills declared by path.
        claude_manifest = {
            "name": name,
            "version": str(spec["version"]),
            "description": spec["description"],
            "author": {"name": "Skill System Maintainers"},
            "license": "MIT",
            "keywords": ["skill-system", "claude", name.removeprefix("skill-system-")],
            "skills": "./skills/",
        }
        claude_plugin_json = claude_pkg / ".claude-plugin" / "plugin.json"
        claude_plugin_json.parent.mkdir(parents=True, exist_ok=True)
        claude_plugin_json.write_text(json.dumps(claude_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        written.append(claude_plugin_json.as_posix())
        # The Claude-projected package is also the portable Grok/Antigravity package. Grok reads
        # Claude plugins natively; Antigravity requires this minimal root marker and discovers the
        # same skills/ tree. Keeping one package avoids two more generated copies of every skill.
        portable_manifest = {
            "name": name,
            "description": spec["description"],
        }
        portable_plugin_json = claude_pkg / "plugin.json"
        portable_plugin_json.write_text(
            json.dumps(portable_manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        written.append(portable_plugin_json.as_posix())
        # Catalog entry for the Claude repo-local marketplace (source is a path relative to the
        # marketplace root = the plugins/ dir that hosts .claude-plugin/marketplace.json).
        marketplace_plugins.append(
            {
                "name": name,
                "source": f"./claude/{name}",
                "description": spec["description"],
                "version": str(spec["version"]),
                "category": "Developer Tools",
            }
        )
        for sid in spec["skills"]:
            if sid not in src_skills:
                raise SystemExit(f"plugin {name}: unknown skill '{sid}' (not in source/skills)")
            if sid in seen:
                raise SystemExit(f"skill '{sid}' assigned to both {seen[sid]} and {name}")
            seen[sid] = name
            _copy_plugin_skill(source / "skills" / sid, codex_pkg / "skills" / sid)
            _attach_plugin_skill_payloads(source, codex_pkg / "skills" / sid)
            written.append((codex_pkg / "skills" / sid).as_posix())
            _copy_plugin_skill(source / "skills" / sid, claude_pkg / "skills" / sid, claude=True)
            _attach_plugin_skill_payloads(source, claude_pkg / "skills" / sid)
            written.append((claude_pkg / "skills" / sid).as_posix())
        if any(sid.startswith("report-") for sid in spec["skills"]):
            _copy(
                source / REPORT_CANVAS_SOURCE,
                codex_pkg / REPORT_CANVAS_PLUGIN_TARGET,
            )
            _copy(
                source / REPORT_CANVAS_SOURCE,
                claude_pkg / REPORT_CANVAS_PLUGIN_TARGET,
            )
            written.append((codex_pkg / REPORT_CANVAS_PLUGIN_TARGET).as_posix())
            written.append((claude_pkg / REPORT_CANVAS_PLUGIN_TARGET).as_posix())
    uncovered = src_skills - seen.keys()
    if uncovered:
        raise SystemExit(f"plugin coverage gap: {len(uncovered)} skills in no plugin: {sorted(uncovered)}")
    # Claude repo-local marketplace catalog (accurate Claude marketplace.json schema): required
    # `name` + `owner`, plugins listed with relative-path `source`. Register with
    # `/plugin marketplace add <repo>/plugins`; install `<name>@skill-system-local`.
    marketplace = {
        "name": "skill-system-local",
        "owner": {"name": "Skill System Maintainers"},
        "description": "Skill System installation-profile packages (local marketplace).",
        "plugins": marketplace_plugins,
    }
    marketplace_json = plugins_root / ".claude-plugin" / "marketplace.json"
    marketplace_json.parent.mkdir(parents=True, exist_ok=True)
    marketplace_json.write_text(json.dumps(marketplace, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    written.append(marketplace_json.as_posix())
    _remove_path(plugins_root / ".generated-manifest.json")
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target",
        choices=[
            "runtime",
            "runtime-codex",
            "runtime-claude",
            "runtime-grok",
            "runtime-antigravity",
            "plugins",
        ],
        required=True,
    )
    parser.add_argument("--source", default="source")
    parser.add_argument("--codex", default=".codex")
    parser.add_argument("--claude", default=".claude")
    parser.add_argument("--grok", default=".grok")
    parser.add_argument("--antigravity", default=".antigravity")
    parser.add_argument("--plugins", default="plugins")
    args = parser.parse_args()

    if args.target == "runtime":
        written = generate_runtime(
            Path(args.source),
            Path(args.codex),
            Path(args.claude),
            Path(args.grok),
            Path(args.antigravity),
        )
    elif args.target == "runtime-codex":
        written = generate_codex_runtime(Path(args.source), Path(args.codex))
    elif args.target == "runtime-claude":
        written = generate_claude_runtime(Path(args.source), Path(args.claude))
    elif args.target == "runtime-grok":
        written = generate_grok_runtime(Path(args.source), Path(args.grok))
    elif args.target == "runtime-antigravity":
        written = generate_antigravity_runtime(Path(args.source), Path(args.antigravity))
    else:
        written = generate_plugins(Path(args.source), Path(args.plugins))
    for path in written:
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
