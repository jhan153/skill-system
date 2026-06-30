#!/usr/bin/env python3
"""Check active guidance documents for stale current-version labels."""

from __future__ import annotations

import argparse
from pathlib import Path


ACTIVE_DOCS = [
    "FIELD_FEEDBACK.md",
    ".codex/docs/field_feedback_guidelines.md",
    ".claude/docs/field_feedback_guidelines.md",
    ".codex/docs/improvement_tracks.md",
    ".claude/docs/improvement_tracks.md",
    ".codex/docs/runtime_terms.md",
    ".claude/docs/runtime_terms.md",
    ".codex/skills/evaluation-harness/SKILL.md",
    ".claude/skills/evaluation-harness/SKILL.md",
]
STALE_PATTERNS = [
    "Current 7.1 Watchlist",
    "active 7.1 improvement tracks",
    "7.1 core",
    "7.1 runtime usage eval cases",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    errors: list[str] = []
    for rel in ACTIVE_DOCS:
        path = root / rel
        if not path.exists():
            continue
        text = read_text(path)
        for pattern in STALE_PATTERNS:
            if pattern in text:
                errors.append(f"{rel}: stale active label {pattern!r}")
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
