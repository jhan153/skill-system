#!/usr/bin/env python3
"""Validate 8.0 Knowledge Store fixtures and context-pack linkage."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from _validation import load_json_file, load_yaml_file, validate_schema
from knowledge_policy import admissible_claims


BASE_FILES = {
    "sources": ("sources.yaml", "source.schema.json"),
    "claims": ("claims.yaml", "claim.schema.json"),
    "edges": ("edges.yaml", "edge.schema.json"),
}
PACK_SCHEMA = "context-pack.schema.json"
FEEDBACK_SCHEMA = "feedback-packet.schema.json"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_hash(data: dict[str, Any]) -> str:
    raw = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def load_checked_yaml(path: Path) -> tuple[Any | None, list[str]]:
    try:
        return load_yaml_file(path), []
    except Exception as exc:  # noqa: BLE001 - CLI validator should report malformed inputs.
        return None, [f"{path}: invalid YAML: {exc}"]


def load_checked_schema(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        return load_json_file(path), []
    except Exception as exc:  # noqa: BLE001 - CLI validator should report malformed schemas.
        return None, [f"{path}: invalid JSON schema: {exc}"]


def validate_against_schema(data: Any, schema_path: Path, label: str) -> list[str]:
    schema, errors = load_checked_schema(schema_path)
    if schema is None:
        return errors
    return [f"{label}: {error}" for error in validate_schema(data, schema)]


def duplicate_errors(records: list[dict[str, Any]], key: str, label: str) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for idx, record in enumerate(records):
        value = record.get(key)
        if not isinstance(value, str):
            continue
        if value in seen:
            errors.append(f"{label}[{idx}]: duplicate {key}: {value}")
        seen.add(value)
    return errors


def source_ids_from_ref_objects(refs: Any) -> list[str]:
    if not isinstance(refs, list):
        return []
    ids: list[str] = []
    for ref in refs:
        if isinstance(ref, dict) and isinstance(ref.get("source_id"), str):
            ids.append(ref["source_id"])
    return ids


def source_ids_from_strings(refs: Any) -> list[str]:
    if not isinstance(refs, list):
        return []
    return [ref for ref in refs if isinstance(ref, str) and ref.startswith("SRC-")]


def validate_repo_locator(source: dict[str, Any], root: Path) -> list[str]:
    source_id = source.get("source_id", "<unknown-source>")
    locator_type = source.get("locator_type")
    locator = source.get("locator")
    if isinstance(locator, str) and (locator.startswith("/Users/") or locator.startswith("/private/")):
        return [f"{source_id}: locator must not be an absolute local path"]
    if locator_type != "repo_path":
        return []
    if not isinstance(locator, str) or not locator.startswith("repo://"):
        return [f"{source_id}: repo_path locator must start with repo://"]
    rel = locator.removeprefix("repo://")
    if rel.startswith("/") or ".." in Path(rel).parts:
        return [f"{source_id}: repo_path locator must be repo-relative"]
    if not (root / rel).exists():
        return [f"{source_id}: repo_path locator target not found: {rel}"]
    return []


def validate_repo_digest(source: dict[str, Any], root: Path) -> list[str]:
    source_id = source.get("source_id", "<unknown-source>")
    if source.get("locator_type") != "repo_path" or source.get("freshness") != "current":
        return []
    locator = source.get("locator")
    if not isinstance(locator, str) or not locator.startswith("repo://"):
        return []
    rel = locator.removeprefix("repo://")
    path = root / rel
    if not path.exists() or not path.is_file():
        return []
    digest = source.get("content_digest") if isinstance(source.get("content_digest"), dict) else {}
    if digest.get("algorithm") != "sha256" or not isinstance(digest.get("value"), str):
        return [f"{source_id}: current repo source requires sha256 content_digest"]
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest["value"] != actual:
        return [f"{source_id}: current repo source digest mismatch: expected {digest['value']}, actual {actual}"]
    return []


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


def validate_source_metadata(source: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    source_id = source.get("source_id", "<unknown-source>")
    metadata = source.get("metadata") if isinstance(source.get("metadata"), dict) else {}
    if source.get("source_kind") == "plan_document" and "plan_lifecycle" not in metadata:
        errors.append(f"{source_id}: plan_document requires metadata.plan_lifecycle")
    if source.get("source_kind") == "kanboard_card":
        if source.get("locator_type") != "kanboard_card":
            errors.append(f"{source_id}: kanboard_card source requires locator_type kanboard_card")
        if "kanboard_status" not in metadata:
            errors.append(f"{source_id}: kanboard_card requires metadata.kanboard_status")
        if "kanboard_card_id" not in metadata:
            errors.append(f"{source_id}: kanboard_card requires metadata.kanboard_card_id")
    return errors


def source_is_active_for_admission(source: dict[str, Any]) -> bool:
    metadata = source.get("metadata") if isinstance(source.get("metadata"), dict) else {}
    if source.get("freshness") != "current":
        return False
    if source.get("source_kind") == "plan_document":
        return metadata.get("plan_lifecycle") in {None, "active"}
    if source.get("source_kind") == "kanboard_card":
        return metadata.get("kanboard_status") in {"active", "blocked"}
    return True


def validate_claim_refs(
    claims: list[dict[str, Any]],
    sources_by_id: dict[str, dict[str, Any]],
    claim_ids: set[str],
) -> list[str]:
    errors: list[str] = []
    for claim in claims:
        claim_id = str(claim.get("claim_id", "<unknown-claim>"))
        claim_freshness = claim.get("freshness")
        for source_id in source_ids_from_ref_objects(claim.get("source_refs")):
            source = sources_by_id.get(source_id)
            if source is None:
                errors.append(f"{claim_id}: source_ref not found: {source_id}")
                continue
            if claim_freshness == "current" and not source_is_active_for_admission(source):
                errors.append(f"{claim_id}: current claim references non-admissible source {source_id} ({source_state(source)})")
        for superseded in claim.get("supersedes", []) or []:
            if superseded not in claim_ids:
                errors.append(f"{claim_id}: supersedes unknown claim {superseded}")
    return errors


def validate_edge_refs(
    edges: list[dict[str, Any]],
    claim_ids: set[str],
    source_ids: set[str],
) -> list[str]:
    errors: list[str] = []
    for edge in edges:
        edge_id = str(edge.get("edge_id", "<unknown-edge>"))
        for field in ["from_claim_id", "to_claim_id"]:
            claim_id = edge.get(field)
            if isinstance(claim_id, str) and claim_id not in claim_ids:
                errors.append(f"{edge_id}: {field} not found: {claim_id}")
        for source_id in source_ids_from_strings(edge.get("source_refs")):
            if source_id not in source_ids:
                errors.append(f"{edge_id}: source_ref not found: {source_id}")
    return errors


def validate_context_pack_refs(
    pack: dict[str, Any],
    path: Path,
    claim_freshness: dict[str, str],
    edge_ids: set[str],
    source_ids: set[str],
    sources_by_id: dict[str, dict[str, Any]],
) -> list[str]:
    errors: list[str] = []
    label = path.name
    for claim in pack.get("admitted_claims", []) or []:
        claim_id = claim.get("claim_id")
        if isinstance(claim_id, str):
            if claim_id not in claim_freshness:
                errors.append(f"{label}: admitted claim not found: {claim_id}")
            elif claim_freshness[claim_id] != "current":
                errors.append(f"{label}: admitted claim is not current: {claim_id}")
        for source_id in source_ids_from_strings(claim.get("evidence_refs")):
            if source_id not in source_ids:
                errors.append(f"{label}: admitted claim evidence not found: {source_id}")
    for path_record in pack.get("relation_paths", []) or []:
        path_id = str(path_record.get("path_id", "<unknown-path>"))
        for edge_id in path_record.get("edge_ids", []) or []:
            if edge_id not in edge_ids:
                errors.append(f"{label}: {path_id} references unknown edge {edge_id}")
    for handle in pack.get("raw_source_handles", []) or []:
        source_id = handle.get("source_id")
        if isinstance(source_id, str) and source_id not in source_ids:
            errors.append(f"{label}: raw source handle not found: {source_id}")
        elif isinstance(source_id, str):
            source = sources_by_id[source_id]
            digest = source.get("content_digest") if isinstance(source.get("content_digest"), dict) else {}
            if handle.get("locator") != source.get("locator"):
                errors.append(f"{label}: raw source handle locator mismatch for {source_id}")
            if handle.get("revision") != digest.get("value"):
                errors.append(f"{label}: raw source handle revision mismatch for {source_id}")
    for handle in pack.get("expansion_handles", []) or []:
        claim_id = handle.get("claim_id")
        if isinstance(claim_id, str) and claim_id not in claim_freshness:
            errors.append(f"{label}: expansion handle claim not found: {claim_id}")
        for source_id in source_ids_from_strings(handle.get("source_ids")):
            if source_id not in source_ids:
                errors.append(f"{label}: expansion handle source not found: {source_id}")
    compilation = pack.get("compilation", {}) if isinstance(pack.get("compilation"), dict) else {}
    for source_id in source_ids_from_strings(compilation.get("source_snapshot")):
        if source_id not in source_ids:
            errors.append(f"{label}: source snapshot not found: {source_id}")
    pack_hash = pack.get("pack_hash")
    if isinstance(pack_hash, dict) and isinstance(pack_hash.get("value"), str):
        body = dict(pack)
        body.pop("pack_hash", None)
        if pack_hash["value"] != canonical_hash(body):
            errors.append(f"{label}: pack_hash does not match canonical pack body")
    return errors


def validate_feedback_refs(packet: dict[str, Any], path: Path, claim_ids: set[str], source_ids: set[str]) -> list[str]:
    errors: list[str] = []
    label = path.name
    for proposal in packet.get("proposals", []) or []:
        proposal_id = str(proposal.get("proposal_id", "<unknown-proposal>"))
        for source_id in source_ids_from_strings(proposal.get("evidence_refs")):
            if source_id not in source_ids:
                errors.append(f"{label}: {proposal_id} evidence_ref not found: {source_id}")
        candidate_claim = proposal.get("candidate_claim")
        if isinstance(candidate_claim, dict):
            for source_id in source_ids_from_strings(candidate_claim.get("source_refs")):
                if source_id not in source_ids:
                    errors.append(f"{label}: {proposal_id} candidate claim source not found: {source_id}")
        candidate_edge = proposal.get("candidate_edge")
        if isinstance(candidate_edge, dict):
            for field in ["from_claim_id", "to_claim_id"]:
                claim_id = candidate_edge.get(field)
                if isinstance(claim_id, str) and claim_id not in claim_ids:
                    errors.append(f"{label}: {proposal_id} candidate edge {field} not found: {claim_id}")
            for source_id in source_ids_from_strings(candidate_edge.get("source_refs")):
                if source_id not in source_ids:
                    errors.append(f"{label}: {proposal_id} candidate edge source not found: {source_id}")
    return errors


def yaml_files(path: Path) -> list[Path]:
    if not path.exists():
        return []
    return sorted([item for item in path.iterdir() if item.suffix in {".yaml", ".yml"} and item.is_file()])


def repo_relative(path: str) -> bool:
    return bool(path) and not path.startswith("/") and ".." not in Path(path).parts


def claim_source_ids(claim: dict[str, Any]) -> list[str]:
    return source_ids_from_ref_objects(claim.get("source_refs"))


def source_hashes_for(source_ids: list[str], sources_by_id: dict[str, dict[str, Any]]) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for source_id in source_ids:
        source = sources_by_id.get(source_id)
        digest = source.get("content_digest") if isinstance(source, dict) else None
        if isinstance(digest, dict) and isinstance(digest.get("value"), str):
            hashes[source_id] = digest["value"]
    return hashes


def load_runtime_index(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    rows: list[dict[str, Any]] = []
    errors: list[str] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"runtime/index.jsonl:{line_no}: invalid JSON: {exc}")
            continue
        if not isinstance(row, dict):
            errors.append(f"runtime/index.jsonl:{line_no}: expected JSON object")
            continue
        rows.append(row)
    return rows, errors


def validate_runtime_projection(store: Path, claims: list[dict[str, Any]], sources: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    projection_claims = admissible_claims(claims)
    projection_claim_ids = {claim["claim_id"] for claim in projection_claims if isinstance(claim.get("claim_id"), str)}
    claims_by_id = {claim["claim_id"]: claim for claim in projection_claims if isinstance(claim.get("claim_id"), str)}
    sources_by_id = {source["source_id"]: source for source in sources if isinstance(source.get("source_id"), str)}

    wiki_path = store / "wiki" / "index.md"
    if not wiki_path.exists():
        return ["missing runtime projection: wiki/index.md"]
    wiki_text = wiki_path.read_text(encoding="utf-8", errors="replace")
    wiki_hash = sha256_text(wiki_text)
    if "not a Source of Truth" not in wiki_text:
        errors.append("wiki/index.md must state that the projection is not a Source of Truth")
    for claim_id in sorted(projection_claim_ids):
        if claim_id not in wiki_text:
            errors.append(f"wiki/index.md missing admissible claim {claim_id}")

    index_path = store / "runtime" / "index.jsonl"
    if not index_path.exists():
        errors.append("missing runtime projection: runtime/index.jsonl")
        return errors
    rows, row_errors = load_runtime_index(index_path)
    errors.extend(row_errors)
    rows_by_claim = {row.get("claim_id"): row for row in rows if isinstance(row.get("claim_id"), str)}
    row_claim_ids = {claim_id for claim_id in rows_by_claim if isinstance(claim_id, str)}
    if row_claim_ids != projection_claim_ids:
        errors.append(f"runtime/index.jsonl claim set mismatch: expected {sorted(projection_claim_ids)}, got {sorted(row_claim_ids)}")
    for claim_id, row in rows_by_claim.items():
        claim = claims_by_id.get(claim_id)
        if not claim:
            continue
        if row.get("wiki_page_hash") != wiki_hash:
            errors.append(f"{claim_id}: runtime index wiki_page_hash mismatch")
        if row.get("freshness") != claim.get("freshness"):
            errors.append(f"{claim_id}: runtime index freshness mismatch")
        expected_source_ids = claim_source_ids(claim)
        if row.get("source_ids") != expected_source_ids:
            errors.append(f"{claim_id}: runtime index source_ids mismatch")
        if row.get("source_hashes") != source_hashes_for(expected_source_ids, sources_by_id):
            errors.append(f"{claim_id}: runtime index source_hashes mismatch")
        if row.get("source_states") != source_states_for(expected_source_ids, sources_by_id):
            errors.append(f"{claim_id}: runtime index source_states mismatch")
        card_ref = row.get("card_ref")
        if not isinstance(card_ref, str) or not repo_relative(card_ref):
            errors.append(f"{claim_id}: runtime card_ref must be store-relative")
            continue
        card_path = store / card_ref
        if not card_path.exists():
            errors.append(f"{claim_id}: runtime card not found: {card_ref}")
            continue
        card_text = card_path.read_text(encoding="utf-8", errors="replace")
        if claim_id not in card_text:
            errors.append(f"{claim_id}: runtime card missing claim_id")
        if wiki_hash not in card_text:
            errors.append(f"{claim_id}: runtime card missing wiki page hash")
        for source_state_value in source_states_for(expected_source_ids, sources_by_id).values():
            if source_state_value not in card_text:
                errors.append(f"{claim_id}: runtime card missing source state {source_state_value}")
    return errors


def validate_store(store: Path, schemas: Path, root: Path, require_projections: bool = False) -> list[str]:
    errors: list[str] = []
    loaded: dict[str, Any] = {}
    for key, (filename, schema_name) in BASE_FILES.items():
        path = store / filename
        if not path.exists():
            errors.append(f"missing required knowledge file: {path}")
            continue
        data, load_errors = load_checked_yaml(path)
        errors.extend(load_errors)
        if data is None:
            continue
        loaded[key] = data
        errors.extend(validate_against_schema(data, schemas / schema_name, filename))
    if errors:
        return errors

    sources = loaded["sources"].get("sources", []) if isinstance(loaded["sources"], dict) else []
    claims = loaded["claims"].get("claims", []) if isinstance(loaded["claims"], dict) else []
    edges = loaded["edges"].get("edges", []) if isinstance(loaded["edges"], dict) else []
    sources = [item for item in sources if isinstance(item, dict)]
    claims = [item for item in claims if isinstance(item, dict)]
    edges = [item for item in edges if isinstance(item, dict)]

    store_ids = {loaded[key].get("store_id") for key in BASE_FILES if isinstance(loaded.get(key), dict)}
    if len(store_ids) > 1:
        errors.append(f"base knowledge files disagree on store_id: {sorted(store_ids)}")

    errors.extend(duplicate_errors(sources, "source_id", "sources"))
    errors.extend(duplicate_errors(claims, "claim_id", "claims"))
    errors.extend(duplicate_errors(edges, "edge_id", "edges"))

    sources_by_id = {source["source_id"]: source for source in sources if isinstance(source.get("source_id"), str)}
    source_ids = set(sources_by_id)
    claim_freshness = {claim["claim_id"]: claim.get("freshness", "") for claim in claims if isinstance(claim.get("claim_id"), str)}
    claim_ids = set(claim_freshness)
    edge_ids = {edge["edge_id"] for edge in edges if isinstance(edge.get("edge_id"), str)}

    for source in sources:
        errors.extend(validate_repo_locator(source, root))
        errors.extend(validate_repo_digest(source, root))
        errors.extend(validate_source_metadata(source))
    errors.extend(validate_claim_refs(claims, sources_by_id, claim_ids))
    errors.extend(validate_edge_refs(edges, claim_ids, source_ids))

    context_pack_files = yaml_files(store / "context-packs")
    if not context_pack_files:
        errors.append("missing context pack fixture under context-packs/")
    for path in context_pack_files:
        pack, load_errors = load_checked_yaml(path)
        errors.extend(load_errors)
        if not isinstance(pack, dict):
            errors.append(f"{path}: expected top-level mapping")
            continue
        errors.extend(validate_against_schema(pack, schemas / PACK_SCHEMA, path.name))
        errors.extend(validate_context_pack_refs(pack, path, claim_freshness, edge_ids, source_ids, sources_by_id))

    feedback_files = yaml_files(store / "feedback-packets")
    if not feedback_files:
        errors.append("missing feedback packet fixture under feedback-packets/")
    for path in feedback_files:
        packet, load_errors = load_checked_yaml(path)
        errors.extend(load_errors)
        if not isinstance(packet, dict):
            errors.append(f"{path}: expected top-level mapping")
            continue
        errors.extend(validate_against_schema(packet, schemas / FEEDBACK_SCHEMA, path.name))
        errors.extend(validate_feedback_refs(packet, path, claim_ids, source_ids))

    if require_projections:
        errors.extend(validate_runtime_projection(store, claims, sources))

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("store", type=Path)
    parser.add_argument("--schemas", type=Path, default=Path(".codex/schemas/knowledge"))
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--require-projections", action="store_true")
    args = parser.parse_args()
    if not args.store.exists():
        print(f"FAIL: missing knowledge store: {args.store}")
        return 2
    if not args.schemas.exists():
        print(f"FAIL: missing knowledge schemas: {args.schemas}")
        return 2
    errors = validate_store(args.store, args.schemas, args.root.resolve(), args.require_projections)
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
