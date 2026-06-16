#!/usr/bin/env python3
"""Read-only static accessibility hint scanner.

This script reports simple source hints. It is not a WCAG conformance test.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


SOURCE_SUFFIXES = {".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte"}
IMG_RE = re.compile(r"<img\b[^>]*>", re.I)
BUTTON_RE = re.compile(r"<button\b([^>]*)>(.*?)</button>", re.I | re.S)
INPUT_RE = re.compile(r"<input\b([^>]*)>", re.I)
ANCHOR_RE = re.compile(r"<a\b([^>]*)>(.*?)</a>", re.I | re.S)
ATTR_RE = re.compile(r"([:@A-Za-z0-9_-]+)\s*=\s*(['\"])(.*?)\2")


def attrs(tag: str) -> dict[str, str]:
    return {name.lower(): value for name, _, value in ATTR_RE.findall(tag)}


def strip_markup(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value).strip()


def iter_files(paths: list[Path]) -> list[Path]:
    found: list[Path] = []
    for path in paths:
        if path.is_dir():
            found.extend(p for p in path.rglob("*") if p.is_file() and p.suffix in SOURCE_SUFFIXES)
        elif path.is_file() and path.suffix in SOURCE_SUFFIXES:
            found.append(path)
    return sorted(set(found))


def inspect(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8", errors="replace")
    hints: list[dict[str, object]] = []

    for tag in IMG_RE.findall(text):
        data = attrs(tag)
        if "alt" not in data and ":alt" not in data:
            hints.append({"type": "img_missing_alt", "evidence": tag[:160]})

    for match in BUTTON_RE.finditer(text):
        attr_text, body = match.groups()
        data = attrs(attr_text)
        label = strip_markup(body)
        if not label and not any(key in data for key in ("aria-label", "aria-labelledby", ":aria-label")):
            hints.append({"type": "button_missing_accessible_name", "evidence": match.group(0)[:160]})

    for tag in INPUT_RE.findall(text):
        data = attrs(tag)
        input_type = data.get("type", "text").lower()
        if input_type in {"hidden", "submit", "button"}:
            continue
        if not any(key in data for key in ("aria-label", "aria-labelledby", "id", "name")):
            hints.append({"type": "input_missing_label_hint", "evidence": tag[:160]})

    for attr_text, body in ANCHOR_RE.findall(text):
        data = attrs(attr_text)
        label = strip_markup(body)
        if "href" in data and not label and not any(key in data for key in ("aria-label", "aria-labelledby")):
            hints.append({"type": "link_missing_accessible_name", "evidence": attr_text[:160]})

    if re.search(r"tabindex\s*=\s*['\"]-[^'\"]*['\"]", text, re.I):
        hints.append({"type": "negative_tabindex_present", "evidence": "tabindex=-* found"})

    return {
        "path": str(path),
        "hint_count": len(hints),
        "hints": hints,
        "note": "Static hints only; manual keyboard/focus and rendered checks remain required.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan UI source for simple accessibility hints.")
    parser.add_argument("paths", nargs="+", help="Source files or directories to scan.")
    parser.add_argument("--output", help="Optional JSON output path. Defaults to stdout.")
    args = parser.parse_args()

    files = iter_files([Path(item) for item in args.paths])
    result = {"files_scanned": len(files), "files": [inspect(path) for path in files]}
    payload = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
