#!/usr/bin/env python3
"""Generate provider runtimes and plugins from canonical source/.

Portable skills and data contracts are shared. Each skill-local Routing Card owns neutral routing
semantics and an explicit Resource Closure; generated registries and package resources are one-way
projections of those declarations. Harness entry files, host routing overlays, hooks, permissions,
and platform tools remain owned by source/platform/<provider>. ``runtime`` generates all declared
runtime companions in one command.

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
from pathlib import Path, PurePosixPath

DISTRIBUTION_METADATA_SOURCE = Path("distribution.json")

# (source_rel, target_rel) copied unchanged into either requested target.
NEUTRAL_VERBATIM: list[tuple[str, str]] = [
    ("shared/docs", "docs"),
    ("shared/schemas", "schemas"),  # Phase 1b: schema definitions are platform-neutral data contracts
]
NEUTRAL_TARGET_ROOTS = {target_rel.split("/", 1)[0] for _, target_rel in NEUTRAL_VERBATIM}
EXECUTION_ITEM_CONTRACT_SOURCE = Path("shared/docs/execution_item_contract.md")
EXECUTION_ITEM_VIEW_TARGET = Path("references/execution_item_view.md")
EXECUTION_CARD_REFERENCE_RE = re.compile(
    r"references/core-execution-items-v1/cards/[A-Za-z0-9][A-Za-z0-9_.-]*\.md"
)

ROUTING_CARD_HEADING = "## Routing Card"
RESOURCE_CLOSURE_HEADING = "### Resource Closure"
ROUTING_FIELDS = (
    "role",
    "family",
    "intent_signature",
    "use_when",
    "do_not_use_when",
    "expected_inputs",
    "expected_outputs",
    "context_targets",
    "risk_profile",
    "entry_scene",
)
ROUTING_FAMILIES_SOURCE = Path("shared/routing/families.json")
SKILL_REGISTRY_TARGET = Path("shared/docs/skill_registry.md")
SKILL_ROUTING_INDEX_TARGET = Path("shared/docs/skill_routing.md")
SKILL_ROUTING_FAMILY_TARGET = Path("shared/docs/routing")
RESOURCE_PROJECTIONS = {"verbatim", "tree", "execution-item-view"}
RESOURCE_LOAD_CLASSES = {"must_read", "read_if_needed"}

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


def _load_distribution(source: Path) -> dict:
    path = source / DISTRIBUTION_METADATA_SOURCE
    try:
        metadata = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"invalid distribution metadata {path}: {exc}") from exc
    if metadata.get("schema_version") != 1:
        raise SystemExit(
            f"distribution metadata schema_version must be 1: {path}"
        )
    required = (
        ("bundle_version", metadata.get("bundle_version")),
        ("publisher.name", metadata.get("publisher", {}).get("name")),
        ("marketplace.name", metadata.get("marketplace", {}).get("name")),
        (
            "marketplace.display_name",
            metadata.get("marketplace", {}).get("display_name"),
        ),
        (
            "marketplace.description",
            metadata.get("marketplace", {}).get("description"),
        ),
        ("marketplace.category", metadata.get("marketplace", {}).get("category")),
    )
    missing = [
        name
        for name, value in required
        if not isinstance(value, str) or not value
    ]
    if missing:
        raise SystemExit(
            f"distribution metadata has missing string fields {missing}: {path}"
        )
    codex_policy = metadata.get("marketplace", {}).get("codex_policy")
    if not isinstance(codex_policy, dict) or not codex_policy:
        raise SystemExit(
            f"distribution metadata has no Codex marketplace policy: {path}"
        )
    return metadata


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


def _frontmatter_scalar(text: str, key: str, path: Path) -> str:
    if not text.startswith("---\n"):
        raise SystemExit(f"skill frontmatter must start on the first line: {path}")
    closing = text.find("\n---\n", 4)
    if closing < 0:
        raise SystemExit(f"skill frontmatter is not closed: {path}")
    prefix = key + ":"
    matches = [line[len(prefix) :].strip() for line in text[4:closing].splitlines() if line.startswith(prefix)]
    if len(matches) != 1 or not matches[0]:
        raise SystemExit(f"skill frontmatter must contain one non-empty {key}: {path}")
    value = matches[0]
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        if value[0] == '"':
            try:
                return str(json.loads(value))
            except json.JSONDecodeError as exc:
                raise SystemExit(f"invalid quoted {key} in {path}: {exc}") from exc
        return value[1:-1].replace("''", "'")
    return value


def _safe_package_path(value: str, label: str, *, plugin_target: bool = False) -> PurePosixPath:
    raw = value
    if plugin_target and raw.startswith("@plugin/"):
        raw = raw.removeprefix("@plugin/")
    elif raw.startswith("@plugin/"):
        raise SystemExit(f"{label} uses @plugin outside a target: {value!r}")
    if not raw or "\\" in raw or "\x00" in raw or ":" in raw:
        raise SystemExit(f"{label} must be a non-empty POSIX path: {value!r}")
    raw_parts = raw.split("/")
    if raw.startswith("/") or raw.endswith("/") or any(part in {"", ".", ".."} for part in raw_parts):
        raise SystemExit(f"{label} must be a normalized relative path: {value!r}")
    path = PurePosixPath(raw)
    if path.is_absolute():
        raise SystemExit(f"{label} must be a safe relative path: {value!r}")
    if plugin_target and value.startswith("@plugin/"):
        if not raw_parts or raw_parts[0] != "shared":
            raise SystemExit(f"plugin resource target must stay under @plugin/shared: {value!r}")
    elif plugin_target and (not raw_parts or raw_parts[0] not in {"references", "assets", "scripts"}):
        raise SystemExit(f"skill resource target must stay under references/assets/scripts: {value!r}")
    return path


def _json_object_without_duplicates(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _routing_card(text: str, path: Path) -> tuple[str, str, str, list[dict[str, str]]]:
    marker = "\n" + ROUTING_CARD_HEADING + "\n"
    start = text.find(marker)
    if start < 0:
        raise SystemExit(f"missing {ROUTING_CARD_HEADING}: {path}")
    start += 1
    end = text.find("\n## ", start + len(ROUTING_CARD_HEADING))
    if end < 0:
        end = len(text)
    card = text[start:end].rstrip()
    if text.find(marker, start + 1) >= 0:
        raise SystemExit(f"duplicate {ROUTING_CARD_HEADING}: {path}")

    positions: list[int] = []
    for field in ROUTING_FIELDS:
        field_marker = f"\n- {field}:"
        matches = [match.start() for match in re.finditer(re.escape(field_marker), "\n" + card)]
        if len(matches) != 1:
            raise SystemExit(f"routing card field {field} must appear exactly once: {path}")
        positions.append(matches[0])
    if positions != sorted(positions):
        raise SystemExit(f"routing card fields are out of order: {path}")
    def scalar(field: str) -> str:
        match = re.search(rf"(?m)^- {re.escape(field)}:\s*([^\n]+)$", card)
        if match is None or not match.group(1).strip():
            raise SystemExit(f"routing card {field} must be a scalar: {path}")
        return match.group(1).strip()

    role = scalar("role")
    family = scalar("family")
    closure_marker = "\n" + RESOURCE_CLOSURE_HEADING + "\n\n```json\n"
    closure_start = card.find(closure_marker)
    if closure_start < 0:
        raise SystemExit(f"missing structured {RESOURCE_CLOSURE_HEADING}: {path}")
    json_start = closure_start + len(closure_marker)
    json_end = card.find("\n```", json_start)
    if json_end < 0 or card[json_end + 4 :].strip():
        raise SystemExit(f"resource closure must be the final routing-card subsection: {path}")
    try:
        resources = json.loads(
            card[json_start:json_end], object_pairs_hook=_json_object_without_duplicates
        )
    except (json.JSONDecodeError, ValueError) as exc:
        raise SystemExit(f"invalid resource closure JSON in {path}: {exc}") from exc
    if not isinstance(resources, list):
        raise SystemExit(f"resource closure must be a JSON array: {path}")
    normalized: list[dict[str, str]] = []
    seen_targets: set[str] = set()
    required_keys = {"source", "target", "projection", "load", "condition"}
    for index, item in enumerate(resources):
        if not isinstance(item, dict) or set(item) != required_keys or not all(isinstance(value, str) for value in item.values()):
            raise SystemExit(
                f"resource closure entry {index} must contain only string fields {sorted(required_keys)}: {path}"
            )
        source_value = item["source"]
        target_value = item["target"]
        source_path = _safe_package_path(source_value, f"{path} resource source")
        _safe_package_path(target_value, f"{path} resource target", plugin_target=True)
        if not source_path.parts or source_path.parts[0] != "shared":
            raise SystemExit(f"resource source must be shared canonical input: {path}: {source_value}")
        if item["projection"] not in RESOURCE_PROJECTIONS:
            raise SystemExit(f"unknown resource projection {item['projection']!r}: {path}")
        if item["load"] not in RESOURCE_LOAD_CLASSES:
            raise SystemExit(f"unknown resource load class {item['load']!r}: {path}")
        if not item["condition"].strip():
            raise SystemExit(f"resource closure condition is empty: {path}: {target_value}")
        if target_value in seen_targets:
            raise SystemExit(f"duplicate resource target {target_value!r}: {path}")
        seen_targets.add(target_value)
        normalized.append(dict(item))
    return card[:closure_start].rstrip(), role, family, normalized


def _load_skill_declarations(source: Path) -> dict[str, dict]:
    declarations: dict[str, dict] = {}
    shared_root = (source / "shared").resolve(strict=True)
    for skill_dir in sorted((source / "skills").iterdir()):
        if not skill_dir.is_dir():
            continue
        path = skill_dir / "SKILL.md"
        if not path.is_file():
            raise SystemExit(f"missing canonical skill file: {path}")
        text = path.read_text(encoding="utf-8")
        name = _frontmatter_scalar(text, "name", path)
        description = _frontmatter_scalar(text, "description", path)
        if name != skill_dir.name:
            raise SystemExit(f"skill directory {skill_dir.name} has frontmatter name {name!r}")
        card, role, family, resources = _routing_card(text, path)
        for resource in resources:
            canonical = source / Path(resource["source"])
            try:
                canonical.resolve(strict=True).relative_to(shared_root)
            except (OSError, ValueError) as exc:
                raise SystemExit(f"resource source resolves outside source/shared: {path}: {canonical}") from exc
            if resource["projection"] in {"verbatim", "execution-item-view"} and not canonical.is_file():
                raise SystemExit(f"resource source is not a file: {path}: {canonical}")
            if resource["projection"] == "tree" and not canonical.is_dir():
                raise SystemExit(f"resource source is not a directory: {path}: {canonical}")
            if canonical.is_symlink() or (
                resource["projection"] == "tree"
                and any(candidate.is_symlink() for candidate in canonical.rglob("*"))
            ):
                raise SystemExit(f"resource source contains a symlink: {path}: {canonical}")
        declarations[name] = {
            "id": name,
            "description": description,
            "role": role,
            "family": family,
            "card": card,
            "resources": resources,
            "implicit": _allow_implicit_invocation(skill_dir),
            "source_dir": skill_dir,
        }
    if not declarations:
        raise SystemExit(f"no canonical skills under {source / 'skills'}")
    return declarations


def _load_routing_families(source: Path) -> list[dict]:
    path = source / ROUTING_FAMILIES_SOURCE
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"invalid routing family declaration {path}: {exc}") from exc
    if value.get("schema_version") != 1 or not isinstance(value.get("families"), list):
        raise SystemExit(f"routing family declaration must use schema_version 1: {path}")
    required = {"id", "display_name", "entry_owners", "aliases"}
    families: list[dict] = []
    seen_ids: set[str] = set()
    seen_aliases: set[str] = set()
    for entry in value["families"]:
        if not isinstance(entry, dict) or set(entry) != required:
            raise SystemExit(f"routing family entry must contain {sorted(required)}: {path}")
        if not all(isinstance(entry[key], str) and entry[key].strip() for key in required - {"aliases"}):
            raise SystemExit(f"routing family entry has an empty string field: {entry!r}")
        aliases = entry["aliases"]
        if not isinstance(aliases, list) or not aliases or not all(isinstance(alias, str) and alias.strip() for alias in aliases):
            raise SystemExit(f"routing family aliases must be non-empty strings: {entry!r}")
        family_id = entry["id"]
        if re.fullmatch(r"[a-z][a-z0-9-]*", family_id) is None:
            raise SystemExit(f"routing family id must be one portable path component: {family_id!r}")
        if family_id in seen_ids:
            raise SystemExit(f"duplicate routing family {family_id!r}: {path}")
        seen_ids.add(family_id)
        for alias in aliases:
            normalized = alias.casefold()
            if normalized in seen_aliases:
                raise SystemExit(f"duplicate routing family alias {alias!r}: {path}")
            seen_aliases.add(normalized)
        families.append(entry)
    return families


def _plugin_owners(source: Path, skill_ids: set[str]) -> dict[str, str]:
    owners: dict[str, str] = {}
    for manifest_path in sorted((source / "plugins").glob("*.yaml")):
        manifest = _load_manifest(manifest_path)
        plugin = manifest.get("name", "")
        for skill_id in manifest["skills"]:
            if skill_id not in skill_ids:
                raise SystemExit(f"plugin {plugin}: unknown skill {skill_id!r}")
            if skill_id in owners:
                raise SystemExit(f"skill {skill_id!r} assigned to both {owners[skill_id]} and {plugin}")
            owners[skill_id] = plugin
    missing = sorted(skill_ids - owners.keys())
    if missing:
        raise SystemExit(f"plugin coverage gap: {missing}")
    return owners


def _markdown_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def _refresh_shared_routing_docs(source: Path) -> dict[str, dict]:
    declarations = _load_skill_declarations(source)
    families = _load_routing_families(source)
    family_by_id = {entry["id"]: entry for entry in families}
    unknown = sorted({entry["family"] for entry in declarations.values()} - family_by_id.keys())
    if unknown:
        raise SystemExit(f"skills reference unknown routing families: {unknown}")
    owners = _plugin_owners(source, set(declarations))

    registry_lines = [
        "# Skill Registry",
        "",
        "> Generated from each canonical `source/skills/*/SKILL.md` Routing Card plus",
        "> `source/shared/routing/families.json` and `source/plugins/*.yaml`. Do not edit this projection.",
        "",
        "## Registry",
        "",
        "| skill | family | role | plugin owner | implicit invocation |",
        "| --- | --- | --- | --- | --- |",
    ]
    for skill_id, declaration in sorted(declarations.items()):
        registry_lines.append(
            "| `" + "` | `".join(
                _markdown_cell(value)
                for value in (
                    skill_id,
                    declaration["family"],
                    declaration["role"],
                    owners[skill_id],
                    str(declaration["implicit"]).lower(),
                )
            ) + "` |"
        )
    registry_lines.extend(
        [
            "",
            "## Group Alias Map",
            "",
            "Family aliases are a separate cross-skill concern. They select a family only; the",
            "matching skill Routing Card retains use/exclusion authority.",
            "",
            "| family | display name | entry owner(s) | aliases |",
            "| --- | --- | --- | --- |",
        ]
    )
    for family in families:
        registry_lines.append(
            f"| `{_markdown_cell(family['id'])}` | {_markdown_cell(family['display_name'])} | "
            f"{_markdown_cell(family['entry_owners'])} | {_markdown_cell(', '.join(family['aliases']))} |"
        )
    registry_lines.extend(
        [
            "",
            "## Ownership Boundary",
            "",
            "- Routing semantics and conditional context remain local to each skill Routing Card.",
            "- Agent metadata owns provider discoverability and implicit invocation, not authorization.",
            "- Plugin manifests own installation-profile membership only.",
            "- Provider overlays own genuine host trigger, permission, path, hook, lifecycle, and compatibility rules.",
            "- Unknown or stale skill IDs remain `unresolved`; no generated view invents aliases or fallback routes.",
        ]
    )
    registry_path = source / SKILL_REGISTRY_TARGET
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text("\n".join(registry_lines) + "\n", encoding="utf-8")

    routing_root = source / SKILL_ROUTING_FAMILY_TARGET
    if routing_root.exists():
        shutil.rmtree(routing_root)
    routing_root.mkdir(parents=True)
    index_lines = [
        "# Skill Routing Index",
        "",
        "> Generated from canonical skill-local Routing Cards. Do not edit this projection.",
        "",
        "Use explicit skill/path selection directly. For a genuinely ambiguous request, select the",
        "smallest matching family below and read only that family file or the exact installed skill;",
        "never load the whole routing library. Family lookup grants no write or side-effect authority.",
        "",
        "| family | route view | skills |",
        "| --- | --- | ---: |",
    ]
    for family in families:
        family_id = family["id"]
        selected = [entry for entry in declarations.values() if entry["family"] == family_id]
        index_lines.append(f"| `{family_id}` | `docs/routing/{family_id}.md` | {len(selected)} |")
        family_lines = [
            f"# {family['display_name']} Routing",
            "",
            "> Generated from canonical skill-local Routing Cards. Read only the matching section.",
            "",
        ]
        for declaration in sorted(selected, key=lambda entry: entry["id"]):
            family_lines.extend(
                [
                    f"## `{declaration['id']}`",
                    "",
                    declaration["card"].removeprefix(ROUTING_CARD_HEADING).strip(),
                    "",
                ]
            )
        (routing_root / f"{family_id}.md").write_text(
            "\n".join(family_lines).rstrip() + "\n", encoding="utf-8"
        )
    index_path = source / SKILL_ROUTING_INDEX_TARGET
    index_path.write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    return declarations


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


def _strip_resource_closure(skill_md: Path) -> None:
    text = skill_md.read_text(encoding="utf-8")
    marker = "\n" + RESOURCE_CLOSURE_HEADING + "\n"
    start = text.find(marker)
    if start < 0:
        raise SystemExit(f"generated skill has no {RESOURCE_CLOSURE_HEADING}: {skill_md}")
    end = text.find("\n## ", start + len(marker))
    if end < 0:
        end = len(text.rstrip())
    text = text[:start].rstrip() + "\n\n" + text[end:].lstrip("\n")
    skill_md.write_text(text.rstrip() + "\n", encoding="utf-8")


def _copy_plugin_skill(src: Path, dst: Path, *, claude: bool = False) -> None:
    _copy(src, dst)
    _strip_resource_closure(dst / "SKILL.md")
    agent_manifest = dst / "agents" / "openai.yaml"
    if agent_manifest.is_file():
        _sanitize_plugin_agent_manifest(agent_manifest)
    if claude:
        _project_claude_invocation(src, dst)


def _resource_target(
    package_root: Path, skill_dir: Path, target: str
) -> tuple[Path, str]:
    if target.startswith("@plugin/"):
        relative = target.removeprefix("@plugin/")
        return package_root / Path(relative), relative
    return skill_dir / Path(target), (Path("skills") / skill_dir.name / Path(target)).as_posix()


def _apply_resource_closure(
    source: Path,
    package_root: Path,
    skill_dir: Path,
    declaration: dict,
    claimed_targets: dict[str, tuple[str, str, str, str]],
) -> None:
    skill_id = declaration["id"]
    for resource in declaration["resources"]:
        canonical = source / Path(resource["source"])
        target, package_relative = _resource_target(package_root, skill_dir, resource["target"])
        normalized_target = package_relative.casefold()
        coalesced = False
        for existing, previous in claimed_targets.items():
            if normalized_target == existing:
                previous_skill, previous_source, previous_projection, previous_target = previous
                if (
                    resource["target"].startswith("@plugin/")
                    and package_relative == previous_target
                    and resource["source"] == previous_source
                    and resource["projection"] == previous_projection
                ):
                    coalesced = True
                    break
                raise SystemExit(
                    f"resource target {package_relative!r} conflicts between {previous_skill} and {skill_id}"
                )
            if normalized_target.startswith(existing + "/") or existing.startswith(normalized_target + "/"):
                raise SystemExit(
                    f"overlapping resource targets {package_relative!r} ({skill_id}) and {existing!r} ({previous[0]})"
                )
        if coalesced:
            continue
        claimed_targets[normalized_target] = (
            skill_id,
            resource["source"],
            resource["projection"],
            package_relative,
        )
        projection = resource["projection"]
        if projection == "execution-item-view":
            if resource["source"] != EXECUTION_ITEM_CONTRACT_SOURCE.as_posix() or resource["target"] != EXECUTION_ITEM_VIEW_TARGET.as_posix():
                raise SystemExit(f"invalid execution-item-view closure for {skill_id}: {resource}")
            if target.exists():
                raise SystemExit(f"resource target already exists before projection: {target}")
            _render_execution_item_view(source, skill_dir, (skill_dir / "SKILL.md").read_text(encoding="utf-8"))
            continue
        if projection == "verbatim" and not canonical.is_file():
            raise SystemExit(f"verbatim resource source is not a file: {canonical}")
        if projection == "tree" and not canonical.is_dir():
            raise SystemExit(f"tree resource source is not a directory: {canonical}")
        if target.exists():
            raise SystemExit(f"resource target already exists before projection: {target}")
        _copy(canonical, target)



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
    version = str(_load_distribution(source)["bundle_version"])
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
    _refresh_shared_routing_docs(source)
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
    _refresh_shared_routing_docs(source)
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
    _refresh_shared_routing_docs(source)
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
    """Minimal YAML profile reader without a YAML dependency."""
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
    declarations = _refresh_shared_routing_docs(source)
    distribution = _load_distribution(source)
    bundle_version = str(distribution["bundle_version"])
    publisher_name = distribution["publisher"]["name"]
    marketplace_spec = distribution["marketplace"]
    marketplace_name = marketplace_spec["name"]
    marketplace_category = marketplace_spec["category"]
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
    codex_marketplace_plugins: list[tuple[int, dict]] = []
    claude_packages_root = plugins_root / "claude"
    if claude_packages_root.exists():
        shutil.rmtree(claude_packages_root)
    for mf in manifests:
        spec = _load_manifest(mf)
        name = spec["name"]
        codex_pkg = plugins_root / name
        claude_pkg = claude_packages_root / name
        codex_resource_targets: dict[str, tuple[str, str, str, str]] = {}
        claude_resource_targets: dict[str, tuple[str, str, str, str]] = {}
        if codex_pkg.exists():
            shutil.rmtree(codex_pkg)
        display_name = name.replace("-", " ").title()
        short_description = spec["short_description"]
        manifest = {
            "name": name,
            "version": bundle_version,
            "description": spec["description"],
            "author": {"name": publisher_name},
            "license": "MIT",
            "keywords": ["skill-system", "codex", name.removeprefix("skill-system-")],
            "skills": "./skills/",
            "interface": {
                "displayName": display_name,
                "shortDescription": short_description,
                "longDescription": spec["description"],
                "developerName": publisher_name,
                "category": marketplace_category,
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
            "version": bundle_version,
            "description": spec["description"],
            "author": {"name": publisher_name},
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
                "version": bundle_version,
                "category": marketplace_category,
            }
        )
        codex_marketplace_plugins.append(
            (
                int(spec["codex_catalog_order"]),
                {
                    "name": name,
                    "source": {
                        "source": "local",
                        "path": f"./{plugins_root.name}/{name}",
                    },
                    "policy": marketplace_spec["codex_policy"],
                    "category": marketplace_category,
                },
            )
        )
        for sid in spec["skills"]:
            if sid not in src_skills:
                raise SystemExit(f"plugin {name}: unknown skill '{sid}' (not in source/skills)")
            if sid in seen:
                raise SystemExit(f"skill '{sid}' assigned to both {seen[sid]} and {name}")
            seen[sid] = name
            _copy_plugin_skill(source / "skills" / sid, codex_pkg / "skills" / sid)
            _apply_resource_closure(
                source,
                codex_pkg,
                codex_pkg / "skills" / sid,
                declarations[sid],
                codex_resource_targets,
            )
            written.append((codex_pkg / "skills" / sid).as_posix())
            _copy_plugin_skill(source / "skills" / sid, claude_pkg / "skills" / sid, claude=True)
            _apply_resource_closure(
                source,
                claude_pkg,
                claude_pkg / "skills" / sid,
                declarations[sid],
                claude_resource_targets,
            )
            written.append((claude_pkg / "skills" / sid).as_posix())
    uncovered = src_skills - seen.keys()
    if uncovered:
        raise SystemExit(f"plugin coverage gap: {len(uncovered)} skills in no plugin: {sorted(uncovered)}")
    # Claude repo-local marketplace catalog (accurate Claude marketplace.json schema): required
    # `name` + `owner`, plugins listed with relative-path `source`. Register with
    # `/plugin marketplace add <repo>/plugins`; install `<name>@skill-system-local`.
    marketplace = {
        "name": marketplace_name,
        "owner": {"name": publisher_name},
        "description": marketplace_spec["description"],
        "plugins": marketplace_plugins,
    }
    marketplace_json = plugins_root / ".claude-plugin" / "marketplace.json"
    marketplace_json.parent.mkdir(parents=True, exist_ok=True)
    marketplace_json.write_text(
        json.dumps(marketplace, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    written.append(marketplace_json.as_posix())
    codex_marketplace = {
        "name": marketplace_name,
        "interface": {"displayName": marketplace_spec["display_name"]},
        "plugins": [
            entry
            for _, entry in sorted(
                codex_marketplace_plugins,
                key=lambda ordered_entry: ordered_entry[0],
            )
        ],
    }
    codex_marketplace_json = (
        plugins_root.parent / ".agents" / "plugins" / "marketplace.json"
    )
    # Keep custom plugin generation self-contained: /stage/plugins projects its Codex
    # catalog into /stage/.agents instead of mutating the current checkout catalog.
    codex_marketplace_json.parent.mkdir(parents=True, exist_ok=True)
    codex_marketplace_json.write_text(
        json.dumps(codex_marketplace, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    written.append(codex_marketplace_json.as_posix())
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
