#!/usr/bin/env python3
"""Check static context/document targets referenced by skills and plans."""

from __future__ import annotations

from pathlib import Path


REFERENCE_RULES = [
    (
        "integrations/kanboard-plan-sync README",
        [Path("integrations/kanboard-plan-sync/README.md")],
    ),
    (
        "integrations/kanboard-plan-sync README + localhost setup doc",
        [
            Path("integrations/kanboard-plan-sync/README.md"),
            Path("integrations/kanboard-plan-sync/docs/kanboard-localhost-setup.md"),
        ],
    ),
]


def text_files(root: Path) -> list[Path]:
    candidates: list[Path] = []
    for base in [root / ".codex" / "skills", root / ".claude" / "skills", root / "docs" / "plan"]:
        if not base.exists():
            continue
        candidates.extend(path for path in base.rglob("*.md") if path.is_file())
    return sorted(candidates)


def main() -> int:
    root = Path(".").resolve()
    errors: list[str] = []
    for path in text_files(root):
        text = path.read_text(encoding="utf-8", errors="replace")
        for marker, targets in REFERENCE_RULES:
            if marker not in text:
                continue
            for target in targets:
                if not (root / target).exists():
                    errors.append(f"{path.relative_to(root)} references missing target: {target}")
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
