#!/usr/bin/env python3
"""Check verifier tool dependency manifest."""

from __future__ import annotations

from pathlib import Path


REQUIRED = {"pyyaml", "jsonschema"}


def main() -> int:
    path = Path(".codex/tools/requirements.txt")
    if not path.exists():
        print("FAIL: missing .codex/tools/requirements.txt")
        return 1
    text = path.read_text(encoding="utf-8").lower()
    missing = sorted(name for name in REQUIRED if name not in text)
    if missing:
        print("FAIL")
        for name in missing:
            print(f"- missing dependency: {name}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
