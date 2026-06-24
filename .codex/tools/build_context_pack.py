#!/usr/bin/env python3
"""Build deterministic Wiki, Runtime Projection, and Context Pack artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from _validation import load_yaml_file
from knowledge_policy import admissible_claims, is_admissible_edge

try:
    import yaml
except ModuleNotFoundError as exc:  # pragma: no cover - covered by shared validation import path.
    raise SystemExit("FAIL: PyYAML is required for context pack generation") from exc


DEFAULT_GENERATED_AT = "2026-06-21T00:00:00Z"
DEFAULT_COMPILER_VERSION = "context-pack-builder-v1"
TOKEN_RE = re.compile(r"[A-Za-z0-9_.:-]+")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_hash(data: dict[str, Any]) -> str:
    raw = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def yaml_dump(data: dict[str, Any]) -> str:
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=False)


def load_store(store: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    sources = load_yaml_file(store / "sources.yaml").get("sources", [])
    claims = load_yaml_file(store / "claims.yaml").get("claims", [])
    edges = load_yaml_file(store / "edges.yaml").get("edges", [])
    return (
        [item for item in sources if isinstance(item, dict)],
        [item for item in claims if isinstance(item, dict)],
        [item for item in edges if isinstance(item, dict)],
    )


def source_ids_for_claim(claim: dict[str, Any]) -> list[str]:
    refs = claim.get("source_refs", [])
    if not isinstance(refs, list):
        return []
    return [ref["source_id"] for ref in refs if isinstance(ref, dict) and isinstance(ref.get("source_id"), str)]


def source_span_summary(claim: dict[str, Any]) -> str:
    refs = claim.get("source_refs", [])
    spans = [ref.get("span") for ref in refs if isinstance(ref, dict) and isinstance(ref.get("span"), str)]
    return ", ".join(spans) if spans else "source span unavailable"


def source_state(source: dict[str, Any]) -> str:
    metadata = source.get("metadata") if isinstance(source.get("metadata"), dict) else {}
    if source.get("source_kind") == "plan_document":
        return f"plan:{metadata.get('plan_lifecycle', source.get('lifecycle_state', 'unknown'))}"
    if source.get("source_kind") == "kanboard_card":
        return f"kanboard:{metadata.get('kanboard_status', source.get('lifecycle_state', 'unknown'))}"
    return f"{source.get('source_kind', 'source')}:{source.get('freshness', 'unknown')}"


def source_states_for(source_ids: list[str], sources_by_id: dict[str, dict[str, Any]]) -> dict[str, str]:
    return {
        source_id: source_state(sources_by_id[source_id])
        for source_id in source_ids
        if source_id in sources_by_id
    }


def tokens_for(value: str) -> set[str]:
    return {token.lower() for token in TOKEN_RE.findall(value)}


def claim_text(claim: dict[str, Any]) -> str:
    tags = " ".join(tag for tag in claim.get("tags", []) if isinstance(tag, str))
    return " ".join(
        item
        for item in [str(claim.get("claim_id", "")), str(claim.get("claim_type", "")), str(claim.get("statement", "")), tags]
        if item
    )


def task_seed_claims(claims: list[dict[str, Any]], task: str, primary_skill: str) -> list[dict[str, Any]]:
    query_tokens = tokens_for(task + " " + primary_skill)
    if not query_tokens:
        return []
    scored: list[tuple[int, dict[str, Any]]] = []
    for claim in claims:
        score = len(query_tokens & tokens_for(claim_text(claim)))
        if score > 0:
            scored.append((score, claim))
    return [claim for _, claim in sorted(scored, key=lambda item: (-item[0], item[1]["claim_id"]))]


def expand_claims_by_edges(
    seeds: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    max_hops: int,
) -> list[dict[str, Any]]:
    if max_hops <= 0 or not seeds:
        return seeds
    claims_by_id = {claim["claim_id"]: claim for claim in claims if isinstance(claim.get("claim_id"), str)}
    admitted = {claim["claim_id"] for claim in seeds}
    frontier = set(admitted)
    for _ in range(max_hops):
        next_frontier: set[str] = set()
        for edge in edges:
            if not is_admissible_edge(edge):
                continue
            left = edge.get("from_claim_id")
            right = edge.get("to_claim_id")
            if left in frontier and right in claims_by_id and right not in admitted:
                next_frontier.add(right)
            if right in frontier and left in claims_by_id and left not in admitted:
                next_frontier.add(left)
        admitted.update(next_frontier)
        frontier = next_frontier
        if not frontier:
            break
    return [claim for claim in claims if claim.get("claim_id") in admitted]


def apply_token_budget(claims: list[dict[str, Any]], token_budget: int) -> list[dict[str, Any]]:
    admitted: list[dict[str, Any]] = []
    used = 0
    for claim in claims:
        cost = max(1, len(tokens_for(str(claim.get("statement", "")))))
        if used + cost > token_budget:
            break
        admitted.append(claim)
        used += cost
    return admitted


def select_claims(
    claims: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    task: str,
    primary_skill: str,
    token_budget: int,
    max_hops: int,
) -> list[dict[str, Any]]:
    candidates = admissible_claims(claims)
    seeds = task_seed_claims(candidates, task, primary_skill)
    expanded = expand_claims_by_edges(seeds, candidates, edges, max_hops)
    return apply_token_budget(expanded, token_budget)


def active_edges(edges: list[dict[str, Any]], admitted_ids: set[str], max_hops: int) -> list[dict[str, Any]]:
    if max_hops <= 0:
        return []
    return [
        edge
        for edge in edges
        if edge.get("from_claim_id") in admitted_ids
        and edge.get("to_claim_id") in admitted_ids
        and is_admissible_edge(edge)
    ]


def projection_edges(edges: list[dict[str, Any]], admitted_ids: set[str]) -> list[dict[str, Any]]:
    return [
        edge
        for edge in edges
        if edge.get("from_claim_id") in admitted_ids
        and edge.get("to_claim_id") in admitted_ids
        and is_admissible_edge(edge)
    ]


def build_wiki(claims: list[dict[str, Any]], edges: list[dict[str, Any]]) -> str:
    lines = [
        "# Wiki Bank Projection",
        "",
        "Generated from accepted knowledge claims. This projection is not a Source of Truth.",
        "",
        "## Claims",
        "",
    ]
    for claim in claims:
        lines.extend(
            [
                f"### {claim['claim_id']}",
                "",
                f"- Type: `{claim['claim_type']}`",
                f"- Authority: `{claim['authority_class']}`",
                f"- Context density: `{claim['context_density']}`",
                f"- Freshness: `{claim['freshness']}`",
                f"- Statement: {claim['statement']}",
                f"- Source spans: {source_span_summary(claim)}",
                "",
            ]
        )
    lines.extend(["## Relations", ""])
    if not edges:
        lines.extend(["No relation edges admitted.", ""])
    for edge in edges:
        lines.extend(
            [
                f"- `{edge['edge_id']}`: `{edge['from_claim_id']}` {edge['relation_type']} `{edge['to_claim_id']}`",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def runtime_card(claim: dict[str, Any], sources_by_id: dict[str, dict[str, Any]], wiki_hash: str) -> str:
    source_ids = source_ids_for_claim(claim)
    source_hashes = [
        f"{source_id}={sources_by_id[source_id]['content_digest']['value']}"
        for source_id in source_ids
        if source_id in sources_by_id and isinstance(sources_by_id[source_id].get("content_digest"), dict)
    ]
    source_states = [
        f"{source_id}={source_state(sources_by_id[source_id])}"
        for source_id in source_ids
        if source_id in sources_by_id
    ]
    lines = [
        "---",
        f"claim_id: {claim['claim_id']}",
        f"freshness: {claim['freshness']}",
        f"wiki_page: ../wiki/index.md",
        f"wiki_page_hash: {wiki_hash}",
        "source_ids:",
    ]
    lines.extend(f"  - {source_id}" for source_id in source_ids)
    lines.append("source_hashes:")
    lines.extend(f"  - {item}" for item in source_hashes)
    lines.append("source_states:")
    lines.extend(f"  - {item}" for item in source_states)
    lines.extend(
        [
            "---",
            "",
            f"# {claim['claim_id']}",
            "",
            claim["statement"],
            "",
            f"Operational freshness: `{claim['freshness']}`.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def build_runtime_index(
    claims: list[dict[str, Any]],
    sources_by_id: dict[str, dict[str, Any]],
    wiki_hash: str,
) -> str:
    rows: list[str] = []
    for claim in claims:
        source_ids = source_ids_for_claim(claim)
        source_hashes = {
            source_id: sources_by_id[source_id]["content_digest"]["value"]
            for source_id in source_ids
            if source_id in sources_by_id and isinstance(sources_by_id[source_id].get("content_digest"), dict)
        }
        row = {
            "claim_id": claim["claim_id"],
            "card_ref": f"runtime/cards/{claim['claim_id']}.md",
            "claim_type": claim["claim_type"],
            "freshness": claim["freshness"],
            "source_ids": source_ids,
            "source_hashes": source_hashes,
            "source_states": source_states_for(source_ids, sources_by_id),
            "wiki_page": "wiki/index.md",
            "wiki_page_hash": wiki_hash,
        }
        rows.append(json.dumps(row, sort_keys=True, separators=(",", ":")))
    return "\n".join(rows) + "\n"


def build_context_pack(
    pack_id: str,
    task: str,
    primary_skill: str,
    claims: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    sources_by_id: dict[str, dict[str, Any]],
    generated_at: str,
    compiler_version: str,
    token_budget: int,
    max_hops: int,
) -> dict[str, Any]:
    source_ids = sorted({source_id for claim in claims for source_id in source_ids_for_claim(claim)})
    pack: dict[str, Any] = {
        "schema_version": 2,
        "pack_id": pack_id,
        "task": task,
        "primary_skill": primary_skill,
        "anchors": {
            "files": [
                sources_by_id[source_id]["locator"].removeprefix("repo://")
                for source_id in source_ids
                if source_id in sources_by_id and sources_by_id[source_id].get("locator_type") == "repo_path"
            ],
            "topics": sorted({tag for claim in claims for tag in claim.get("tags", []) if isinstance(tag, str)}),
            "decisions": [claim["claim_id"] for claim in claims if claim.get("claim_type") == "decision"],
            "components": [],
            "kanboard_cards": [
                sources_by_id[source_id]["locator"]
                for source_id in source_ids
                if source_id in sources_by_id and sources_by_id[source_id].get("locator_type") == "kanboard_card"
            ],
        },
        "admitted_claims": [
            {
                "claim_id": claim["claim_id"],
                "statement": claim["statement"],
                "authority_class": claim["authority_class"],
                "verification_state": claim["verification_state"],
                "freshness": claim["freshness"],
                "operational_effect": f"For task '{task}', apply this {claim['claim_type']} during skill routing and context lowering.",
                "evidence_refs": source_ids_for_claim(claim),
            }
            for claim in claims
        ],
        "relation_paths": [
            {
                "path_id": f"RP-{edge['edge_id'].removeprefix('KE-')}",
                "edge_ids": [edge["edge_id"]],
                "relation_summary": f"{edge['from_claim_id']} {edge['relation_type']} {edge['to_claim_id']}",
            }
            for edge in edges
        ],
        "raw_source_handles": [
            {
                "source_id": source_id,
                "locator": sources_by_id[source_id]["locator"],
                "revision": sources_by_id[source_id]["content_digest"]["value"],
                "load_when": f"Need raw evidence for source {source_id}.",
            }
            for source_id in source_ids
            if source_id in sources_by_id
        ],
        "expansion_handles": [
            {
                "handle_id": f"EH-{claim['claim_id'].removeprefix('KC-')}",
                "claim_id": claim["claim_id"],
                "source_ids": source_ids_for_claim(claim),
                "expand_when": f"Need high-context background for {claim['claim_id']}.",
            }
            for claim in claims
        ],
        "retrieval_trace": {
            "query_type": "lexical-graph-fixture",
            "lexical_hits": [claim["claim_id"] for claim in claims],
            "vector_hits": [],
            "graph_expansions": [edge["edge_id"] for edge in edges],
            "reranked": [claim["claim_id"] for claim in claims],
        },
        "compilation": {
            "knowledge_graph_version": "fixture",
            "index_version": "runtime-index-v1",
            "source_snapshot": source_ids,
            "max_hops": max_hops,
            "token_budget": token_budget,
            "generated_at": generated_at,
            "compiler_version": compiler_version,
        },
    }
    pack["pack_hash"] = {"algorithm": "sha256", "value": canonical_hash(pack)}
    return pack


def expected_projection_files(store: Path) -> dict[Path, str]:
    sources, claims, edges = load_store(store)
    projection_claims = admissible_claims(claims)
    projection_ids = {claim["claim_id"] for claim in projection_claims}
    projection_edge_records = projection_edges(edges, projection_ids)
    sources_by_id = {source["source_id"]: source for source in sources}
    wiki = build_wiki(projection_claims, projection_edge_records)
    wiki_hash = sha256_text(wiki)
    files: dict[Path, str] = {
        Path("wiki/index.md"): wiki,
        Path("runtime/index.jsonl"): build_runtime_index(projection_claims, sources_by_id, wiki_hash),
    }
    for claim in projection_claims:
        files[Path(f"runtime/cards/{claim['claim_id']}.md")] = runtime_card(claim, sources_by_id, wiki_hash)
    return files


def expected_context_pack_files(
    store: Path,
    pack_id: str,
    task: str,
    primary_skill: str,
    generated_at: str,
    compiler_version: str,
    token_budget: int,
    max_hops: int,
) -> dict[Path, str]:
    sources, claims, edges = load_store(store)
    admitted_claims = select_claims(claims, edges, task, primary_skill, token_budget, max_hops)
    admitted_ids = {claim["claim_id"] for claim in admitted_claims}
    admitted_edges = active_edges(edges, admitted_ids, max_hops)
    sources_by_id = {source["source_id"]: source for source in sources}
    pack = build_context_pack(
        pack_id,
        task,
        primary_skill,
        admitted_claims,
        admitted_edges,
        sources_by_id,
        generated_at,
        compiler_version,
        token_budget,
        max_hops,
    )
    return {Path(f"context-packs/{pack_id}.yaml"): yaml_dump(pack)}


def write_files(base: Path, files: dict[Path, str]) -> None:
    for rel, text in files.items():
        path = base / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def check_files(base: Path, files: dict[Path, str]) -> list[str]:
    errors: list[str] = []
    for rel, expected in files.items():
        path = base / rel
        if not path.exists():
            errors.append(f"missing generated file: {rel}")
            continue
        actual = path.read_text(encoding="utf-8")
        if actual != expected:
            errors.append(f"generated file is stale: {rel}")
    return errors


def run(args: argparse.Namespace) -> int:
    target = args.output or args.store
    rebuild_projections = args.rebuild_projections
    build_run_pack = args.build_run_pack
    if not rebuild_projections and not build_run_pack:
        rebuild_projections = args.check
        build_run_pack = True
    files: dict[Path, str] = {}
    if rebuild_projections:
        files.update(expected_projection_files(args.store))
    if build_run_pack:
        files.update(
            expected_context_pack_files(
                args.store,
                args.pack_id,
                args.task,
                args.primary_skill,
                args.generated_at,
                args.compiler_version,
                args.token_budget,
                args.max_hops,
            )
        )
    if args.check:
        errors = check_files(target, files)
        if errors:
            print("FAIL")
            for error in errors:
                print(f"- {error}")
            return 1
        print("PASS")
        return 0
    if args.output is None and not args.write:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            write_files(Path(tmp), files)
        print("PASS")
        return 0
    write_files(target, files)
    print("PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("store", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--pack-id", default="CP-20260621-101")
    parser.add_argument("--task", default="Compile the minimum context needed to continue 8.0 implementation.")
    parser.add_argument("--primary-skill", default="workflow-plan-runner")
    parser.add_argument("--generated-at", default=DEFAULT_GENERATED_AT)
    parser.add_argument("--compiler-version", default=DEFAULT_COMPILER_VERSION)
    parser.add_argument("--token-budget", type=int, default=1024)
    parser.add_argument("--max-hops", type=int, default=1)
    parser.add_argument("--rebuild-projections", action="store_true")
    parser.add_argument("--build-run-pack", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if not args.store.exists():
        print(f"FAIL: missing knowledge store: {args.store}")
        return 2
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
