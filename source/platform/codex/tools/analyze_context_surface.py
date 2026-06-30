#!/usr/bin/env python3
"""Report advisory context-surface metrics for skill metadata and bodies."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _validation import load_yaml_file, read_text  # noqa: E402


SECTION_RE = re.compile(r"^##\s+", re.M)
RELATED_SKILL_RE = re.compile(r"`([a-z][a-z0-9-]+)`")


def skill_dirs(root: Path, namespace: str) -> list[Path]:
    base = root / namespace / "skills"
    if not base.exists():
        return []
    return sorted(path for path in base.iterdir() if (path / "SKILL.md").is_file())


def section_text(text: str, heading: str) -> str:
    marker = f"## {heading}"
    start = text.find(marker)
    if start < 0:
        return ""
    next_match = SECTION_RE.search(text, start + len(marker))
    end = next_match.start() if next_match else len(text)
    return text[start:end].strip()


def count_context_items(routing_card: str, key: str) -> int:
    lines = routing_card.splitlines()
    count = 0
    in_key = False
    key_indent = 0
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(f"{key}:"):
            in_key = True
            key_indent = len(line) - len(line.lstrip())
            continue
        if in_key:
            indent = len(line) - len(line.lstrip())
            if stripped and indent <= key_indent and not stripped.startswith("-"):
                break
            if stripped.startswith("- "):
                count += 1
    return count


def related_skill_count(text: str) -> int:
    related = section_text(text, "Related Skills")
    return len(set(RELATED_SKILL_RE.findall(related)))


def reference_count(skill_dir: Path) -> int:
    total = 0
    for folder in ["references", "docs"]:
        base = skill_dir / folder
        if base.exists():
            total += sum(1 for path in base.rglob("*") if path.is_file())
    return total


def load_agent(agent_file: Path) -> dict[str, Any]:
    if not agent_file.exists():
        return {}
    data = load_yaml_file(agent_file)
    return data if isinstance(data, dict) else {}


def metric_for(skill_dir: Path, root: Path, namespace: str) -> dict[str, Any]:
    skill_text = read_text(skill_dir / "SKILL.md")
    agent = load_agent(skill_dir / "agents" / "openai.yaml")
    interface = agent.get("interface") if isinstance(agent.get("interface"), dict) else {}
    policy = agent.get("policy") if isinstance(agent.get("policy"), dict) else {}
    routing_card = section_text(skill_text, "Routing Card")
    short_description = str(interface.get("short_description") or "")
    default_prompt = str(interface.get("default_prompt") or "")
    allow_implicit = bool(policy.get("allow_implicit_invocation"))
    surface = str(policy.get("invocation_surface") or "missing")
    initial_surface_chars = len(short_description) + len(default_prompt) + len(routing_card)
    static_size_score = len(skill_text) + len(default_prompt)
    activation_risk_score = 3 if allow_implicit else (2 if surface in {"selective_router", "support_only"} else 1)
    fanout_score = (
        count_context_items(routing_card, "must_read")
        + count_context_items(routing_card, "read_if_needed")
        + reference_count(skill_dir)
        + related_skill_count(skill_text)
    )
    leakage_risk_score = activation_risk_score * initial_surface_chars
    return {
        "skill_id": skill_dir.name,
        "namespace": namespace,
        "short_description_chars": len(short_description),
        "default_prompt_chars": len(default_prompt),
        "skill_body_chars": len(skill_text),
        "routing_card_chars": len(routing_card),
        "must_read_count": count_context_items(routing_card, "must_read"),
        "read_if_needed_count": count_context_items(routing_card, "read_if_needed"),
        "reference_count": reference_count(skill_dir),
        "support_skill_fanout": related_skill_count(skill_text),
        "allow_implicit_invocation": allow_implicit,
        "invocation_surface": surface,
        "static_size_score": static_size_score,
        "activation_risk_score": activation_risk_score,
        "fanout_score": fanout_score,
        "leakage_risk_score": leakage_risk_score,
    }


def collect_metrics(root: Path, namespace: str) -> list[dict[str, Any]]:
    return [metric_for(skill_dir, root, namespace) for skill_dir in skill_dirs(root, namespace)]


def markdown_report(metrics: list[dict[str, Any]], top: int) -> str:
    rows = sorted(metrics, key=lambda item: int(item["leakage_risk_score"]), reverse=True)[:top]
    lines = [
        "# Context Surface Advisory Report",
        "",
        "This report is advisory only. It does not fail release verification.",
        "",
        "| Skill | Surface | Implicit | Initial chars | Fanout | Leakage risk |",
        "| --- | --- | --- | ---: | ---: | ---: |",
    ]
    for item in rows:
        lines.append(
            "| {skill_id} | {invocation_surface} | {allow_implicit_invocation} | "
            "{initial_chars} | {fanout_score} | {leakage_risk_score} |".format(
                initial_chars=(
                    int(item["short_description_chars"])
                    + int(item["default_prompt_chars"])
                    + int(item["routing_card_chars"])
                ),
                **item,
            )
        )
    lines.append("")
    lines.append("Use this to inspect likely context leakage, not to penalize long explicit procedures.")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--namespace", choices=[".codex", ".claude"], default=".codex")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--top", type=int, default=12)
    args = parser.parse_args()
    metrics = collect_metrics(args.root.resolve(), args.namespace)
    if args.format == "json":
        print(json.dumps({"status": "advisory", "metrics": metrics}, indent=2, ensure_ascii=True))
    else:
        print(markdown_report(metrics, args.top), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
