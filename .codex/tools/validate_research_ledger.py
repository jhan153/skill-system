#!/usr/bin/env python3
"""Validate optional research evidence ledger files."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from _validation import load_json_file, load_yaml_file, validate_schema


def source_ids(registry: Path) -> set[str]:
    data = load_yaml_file(registry)
    if not isinstance(data, dict):
        return set()
    sources = data.get("sources")
    if not isinstance(sources, list):
        return set()
    return {source["source_id"] for source in sources if isinstance(source, dict) and isinstance(source.get("source_id"), str)}


def validate_references(ledger: dict[str, Any], known_sources: set[str], root: Path) -> list[str]:
    errors: list[str] = []
    entries = ledger.get("entries", [])
    if not isinstance(entries, list):
        return errors
    seen: set[str] = set()
    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            continue
        entry_id = entry.get("entry_id", f"entries[{idx}]")
        if isinstance(entry_id, str):
            if entry_id in seen:
                errors.append(f"{entry_id}: duplicate entry_id")
            seen.add(entry_id)
        source_id = entry.get("source_id")
        if isinstance(source_id, str) and source_id not in known_sources:
            errors.append(f"{entry_id}: source_id not found in source registry: {source_id}")
        consumers = entry.get("local_consumers", [])
        if isinstance(consumers, list):
            for consumer in consumers:
                if not isinstance(consumer, str):
                    continue
                if consumer.startswith("/") or not (root / consumer).exists():
                    errors.append(f"{entry_id}: local consumer not found or not repo-relative: {consumer}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--schema", type=Path, default=Path(".codex/research/research-ledger.schema.json"))
    parser.add_argument("--source-registry", type=Path, default=Path(".codex/docs/source_registry.yaml"))
    args = parser.parse_args()
    if not args.ledger.exists():
        print(f"SKIP: research ledger not found: {args.ledger}")
        return 0
    if not args.schema.exists():
        print(f"FAIL: research ledger schema not found: {args.schema}")
        return 2
    if not args.source_registry.exists():
        print(f"FAIL: source registry not found: {args.source_registry}")
        return 2
    try:
        schema = load_json_file(args.schema)
        ledger = load_yaml_file(args.ledger)
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: invalid research ledger input: {exc}")
        return 2
    if not isinstance(ledger, dict):
        print(f"FAIL: {args.ledger}: expected top-level mapping")
        return 1
    errors = [f"{args.ledger}: {error}" for error in validate_schema(ledger, schema)]
    errors.extend(validate_references(ledger, source_ids(args.source_registry), Path(".").resolve()))
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
