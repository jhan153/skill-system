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

from _validation import load_yaml_file, read_text, skill_dirs as iter_skill_dirs  # noqa: E402


SECTION_RE = re.compile(r"^##\s+", re.M)
RELATED_SKILL_RE = re.compile(r"`([a-z][a-z0-9-]+)`")
VOLATILE_CONTEXT_RE = re.compile(
    r"\b("
    r"latest|current|transient|temporary|raw|logs?|output|history|full\s+repo|"
    r"all\s+skills?|all\s+plans?|memory\s+bank|chat\s+history|field\s+feedback"
    r")\b",
    re.I,
)
REFERENCE_FANOUT_FREE_ALLOWANCE = 3
REFERENCE_PATH_RE = re.compile(r"(?:references|docs)/[^\s`,;]+", re.I)
SELECTIVE_REFERENCE_RE = re.compile(
    r"(do not load[^\n]{0,80}(?:entire|all)[^\n]{0,40}(?:references|templates)|"
    r"index(?:-first|/catalog| or catalog)|"
    r"load only[^\n]{0,80}(?:reference|template)|"
    r"1-3 (?:files|references|templates))",
    re.I,
)


def skill_dirs(root: Path, namespace: str) -> list[Path]:
    return iter_skill_dirs(root, namespace)


def section_text(text: str, heading: str) -> str:
    marker = f"## {heading}"
    start = text.find(marker)
    if start < 0:
        return ""
    next_match = SECTION_RE.search(text, start + len(marker))
    end = next_match.start() if next_match else len(text)
    return text[start:end].strip()


def context_items(routing_card: str, key: str) -> list[str]:
    lines = routing_card.splitlines()
    items: list[str] = []
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
                items.append(stripped[2:].strip())
    return items


def count_context_items(routing_card: str, key: str) -> int:
    return len(context_items(routing_card, key))


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


def volatile_context_mentions(text: str) -> int:
    return len(VOLATILE_CONTEXT_RE.findall(text))


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
    must_read_items = context_items(routing_card, "must_read")
    read_if_needed_items = context_items(routing_card, "read_if_needed")
    must_read_count = len(must_read_items)
    read_if_needed_count = len(read_if_needed_items)
    references = reference_count(skill_dir)
    eager_reference_count = sum(bool(REFERENCE_PATH_RE.search(item)) for item in must_read_items)
    conditional_reference_count = sum(bool(REFERENCE_PATH_RE.search(item)) for item in read_if_needed_items)
    selective_reference_admission = bool(SELECTIVE_REFERENCE_RE.search(skill_text))
    reference_inventory_risk = (
        0
        if references <= REFERENCE_FANOUT_FREE_ALLOWANCE
        else 1 + (references - REFERENCE_FANOUT_FREE_ALLOWANCE) // 10
    )
    support_fanout = related_skill_count(skill_text)
    fanout_score = (
        must_read_count
        + read_if_needed_count
        + support_fanout
        + (0 if selective_reference_admission else reference_inventory_risk)
    )
    leakage_risk_score = activation_risk_score * initial_surface_chars
    volatile_context_risk = activation_risk_score * volatile_context_mentions(
        "\n".join([short_description, default_prompt, routing_card])
    )
    reference_fanout_risk = (
        eager_reference_count * 2
        + max(0, conditional_reference_count - 8)
        + (0 if selective_reference_admission else reference_inventory_risk)
        + max(0, fanout_score - 12)
    )
    support_attachment_risk = (
        support_fanout
        + (3 if surface == "support_only" else 2 if surface in {"selective_router", "evidence_gate"} else 0)
        + (2 if allow_implicit else 0)
    )
    cache_stability_risk = (initial_surface_chars // 1000) + volatile_context_risk + (2 if allow_implicit else 0)
    token_cost_risk_score = (
        static_size_score // 5000
        + reference_fanout_risk
        + cache_stability_risk
        + volatile_context_risk
        + support_attachment_risk
    )
    return {
        "skill_id": skill_dir.name,
        "namespace": namespace,
        "short_description_chars": len(short_description),
        "default_prompt_chars": len(default_prompt),
        "skill_body_chars": len(skill_text),
        "routing_card_chars": len(routing_card),
        "initial_surface_chars": initial_surface_chars,
        "must_read_count": must_read_count,
        "read_if_needed_count": read_if_needed_count,
        "reference_count": references,
        "eager_reference_count": eager_reference_count,
        "conditional_reference_count": conditional_reference_count,
        "selective_reference_admission": selective_reference_admission,
        "reference_inventory_risk": reference_inventory_risk,
        "support_skill_fanout": support_fanout,
        "allow_implicit_invocation": allow_implicit,
        "invocation_surface": surface,
        "static_size_score": static_size_score,
        "activation_risk_score": activation_risk_score,
        "fanout_score": fanout_score,
        "leakage_risk_score": leakage_risk_score,
        "reference_fanout_risk": reference_fanout_risk,
        "cache_stability_risk": cache_stability_risk,
        "volatile_context_risk": volatile_context_risk,
        "support_attachment_risk": support_attachment_risk,
        "token_cost_risk_score": token_cost_risk_score,
    }


def collect_metrics(root: Path, namespace: str) -> list[dict[str, Any]]:
    return [metric_for(skill_dir, root, namespace) for skill_dir in skill_dirs(root, namespace)]


def markdown_report(metrics: list[dict[str, Any]], top: int) -> str:
    rows = sorted(metrics, key=lambda item: int(item["token_cost_risk_score"]), reverse=True)[:top]
    lines = [
        "# Context Surface Advisory Report",
        "",
        "This report is advisory only. It does not fail release verification or estimate billing tokens.",
        "",
        "| Skill | Surface | Implicit | Initial chars | Ref files | Selective | Fanout | Token-cost risk | Reference risk | Cache risk | Volatile risk | Support risk |",
        "| --- | --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in rows:
        lines.append(
            "| {skill_id} | {invocation_surface} | {allow_implicit_invocation} | "
            "{initial_surface_chars} | {reference_count} | {selective_reference_admission} | "
            "{fanout_score} | {token_cost_risk_score} | "
            "{reference_fanout_risk} | {cache_stability_risk} | {volatile_context_risk} | "
            "{support_attachment_risk} |".format(
                **item,
            )
        )
    lines.append("")
    lines.append(
        "Use this to inspect likely context leakage, reference fanout, cache-instability, volatile input, and support over-attachment risk. "
        "Do not treat the scores as measured cost savings."
    )
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
