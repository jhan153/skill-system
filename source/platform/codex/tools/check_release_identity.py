#!/usr/bin/env python3
"""Fail closed when current source-bundle identity surfaces disagree."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


CURRENT_VERSION = "9.4.6"
PLUGIN_NAMES = (
    "skill-system-core",
    "skill-system-dev",
    "skill-system-design",
    "skill-system-research",
    "skill-system-quality",
)
SOURCE_PLUGIN_NAMES = {
    name.removeprefix("skill-system-"): name
    for name in PLUGIN_NAMES
}
EVAL_MANIFESTS = (
    "design_usage_cases.yaml",
    "handoff_cases.yaml",
    "knowledge_context_usage_cases.yaml",
    "memory_usage_cases.yaml",
    "negative_routing_cases.yaml",
    "pre_answer_depth_cases.yaml",
    "research_regression_cases.yaml",
    "routing_cases.yaml",
    "runtime_usage_cases.yaml",
)
RETIRED_PUBLIC_PROVENANCE_PATHS = (
    "source/shared/docs/source_registry.yaml",
    "source/platform/codex/tools/validate_source_registry.py",
    ".codex/docs/source_registry.yaml",
    ".codex/tools/validate_source_registry.py",
    ".claude/docs/source_registry.yaml",
)
PUBLIC_TEXT_ROOTS = ("source", ".codex", ".claude", "plugins", "integrations")
PUBLIC_ROOT_TEXT_FILES = ("README.md", "README.ko.md", "CHANGELOG.md", "TERMS.md")
PUBLIC_TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".json"}
RETIRED_LEDGER_MARKERS = (
    ("source_id:", "retrieved_at:", "local_modifications:"),
    ("upstream_reference:", "local_surface:", "rationale:"),
)
RETIRED_EXACT_MARKERS = ("adoption_decisions:", "transient_locator: codex_attachment:")


def yaml_scalar(path: Path, key: str) -> str | None:
    pattern = re.compile(rf"^{re.escape(key)}:\s*['\"]?([^'\"#]+?)['\"]?\s*$")
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            return match.group(1).strip()
    return None


def check_retired_public_provenance(root: Path) -> list[str]:
    """Keep external revision/license/adoption ledgers out of the public bundle."""
    errors: list[str] = []
    for rel in RETIRED_PUBLIC_PROVENANCE_PATHS:
        if (root / rel).exists():
            errors.append(f"retired public provenance path exists: {rel}")

    candidates = [root / rel for rel in PUBLIC_ROOT_TEXT_FILES]
    for rel in PUBLIC_TEXT_ROOTS:
        base = root / rel
        if base.is_dir():
            public_files = [path for path in base.rglob("*") if path.is_file()]
            candidates.extend(public_files)
            for path in public_files:
                if path.name in {"source_registry.yaml", "validate_source_registry.py"}:
                    error = f"retired public provenance path exists: {path.relative_to(root).as_posix()}"
                    if error not in errors:
                        errors.append(error)
    for path in candidates:
        if not path.is_file() or path.suffix.lower() not in PUBLIC_TEXT_SUFFIXES:
            continue
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        if any(marker in text for marker in RETIRED_EXACT_MARKERS) or any(
            all(marker in text for marker in marker_set) for marker_set in RETIRED_LEDGER_MARKERS
        ):
            errors.append(f"retired public provenance ledger content exists: {rel}")
    return errors


def check(root: Path) -> list[str]:
    errors: list[str] = []
    errors.extend(check_retired_public_provenance(root))
    source_manifests = sorted((root / "source" / "plugins").glob("*.yaml"))
    expected_source_paths = {
        root / "source" / "plugins" / f"{short_name}.yaml"
        for short_name in SOURCE_PLUGIN_NAMES
    }
    actual_source_paths = set(source_manifests)
    if actual_source_paths != expected_source_paths:
        missing = sorted(path.name for path in expected_source_paths - actual_source_paths)
        extra = sorted(path.name for path in actual_source_paths - expected_source_paths)
        errors.append(f"source plugin manifest set mismatch: missing={missing}; extra={extra}")
    for path in source_manifests:
        expected_name = SOURCE_PLUGIN_NAMES.get(path.stem)
        name = yaml_scalar(path, "name")
        if expected_name is None or name != expected_name:
            errors.append(f"{path.relative_to(root)} name {name!r} != {expected_name!r}")
        version = yaml_scalar(path, "version")
        if version != CURRENT_VERSION:
            errors.append(f"{path.relative_to(root)} version {version!r} != {CURRENT_VERSION!r}")
        if version and "+codex" in version:
            errors.append(f"development cachebuster remains in {path.relative_to(root)}")

    for plugin in PLUGIN_NAMES:
        platform_paths = (
            root / "plugins" / plugin / ".codex-plugin" / "plugin.json",
            root / "plugins" / "claude" / plugin / ".claude-plugin" / "plugin.json",
        )
        for path in platform_paths:
            if not path.is_file():
                errors.append(f"missing generated plugin manifest: {path.relative_to(root)}")
                continue
            payload = json.loads(path.read_text(encoding="utf-8"))
            if payload.get("name") != plugin:
                errors.append(
                    f"{path.relative_to(root)} name {payload.get('name')!r} != {plugin!r}"
                )
            if payload.get("version") != CURRENT_VERSION:
                errors.append(
                    f"{path.relative_to(root)} version {payload.get('version')!r} != {CURRENT_VERSION!r}"
                )

    marketplace_path = root / "plugins" / ".claude-plugin" / "marketplace.json"
    if not marketplace_path.is_file():
        errors.append("missing generated Claude marketplace")
    else:
        marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
        entries = marketplace.get("plugins", []) if isinstance(marketplace, dict) else []
        entry_names = [str(item.get("name")) for item in entries if isinstance(item, dict)]
        if len(entries) != len(PLUGIN_NAMES) or len(entry_names) != len(PLUGIN_NAMES):
            errors.append(
                f"Claude marketplace must contain exactly {len(PLUGIN_NAMES)} plugin objects, found {len(entries)}"
            )
        if len(entry_names) != len(set(entry_names)):
            errors.append("Claude marketplace contains duplicate plugin names")
        missing = sorted(set(PLUGIN_NAMES) - set(entry_names))
        extra = sorted(set(entry_names) - set(PLUGIN_NAMES))
        if missing or extra:
            errors.append(f"Claude marketplace plugin set mismatch: missing={missing}; extra={extra}")
        versions = {
            str(item.get("name")): item.get("version")
            for item in entries
            if isinstance(item, dict)
        }
        sources = {
            str(item.get("name")): item.get("source")
            for item in entries
            if isinstance(item, dict)
        }
        for plugin in PLUGIN_NAMES:
            if versions.get(plugin) != CURRENT_VERSION:
                errors.append(
                    f"Claude marketplace {plugin} version {versions.get(plugin)!r} != {CURRENT_VERSION!r}"
                )
            expected_source = f"./claude/{plugin}"
            if sources.get(plugin) != expected_source:
                errors.append(
                    f"Claude marketplace {plugin} source {sources.get(plugin)!r} != {expected_source!r}"
                )

    codex_marketplace_path = root / ".agents" / "plugins" / "marketplace.json"
    if not codex_marketplace_path.is_file():
        errors.append("missing generated Codex marketplace")
    else:
        marketplace = json.loads(codex_marketplace_path.read_text(encoding="utf-8"))
        entries = marketplace.get("plugins", []) if isinstance(marketplace, dict) else []
        entry_names = [str(item.get("name")) for item in entries if isinstance(item, dict)]
        if len(entries) != len(PLUGIN_NAMES) or len(entry_names) != len(PLUGIN_NAMES):
            errors.append(
                f"Codex marketplace must contain exactly {len(PLUGIN_NAMES)} plugin objects, found {len(entries)}"
            )
        if len(entry_names) != len(set(entry_names)):
            errors.append("Codex marketplace contains duplicate plugin names")
        missing = sorted(set(PLUGIN_NAMES) - set(entry_names))
        extra = sorted(set(entry_names) - set(PLUGIN_NAMES))
        if missing or extra:
            errors.append(f"Codex marketplace plugin set mismatch: missing={missing}; extra={extra}")
        for item in entries:
            if not isinstance(item, dict):
                continue
            plugin = item.get("name")
            source = item.get("source")
            expected_path = f"./plugins/{plugin}"
            if plugin in PLUGIN_NAMES and (
                not isinstance(source, dict)
                or source.get("source") != "local"
                or source.get("path") != expected_path
            ):
                errors.append(f"Codex marketplace {plugin} source must be local {expected_path!r}")

    eval_root = root / "source" / "shared" / "eval"
    for name in EVAL_MANIFESTS:
        path = eval_root / name
        version = yaml_scalar(path, "version") if path.is_file() else None
        if version != CURRENT_VERSION:
            errors.append(f"{path.relative_to(root)} version {version!r} != {CURRENT_VERSION!r}")

    claude_rules = root / "source" / "platform" / "claude" / "CLAUDE.md"
    if not claude_rules.is_file() or f"bundle ({CURRENT_VERSION})" not in claude_rules.read_text(
        encoding="utf-8"
    ):
        errors.append(f"source/platform/claude/CLAUDE.md does not declare bundle {CURRENT_VERSION}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    errors = check(args.root.resolve())
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"PASS: bundle identity {CURRENT_VERSION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
