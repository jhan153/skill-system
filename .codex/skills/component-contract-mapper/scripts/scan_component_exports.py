#!/usr/bin/env python3
"""Read-only component export inventory helper."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


SOURCE_SUFFIXES = {".ts", ".tsx", ".js", ".jsx", ".vue", ".svelte"}
EXPORT_RE = re.compile(
    r"\bexport\s+(?:default\s+)?(?:function|class|const|let|var)\s+([A-Z][A-Za-z0-9_]*)"
    r"|\bexport\s*\{([^}]+)\}"
)
STORY_RE = re.compile(r"\.stories\.(ts|tsx|js|jsx|mdx)$")


def iter_files(paths: list[Path]) -> list[Path]:
    found: list[Path] = []
    for path in paths:
        if path.is_dir():
            found.extend(p for p in path.rglob("*") if p.is_file() and p.suffix in SOURCE_SUFFIXES)
        elif path.is_file() and path.suffix in SOURCE_SUFFIXES:
            found.append(path)
    return sorted(set(found))


def exported_names(text: str) -> list[str]:
    names: set[str] = set()
    for direct, grouped in EXPORT_RE.findall(text):
        if direct:
            names.add(direct)
        if grouped:
            for item in grouped.split(","):
                clean = item.strip().split(" as ")[-1].strip()
                if clean and clean[0].isupper():
                    names.add(clean)
    return sorted(names)


def inspect(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8", errors="replace")
    return {
        "path": str(path),
        "exports": exported_names(text),
        "looks_like_story": bool(STORY_RE.search(path.name)),
        "line_count": text.count("\n") + 1,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Inventory component exports without modifying files.")
    parser.add_argument("paths", nargs="+", help="Component files or directories to scan.")
    parser.add_argument("--output", help="Optional JSON output path. Defaults to stdout.")
    args = parser.parse_args()

    files = iter_files([Path(item) for item in args.paths])
    result = {
        "files_scanned": len(files),
        "components": [inspect(path) for path in files],
        "note": "Read-only inventory; export names do not prove design contract coverage.",
    }
    payload = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
