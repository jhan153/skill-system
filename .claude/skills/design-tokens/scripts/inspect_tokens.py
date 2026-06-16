#!/usr/bin/env python3
"""Read-only token source inventory helper.

This script scans token-like files and prints a JSON inventory. It does not
modify files and does not decide token correctness.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


TOKEN_SUFFIXES = {".json", ".css", ".scss", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"}
CSS_VAR_RE = re.compile(r"(--[A-Za-z0-9_-]+)\s*:\s*([^;]+);")
HEX_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b")
PX_RE = re.compile(r"\b\d+(?:\.\d+)?(?:px|rem|em|vh|vw|%)\b")


def iter_files(paths: list[Path]) -> list[Path]:
    found: list[Path] = []
    for path in paths:
        if path.is_dir():
            found.extend(p for p in path.rglob("*") if p.is_file() and p.suffix in TOKEN_SUFFIXES)
        elif path.is_file() and path.suffix in TOKEN_SUFFIXES:
            found.append(path)
    return sorted(set(found))


def flatten_json(value: Any, prefix: str = "") -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if isinstance(value, dict):
        token_value = value.get("value", value.get("$value"))
        token_type = value.get("type", value.get("$type"))
        if token_value is not None:
            rows.append({"name": prefix.strip("."), "type": token_type, "value": token_value})
        for key, child in value.items():
            if key in {"value", "$value", "type", "$type", "description", "$description"}:
                continue
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            rows.extend(flatten_json(child, child_prefix))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            rows.extend(flatten_json(child, f"{prefix}.{index}" if prefix else str(index)))
    return rows


def inspect_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - report parser failure
        return {"path": str(path), "format": "json", "error": str(exc), "tokens": []}
    return {"path": str(path), "format": "json", "tokens": flatten_json(data)}


def inspect_text(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    css_vars = [{"name": name, "value": value.strip()} for name, value in CSS_VAR_RE.findall(text)]
    return {
        "path": str(path),
        "format": path.suffix.lstrip(".") or "text",
        "css_variables": css_vars,
        "hex_values": sorted(set(HEX_RE.findall(text))),
        "size_values": sorted(set(PX_RE.findall(text))),
    }


def inspect_file(path: Path) -> dict[str, Any]:
    if path.suffix == ".json":
        return inspect_json(path)
    return inspect_text(path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect token-like files without modifying them.")
    parser.add_argument("paths", nargs="+", help="Token files or directories to scan.")
    parser.add_argument("--output", help="Optional JSON output path. Defaults to stdout.")
    args = parser.parse_args()

    files = iter_files([Path(item) for item in args.paths])
    result = {
        "files_scanned": len(files),
        "files": [inspect_file(path) for path in files],
        "note": "Read-only inventory; inferred values are not confirmed design tokens.",
    }
    payload = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
