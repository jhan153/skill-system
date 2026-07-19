#!/usr/bin/env python3
"""Generate the Codex and Claude runtimes from canonical source/.

Portable skills and data contracts are shared. Harness entry files, routing, hooks,
permissions, and platform tools are owned by source/platform/{codex,claude} and can be
generated independently. ``runtime`` remains the release aggregate that generates both.

Platform entries that overlap shared output are merged. Platform-only entries are replaced from
source so deleted tools and hook files cannot survive in generated targets.

Idempotency: verbatim trees copy unchanged bytes. Mirror files reuse the frozen
generated_from/generated_at from source/mirror-meta.json, so regeneration is byte-stable.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

# (source_rel, target_rel) copied unchanged into either requested target.
NEUTRAL_VERBATIM: list[tuple[str, str]] = [
    ("skills", "skills"),
    ("shared/docs", "docs"),
    ("shared/eval", "eval"),
    ("shared/schemas", "schemas"),  # Phase 1b: schema definitions are platform-neutral data contracts
]
NEUTRAL_TARGET_ROOTS = {target_rel.split("/", 1)[0] for _, target_rel in NEUTRAL_VERBATIM}

# Platform-native trees: every top-level entry under source/platform/<p> is copied verbatim
# into that one target only. AGENTS.md / CLAUDE.md live here as platform-native for Phase 1a;
# factoring them into a shared body + overlay (platform-template) is a Phase 1b refinement.
PLATFORM_CODEX_ROOT = "platform/codex"
PLATFORM_CLAUDE_ROOT = "platform/claude"
REMOVED_CODEX_TARGET_ROOTS = ("research",)

MIRROR_META_FILE = "mirror-meta.json"

_CACHE_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}

PLUGIN_DISPLAY = {
    "skill-system-core": ("Skill System Core", "Shared operating platform skills for Codex workflows."),
    "skill-system-dev": ("Skill System Dev", "Engineering analysis, implementation, refactoring, and recovery skills."),
    "skill-system-design": ("Skill System Design", "Frontend, UI, layout, component, token, and visual validation skills."),
    "skill-system-research": ("Skill System Research", "Scientific research, synthesis, experiment, and manuscript skills."),
    "skill-system-quality": ("Skill System Quality", "QA, qualitative review, critical review, and validation skills."),
    "skill-system-maintainer": ("Skill System Maintainer", "Skill-system evaluation, repository integration, and bundle validation skills."),
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
    """Project the portable invocation bit into Claude's SKILL.md frontmatter."""
    skill_md = target_dir / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    if "disable-model-invocation:" in text:
        raise SystemExit(f"canonical skill must not contain Claude invocation metadata: {skill_md}")
    if _allow_implicit_invocation(skill_dir):
        return
    if not text.startswith("---\n"):
        raise SystemExit(f"skill frontmatter must start on the first line: {skill_md}")
    closing = text.find("\n---\n", 4)
    if closing < 0:
        raise SystemExit(f"skill frontmatter is not closed: {skill_md}")
    text = text[:closing] + "\ndisable-model-invocation: true" + text[closing:]
    skill_md.write_text(text, encoding="utf-8")


def _project_claude_runtime_skills(source: Path, claude: Path) -> None:
    for skill_dir in sorted((source / "skills").iterdir()):
        if skill_dir.is_dir() and (skill_dir / "SKILL.md").is_file():
            _project_claude_invocation(skill_dir, claude / "skills" / skill_dir.name)


def _copy_plugin_skill(src: Path, dst: Path, *, claude: bool = False) -> None:
    _copy(src, dst)
    agent_manifest = dst / "agents" / "openai.yaml"
    if agent_manifest.is_file():
        _sanitize_plugin_agent_manifest(agent_manifest)
    if claude:
        _project_claude_invocation(src, dst)


def _render_yaml_mirror(canonical: Path, generated_from: str, generated_at: str, checksum: str) -> str:
    body = canonical.read_text(encoding="utf-8")
    return "\n".join(
        [
            f"generated_from: {generated_from}",
            f"generated_at: {generated_at}",
            f"source_checksum: {checksum}",
            "do_not_edit: true",
            "",
            body.rstrip(),
            "",
        ]
    )


def _render_json_mirror(canonical: Path, generated_from: str, generated_at: str, checksum: str) -> str:
    data = json.loads(canonical.read_text(encoding="utf-8"))
    mirrored = {
        "x_generated_from": generated_from,
        "x_generated_at": generated_at,
        "x_source_checksum": checksum,
        "x_do_not_edit": True,
    }
    mirrored.update(data)
    return json.dumps(mirrored, indent=2, ensure_ascii=True) + "\n"


def _merge_copy(src: Path, dst: Path) -> None:
    """Overlay src onto dst, copying files without removing pre-existing target content.

    Used for platform overlay so a platform tree can supplement a shared tree
    (e.g. codex-only schemas/workitem/examples on top of shared schema definitions).
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
    output_root: Path,
    command: str,
    targets: tuple[tuple[str, str, str], ...],
    written: list[str],
) -> None:
    module = source / "runtime" / "go"
    if not (module / "go.mod").is_file():
        raise SystemExit(f"missing Go harness module: {module}")
    version = str(_load_manifest(source / "plugins" / "core.yaml")["version"])
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


def _build_notification_overlay(source: Path, output_root: Path, written: list[str]) -> None:
    overlay_source = source / "runtime" / "swift" / "notification_overlay.swift"
    if not overlay_source.is_file():
        raise SystemExit(f"missing Swift notification overlay source: {overlay_source}")
    overlay = output_root / "skill-system-notify-overlay"
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


def _build_codex_harness(source: Path, codex: Path, written: list[str]) -> None:
    """Build the Codex Go dispatchers and packaged macOS notification overlay."""
    output_root = codex / "bin"
    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    _build_go_dispatchers(
        source,
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
    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    _build_go_dispatchers(
        source,
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


def _write_mirror(source: Path, claude: Path, dst_rel: str, spec: dict) -> None:
    canonical = source / spec["canonical"]
    if not canonical.is_file():
        raise SystemExit(f"missing mirror canonical: {canonical}")
    checksum = _sha256(canonical)
    if checksum != spec["source_checksum"]:
        raise SystemExit(
            f"mirror canonical changed for {dst_rel}: source_checksum {checksum} != "
            f"frozen {spec['source_checksum']}. Update source/mirror-meta.json under Phase 1b, "
            f"not Phase 1a baseline."
        )
    if spec["kind"] == "yaml":
        content = _render_yaml_mirror(canonical, spec["generated_from"], spec["generated_at"], checksum)
    elif spec["kind"] == "json":
        content = _render_json_mirror(canonical, spec["generated_from"], spec["generated_at"], checksum)
    else:
        raise SystemExit(f"unknown mirror kind: {spec['kind']}")
    out = claude / dst_rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")


def generate_codex_runtime(source: Path, codex: Path) -> list[str]:
    written: list[str] = []
    _copy_neutral(source, codex, written)
    _copy_platform(source / PLATFORM_CODEX_ROOT, codex, written)
    # Research ledger data and its validation schema are maintainer fixtures, not
    # live runtime payload. Remove the former generated root so an upgrade cannot
    # retain or redeploy the historical ledger.
    for root_name in REMOVED_CODEX_TARGET_ROOTS:
        stale = codex / root_name
        if stale.is_dir():
            shutil.rmtree(stale)
        elif stale.exists():
            stale.unlink()
    _build_codex_harness(source, codex, written)
    return written


def generate_claude_runtime(source: Path, claude: Path) -> list[str]:
    written: list[str] = []
    _copy_neutral(source, claude, written)
    _project_claude_runtime_skills(source, claude)
    _copy_platform(source / PLATFORM_CLAUDE_ROOT, claude, written)
    # 9.3.4 removes the Python-only Claude runtime. Prune the now-absent
    # platform-owned root so stale adapters cannot survive regeneration.
    if not (source / PLATFORM_CLAUDE_ROOT / "tools").exists() and (claude / "tools").exists():
        shutil.rmtree(claude / "tools")
    _build_claude_harness(source, claude, written)
    # Claude keeps the checksum-bearing eval-schema mirror of shared canonical data.
    meta = json.loads((source / MIRROR_META_FILE).read_text(encoding="utf-8"))
    for dst_rel, spec in meta["mirrors"].items():
        _write_mirror(source, claude, dst_rel, spec)
        written.append((claude / dst_rel).as_posix() + " (mirror)")
    return written


def generate_runtime(source: Path, codex: Path, claude: Path) -> list[str]:
    """Release aggregate: generate both platform runtimes under one bundle identity."""
    return generate_codex_runtime(source, codex) + generate_claude_runtime(source, claude)


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
            written.append((codex_pkg / "skills" / sid).as_posix())
            _copy_plugin_skill(source / "skills" / sid, claude_pkg / "skills" / sid, claude=True)
            written.append((claude_pkg / "skills" / sid).as_posix())
    uncovered = src_skills - seen.keys()
    if uncovered:
        raise SystemExit(f"plugin coverage gap: {len(uncovered)} skills in no plugin: {sorted(uncovered)}")
    # Claude repo-local marketplace catalog (accurate Claude marketplace.json schema): required
    # `name` + `owner`, plugins listed with relative-path `source`. Register with
    # `/plugin marketplace add <repo>/plugins`; install `<name>@skill-system-local`.
    marketplace = {
        "name": "skill-system-local",
        "owner": {"name": "Skill System Maintainers"},
        "description": "Skill System role-based plugin packages (local marketplace).",
        "plugins": marketplace_plugins,
    }
    marketplace_json = plugins_root / ".claude-plugin" / "marketplace.json"
    marketplace_json.parent.mkdir(parents=True, exist_ok=True)
    marketplace_json.write_text(json.dumps(marketplace, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    written.append(marketplace_json.as_posix())
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target",
        choices=["runtime", "runtime-codex", "runtime-claude", "plugins"],
        required=True,
    )
    parser.add_argument("--source", default="source")
    parser.add_argument("--codex", default=".codex")
    parser.add_argument("--claude", default=".claude")
    parser.add_argument("--plugins", default="plugins")
    args = parser.parse_args()

    if args.target == "runtime":
        written = generate_runtime(Path(args.source), Path(args.codex), Path(args.claude))
    elif args.target == "runtime-codex":
        written = generate_codex_runtime(Path(args.source), Path(args.codex))
    elif args.target == "runtime-claude":
        written = generate_claude_runtime(Path(args.source), Path(args.claude))
    else:
        written = generate_plugins(Path(args.source), Path(args.plugins))
    for path in written:
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
