#!/usr/bin/env python3
"""Verify source/ regenerates the current runtime targets byte-identically (Phase 1a).

Regenerates everything the generator manages into a throwaway temp directory, then asserts
each generated file is byte-identical to the live .codex / .claude target at the same path.
Junk files (.DS_Store, ._*, caches, *.pyc) are ignored.

This is incremental: live targets contain unmanaged files (tools/, AGENTS.md, ...) that the
generator does not yet produce. The check only asserts that every file the generator DOES
produce matches live exactly. It does not require the generator to cover the whole target yet.

--baseline : Phase 1a regression-baseline mode. ANY managed-file difference fails, no allowlist.
"""
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

import generate_targets as gt


def _rel_files(root: Path) -> dict[str, Path]:
    out: dict[str, Path] = {}
    if not root.exists():
        return out
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(gt._is_junk(part) for part in rel.parts):
            continue
        out[rel.as_posix()] = path
    return out


def check_runtime(source: Path, codex: Path, claude: Path, baseline: bool) -> int:
    diffs: list[str] = []
    managed = 0
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        gen_codex = tmp_path / "codex"
        gen_claude = tmp_path / "claude"
        gt.generate_runtime(source, gen_codex, gen_claude)

        for label, live_root, gen_root in (
            ("codex", codex, gen_codex),
            ("claude", claude, gen_claude),
        ):
            for rel, gen_path in sorted(_rel_files(gen_root).items()):
                managed += 1
                live_path = live_root / rel
                if not live_path.exists():
                    diffs.append(f"[{label}] extra-in-generated (not in live): {rel}")
                elif live_path.read_bytes() != gen_path.read_bytes():
                    diffs.append(f"[{label}] content-differs: {rel}")

    if diffs:
        print(f"FAIL: {len(diffs)} managed-file difference(s) vs live targets:")
        for d in diffs:
            print(f"  {d}")
        return 1

    mode = "baseline byte-identical" if baseline else "drift"
    print(f"PASS ({mode}): {managed} managed files match live targets (junk ignored).")
    return 0


def check_plugins(source: Path, plugins_root: Path, baseline: bool) -> int:
    diffs: list[str] = []
    managed = 0
    with tempfile.TemporaryDirectory() as tmp:
        gen_root = Path(tmp) / "plugins"
        gt.generate_plugins(source, gen_root)
        for rel, gen_path in sorted(_rel_files(gen_root).items()):
            managed += 1
            live_path = plugins_root / rel
            if not live_path.exists():
                diffs.append(f"extra-in-generated (not in live): {rel}")
            elif live_path.read_bytes() != gen_path.read_bytes():
                diffs.append(f"content-differs: {rel}")
        # also flag live plugin files the generator no longer produces (stale)
        gen_rels = set(_rel_files(gen_root))
        for rel in sorted(_rel_files(plugins_root)):
            if rel not in gen_rels:
                diffs.append(f"stale-in-live (not generated): {rel}")

    if diffs:
        print(f"FAIL: {len(diffs)} plugin difference(s) vs live:")
        for d in diffs:
            print(f"  {d}")
        return 1
    mode = "baseline byte-identical" if baseline else "drift"
    print(f"PASS ({mode}): {managed} generated plugin files match live (junk ignored).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=["runtime", "plugins"], required=True)
    parser.add_argument("--baseline", action="store_true")
    parser.add_argument("--source", default="source")
    parser.add_argument("--codex", default=".codex")
    parser.add_argument("--claude", default=".claude")
    parser.add_argument("--plugins", default="plugins")
    args = parser.parse_args()

    if args.target == "runtime":
        return check_runtime(Path(args.source), Path(args.codex), Path(args.claude), args.baseline)
    return check_plugins(Path(args.source), Path(args.plugins), args.baseline)


if __name__ == "__main__":
    raise SystemExit(main())
