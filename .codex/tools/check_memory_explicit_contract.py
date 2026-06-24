#!/usr/bin/env python3
"""Check that Knowledge integration does not weaken explicit-only Memory Bank mutation."""

from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True

from _validation import load_yaml_file, read_text


ROOT = Path(".")
MEMORY_SKILL_GLOB = ".codex/skills/memory-bank-*/agents/openai.yaml"
KNOWLEDGE_SKILLS = [
    ".codex/skills/knowledge-context-harness/agents/openai.yaml",
    ".codex/skills/knowledge-base-maintenance/agents/openai.yaml",
]
REQUIRED_TEXT = {
    ".codex/skills/knowledge-context-harness/SKILL.md": [
        "Do not promote, edit, or delete accepted knowledge from this skill.",
        "`memory-bank-harness` remains the read-only accepted-memory context compiler.",
    ],
    ".codex/skills/knowledge-base-maintenance/SKILL.md": [
        "Memory Bank skills keep ownership of explicit persistent memory operations.",
        "this skill does not rewrite Memory Bank files",
    ],
    ".codex/context-routing.md": [
        "Memory Bank mutation",
        "Persistent Memory Bank mutation still requires explicit memory-bank workflows",
    ],
    ".codex/eval/knowledge_routing_cases.yaml": [
        "memory-bank-update",
        "preserve_memory_explicit_only_contract",
    ],
}


def allow_implicit(path: Path) -> bool | None:
    data = load_yaml_file(path)
    if not isinstance(data, dict):
        return None
    policy = data.get("policy")
    if not isinstance(policy, dict):
        return None
    value = policy.get("allow_implicit_invocation")
    return value if isinstance(value, bool) else None


def main() -> int:
    errors: list[str] = []
    memory_skill_paths = sorted(ROOT.glob(MEMORY_SKILL_GLOB))
    if not memory_skill_paths:
        errors.append("no memory-bank skill agent metadata found")
    for path in memory_skill_paths:
        if allow_implicit(path) is not False:
            errors.append(f"{path}: memory-bank skills must keep allow_implicit_invocation: false")
    for rel in KNOWLEDGE_SKILLS:
        path = ROOT / rel
        if not path.exists():
            errors.append(f"missing knowledge skill agent metadata: {rel}")
            continue
        if allow_implicit(path) is not False:
            errors.append(f"{rel}: knowledge skills must start explicit-only")
    for rel, required_snippets in REQUIRED_TEXT.items():
        path = ROOT / rel
        if not path.exists():
            errors.append(f"missing contract file: {rel}")
            continue
        text = read_text(path)
        for snippet in required_snippets:
            if snippet not in text:
                errors.append(f"{rel}: missing explicit-only contract text: {snippet}")
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
