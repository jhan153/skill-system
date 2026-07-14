#!/usr/bin/env python3
"""Snapshot and compare canonical skill instruction surfaces without claiming behavior from size alone."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import hmac
import io
import json
import re
import subprocess
import sys
import tarfile
import tempfile
from collections import Counter
from copy import deepcopy
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, Iterator

import yaml


sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _validation import load_yaml_file, validate_schema  # noqa: E402


SCHEMA_VERSION = 1
WORD_RE = re.compile(r"\S+", re.UNICODE)
FRONTMATTER_RE = re.compile(
    r"\A---[ \t]*\r?\n(?P<frontmatter>.*?)\r?\n---[ \t]*\r?\n(?P<body>.*)\Z",
    re.DOTALL,
)
SECTION_RE_TEMPLATE = r"(?ms)^## {heading}[ \t]*\r?\n(?P<body>.*?)(?=^## |\Z)"
JUNK_NAMES = {".DS_Store", "Thumbs.db", "__pycache__", ".pytest_cache"}
ADMISSION_CLASSES = (
    "must_read_exact",
    "read_if_needed_exact",
    "linked_exact",
    "not_explicitly_named",
)
SHARED_CONTEXT_KINDS = (
    "context_routing",
    "shared_doc",
    "shared_schema",
    "shared_script",
    "platform_instruction",
)
EVIDENCE_SCHEMA_VERSION = 2
RECEIPT_SCHEMA_VERSION = 1
INDEPENDENT_SIGNED_TIER = "independent_signed"
AGENT_REVIEWED_LOCAL_PILOT_TIER = "agent_reviewed_local_pilot"
LOCAL_PILOT_SKILLS = {
    "analysis-router",
    "design-frontend",
    "design-visual-regression",
    "workflow-comment-maintenance",
}
LOCAL_PILOT_EVAL_CONTRACT_DIGEST = "96f0e0155f873dceb9a634183e4e20ad61520be3ba8daf04817c015d66332a81"
LOCAL_PILOT_ACCEPTED_STATE_PATH = Path("docs/reference/skill-diet/local-pilot-accepted-state.json")
LOCAL_PILOT_ACCEPTED_STATE_SHA256 = "fc21111ce8e7549682fba9f15843c6a60fb754a74530d781f939c88f43aeabc8"
PINNED_REVIEW_TRUST_STORE_SHA256 = "4602f335d986a8634e8b3230efac26a106155d089f374e342f0783cfbd3cc052"
RSA_SHA256_DIGEST_INFO_PREFIX = bytes.fromhex("3031300d060960864801650304020105000420")
OVERLAY_MONOTONIC_FIELDS = {
    "schema_version",
    "expected_supporting_skills",
    "should_not_trigger",
    "expected_behaviors",
    "forbidden_behaviors",
    "required_evidence",
    "required_eval_mode",
    "behavior_contract_owners",
    "scenario_tags",
}
EXECUTION_CONTRACT_FIELDS = (
    "host_id",
    "prompt_sha256",
    "input_sha256",
    "permission_profile_sha256",
    "validator_sha256",
)


class DietError(RuntimeError):
    """Raised for fail-closed snapshot or comparison input errors."""


def text_measure(text: str) -> dict[str, int]:
    return {
        "words": len(WORD_RE.findall(text)),
        "characters": len(text),
        "utf8_bytes": len(text.encode("utf-8")),
    }


def bytes_measure(data: bytes) -> dict[str, int | None | str]:
    result: dict[str, int | None | str] = {
        "words": None,
        "characters": None,
        "utf8_bytes": len(data),
        "text_status": "binary",
    }
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        return result
    result.update(text_measure(text))
    result["text_status"] = "utf8"
    return result


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_json(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(encoded)


def parse_skill_text(text: str, path: Path) -> tuple[dict[str, Any], str]:
    match = FRONTMATTER_RE.match(text)
    if match is None:
        raise DietError(f"{path}: SKILL.md requires line-delimited YAML frontmatter")
    frontmatter = yaml.safe_load(match.group("frontmatter"))
    if not isinstance(frontmatter, dict):
        raise DietError(f"{path}: frontmatter must be a mapping")
    if not isinstance(frontmatter.get("name"), str) or not isinstance(frontmatter.get("description"), str):
        raise DietError(f"{path}: frontmatter name and description are required strings")
    return frontmatter, match.group("body").lstrip()


def section_body(text: str, heading: str) -> str:
    pattern = re.compile(SECTION_RE_TEMPLATE.format(heading=re.escape(heading)))
    match = pattern.search(text)
    return match.group("body").rstrip() if match else ""


def nested_list_items(section: str, key: str) -> list[str]:
    items: list[str] = []
    active = False
    key_indent = 0
    for line in section.splitlines():
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())
        if stripped == f"{key}:":
            active = True
            key_indent = indent
            continue
        if not active:
            continue
        if stripped and indent <= key_indent:
            break
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
    return items


def scalar_field(section: str, key: str) -> str | None:
    match = re.search(rf"(?m)^- {re.escape(key)}:\s*(\S.*?)\s*$", section)
    return match.group(1) if match else None


def is_junk(path: Path) -> bool:
    return any(part in JUNK_NAMES or part.startswith("._") or part.endswith((".pyc", ".pyo")) for part in path.parts)


def resource_kind(rel: Path) -> str:
    parts = rel.parts
    if parts[:2] == ("agents", "openai.yaml") or (parts and parts[0] == "agents"):
        return "agent_metadata"
    if (parts and parts[0] in {"references", "docs"}) or rel.as_posix() == "reference.md":
        return "instruction_reference"
    if parts and parts[0] == "scripts":
        return "script"
    if parts and parts[0] in {"schemas", "schema"}:
        return "schema_contract"
    if ".schema." in rel.name or rel.name.endswith(("-schema.json", "-schema.yaml", "-schema.yml")):
        return "schema_contract"
    if parts and parts[0] == "assets":
        return "asset"
    return "other"


def exact_mention(text: str, rel: Path) -> bool:
    candidates = {rel.as_posix(), rel.name}
    return any(candidate and candidate in text for candidate in candidates)


def classify_admission(rel: Path, body: str, must_read: list[str], read_if_needed: list[str]) -> str:
    must_text = "\n".join(must_read)
    conditional_text = "\n".join(read_if_needed)
    if exact_mention(must_text, rel):
        return "must_read_exact"
    if exact_mention(conditional_text, rel):
        return "read_if_needed_exact"
    if exact_mention(body, rel):
        return "linked_exact"
    return "not_explicitly_named"


def load_agent(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    payload = load_yaml_file(path)
    if not isinstance(payload, dict):
        raise DietError(f"{path}: agent metadata must be a mapping")
    return payload


def load_eval_cases(source: Path) -> dict[str, dict[str, Any]]:
    cases: dict[str, dict[str, Any]] = {}
    eval_root = source / "shared" / "eval"
    for manifest in sorted(eval_root.glob("*_cases.yaml")):
        payload = load_yaml_file(manifest)
        if not isinstance(payload, dict) or not isinstance(payload.get("cases"), list):
            continue
        for raw in payload["cases"]:
            if not isinstance(raw, dict) or not isinstance(raw.get("case_id"), str):
                continue
            case_id = raw["case_id"]
            if case_id in cases:
                raise DietError(f"duplicate eval case_id {case_id!r}")
            case = dict(raw)
            case["_case_ref"] = f"{manifest.name}#{case_id}"
            cases[case_id] = case
    return cases


def validate_eval_case_skill_ids(cases: dict[str, dict[str, Any]], skill_ids: set[str]) -> None:
    for case_id, case in cases.items():
        primary = case.get("expected_primary_skill")
        if primary is not None and (not isinstance(primary, str) or primary not in skill_ids):
            raise DietError(f"{case_id}: expected_primary_skill must name a canonical skill or null")
        lanes: dict[str, list[str]] = {}
        for field in ("expected_supporting_skills", "should_not_trigger", "behavior_contract_owners"):
            value = case.get(field) or []
            if (
                not isinstance(value, list)
                or any(not isinstance(item, str) or item not in skill_ids for item in value)
                or len(value) != len(set(value))
            ):
                raise DietError(f"{case_id}: {field} must contain unique canonical skill ids")
            lanes[field] = value
        supporting = set(lanes["expected_supporting_skills"])
        negative = set(lanes["should_not_trigger"])
        owners = set(lanes["behavior_contract_owners"])
        positive = ({primary} if isinstance(primary, str) else set()) | supporting
        if (isinstance(primary, str) and primary in supporting | negative) or supporting & negative:
            raise DietError(f"{case_id}: primary/supporting/negative route lanes must be disjoint")
        associations = positive | negative
        if not associations:
            raise DietError(f"{case_id}: eval case must associate at least one canonical skill")
        if not owners <= associations:
            raise DietError(f"{case_id}: behavior_contract_owners must be route-associated skills")


def load_observed_runs(source: Path, cases: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    runs: list[dict[str, Any]] = []
    observed = source / "shared" / "eval" / "observed-runs"
    if not observed.is_dir():
        return runs
    for path in sorted(observed.rglob("*.yaml")):
        if "artifacts" in path.relative_to(observed).parts:
            continue
        payload = load_yaml_file(path)
        if not isinstance(payload, dict):
            continue
        if not all(isinstance(payload.get(key), str) for key in ("run_id", "case_id", "bundle_version")):
            continue
        case = cases.get(str(payload["case_id"]))
        expected_route = case.get("expected_primary_skill") if case else None
        observed_route = payload.get("observed_route")
        case_exists = case is not None
        route_matches = case_exists and expected_route is not None and observed_route == expected_route
        source_bound = bool(payload.get("source_commit") and payload.get("skills_tree"))
        runs.append(
            {
                "run_id": payload["run_id"],
                "case_id": payload["case_id"],
                "bundle_version": payload["bundle_version"],
                "observed_route": observed_route,
                "model": payload.get("model"),
                "path": path.relative_to(source.parent).as_posix(),
                "inventory_status": "declared_route_match" if route_matches else "invalid_or_unmatched",
                "case_exists": case_exists,
                "route_matches_declared_primary": route_matches,
                "source_bound": source_bound,
            }
        )
    return runs


def oracle_digest(case: dict[str, Any]) -> str:
    return sha256_json({key: value for key, value in case.items() if not key.startswith("_")})


def overlay_stable_digest(case: dict[str, Any]) -> str:
    return sha256_json(
        {
            key: value
            for key, value in case.items()
            if not key.startswith("_") and key not in OVERLAY_MONOTONIC_FIELDS
        }
    )


def required_evidence_types(case: dict[str, Any]) -> list[str]:
    evidence = case.get("required_evidence")
    if not isinstance(evidence, list):
        return []
    return sorted(
        {
            str(item["type"])
            for item in evidence
            if isinstance(item, dict) and isinstance(item.get("type"), str) and item["type"]
        }
    )


def required_evidence_contracts(case: dict[str, Any]) -> list[dict[str, str]]:
    evidence = case.get("required_evidence")
    if not isinstance(evidence, list):
        return []
    return sorted(
        (
            {
                "type": str(item["type"]),
                "requirement_sha256": sha256_json(item),
            }
            for item in evidence
            if isinstance(item, dict) and isinstance(item.get("type"), str) and item["type"]
        ),
        key=lambda item: (item["type"], item["requirement_sha256"]),
    )


def eval_coverage(skill_id: str, cases: dict[str, dict[str, Any]], runs: list[dict[str, Any]], bundle: str) -> dict[str, Any]:
    primary: list[str] = []
    supporting: list[str] = []
    negative: list[str] = []
    structured: list[str] = []
    structured_negative: list[str] = []
    contracts: dict[str, str] = {}
    overlay_stable_digests: dict[str, str] = {}
    case_sources: dict[str, str] = {}
    case_modes: dict[str, str] = {}
    case_required_evidence: dict[str, list[str]] = {}
    case_required_evidence_contracts: dict[str, list[dict[str, str]]] = {}
    case_schema_versions: dict[str, int | None] = {}
    case_expected_primary: dict[str, str | None] = {}
    case_expected_supporting: dict[str, list[str]] = {}
    case_should_not_trigger: dict[str, list[str]] = {}
    case_expected_behaviors: dict[str, list[str]] = {}
    case_forbidden_behaviors: dict[str, list[str]] = {}
    case_behavior_contract_owners: dict[str, list[str]] = {}
    case_scenario_tags: dict[str, list[str]] = {}
    explicit_edge_cases: list[str] = []
    for case in cases.values():
        ref = str(case["case_id"])
        is_primary = case.get("expected_primary_skill") == skill_id
        is_supporting = skill_id in (case.get("expected_supporting_skills") or [])
        is_negative = skill_id in (case.get("should_not_trigger") or [])
        owners = case.get("behavior_contract_owners")
        tags = case.get("scenario_tags")
        is_behavior_owner = is_primary or (isinstance(owners, list) and skill_id in owners)
        if is_primary:
            primary.append(ref)
        if is_supporting:
            supporting.append(ref)
        if is_negative:
            negative.append(ref)
        if is_behavior_owner and case.get("schema_version") == 2:
            structured.append(ref)
        if is_negative and not is_primary and not is_supporting and case.get("schema_version") == 2 and required_evidence_contracts(case):
            structured_negative.append(ref)
        if is_primary or is_supporting or is_negative:
            contracts[ref] = oracle_digest(case)
            overlay_stable_digests[ref] = overlay_stable_digest(case)
            case_sources[ref] = str(case["_case_ref"])
            case_modes[case["case_id"]] = str(case.get("required_eval_mode") or "declared_only")
            case_required_evidence[ref] = required_evidence_types(case)
            case_required_evidence_contracts[ref] = required_evidence_contracts(case)
            schema_version = case.get("schema_version")
            case_schema_versions[ref] = schema_version if isinstance(schema_version, int) else None
            expected_primary = case.get("expected_primary_skill")
            case_expected_primary[ref] = expected_primary if isinstance(expected_primary, str) else None
            case_expected_supporting[ref] = sorted(
                item for item in (case.get("expected_supporting_skills") or []) if isinstance(item, str)
            )
            case_should_not_trigger[ref] = sorted(
                item for item in (case.get("should_not_trigger") or []) if isinstance(item, str)
            )
            case_expected_behaviors[ref] = sorted(
                item for item in (case.get("expected_behaviors") or []) if isinstance(item, str)
            )
            case_forbidden_behaviors[ref] = sorted(
                item for item in (case.get("forbidden_behaviors") or []) if isinstance(item, str)
            )
            case_behavior_contract_owners[ref] = sorted(
                item for item in (case.get("behavior_contract_owners") or []) if isinstance(item, str)
            )
            case_scenario_tags[ref] = sorted(
                item for item in (case.get("scenario_tags") or []) if isinstance(item, str)
            )
        if (
            isinstance(owners, list)
            and skill_id in owners
            and isinstance(tags, list)
            and bool({"edge", "safety"} & set(tags))
            and case.get("schema_version") == 2
            and bool(required_evidence_contracts(case))
        ):
            explicit_edge_cases.append(ref)

    observed_primary: list[dict[str, Any]] = []
    for run in runs:
        if run.get("observed_route") != skill_id or run.get("inventory_status") != "declared_route_match":
            continue
        item = dict(run)
        item["required_eval_mode"] = case_modes.get(str(run["case_id"]), "unknown")
        observed_primary.append(item)

    current_runs = [item for item in observed_primary if item["bundle_version"] == bundle]
    return {
        "declared_route_cases": {
            "primary": sorted(primary),
            "supporting": sorted(supporting),
            "negative": sorted(negative),
        },
        "structured_behavior_candidates": sorted(structured),
        "structured_observed_candidates": sorted(
            case_id
            for case_id in structured
            if case_modes.get(case_id) in {"host-assisted", "replay"}
            and bool(case_required_evidence_contracts.get(case_id))
        ),
        "structured_negative_candidates": sorted(structured_negative),
        "case_oracle_digests": dict(sorted(contracts.items())),
        "case_overlay_stable_digests": dict(sorted(overlay_stable_digests.items())),
        "case_sources": dict(sorted(case_sources.items())),
        "case_required_eval_modes": dict(sorted(case_modes.items())),
        "case_required_evidence_types": dict(sorted(case_required_evidence.items())),
        "case_required_evidence_contracts": dict(sorted(case_required_evidence_contracts.items())),
        "case_schema_versions": dict(sorted(case_schema_versions.items())),
        "case_expected_primary_skills": dict(sorted(case_expected_primary.items())),
        "case_expected_supporting_skills": dict(sorted(case_expected_supporting.items())),
        "case_should_not_trigger": dict(sorted(case_should_not_trigger.items())),
        "case_expected_behaviors": dict(sorted(case_expected_behaviors.items())),
        "case_forbidden_behaviors": dict(sorted(case_forbidden_behaviors.items())),
        "case_behavior_contract_owners": dict(sorted(case_behavior_contract_owners.items())),
        "case_scenario_tags": dict(sorted(case_scenario_tags.items())),
        "edge_status": "explicit" if explicit_edge_cases else "unclassified_no_schema_field",
        "explicit_edge_cases": sorted(explicit_edge_cases),
        "observed_primary_run_inventory": observed_primary,
        "current_bundle_run_inventory_ids": sorted(item["run_id"] for item in current_runs),
        "current_bundle_source_bound_run_ids": sorted(
            item["run_id"] for item in current_runs if item.get("source_bound") is True
        ),
        "supporting_and_negative_observation": "not_instrumented",
    }


def measure_skill(skill_dir: Path, source: Path, cases: dict[str, dict[str, Any]], runs: list[dict[str, Any]], bundle: str) -> dict[str, Any]:
    skill_path = skill_dir / "SKILL.md"
    skill_bytes = skill_path.read_bytes()
    try:
        skill_text = skill_bytes.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise DietError(f"{skill_path}: SKILL.md must be valid UTF-8") from exc
    frontmatter, body = parse_skill_text(skill_text, skill_path)
    skill_id = skill_dir.name
    if frontmatter["name"] != skill_id:
        raise DietError(f"{skill_path}: frontmatter name {frontmatter['name']!r} != directory {skill_id!r}")

    routing_card = section_body(body, "Routing Card")
    must_read = nested_list_items(routing_card, "must_read")
    read_if_needed = nested_list_items(routing_card, "read_if_needed")
    do_not_load = nested_list_items(routing_card, "do_not_load_by_default")
    agent_path = skill_dir / "agents" / "openai.yaml"
    agent = load_agent(agent_path)
    interface = agent.get("interface") if isinstance(agent.get("interface"), dict) else {}
    policy = agent.get("policy") if isinstance(agent.get("policy"), dict) else {}

    resources: list[dict[str, Any]] = []
    for path in sorted(candidate for candidate in skill_dir.rglob("*") if candidate.is_file()):
        rel = path.relative_to(skill_dir)
        if rel.as_posix() == "SKILL.md" or is_junk(rel):
            continue
        data = path.read_bytes()
        kind = resource_kind(rel)
        item: dict[str, Any] = {
            "path": rel.as_posix(),
            "kind": kind,
            "sha256": sha256_bytes(data),
            "size": bytes_measure(data),
        }
        if kind == "instruction_reference":
            item["admission_class"] = classify_admission(rel, body, must_read, read_if_needed)
            item["admission_claim"] = "declared_exact_only"
        resources.append(item)

    description = str(frontmatter["description"])
    short_description = str(interface.get("short_description") or "")
    default_prompt = str(interface.get("default_prompt") or "")
    return {
        "skill_id": skill_id,
        "source_path": skill_path.relative_to(source.parent).as_posix(),
        "source_sha256": sha256_bytes(skill_bytes),
        "measurements": {
            "skill_file": text_measure(skill_text),
            "body": text_measure(body),
            "routing_card": text_measure(routing_card),
            "frontmatter_description": text_measure(description),
            "agent_short_description": text_measure(short_description),
            "agent_default_prompt": text_measure(default_prompt),
        },
        "content_digests": {
            "body": sha256_bytes(body.encode("utf-8")),
            "routing_card": sha256_bytes(routing_card.encode("utf-8")),
            "frontmatter_description": sha256_bytes(description.encode("utf-8")),
            "agent_short_description": sha256_bytes(short_description.encode("utf-8")),
            "agent_default_prompt": sha256_bytes(default_prompt.encode("utf-8")),
            "context_targets": sha256_json(
                {
                    "must_read": must_read,
                    "read_if_needed": read_if_needed,
                    "do_not_load_by_default": do_not_load,
                }
            ),
            "resource_inventory": sha256_json(
                [
                    {
                        "path": item["path"],
                        "kind": item["kind"],
                        "sha256": item["sha256"],
                        "admission_class": item.get("admission_class"),
                    }
                    for item in resources
                ]
            ),
        },
        "routing": {
            "card_role": scalar_field(routing_card, "role"),
            "invocation_surface": policy.get("invocation_surface"),
            "allow_implicit_invocation": policy.get("allow_implicit_invocation"),
            "may_own_execution": policy.get("may_own_execution"),
            "may_write": policy.get("may_write"),
            "may_block_completion": policy.get("may_block_completion"),
        },
        "context_targets": {
            "must_read": must_read,
            "read_if_needed": read_if_needed,
            "do_not_load_by_default": do_not_load,
        },
        "resources": resources,
        "eval_coverage": eval_coverage(skill_id, cases, runs, bundle),
        "observed_admission": {
            "status": "unverified",
            "words": None,
            "utf8_bytes": None,
            "receipt_ids": [],
        },
    }


def add_metric(target: dict[str, int], metric: dict[str, Any]) -> None:
    for key in ("words", "characters", "utf8_bytes"):
        value = metric.get(key)
        if isinstance(value, int):
            target[key] += value


def empty_metric() -> dict[str, int]:
    return {"words": 0, "characters": 0, "utf8_bytes": 0}


def aggregate(skills: list[dict[str, Any]], bundle: str, runs: list[dict[str, Any]]) -> dict[str, Any]:
    metrics = {
        "skill_file": empty_metric(),
        "body": empty_metric(),
        "routing_card": empty_metric(),
        "frontmatter_description": empty_metric(),
        "agent_short_description": empty_metric(),
        "agent_default_prompt": empty_metric(),
        "owned_inventory": empty_metric(),
    }
    resource_kinds: Counter[str] = Counter()
    resource_bytes: Counter[str] = Counter()
    admission_counts: Counter[str] = Counter()
    admission_bytes: Counter[str] = Counter()
    surfaces: Counter[str] = Counter()
    implicit: list[str] = []
    without_declared_positive: list[str] = []
    without_declared_negative: list[str] = []
    without_structured: list[str] = []
    without_observable_structured: list[str] = []
    without_structured_negative: list[str] = []
    without_explicit_edge: list[str] = []
    without_current_run: list[str] = []
    for skill in skills:
        for key in metrics:
            if key == "owned_inventory":
                continue
            add_metric(metrics[key], skill["measurements"][key])
        add_metric(metrics["owned_inventory"], skill["measurements"]["skill_file"])
        surface = str(skill["routing"].get("invocation_surface") or "missing")
        surfaces[surface] += 1
        if skill["routing"].get("allow_implicit_invocation") is True:
            implicit.append(skill["skill_id"])
        declared = skill["eval_coverage"]["declared_route_cases"]
        if not declared["primary"] and not declared["supporting"]:
            without_declared_positive.append(skill["skill_id"])
        if not declared["negative"]:
            without_declared_negative.append(skill["skill_id"])
        if not skill["eval_coverage"]["structured_behavior_candidates"]:
            without_structured.append(skill["skill_id"])
        if not skill["eval_coverage"]["structured_observed_candidates"]:
            without_observable_structured.append(skill["skill_id"])
        if not skill["eval_coverage"]["structured_negative_candidates"]:
            without_structured_negative.append(skill["skill_id"])
        if not skill["eval_coverage"]["explicit_edge_cases"]:
            without_explicit_edge.append(skill["skill_id"])
        if not skill["eval_coverage"]["current_bundle_source_bound_run_ids"]:
            without_current_run.append(skill["skill_id"])
        for resource in skill["resources"]:
            kind = resource["kind"]
            resource_kinds[kind] += 1
            resource_bytes[kind] += int(resource["size"]["utf8_bytes"])
            add_metric(metrics["owned_inventory"], resource["size"])
            if kind == "instruction_reference":
                admission = resource["admission_class"]
                admission_counts[admission] += 1
                admission_bytes[admission] += int(resource["size"]["utf8_bytes"])

    current_inventory = sorted(
        run["run_id"]
        for run in runs
        if run["bundle_version"] == bundle and run["inventory_status"] == "declared_route_match"
    )
    current_source_bound = sorted(
        run["run_id"]
        for run in runs
        if run["bundle_version"] == bundle
        and run["inventory_status"] == "declared_route_match"
        and run["source_bound"] is True
    )
    invalid_inventory = sorted(run["run_id"] for run in runs if run["inventory_status"] != "declared_route_match")
    historical_versions = Counter(run["bundle_version"] for run in runs if run["bundle_version"] != bundle)
    return {
        "skill_count": len(skills),
        "measurements": metrics,
        "resources": {
            "count": sum(resource_kinds.values()),
            "by_kind_count": dict(sorted(resource_kinds.items())),
            "by_kind_utf8_bytes": dict(sorted(resource_bytes.items())),
        },
        "declared_exact_reference_admission": {
            "by_class_count": {key: admission_counts.get(key, 0) for key in ADMISSION_CLASSES},
            "by_class_utf8_bytes": {key: admission_bytes.get(key, 0) for key in ADMISSION_CLASSES},
            "claim_limit": "exact_file_mentions_only_not_observed_admission",
        },
        "invocation": {
            "surface_counts": dict(sorted(surfaces.items())),
            "implicit_skill_ids": sorted(implicit),
        },
        "eval_gaps": {
            "skills_without_declared_positive": sorted(without_declared_positive),
            "skills_without_declared_negative": sorted(without_declared_negative),
            "skills_without_structured_primary_contract": sorted(without_structured),
            "skills_without_observable_structured_positive": sorted(without_observable_structured),
            "skills_without_structured_negative": sorted(without_structured_negative),
            "skills_without_explicit_edge": sorted(without_explicit_edge),
            "skills_without_current_bundle_observed_run": sorted(without_current_run),
            "explicit_edge_coverage": "unclassified_no_schema_field",
        },
        "forward_evidence": {
            "status": "source_bound_inventory_only" if current_source_bound else "missing_source_bound_current_bundle",
            "current_bundle_version": bundle,
            "current_bundle_run_inventory_ids": current_inventory,
            "current_bundle_source_bound_run_ids": current_source_bound,
            "invalid_or_unmatched_run_ids": invalid_inventory,
            "historical_run_counts": dict(sorted(historical_versions.items())),
        },
        "observed_admission": {
            "status": "unverified",
            "words": None,
            "utf8_bytes": None,
            "receipt_count": 0,
        },
    }


def bundle_version(source: Path) -> str:
    payload = load_yaml_file(source / "plugins" / "core.yaml")
    version = payload.get("version") if isinstance(payload, dict) else None
    if not isinstance(version, str):
        raise DietError("source/plugins/core.yaml has no string version")
    return version


def input_digest(source: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(
        candidate
        for candidate in source.rglob("*")
        if candidate.is_file() and not is_junk(candidate.relative_to(source))
    ):
        rel = path.relative_to(source.parent).as_posix().encode("utf-8")
        digest.update(len(rel).to_bytes(4, "big"))
        digest.update(rel)
        data = path.read_bytes()
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return digest.hexdigest()


def shared_context_kind(path: Path, source: Path) -> str | None:
    rel = path.relative_to(source)
    if rel.as_posix() == "shared/context-routing.md":
        return "context_routing"
    if rel.parts[:2] == ("shared", "docs"):
        return "shared_doc"
    if rel.parts[:2] == ("shared", "schemas"):
        return "shared_schema"
    if rel.parts[:2] == ("shared", "scripts"):
        return "shared_script"
    if rel.as_posix() in {"platform/codex/AGENTS.md", "platform/claude/CLAUDE.md"}:
        return "platform_instruction"
    return None


def shared_context_aliases(path: Path, source: Path) -> set[str]:
    source_rel = path.relative_to(source).as_posix()
    repo_rel = path.relative_to(source.parent).as_posix()
    candidates = {source_rel, repo_rel, path.name}
    if source_rel.startswith("shared/docs/"):
        suffix = source_rel.removeprefix("shared/docs/")
        candidates.update({f".codex/docs/{suffix}", f".claude/docs/{suffix}"})
    if source_rel.startswith("shared/schemas/"):
        suffix = source_rel.removeprefix("shared/schemas/")
        candidates.update({f".codex/schemas/{suffix}", f".claude/schemas/{suffix}"})
    return candidates


def collect_shared_context_inventory(source: Path) -> list[dict[str, Any]]:
    skill_texts = {
        skill_file.parent.name: skill_file.read_text(encoding="utf-8", errors="strict")
        for skill_file in sorted((source / "skills").glob("*/SKILL.md"))
    }
    all_skill_ids = set(skill_texts)
    working: list[dict[str, Any]] = []
    for path in sorted(candidate for candidate in source.rglob("*") if candidate.is_file()):
        kind = shared_context_kind(path, source)
        if kind is None:
            continue
        data = path.read_bytes()
        try:
            text = data.decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            text = ""
        aliases = shared_context_aliases(path, source)
        consumers = (
            set(all_skill_ids)
            if kind in {"context_routing", "platform_instruction"}
            else {
                skill_id
                for skill_id, skill_text in skill_texts.items()
                if any(alias in skill_text for alias in aliases)
            }
        )
        working.append(
            {
                "path": path.relative_to(source.parent).as_posix(),
                "kind": kind,
                "consumers": consumers,
                "sha256": sha256_bytes(data),
                "size": bytes_measure(data),
                "_text": text,
                "_aliases": aliases,
            }
        )
    changed = True
    while changed:
        changed = False
        for parent in working:
            if not parent["consumers"]:
                continue
            for child in working:
                if parent is child or not any(alias in parent["_text"] for alias in child["_aliases"]):
                    continue
                before = len(child["consumers"])
                child["consumers"].update(parent["consumers"])
                changed = changed or len(child["consumers"]) != before
    return [
        {
            "path": item["path"],
            "kind": item["kind"],
            "consumers": sorted(item["consumers"]),
            "sha256": item["sha256"],
            "size": item["size"],
        }
        for item in working
    ]


def evaluation_contract(cases: dict[str, dict[str, Any]]) -> dict[str, Any]:
    entries = [
        {
            "case_id": case_id,
            "oracle_sha256": oracle_digest(case),
        }
        for case_id, case in sorted(cases.items())
    ]
    return {
        "case_count": len(entries),
        "digest": sha256_json(entries),
    }


def collect_snapshot(root: Path, source_info: dict[str, Any]) -> dict[str, Any]:
    source = root / "source"
    skills_root = source / "skills"
    if not skills_root.is_dir():
        raise DietError(f"missing canonical skills root: {skills_root}")
    bundle = bundle_version(source)
    cases = load_eval_cases(source)
    skill_dirs = [
        path
        for path in sorted(skills_root.iterdir())
        if path.is_dir() and (path / "SKILL.md").is_file()
    ]
    validate_eval_case_skill_ids(cases, {path.name for path in skill_dirs})
    runs = load_observed_runs(source, cases)
    skills = [
        measure_skill(path, source, cases, runs, bundle)
        for path in skill_dirs
    ]
    shared_context_inventory = collect_shared_context_inventory(source)
    return {
        "schema_version": SCHEMA_VERSION,
        "baseline_id": "skill-diet-9.1.2" if bundle == "9.1.2" else f"skill-diet-{bundle}",
        "bundle_version": bundle,
        "source": source_info,
        "measurement_contract": {
            "words": "unicode_non_whitespace_spans",
            "bytes": "strict_utf8",
            "body": "after_line_delimited_frontmatter_and_separator_whitespace",
            "routing_card": "section_body_without_heading",
            "reference_admission": "exact_mentions_only",
            "observed_admission": "null_without_source_bound_artifact_and_verifier_receipt",
            "observed_admission_scope": "canonical_skill_cross_skill_shared_and_platform_context_units",
        },
        "evaluation_contract": evaluation_contract(cases),
        "aggregates": aggregate(skills, bundle, runs),
        "shared_context_inventory": shared_context_inventory,
        "skills": skills,
    }


def run_git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def git_text(root: Path, *args: str) -> str:
    try:
        return run_git(root, *args).stdout.decode("utf-8", errors="strict").strip()
    except (subprocess.CalledProcessError, UnicodeDecodeError) as exc:
        raise DietError(f"git {' '.join(args)} failed") from exc


def safe_extract(archive: bytes, destination: Path) -> None:
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as tar:
        destination_root = destination.resolve()
        for member in tar.getmembers():
            path = PurePosixPath(member.name)
            target = (destination / Path(*path.parts)).resolve()
            if (
                path.is_absolute()
                or ".." in path.parts
                or not target.is_relative_to(destination_root)
                or member.issym()
                or member.islnk()
            ):
                raise DietError(f"unsafe git archive member: {member.name}")
        tar.extractall(destination)


@contextlib.contextmanager
def archived_ref(root: Path, ref: str, label: str | None = None) -> Iterator[tuple[Path, dict[str, Any]]]:
    commit = git_text(root, "rev-parse", f"{ref}^{{commit}}")
    skills_tree = git_text(root, "rev-parse", f"{commit}:source/skills")
    commit_time = git_text(root, "show", "-s", "--format=%cI", commit)
    archive = run_git(root, "archive", "--format=tar", commit).stdout
    with tempfile.TemporaryDirectory(prefix="skill-diet-", dir="/private/tmp") as tmp:
        extracted = Path(tmp)
        safe_extract(archive, extracted)
        yield extracted, {
            "label": label or ref,
            "commit": commit,
            "skills_tree": skills_tree,
            "commit_time": commit_time,
            "reproducible": True,
            "tracked_input_digest": input_digest(extracted / "source"),
        }


def worktree_source_info(root: Path) -> dict[str, Any]:
    try:
        commit = git_text(root, "rev-parse", "HEAD")
    except DietError:
        commit = None
    return {
        "label": "candidate-worktree",
        "commit": commit,
        "skills_tree": None,
        "commit_time": None,
        "reproducible": False,
        "tracked_input_digest": input_digest(root / "source"),
    }


def load_manifest(path: Path) -> dict[str, Any]:
    payload = load_yaml_file(path)
    if not isinstance(payload, dict):
        raise DietError(f"{path}: baseline manifest must be a mapping")
    return payload


def schema_errors(manifest: dict[str, Any], schema_path: Path | None) -> list[str]:
    if schema_path is None:
        return []
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    return validate_schema(manifest, schema)


def canonical_schema_path(root: Path, provided: Path | None, filename: str) -> Path:
    if provided is not None:
        return provided
    for path in (
        root / "source" / "shared" / "eval" / filename,
        root / ".codex" / "eval" / filename,
    ):
        if path.is_file():
            return path
    raise DietError(f"canonical schema is unavailable: {filename}")


def reviewer_key_fingerprint(modulus_hex: str, exponent: int) -> str:
    return sha256_json(
        {
            "algorithm": "rsa-pkcs1v15-sha256",
            "modulus_hex": modulus_hex.lower().lstrip("0") or "0",
            "exponent": exponent,
        }
    )


def reviewer_public_entry(reviewer_id: str, modulus_hex: str, exponent: int) -> dict[str, Any]:
    if not reviewer_id:
        raise DietError("reviewer id is required")
    if re.fullmatch(r"[0-9a-fA-F]+", modulus_hex) is None:
        raise DietError("reviewer RSA modulus must be hexadecimal")
    if exponent < 3 or exponent % 2 == 0:
        raise DietError("reviewer RSA exponent must be an odd integer of at least 3")
    normalized_modulus = modulus_hex.lower().lstrip("0") or "0"
    if int(normalized_modulus, 16).bit_length() < 2048:
        raise DietError("reviewer RSA modulus must be at least 2048 bits")
    return {
        "reviewer_id": reviewer_id,
        "algorithm": "rsa-pkcs1v15-sha256",
        "modulus_hex": normalized_modulus,
        "exponent": exponent,
        "fingerprint_sha256": reviewer_key_fingerprint(normalized_modulus, exponent),
    }


def load_pinned_trusted_reviewers(root: Path) -> dict[str, dict[str, Any]]:
    path = next(
        (
            candidate
            for candidate in (
                root / "source" / "shared" / "eval" / "skill-diet-trusted-reviewers.json",
                root / ".codex" / "eval" / "skill-diet-trusted-reviewers.json",
            )
            if candidate.is_file()
        ),
        None,
    )
    if path is None:
        raise DietError("pinned skill-diet reviewer trust store is unavailable")
    data = path.read_bytes()
    if sha256_bytes(data) != PINNED_REVIEW_TRUST_STORE_SHA256:
        raise DietError("pinned skill-diet reviewer trust store digest mismatch")
    try:
        payload = json.loads(data.decode("utf-8", errors="strict"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DietError("pinned skill-diet reviewer trust store is invalid JSON") from exc
    if not isinstance(payload, dict) or payload.get("schema_version") != 1 or not isinstance(payload.get("reviewers"), list):
        raise DietError("pinned skill-diet reviewer trust store is invalid")
    reviewers: dict[str, dict[str, Any]] = {}
    for item in payload["reviewers"]:
        if not isinstance(item, dict):
            raise DietError("pinned reviewer entry must be a mapping")
        reviewer_id = item.get("reviewer_id")
        modulus_hex = item.get("modulus_hex")
        exponent = item.get("exponent")
        if (
            not isinstance(reviewer_id, str)
            or not reviewer_id
            or reviewer_id in reviewers
            or item.get("algorithm") != "rsa-pkcs1v15-sha256"
            or not isinstance(modulus_hex, str)
            or re.fullmatch(r"[0-9a-fA-F]+", modulus_hex) is None
            or not isinstance(exponent, int)
            or exponent < 3
            or exponent % 2 == 0
        ):
            raise DietError("pinned reviewer entry is invalid")
        normalized_modulus = modulus_hex.lower().lstrip("0") or "0"
        if int(normalized_modulus, 16).bit_length() < 2048:
            raise DietError("pinned reviewer RSA modulus must be at least 2048 bits")
        fingerprint = reviewer_key_fingerprint(normalized_modulus, exponent)
        if item.get("fingerprint_sha256") != fingerprint:
            raise DietError("pinned reviewer fingerprint mismatch")
        reviewers[reviewer_id] = {
            "algorithm": "rsa-pkcs1v15-sha256",
            "modulus": int(normalized_modulus, 16),
            "exponent": exponent,
            "fingerprint_sha256": fingerprint,
        }
    return reviewers


def verify_reviewer_signature(message: bytes, signature_hex: object, reviewer: dict[str, Any] | None) -> bool:
    if reviewer is None or not isinstance(signature_hex, str) or re.fullmatch(r"[0-9a-f]+", signature_hex) is None:
        return False
    modulus = int(reviewer["modulus"])
    exponent = int(reviewer["exponent"])
    width = (modulus.bit_length() + 7) // 8
    if len(signature_hex) != width * 2:
        return False
    signature = int(signature_hex, 16)
    if signature >= modulus:
        return False
    decoded = pow(signature, exponent, modulus).to_bytes(width, "big")
    digest_info = RSA_SHA256_DIGEST_INFO_PREFIX + hashlib.sha256(message).digest()
    padding_length = width - len(digest_info) - 3
    if padding_length < 8:
        return False
    expected = b"\x00\x01" + (b"\xff" * padding_length) + b"\x00" + digest_info
    return hmac.compare_digest(decoded, expected)


def semantic_errors(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append("manifest.schema_version must be 1")
    if not isinstance(manifest.get("bundle_version"), str):
        errors.append("manifest.bundle_version must be a string")
    evaluation = manifest.get("evaluation_contract")
    if not isinstance(evaluation, dict):
        errors.append("manifest.evaluation_contract must be a mapping")
    else:
        if not isinstance(evaluation.get("case_count"), int) or evaluation["case_count"] < 1:
            errors.append("evaluation_contract.case_count must be a positive integer")
        if not isinstance(evaluation.get("digest"), str) or re.fullmatch(r"[0-9a-f]{64}", evaluation["digest"]) is None:
            errors.append("evaluation_contract.digest must be a SHA-256 hex digest")
    source = manifest.get("source")
    if not isinstance(source, dict):
        errors.append("manifest.source must be a mapping")
    else:
        commit = source.get("commit")
        if not isinstance(commit, str) or re.fullmatch(r"[0-9a-f]{40}", commit) is None:
            errors.append("manifest.source.commit must be a full Git commit SHA")
        tree = source.get("skills_tree")
        if not isinstance(tree, str) or re.fullmatch(r"[0-9a-f]{40}", tree) is None:
            errors.append("manifest.source.skills_tree must be a full Git tree SHA")
        if source.get("reproducible") is not True:
            errors.append("baseline manifest source must be reproducible")
        tracked_digest = source.get("tracked_input_digest")
        if not isinstance(tracked_digest, str) or re.fullmatch(r"[0-9a-f]{64}", tracked_digest) is None:
            errors.append("manifest.source.tracked_input_digest must be a SHA-256 hex digest")
    skills = manifest.get("skills")
    if not isinstance(skills, list):
        errors.append("manifest.skills must be a list")
        return errors
    ids = [item.get("skill_id") for item in skills if isinstance(item, dict)]
    if len(ids) != len(skills) or any(not isinstance(item, str) for item in ids):
        errors.append("every skill requires a string skill_id")
    elif len(ids) != len(set(ids)):
        errors.append("manifest skill_id values must be unique")
    shared_context = manifest.get("shared_context_inventory")
    if not isinstance(shared_context, list):
        errors.append("manifest.shared_context_inventory must be a list")
        shared_context = []
    shared_paths: set[str] = set()
    for item in shared_context:
        if not isinstance(item, dict):
            errors.append("shared context inventory entry must be a mapping")
            continue
        path = item.get("path")
        if not isinstance(path, str) or not path.startswith("source/") or path in shared_paths:
            errors.append(f"invalid or duplicate shared context path: {path!r}")
        else:
            shared_paths.add(path)
        if item.get("kind") not in SHARED_CONTEXT_KINDS:
            errors.append(f"{path}: invalid shared context kind")
        consumers = item.get("consumers")
        if (
            not isinstance(consumers, list)
            or consumers != sorted(set(consumers))
            or any(consumer not in set(ids) for consumer in consumers)
        ):
            errors.append(f"{path}: invalid shared context consumers")
        digest = item.get("sha256")
        if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
            errors.append(f"{path}: invalid shared context SHA-256")
        size = item.get("size")
        if not isinstance(size, dict) or not isinstance(size.get("utf8_bytes"), int):
            errors.append(f"{path}: invalid shared context size")
    aggregates = manifest.get("aggregates")
    if not isinstance(aggregates, dict) or aggregates.get("skill_count") != len(skills):
        errors.append("aggregates.skill_count must equal manifest skill count")
        aggregates = None
    for skill in skills:
        if not isinstance(skill, dict):
            continue
        skill_id = skill.get("skill_id")
        for key in (
            "source_path",
            "source_sha256",
            "measurements",
            "content_digests",
            "routing",
            "context_targets",
            "resources",
            "eval_coverage",
            "observed_admission",
        ):
            if key not in skill:
                errors.append(f"{skill_id}: missing required field {key}")
        source_sha = skill.get("source_sha256")
        if not isinstance(source_sha, str) or re.fullmatch(r"[0-9a-f]{64}", source_sha) is None:
            errors.append(f"{skill_id}: source_sha256 must be a SHA-256 hex digest")
        digests = skill.get("content_digests")
        if not isinstance(digests, dict):
            errors.append(f"{skill_id}: content_digests must be a mapping")
        else:
            for key in (
                "body",
                "routing_card",
                "frontmatter_description",
                "agent_short_description",
                "agent_default_prompt",
                "context_targets",
                "resource_inventory",
            ):
                value = digests.get(key)
                if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
                    errors.append(f"{skill_id}: invalid content digest {key}")
        coverage = skill.get("eval_coverage")
        if not isinstance(coverage, dict):
            errors.append(f"{skill_id}: eval_coverage must be a mapping")
        else:
            declared = coverage.get("declared_route_cases")
            if not isinstance(declared, dict) or any(
                not isinstance(declared.get(lane), list) for lane in ("primary", "supporting", "negative")
            ):
                errors.append(f"{skill_id}: invalid declared route case lanes")
            contracts = coverage.get("case_oracle_digests")
            if not isinstance(contracts, dict) or any(
                not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None
                for value in contracts.values()
            ):
                errors.append(f"{skill_id}: invalid case oracle digests")
                contract_keys: set[str] = set()
            else:
                contract_keys = set(contracts)
            for mapping_key in (
                "case_sources",
                "case_overlay_stable_digests",
                "case_required_eval_modes",
                "case_required_evidence_types",
                "case_required_evidence_contracts",
                "case_schema_versions",
                "case_expected_primary_skills",
                "case_expected_supporting_skills",
                "case_should_not_trigger",
                "case_expected_behaviors",
                "case_forbidden_behaviors",
                "case_behavior_contract_owners",
                "case_scenario_tags",
            ):
                mapping = coverage.get(mapping_key)
                if not isinstance(mapping, dict):
                    errors.append(f"{skill_id}: invalid {mapping_key}")
                elif set(mapping) != contract_keys:
                    errors.append(f"{skill_id}: {mapping_key} keys must match case oracle keys")
            for list_key in (
                "structured_behavior_candidates",
                "structured_observed_candidates",
                "structured_negative_candidates",
                "explicit_edge_cases",
            ):
                if not isinstance(coverage.get(list_key), list):
                    errors.append(f"{skill_id}: invalid {list_key}")
            required_contracts = coverage.get("case_required_evidence_contracts")
            if isinstance(required_contracts, dict):
                for case_id, entries in required_contracts.items():
                    if not isinstance(entries, list) or any(
                        not isinstance(entry, dict)
                        or not isinstance(entry.get("type"), str)
                        or not isinstance(entry.get("requirement_sha256"), str)
                        or re.fullmatch(r"[0-9a-f]{64}", entry["requirement_sha256"]) is None
                        for entry in entries
                    ):
                        errors.append(f"{skill_id}: invalid required evidence contracts for {case_id}")
            stable_digests = coverage.get("case_overlay_stable_digests")
            if isinstance(stable_digests, dict) and any(
                not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None
                for value in stable_digests.values()
            ):
                errors.append(f"{skill_id}: invalid overlay-stable digests")
            for mapping_key in (
                "case_expected_supporting_skills",
                "case_should_not_trigger",
                "case_expected_behaviors",
                "case_forbidden_behaviors",
                "case_behavior_contract_owners",
                "case_scenario_tags",
                "case_required_evidence_types",
            ):
                mapping = coverage.get(mapping_key)
                if isinstance(mapping, dict) and any(
                    not isinstance(value, list)
                    or any(not isinstance(item, str) for item in value)
                    or value != sorted(set(value))
                    for value in mapping.values()
                ):
                    errors.append(f"{skill_id}: invalid list values in {mapping_key}")
            structured = coverage.get("structured_behavior_candidates")
            observed_structured = coverage.get("structured_observed_candidates")
            if isinstance(structured, list) and isinstance(observed_structured, list) and not set(observed_structured) <= set(structured):
                errors.append(f"{skill_id}: observed structured cases must be structured candidates")
            explicit_edge = coverage.get("explicit_edge_cases")
            if isinstance(explicit_edge, list) and not set(explicit_edge) <= contract_keys:
                errors.append(f"{skill_id}: explicit edge cases must be owned oracle cases")
        admission = skill.get("observed_admission")
        if not isinstance(admission, dict) or admission.get("status") != "unverified":
            errors.append(f"{skill.get('skill_id')}: observed admission must be explicitly unverified")
        elif admission.get("words") is not None or admission.get("utf8_bytes") is not None:
            errors.append(f"{skill.get('skill_id')}: missing admission receipt must use null metrics")
    if aggregates is not None:
        measured = {
            "skill_file": empty_metric(),
            "body": empty_metric(),
            "routing_card": empty_metric(),
            "frontmatter_description": empty_metric(),
            "agent_short_description": empty_metric(),
            "agent_default_prompt": empty_metric(),
            "owned_inventory": empty_metric(),
        }
        kind_counts: Counter[str] = Counter()
        kind_bytes: Counter[str] = Counter()
        admission_counts: Counter[str] = Counter()
        admission_bytes: Counter[str] = Counter()
        surface_counts: Counter[str] = Counter()
        implicit_ids: list[str] = []
        for skill in skills:
            if not isinstance(skill, dict):
                continue
            skill_metrics = skill.get("measurements")
            if not isinstance(skill_metrics, dict):
                errors.append(f"{skill.get('skill_id')}: measurements must be a mapping")
                continue
            for key in measured:
                if key == "owned_inventory":
                    continue
                metric = skill_metrics.get(key)
                if not isinstance(metric, dict):
                    errors.append(f"{skill.get('skill_id')}: missing measurement {key}")
                    continue
                add_metric(measured[key], metric)
            add_metric(measured["owned_inventory"], skill_metrics.get("skill_file") or {})
            routing = skill.get("routing") if isinstance(skill.get("routing"), dict) else {}
            surface_counts[str(routing.get("invocation_surface") or "missing")] += 1
            if routing.get("allow_implicit_invocation") is True:
                implicit_ids.append(str(skill.get("skill_id")))
            resources = skill.get("resources")
            if not isinstance(resources, list):
                errors.append(f"{skill.get('skill_id')}: resources must be a list")
                continue
            for resource in resources:
                if not isinstance(resource, dict) or not isinstance(resource.get("size"), dict):
                    errors.append(f"{skill.get('skill_id')}: invalid resource entry")
                    continue
                if not isinstance(resource.get("path"), str) or not isinstance(resource.get("kind"), str):
                    errors.append(f"{skill.get('skill_id')}: invalid resource identity")
                    continue
                resource_sha = resource.get("sha256")
                if not isinstance(resource_sha, str) or re.fullmatch(r"[0-9a-f]{64}", resource_sha) is None:
                    errors.append(f"{skill.get('skill_id')}: invalid resource SHA-256")
                    continue
                kind = str(resource.get("kind"))
                size = resource["size"]
                kind_counts[kind] += 1
                kind_bytes[kind] += int(size.get("utf8_bytes") or 0)
                add_metric(measured["owned_inventory"], size)
                if kind == "instruction_reference":
                    admission_class = str(resource.get("admission_class"))
                    admission_counts[admission_class] += 1
                    admission_bytes[admission_class] += int(size.get("utf8_bytes") or 0)
        if aggregates.get("measurements") != measured:
            errors.append("aggregates.measurements do not match per-skill inventory")
        resources = aggregates.get("resources") if isinstance(aggregates.get("resources"), dict) else {}
        if resources.get("count") != sum(kind_counts.values()):
            errors.append("aggregates.resources.count does not match per-skill resources")
        if resources.get("by_kind_count") != dict(sorted(kind_counts.items())):
            errors.append("aggregates.resources.by_kind_count does not match per-skill resources")
        if resources.get("by_kind_utf8_bytes") != dict(sorted(kind_bytes.items())):
            errors.append("aggregates.resources.by_kind_utf8_bytes does not match per-skill resources")
        exact = (
            aggregates.get("declared_exact_reference_admission")
            if isinstance(aggregates.get("declared_exact_reference_admission"), dict)
            else {}
        )
        if exact.get("by_class_count") != {key: admission_counts.get(key, 0) for key in ADMISSION_CLASSES}:
            errors.append("declared exact admission counts do not match per-skill resources")
        if exact.get("by_class_utf8_bytes") != {key: admission_bytes.get(key, 0) for key in ADMISSION_CLASSES}:
            errors.append("declared exact admission bytes do not match per-skill resources")
        invocation = aggregates.get("invocation") if isinstance(aggregates.get("invocation"), dict) else {}
        if invocation.get("surface_counts") != dict(sorted(surface_counts.items())):
            errors.append("aggregates.invocation.surface_counts do not match per-skill routing")
        if invocation.get("implicit_skill_ids") != sorted(implicit_ids):
            errors.append("aggregates.invocation.implicit_skill_ids do not match per-skill routing")
    return errors


def comparable_payload(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        key: manifest.get(key)
        for key in (
            "schema_version",
            "baseline_id",
            "bundle_version",
            "measurement_contract",
            "evaluation_contract",
            "aggregates",
            "shared_context_inventory",
            "skills",
        )
    }


def verify_git_provenance(root: Path, manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    source = manifest["source"]
    commit = str(source["commit"])
    try:
        actual_tree = git_text(root, "rev-parse", f"{commit}:source/skills")
    except DietError:
        return [f"baseline commit is unavailable: {commit}"]
    if actual_tree != source["skills_tree"]:
        errors.append(f"skills tree mismatch: {actual_tree} != {source['skills_tree']}")
    label = source.get("label")
    if isinstance(label, str) and label:
        probe = run_git(root, "rev-parse", "--verify", f"refs/tags/{label}^{{commit}}", check=False)
        if probe.returncode == 0:
            tag_commit = probe.stdout.decode("utf-8", errors="replace").strip()
            if tag_commit != commit:
                errors.append(f"baseline tag {label} points to {tag_commit}, expected {commit}")
    if errors:
        return errors
    with archived_ref(root, commit, label=str(label or commit)) as (archived, info):
        recomputed = collect_snapshot(archived, info)
    if recomputed["source"]["tracked_input_digest"] != source.get("tracked_input_digest"):
        errors.append("baseline tracked input digest does not reproduce from its pinned commit")
    if comparable_payload(recomputed) != comparable_payload(manifest):
        errors.append("baseline manifest does not reproduce from its pinned commit")
    return errors


def candidate_lineage_issues(
    root: Path,
    baseline: dict[str, Any],
    candidate: dict[str, Any],
) -> list[dict[str, Any]]:
    baseline_commit = baseline.get("source", {}).get("commit")
    candidate_commit = candidate.get("source", {}).get("commit")
    if not isinstance(baseline_commit, str) or not isinstance(candidate_commit, str):
        return [
            {
                "code": "candidate_lineage_unverifiable",
                "baseline_commit": baseline_commit,
                "candidate_commit": candidate_commit,
            }
        ]
    probe = run_git(
        root,
        "merge-base",
        "--is-ancestor",
        baseline_commit,
        candidate_commit,
        check=False,
    )
    if probe.returncode == 0:
        return []
    if probe.returncode == 1:
        return [
            {
                "code": "candidate_not_descendant",
                "baseline_commit": baseline_commit,
                "candidate_commit": candidate_commit,
            }
        ]
    detail = probe.stderr.decode("utf-8", errors="replace").strip()
    raise DietError(
        "candidate ancestry check failed"
        + (f": {detail}" if detail else "")
    )


def index_skills(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(item["skill_id"]): item for item in manifest["skills"]}


def context_unit_index(manifest: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    units: dict[tuple[str, str], dict[str, Any]] = {}

    def add(
        path: str,
        content_unit: str,
        sha256: str,
        metric: dict[str, Any],
        owner_skill_id: str | None,
        kind: str,
    ) -> None:
        key = (path, content_unit)
        if key in units:
            raise DietError(f"duplicate context unit {path}#{content_unit}")
        units[key] = {
            "path": path,
            "content_unit": content_unit,
            "sha256": sha256,
            "words": metric.get("words"),
            "utf8_bytes": metric.get("utf8_bytes"),
            "owner_skill_id": owner_skill_id,
            "kind": kind,
        }

    for skill in manifest["skills"]:
        skill_id = str(skill["skill_id"])
        source_path = str(skill["source_path"])
        measurements = skill["measurements"]
        digests = skill["content_digests"]
        add(source_path, "full_file", skill["source_sha256"], measurements["skill_file"], skill_id, "skill")
        add(source_path, "body", digests["body"], measurements["body"], skill_id, "skill_slice")
        add(source_path, "routing_card", digests["routing_card"], measurements["routing_card"], skill_id, "skill_slice")
        add(
            source_path,
            "frontmatter_description",
            digests["frontmatter_description"],
            measurements["frontmatter_description"],
            skill_id,
            "discovery_slice",
        )
        base = Path(source_path).parent
        for resource in skill["resources"]:
            path = (base / resource["path"]).as_posix()
            add(path, "full_file", resource["sha256"], resource["size"], skill_id, str(resource["kind"]))
            if resource["path"] == "agents/openai.yaml":
                add(
                    path,
                    "agent_short_description",
                    digests["agent_short_description"],
                    measurements["agent_short_description"],
                    skill_id,
                    "discovery_slice",
                )
                add(
                    path,
                    "agent_default_prompt",
                    digests["agent_default_prompt"],
                    measurements["agent_default_prompt"],
                    skill_id,
                    "discovery_slice",
                )
    for item in manifest.get("shared_context_inventory") or []:
        add(str(item["path"]), "full_file", item["sha256"], item["size"], None, str(item["kind"]))
    return units


def evidence_source_errors(snapshot: dict[str, Any], evidence: dict[str, Any], label: str) -> list[dict[str, Any]]:
    if not isinstance(evidence, dict):
        return [{"code": "evidence_document_invalid", "side": label}]
    source = evidence.get("source")
    if not isinstance(source, dict):
        return [{"code": "evidence_source_missing", "side": label}]
    expected = snapshot["source"]
    for key in ("commit", "skills_tree", "tracked_input_digest"):
        if source.get(key) != expected.get(key):
            return [{"code": "evidence_source_mismatch", "side": label, "field": key}]
    return []


def parsed_iso_datetime(value: object) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def valid_iso_datetime(value: object) -> bool:
    return parsed_iso_datetime(value) is not None


def validate_artifact_ref(
    evidence_root: Path | None,
    ref: object,
    label: str,
    artifact_kind: str,
) -> tuple[list[dict[str, Any]], bytes | None]:
    issues: list[dict[str, Any]] = []
    if evidence_root is None:
        return [{"code": "evidence_artifact_root_missing", "side": label, "artifact": artifact_kind}], None
    if not isinstance(ref, dict):
        return [{"code": "evidence_artifact_ref_invalid", "side": label, "artifact": artifact_kind}], None
    raw_path = ref.get("path")
    if not isinstance(raw_path, str) or not raw_path:
        return [{"code": "evidence_artifact_path_unsafe", "side": label, "artifact": artifact_kind}], None
    relative = PurePosixPath(raw_path)
    if relative.is_absolute() or ".." in relative.parts or relative.as_posix() != raw_path:
        return [{"code": "evidence_artifact_path_unsafe", "side": label, "artifact": artifact_kind}], None
    root = evidence_root.resolve()
    target = evidence_root.joinpath(*relative.parts)
    current = evidence_root
    if evidence_root.is_symlink():
        issues.append({"code": "evidence_artifact_symlink", "side": label, "artifact": artifact_kind, "path": raw_path})
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            issues.append({"code": "evidence_artifact_symlink", "side": label, "artifact": artifact_kind, "path": raw_path})
            break
    try:
        resolved = target.resolve(strict=True)
    except OSError:
        issues.append({"code": "evidence_artifact_missing", "side": label, "artifact": artifact_kind, "path": raw_path})
        return issues, None
    if not resolved.is_relative_to(root):
        issues.append({"code": "evidence_artifact_path_unsafe", "side": label, "artifact": artifact_kind, "path": raw_path})
        return issues, None
    if issues:
        return issues, None
    if not resolved.is_file():
        return [{"code": "evidence_artifact_missing", "side": label, "artifact": artifact_kind, "path": raw_path}], None
    data = resolved.read_bytes()
    if ref.get("utf8_bytes") != len(data):
        issues.append({"code": "evidence_artifact_size_mismatch", "side": label, "artifact": artifact_kind, "path": raw_path})
    if ref.get("sha256") != sha256_bytes(data):
        issues.append({"code": "evidence_artifact_hash_mismatch", "side": label, "artifact": artifact_kind, "path": raw_path})
    return issues, data if not issues else None


def json_artifact(data: bytes | None, label: str, artifact_kind: str) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    if data is None:
        return [], None
    try:
        payload = json.loads(data.decode("utf-8", errors="strict"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return [{"code": "evidence_receipt_invalid", "side": label, "artifact": artifact_kind}], None
    if not isinstance(payload, dict):
        return [{"code": "evidence_receipt_invalid", "side": label, "artifact": artifact_kind}], None
    return [], payload


def validate_accepted_dependency_locks(
    owner_skill_id: str,
    historical_candidate: dict[str, Any],
    current_candidate: dict[str, Any],
    candidate_runs: dict[tuple[str, str], dict[str, Any]],
) -> None:
    historical_skills = index_skills(historical_candidate)
    current_skills = index_skills(current_candidate)
    current_units = context_unit_index(current_candidate)
    for (run_skill_id, case_id), run in sorted(candidate_runs.items()):
        routed_skill_ids = {run_skill_id}
        primary = run.get("observed_primary_skill")
        if isinstance(primary, str):
            routed_skill_ids.add(primary)
        routed_skill_ids.update(run.get("observed_supporting_skills") or [])
        for dependency_skill_id in sorted(routed_skill_ids):
            historical_skill = historical_skills.get(dependency_skill_id)
            current_skill = current_skills.get(dependency_skill_id)
            if (
                historical_skill is None
                or current_skill is None
                or historical_skill.get("source_sha256") != current_skill.get("source_sha256")
                or historical_skill.get("content_digests") != current_skill.get("content_digests")
            ):
                raise DietError(
                    "local pilot accepted routed skill drift: "
                    f"{owner_skill_id}#{case_id}#{dependency_skill_id}"
                )
        for admitted in run.get("admitted_context") or []:
            path = admitted.get("path")
            content_unit = admitted.get("content_unit")
            current_unit = current_units.get((path, content_unit))
            if current_unit is None or any(
                admitted.get(field) != current_unit.get(field)
                for field in ("sha256", "owner_skill_id", "kind")
            ):
                raise DietError(
                    "local pilot accepted admitted context drift: "
                    f"{owner_skill_id}#{case_id}#{path}#{content_unit}"
                )


def accepted_atomic_dependency_groups(
    entries: list[dict[str, Any]],
    schema_version: int,
) -> dict[str, list[str]]:
    groups: dict[str, list[tuple[int, str]]] = {}
    for position, entry in enumerate(entries):
        group_id = entry.get("atomic_dependency_group")
        if group_id is None:
            continue
        if schema_version < 2:
            raise DietError("local pilot atomic dependency groups require state schema v2")
        groups.setdefault(str(group_id), []).append((position, str(entry["skill_id"])))

    normalized: dict[str, list[str]] = {}
    seen_members: set[str] = set()
    for group_id, positioned_members in sorted(groups.items()):
        positions = [position for position, _ in positioned_members]
        members = [skill_id for _, skill_id in positioned_members]
        if len(members) < 2:
            raise DietError(f"local pilot atomic dependency group is not a group: {group_id}")
        if positions != list(range(positions[0], positions[-1] + 1)):
            raise DietError(f"local pilot atomic dependency group is not contiguous: {group_id}")
        overlap = seen_members.intersection(members)
        if overlap:
            raise DietError(
                "local pilot atomic dependency group member is duplicated: "
                + ", ".join(sorted(overlap))
            )
        seen_members.update(members)
        normalized[group_id] = members
    return normalized


def accepted_validation_prefixes(
    baseline: dict[str, Any],
    candidate: dict[str, Any],
    entries: list[dict[str, Any]],
    atomic_groups: dict[str, list[str]],
) -> dict[str, dict[str, Any]]:
    candidate_skills = index_skills(candidate)
    historical_prefix = deepcopy(baseline)
    prefix_by_position: list[dict[str, Any]] = []
    position_by_skill: dict[str, int] = {}
    for position, entry in enumerate(entries):
        skill_id = entry["skill_id"]
        current = candidate_skills.get(skill_id)
        if current is None:
            raise DietError(f"local pilot accepted skill missing from candidate: {skill_id}")
        for skill_position, skill in enumerate(historical_prefix["skills"]):
            if skill.get("skill_id") == skill_id:
                historical_prefix["skills"][skill_position] = deepcopy(current)
                break
        else:
            raise DietError(f"local pilot accepted skill missing from historical candidate: {skill_id}")
        position_by_skill[skill_id] = position
        prefix_by_position.append(deepcopy(historical_prefix))

    validation_position = dict(position_by_skill)
    for members in atomic_groups.values():
        closure = max(position_by_skill[skill_id] for skill_id in members)
        for skill_id in members:
            validation_position[skill_id] = closure
    return {
        skill_id: deepcopy(prefix_by_position[position])
        for skill_id, position in validation_position.items()
    }


def validate_atomic_dependency_group_routes(
    atomic_groups: dict[str, list[str]],
    candidate_runs_by_owner: dict[str, dict[tuple[str, str], dict[str, Any]]],
) -> None:
    for group_id, members in sorted(atomic_groups.items()):
        member_set = set(members)
        graph = {skill_id: set() for skill_id in members}
        for owner_skill_id in members:
            for run in candidate_runs_by_owner.get(owner_skill_id, {}).values():
                routed = {run.get("observed_primary_skill")}
                routed.update(run.get("observed_supporting_skills") or [])
                graph[owner_skill_id].update(
                    skill_id for skill_id in routed if skill_id in member_set and skill_id != owner_skill_id
                )
        for origin in members:
            reachable = {origin}
            pending = [origin]
            while pending:
                current = pending.pop()
                for target in graph[current] - reachable:
                    reachable.add(target)
                    pending.append(target)
            if reachable != member_set:
                raise DietError(
                    "local pilot atomic dependency group is not strongly connected: "
                    f"{group_id}#{origin}"
                )


def load_pinned_local_pilot_state(
    root: Path,
    baseline: dict[str, Any],
    candidate: dict[str, Any],
) -> dict[str, dict[str, str]]:
    state_path = root / LOCAL_PILOT_ACCEPTED_STATE_PATH
    if state_path.is_symlink() or not state_path.is_file():
        raise DietError("pinned local pilot accepted state is unavailable or unsafe")
    resolved = state_path.resolve(strict=True)
    if not resolved.is_relative_to(root.resolve()):
        raise DietError("pinned local pilot accepted state escapes the repository")
    state_bytes = resolved.read_bytes()
    if sha256_bytes(state_bytes) != LOCAL_PILOT_ACCEPTED_STATE_SHA256:
        raise DietError("pinned local pilot accepted state digest mismatch")
    try:
        state = json.loads(state_bytes.decode("utf-8", errors="strict"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DietError("pinned local pilot accepted state is invalid JSON") from exc
    if not isinstance(state, dict):
        raise DietError("pinned local pilot accepted state must be an object")
    state_schema_path = canonical_schema_path(
        root,
        None,
        "skill-diet-local-pilot-accepted-state.schema.json",
    )
    state_schema = json.loads(state_schema_path.read_text(encoding="utf-8"))
    state_schema_issues = validate_schema(state, state_schema)
    if state_schema_issues:
        raise DietError("invalid pinned local pilot accepted state: " + "; ".join(state_schema_issues))

    baseline_binding = state["baseline"]
    for field in ("commit", "skills_tree", "tracked_input_digest"):
        if baseline_binding.get(field) != baseline["source"].get(field):
            raise DietError(f"local pilot accepted state baseline mismatch: {field}")
    if (
        state.get("eval_contract_digest") != LOCAL_PILOT_EVAL_CONTRACT_DIGEST
        or candidate["evaluation_contract"]["digest"] != LOCAL_PILOT_EVAL_CONTRACT_DIGEST
    ):
        raise DietError("local pilot accepted state oracle mismatch")

    evidence_schema_path = canonical_schema_path(
        root,
        None,
        "skill-diet-local-pilot-evidence.schema.json",
    )
    evidence_schema = json.loads(evidence_schema_path.read_text(encoding="utf-8"))
    baseline_skills = index_skills(baseline)
    candidate_skills = index_skills(candidate)
    locks: dict[str, dict[str, str]] = {}
    entries = state["entries"]
    expected_orders = list(range(1, len(entries) + 1))
    if [entry["order"] for entry in entries] != expected_orders:
        raise DietError("local pilot accepted state order is not contiguous")
    atomic_groups = accepted_atomic_dependency_groups(entries, state["schema_version"])
    entry_by_skill = {entry["skill_id"]: entry for entry in entries}
    for group_id, members in atomic_groups.items():
        tracked_digests = {
            entry_by_skill[skill_id]["accepted_candidate_tracked_input_digest"]
            for skill_id in members
        }
        if len(tracked_digests) != 1:
            raise DietError(
                f"local pilot atomic dependency group candidate source mismatch: {group_id}"
            )
    validation_prefixes = accepted_validation_prefixes(
        baseline,
        candidate,
        entries,
        atomic_groups,
    )
    candidate_runs_by_owner: dict[str, dict[tuple[str, str], dict[str, Any]]] = {}
    for entry in entries:
        skill_id = entry["skill_id"]
        if skill_id in locks:
            raise DietError(f"duplicate local pilot accepted skill: {skill_id}")
        if skill_id not in LOCAL_PILOT_SKILLS or skill_id not in baseline_skills or skill_id not in candidate_skills:
            raise DietError(f"invalid local pilot accepted skill: {skill_id}")
        before = baseline_skills[skill_id]
        current = candidate_skills[skill_id]
        if entry["source_sha256"] != current["source_sha256"]:
            raise DietError(f"local pilot accepted skill source drift: {skill_id}")
        entry_digests = entry["content_digests"]
        if entry_digests != current["content_digests"]:
            raise DietError(f"local pilot accepted skill content drift: {skill_id}")
        if before["content_digests"]["body"] == entry_digests["body"]:
            raise DietError(f"local pilot accepted skill is unchanged from baseline: {skill_id}")
        if len(entry["case_ids"]) != len(set(entry["case_ids"])):
            raise DietError(f"local pilot accepted state has duplicate cases: {skill_id}")
        for digest_name in (
            "routing_card",
            "frontmatter_description",
            "agent_short_description",
            "agent_default_prompt",
            "context_targets",
        ):
            if entry_digests[digest_name] != before["content_digests"][digest_name]:
                raise DietError(f"local pilot accepted skill routing/trigger drift: {skill_id}#{digest_name}")

        evidence_documents: list[tuple[str, dict[str, Any], Path]] = []
        for evidence_side in ("baseline", "candidate"):
            ref = entry[f"{evidence_side}_evidence"]
            ref_issues, evidence_bytes = validate_artifact_ref(
                state_path.parent,
                ref,
                "accepted-state",
                f"{skill_id}-{evidence_side}",
            )
            if ref_issues or evidence_bytes is None:
                raise DietError(f"local pilot accepted evidence artifact invalid: {skill_id}#{evidence_side}")
            evidence_path = state_path.parent / PurePosixPath(ref["path"])
            try:
                evidence = json.loads(evidence_bytes.decode("utf-8", errors="strict"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise DietError(f"local pilot accepted evidence JSON invalid: {skill_id}#{evidence_side}") from exc
            evidence_errors = validate_schema(evidence, evidence_schema)
            if evidence_errors:
                raise DietError(
                    f"local pilot accepted evidence schema invalid: {skill_id}#{evidence_side}: "
                    + "; ".join(evidence_errors)
                )
            evidence_documents.append((evidence_side, evidence, evidence_path))

        for evidence_side, evidence, evidence_path in evidence_documents:
            if (
                evidence.get("verification_tier") != AGENT_REVIEWED_LOCAL_PILOT_TIER
                or evidence.get("model") != entry["model"]
                or evidence.get("eval_contract_digest") != state["eval_contract_digest"]
                or [run.get("case_id") for run in evidence.get("runs") or []] != entry["case_ids"]
            ):
                raise DietError(f"local pilot accepted evidence contract mismatch: {skill_id}#{evidence_side}")
            source = evidence.get("source") or {}
            if evidence_side == "baseline":
                expected_source = {
                    "commit": baseline["source"]["commit"],
                    "skills_tree": baseline["source"]["skills_tree"],
                    "tracked_input_digest": baseline["source"]["tracked_input_digest"],
                }
            else:
                expected_source = {
                    "commit": baseline["source"]["commit"],
                    "skills_tree": None,
                    "tracked_input_digest": entry["accepted_candidate_tracked_input_digest"],
                }
            if source != expected_source:
                raise DietError(f"local pilot accepted evidence source mismatch: {skill_id}#{evidence_side}")
            for run in evidence["runs"]:
                for artifact_kind in (
                    "prompt_artifact",
                    "run_artifact",
                    "output_artifact",
                    "review_artifact",
                    "verifier_receipt",
                ):
                    artifact_issues, artifact_bytes = validate_artifact_ref(
                        evidence_path.parent,
                        run.get(artifact_kind),
                        "accepted-state",
                        f"{skill_id}-{evidence_side}-{artifact_kind}",
                    )
                    if artifact_issues or artifact_bytes is None:
                        raise DietError(
                            f"local pilot accepted evidence chain invalid: {skill_id}#{evidence_side}#{artifact_kind}"
                        )

        evidence_by_side = {
            evidence_side: (evidence, evidence_path)
            for evidence_side, evidence, evidence_path in evidence_documents
        }
        historical_candidate = deepcopy(validation_prefixes[skill_id])
        historical_candidate["source"] = {
            **historical_candidate["source"],
            **evidence_by_side["candidate"][0]["source"],
        }
        semantic_result = paired_evidence_result(
            baseline,
            historical_candidate,
            evidence_by_side["baseline"][0],
            evidence_by_side["candidate"][0],
            evidence_by_side["baseline"][1].parent,
            evidence_by_side["candidate"][1].parent,
            oracle_snapshot=candidate,
            verification_tier=AGENT_REVIEWED_LOCAL_PILOT_TIER,
        )
        if (
            semantic_result["issues"]
            or semantic_result["behavior"] != "agent-reviewed"
            or semantic_result["admission"] != "unverified"
            or semantic_result["release_eligible"] is not False
        ):
            issue_codes = sorted(
                {
                    str(issue.get("code"))
                    for issue in semantic_result["issues"]
                    if isinstance(issue, dict)
                }
            )
            detail = ", ".join(issue_codes) if issue_codes else "invalid local pilot result"
            raise DietError(f"local pilot accepted evidence semantic validation failed: {skill_id}: {detail}")
        scope_validation_issues = paired_scope_issues(candidate, semantic_result, {skill_id})
        if scope_validation_issues:
            issue_codes = sorted(
                {
                    str(issue.get("code"))
                    for issue in scope_validation_issues
                    if isinstance(issue, dict)
                }
            )
            raise DietError(
                f"local pilot accepted evidence coverage validation failed: {skill_id}: "
                + ", ".join(issue_codes)
            )
        candidate_validation_issues, candidate_runs = validate_evidence(
            historical_candidate,
            candidate,
            evidence_by_side["candidate"][0],
            "accepted-candidate",
            evidence_by_side["candidate"][1].parent,
            None,
            AGENT_REVIEWED_LOCAL_PILOT_TIER,
        )
        if candidate_validation_issues:
            issue_codes = sorted(
                {
                    str(issue.get("code"))
                    for issue in candidate_validation_issues
                    if isinstance(issue, dict)
                }
            )
            raise DietError(
                f"local pilot accepted candidate validation failed: {skill_id}: "
                + ", ".join(issue_codes)
            )
        validate_accepted_dependency_locks(
            skill_id,
            historical_candidate,
            candidate,
            candidate_runs,
        )
        candidate_runs_by_owner[skill_id] = candidate_runs
        comparison_issues, comparison_bytes = validate_artifact_ref(
            state_path.parent,
            entry["comparison"],
            "accepted-state",
            f"{skill_id}-comparison",
        )
        if comparison_issues or comparison_bytes is None:
            raise DietError(f"local pilot accepted comparison artifact invalid: {skill_id}")
        try:
            comparison = json.loads(comparison_bytes.decode("utf-8", errors="strict"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise DietError(f"local pilot accepted comparison JSON invalid: {skill_id}") from exc
        if not isinstance(comparison, dict) or comparison != {
            "skill_id": skill_id,
            "status": "PASS",
            "verification_tier": AGENT_REVIEWED_LOCAL_PILOT_TIER,
            "behavior": "agent-reviewed",
            "admission": "unverified",
            "release_eligible": False,
            "body_delta_words": comparison.get("body_delta_words") if isinstance(comparison, dict) else None,
            "body_delta_utf8_bytes": (
                comparison.get("body_delta_utf8_bytes") if isinstance(comparison, dict) else None
            ),
            "case_ids": entry["case_ids"],
        }:
            raise DietError(f"local pilot accepted comparison contract mismatch: {skill_id}")
        if (
            not isinstance(comparison["body_delta_words"], int)
            or comparison["body_delta_words"] >= 0
            or not isinstance(comparison["body_delta_utf8_bytes"], int)
            or comparison["body_delta_utf8_bytes"] >= 0
        ):
            raise DietError(f"local pilot accepted comparison has no body reduction: {skill_id}")
        actual_body_delta = metric_delta(current["measurements"]["body"], before["measurements"]["body"])
        if (
            comparison["body_delta_words"] != actual_body_delta["words"]
            or comparison["body_delta_utf8_bytes"] != actual_body_delta["utf8_bytes"]
        ):
            raise DietError(f"local pilot accepted comparison body delta mismatch: {skill_id}")
        locks[skill_id] = dict(entry_digests)
    validate_atomic_dependency_group_routes(atomic_groups, candidate_runs_by_owner)
    return locks


def coverage_for(snapshot: dict[str, Any], skill_id: str) -> dict[str, Any]:
    return index_skills(snapshot)[skill_id]["eval_coverage"]


def validate_admitted_context(
    snapshot: dict[str, Any],
    run_artifact: dict[str, Any],
    skill_id: str,
    case_id: str,
    label: str,
    required_skill_ids: set[str] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    issues: list[dict[str, Any]] = []
    admitted = run_artifact.get("admitted_context")
    if not isinstance(admitted, list):
        return [{"code": "evidence_admission_invalid", "side": label, "skill_id": skill_id, "case_id": case_id}], []
    units = context_unit_index(snapshot)
    seen: set[tuple[str, str]] = set()
    full_paths: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for item in admitted:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str) or not isinstance(item.get("content_unit"), str):
            issues.append({"code": "evidence_admitted_context_invalid", "side": label, "skill_id": skill_id, "case_id": case_id})
            continue
        key = (item["path"], item["content_unit"])
        if key in seen:
            issues.append({"code": "evidence_admitted_context_duplicate", "side": label, "path": item["path"], "content_unit": item["content_unit"]})
            continue
        seen.add(key)
        expected = units.get(key)
        if expected is None:
            issues.append({"code": "evidence_admitted_context_unknown", "side": label, "path": item["path"], "content_unit": item["content_unit"]})
            continue
        for field in ("sha256", "words", "utf8_bytes"):
            if item.get(field) != expected[field]:
                issues.append({"code": "evidence_admitted_context_mismatch", "side": label, "path": item["path"], "content_unit": item["content_unit"], "field": field})
        if item["content_unit"] == "full_file":
            full_paths.add(item["path"])
        normalized.append(dict(expected))
    for path, content_unit in seen:
        if content_unit != "full_file" and path in full_paths:
            issues.append({"code": "evidence_admitted_context_overlap", "side": label, "path": path})
    units_by_path: dict[str, set[str]] = {}
    for path, content_unit in seen:
        units_by_path.setdefault(path, set()).add(content_unit)
    for path, content_units in units_by_path.items():
        if {"body", "routing_card"} <= content_units:
            issues.append({"code": "evidence_admitted_context_overlap", "side": label, "path": path})
    invoked = run_artifact.get("skill_invoked")
    owner = index_skills(snapshot)[skill_id]
    owner_path = owner["source_path"]
    if invoked is True and (owner_path, "full_file") not in seen:
        issues.append({"code": "evidence_skill_file_missing", "side": label, "skill_id": skill_id, "case_id": case_id})
    if invoked is False and any((owner_path, unit) in seen for unit in ("full_file", "body", "routing_card")):
        issues.append({"code": "evidence_noninvoked_execution_context", "side": label, "skill_id": skill_id, "case_id": case_id})
    for required_skill_id in sorted(required_skill_ids or set()):
        required_skill = index_skills(snapshot).get(required_skill_id)
        if required_skill is None:
            continue
        if (required_skill["source_path"], "full_file") not in seen:
            issues.append(
                {
                    "code": "evidence_invoked_skill_context_missing",
                    "side": label,
                    "skill_id": skill_id,
                    "case_id": case_id,
                    "missing_skill_id": required_skill_id,
                }
            )
    return issues, normalized


def validate_evidence(
    snapshot: dict[str, Any],
    oracle_snapshot: dict[str, Any],
    evidence: dict[str, Any],
    label: str,
    evidence_root: Path | None,
    trusted_reviewers: dict[str, dict[str, Any]] | None,
    verification_tier: str = INDEPENDENT_SIGNED_TIER,
) -> tuple[list[dict[str, Any]], dict[tuple[str, str], dict[str, Any]]]:
    issues = evidence_source_errors(snapshot, evidence, label)
    if not isinstance(evidence, dict):
        return issues, {}
    local_pilot = verification_tier == AGENT_REVIEWED_LOCAL_PILOT_TIER
    if verification_tier not in {INDEPENDENT_SIGNED_TIER, AGENT_REVIEWED_LOCAL_PILOT_TIER}:
        issues.append({"code": "evidence_verification_tier_invalid", "side": label})
    if not local_pilot and trusted_reviewers is None:
        issues.append({"code": "evidence_trust_anchor_missing", "side": label})
    expected_schema_version = 1 if local_pilot else EVIDENCE_SCHEMA_VERSION
    if evidence.get("schema_version") != expected_schema_version:
        issues.append({"code": "evidence_schema_version_invalid", "side": label})
    if local_pilot and evidence.get("verification_tier") != AGENT_REVIEWED_LOCAL_PILOT_TIER:
        issues.append({"code": "evidence_verification_tier_mismatch", "side": label})
    if not isinstance(evidence.get("model"), str) or not evidence.get("model"):
        issues.append({"code": "evidence_model_missing", "side": label})
    if not valid_iso_datetime(evidence.get("generated_at")):
        issues.append({"code": "evidence_generated_at_invalid", "side": label})
    expected_eval_digest = oracle_snapshot["evaluation_contract"]["digest"]
    if evidence.get("eval_contract_digest") != expected_eval_digest:
        issues.append({"code": "evidence_eval_contract_mismatch", "side": label})
    runs = evidence.get("runs")
    if not isinstance(runs, list) or not runs:
        issues.append({"code": "evidence_runs_missing", "side": label})
        return issues, {}
    skill_ids = set(index_skills(snapshot))
    indexed: dict[tuple[str, str], dict[str, Any]] = {}
    seen_run_ids: set[str] = set()
    for run in runs:
        run_issue_count = len(issues)
        if not isinstance(run, dict):
            issues.append({"code": "evidence_run_invalid", "side": label})
            continue
        skill_id = run.get("skill_id")
        case_id = run.get("case_id")
        if not isinstance(skill_id, str) or not isinstance(case_id, str) or skill_id not in skill_ids:
            issues.append({"code": "evidence_run_identity_invalid", "side": label})
            continue
        key = (skill_id, case_id)
        if key in indexed:
            issues.append({"code": "evidence_run_duplicate", "side": label, "skill_id": skill_id, "case_id": case_id})
            continue
        run_id = run.get("run_id")
        if not isinstance(run_id, str) or not run_id or run_id in seen_run_ids:
            issues.append({"code": "evidence_run_id_invalid", "side": label, "skill_id": skill_id, "case_id": case_id})
        else:
            seen_run_ids.add(run_id)
        coverage = coverage_for(oracle_snapshot, skill_id)
        routes = coverage["declared_route_cases"]
        primary_cases = set(routes["primary"])
        supporting_cases = set(routes["supporting"])
        negative_cases = set(routes["negative"])
        if case_id not in primary_cases | supporting_cases | negative_cases:
            issues.append(
                {
                    "code": "evidence_case_not_owned",
                    "side": label,
                    "skill_id": skill_id,
                    "case_id": case_id,
                }
            )
        expected_oracle = coverage["case_oracle_digests"].get(case_id)
        if run.get("case_oracle_sha256") != expected_oracle:
            issues.append({"code": "evidence_case_oracle_mismatch", "side": label, "skill_id": skill_id, "case_id": case_id})

        prompt_ref = run.get("prompt_artifact") if local_pilot else None
        run_ref = run.get("run_artifact")
        output_ref = run.get("output_artifact")
        review_ref = run.get("review_artifact") if local_pilot else None
        verifier_ref = run.get("verifier_receipt")
        prompt_ref_issues: list[dict[str, Any]] = []
        review_ref_issues: list[dict[str, Any]] = []
        prompt_bytes: bytes | None = None
        review_bytes: bytes | None = None
        if local_pilot:
            prompt_ref_issues, prompt_bytes = validate_artifact_ref(evidence_root, prompt_ref, label, "prompt")
            review_ref_issues, review_bytes = validate_artifact_ref(evidence_root, review_ref, label, "review")
        run_ref_issues, run_bytes = validate_artifact_ref(evidence_root, run_ref, label, "run")
        output_ref_issues, output_bytes = validate_artifact_ref(evidence_root, output_ref, label, "output")
        verifier_ref_issues, verifier_bytes = validate_artifact_ref(evidence_root, verifier_ref, label, "verifier")
        issues.extend(
            prompt_ref_issues
            + run_ref_issues
            + output_ref_issues
            + review_ref_issues
            + verifier_ref_issues
        )
        json_issues, run_artifact = json_artifact(run_bytes, label, "run")
        verifier_json_issues, verifier = json_artifact(verifier_bytes, label, "verifier")
        review_json_issues: list[dict[str, Any]] = []
        review_payload: dict[str, Any] | None = None
        if local_pilot:
            review_json_issues, review_payload = json_artifact(review_bytes, label, "review")
        issues.extend(json_issues + review_json_issues + verifier_json_issues)
        if (
            run_artifact is None
            or verifier is None
            or output_bytes is None
            or (local_pilot and (prompt_bytes is None or review_payload is None))
        ):
            continue
        reviewer_id = run.get("reviewer_id")
        if local_pilot:
            if not isinstance(reviewer_id, str) or re.fullmatch(r"agent:[A-Za-z0-9._/-]+", reviewer_id) is None:
                issues.append({"code": "evidence_agent_reviewer_id_invalid", "side": label, "skill_id": skill_id, "case_id": case_id})
            if "verifier_signature" in run:
                issues.append({"code": "evidence_local_pilot_signature_forbidden", "side": label, "skill_id": skill_id, "case_id": case_id})
            for artifact_kind, artifact_bytes in (("prompt", prompt_bytes), ("review", review_bytes)):
                try:
                    artifact_text = artifact_bytes.decode("utf-8", errors="strict") if artifact_bytes is not None else ""
                except UnicodeDecodeError:
                    artifact_text = ""
                if not artifact_text.strip():
                    issues.append(
                        {
                            "code": "evidence_local_pilot_text_artifact_invalid",
                            "side": label,
                            "skill_id": skill_id,
                            "case_id": case_id,
                            "artifact": artifact_kind,
                        }
                    )
            local_hashes = [
                ref.get("sha256")
                for ref in (prompt_ref, run_ref, output_ref, review_ref)
                if isinstance(ref, dict)
            ]
            if len(local_hashes) != len(set(local_hashes)):
                issues.append({"code": "evidence_agent_review_not_distinct", "side": label, "skill_id": skill_id, "case_id": case_id})
            invariant_checks = review_payload.get("invariant_checks") if review_payload is not None else None
            review_limitations = review_payload.get("limitations") if review_payload is not None else None
            if (
                review_payload is None
                or review_payload.get("case_id") != case_id
                or review_payload.get("reviewer_id") != reviewer_id
                or review_payload.get("result") != "pass"
                or review_payload.get("baseline_result") != "pass"
                or review_payload.get("candidate_result") != "pass"
                or not isinstance(review_payload.get("regression_assessment"), str)
                or not review_payload["regression_assessment"].strip()
                or not isinstance(invariant_checks, list)
                or not invariant_checks
                or any(
                    not isinstance(item, dict)
                    or item.get("result") != "pass"
                    or not isinstance(item.get("invariant"), str)
                    or not item["invariant"].strip()
                    or not isinstance(item.get("evidence"), str)
                    or not item["evidence"].strip()
                    for item in invariant_checks
                )
                or not isinstance(review_limitations, list)
                or any(not isinstance(item, str) or not item.strip() for item in review_limitations)
            ):
                issues.append(
                    {
                        "code": "evidence_agent_review_result_invalid",
                        "side": label,
                        "skill_id": skill_id,
                        "case_id": case_id,
                    }
                )
        else:
            signature = run.get("verifier_signature")
            reviewer = (
                trusted_reviewers.get(reviewer_id)
                if trusted_reviewers is not None and isinstance(reviewer_id, str)
                else None
            )
            if reviewer is None:
                issues.append({"code": "evidence_reviewer_untrusted", "side": label, "skill_id": skill_id, "case_id": case_id})
            if not verify_reviewer_signature(verifier_bytes, signature, reviewer):
                issues.append({"code": "evidence_verifier_signature_invalid", "side": label, "skill_id": skill_id, "case_id": case_id})

        expected_source = evidence.get("source")
        execution_contract = run_artifact.get("execution_contract")
        execution_contract_sha256 = run.get("execution_contract_sha256")
        if (
            not isinstance(execution_contract, dict)
            or set(execution_contract) != set(EXECUTION_CONTRACT_FIELDS)
            or not isinstance(execution_contract.get("host_id"), str)
            or not execution_contract["host_id"]
            or any(
                not isinstance(execution_contract.get(field), str)
                or re.fullmatch(r"[0-9a-f]{64}", execution_contract[field]) is None
                for field in EXECUTION_CONTRACT_FIELDS
                if field != "host_id"
            )
            or not isinstance(execution_contract_sha256, str)
            or re.fullmatch(r"[0-9a-f]{64}", execution_contract_sha256) is None
            or sha256_json(execution_contract) != execution_contract_sha256
        ):
            issues.append(
                {
                    "code": "evidence_execution_contract_invalid",
                    "side": label,
                    "skill_id": skill_id,
                    "case_id": case_id,
                }
            )
        elif local_pilot and execution_contract["prompt_sha256"] != (
            prompt_ref.get("sha256") if isinstance(prompt_ref, dict) else None
        ):
            issues.append(
                {
                    "code": "evidence_execution_prompt_mismatch",
                    "side": label,
                    "skill_id": skill_id,
                    "case_id": case_id,
                }
            )
        exact_run_fields = {
            "schema_version": RECEIPT_SCHEMA_VERSION,
            "run_id": run_id,
            "case_id": case_id,
            "skill_id": skill_id,
            "model": evidence.get("model"),
            "eval_contract_digest": expected_eval_digest,
            "case_oracle_sha256": expected_oracle,
            "output_sha256": output_ref.get("sha256") if isinstance(output_ref, dict) else None,
            "execution_contract_sha256": execution_contract_sha256,
        }
        if local_pilot:
            exact_run_fields.update(
                {
                    "verification_tier": AGENT_REVIEWED_LOCAL_PILOT_TIER,
                    "prompt_sha256": prompt_ref.get("sha256") if isinstance(prompt_ref, dict) else None,
                    "context_capture": "declared_context_pack",
                }
            )
        for field, expected_value in exact_run_fields.items():
            if run_artifact.get(field) != expected_value:
                issues.append({"code": "evidence_run_artifact_mismatch", "side": label, "skill_id": skill_id, "case_id": case_id, "field": field})
        if run_artifact.get("source") != expected_source:
            issues.append({"code": "evidence_run_source_mismatch", "side": label, "skill_id": skill_id, "case_id": case_id})
        if not valid_iso_datetime(run_artifact.get("executed_at")):
            issues.append({"code": "evidence_run_time_invalid", "side": label, "skill_id": skill_id, "case_id": case_id})
        eval_mode = run_artifact.get("eval_mode")
        required_mode = coverage["case_required_eval_modes"].get(case_id, "declared_only")
        if eval_mode not in {"host-assisted", "replay"} or (
            required_mode in {"host-assisted", "replay"} and eval_mode != required_mode
        ):
            issues.append({"code": "evidence_eval_mode_invalid", "side": label, "skill_id": skill_id, "case_id": case_id})
        producer = run_artifact.get("producer")
        if not isinstance(producer, dict) or any(not isinstance(producer.get(field), str) or not producer[field] for field in ("kind", "id", "version")):
            issues.append({"code": "evidence_producer_invalid", "side": label, "skill_id": skill_id, "case_id": case_id})
        invoked = run_artifact.get("skill_invoked")
        observed_primary = run_artifact.get("observed_primary_skill")
        observed_supporting = run_artifact.get("observed_supporting_skills")
        if not isinstance(invoked, bool) or not isinstance(observed_supporting, list) or any(not isinstance(item, str) for item in observed_supporting):
            issues.append({"code": "evidence_route_trace_invalid", "side": label, "skill_id": skill_id, "case_id": case_id})
            observed_supporting = []
        expected_primary = coverage["case_expected_primary_skills"].get(case_id)
        expected_supporting = coverage["case_expected_supporting_skills"].get(case_id, [])
        should_not_trigger = set(coverage["case_should_not_trigger"].get(case_id, []))
        if observed_primary != expected_primary:
            issues.append({"code": "evidence_observed_primary_mismatch", "side": label, "skill_id": skill_id, "case_id": case_id})
        if sorted(observed_supporting) != expected_supporting or len(observed_supporting) != len(set(observed_supporting)):
            issues.append({"code": "evidence_observed_supporting_mismatch", "side": label, "skill_id": skill_id, "case_id": case_id})
        if observed_primary in should_not_trigger or should_not_trigger & set(observed_supporting):
            issues.append({"code": "evidence_forbidden_route_observed", "side": label, "skill_id": skill_id, "case_id": case_id})
        if case_id in primary_cases and invoked is not True:
            issues.append({"code": "evidence_primary_not_invoked", "side": label, "skill_id": skill_id, "case_id": case_id})
        if case_id in supporting_cases and (invoked is not True or skill_id not in observed_supporting):
            issues.append({"code": "evidence_supporting_not_invoked", "side": label, "skill_id": skill_id, "case_id": case_id})
        if case_id in negative_cases and case_id not in primary_cases | supporting_cases and (
            invoked is not False or skill_id == observed_primary or skill_id in observed_supporting
        ):
            issues.append({"code": "evidence_negative_invoked", "side": label, "skill_id": skill_id, "case_id": case_id})
        invoked_skill_ids = set(expected_supporting)
        if isinstance(expected_primary, str):
            invoked_skill_ids.add(expected_primary)
        admission_issues, admitted = validate_admitted_context(
            snapshot,
            run_artifact,
            skill_id,
            case_id,
            label,
            invoked_skill_ids,
        )
        issues.extend(admission_issues)

        exact_verifier_fields = {
            "schema_version": RECEIPT_SCHEMA_VERSION,
            "run_id": run_id,
            "case_id": case_id,
            "skill_id": skill_id,
            "model": evidence.get("model"),
            "eval_contract_digest": expected_eval_digest,
            "case_oracle_sha256": expected_oracle,
            "run_artifact_sha256": run_ref.get("sha256") if isinstance(run_ref, dict) else None,
            "output_sha256": output_ref.get("sha256") if isinstance(output_ref, dict) else None,
            "execution_contract_sha256": execution_contract_sha256,
            "eval_mode": eval_mode,
            "executed_at": run_artifact.get("executed_at"),
            "result": "pass",
            "route_result": "pass",
            "behavior_result": "pass",
        }
        if local_pilot:
            exact_verifier_fields.update(
                {
                    "verification_tier": AGENT_REVIEWED_LOCAL_PILOT_TIER,
                    "prompt_sha256": prompt_ref.get("sha256") if isinstance(prompt_ref, dict) else None,
                    "review_artifact_sha256": review_ref.get("sha256") if isinstance(review_ref, dict) else None,
                    "independent": False,
                    "release_eligible": False,
                }
            )
        for field, expected_value in exact_verifier_fields.items():
            if verifier.get(field) != expected_value:
                issues.append({"code": "evidence_verifier_mismatch", "side": label, "skill_id": skill_id, "case_id": case_id, "field": field})
        verifier_identity = verifier.get("verifier")
        if not isinstance(verifier_identity, dict) or any(not isinstance(verifier_identity.get(field), str) or not verifier_identity[field] for field in ("kind", "id", "version")):
            issues.append({"code": "evidence_verifier_identity_invalid", "side": label, "skill_id": skill_id, "case_id": case_id})
        elif (
            verifier_identity.get("kind") != ("agent_review" if local_pilot else "independent_review")
            or verifier_identity.get("id") == (producer.get("id") if isinstance(producer, dict) else None)
            or verifier_identity.get("id") != reviewer_id
        ):
            issues.append(
                {
                    "code": (
                        "evidence_verifier_separation_invalid"
                        if local_pilot
                        else "evidence_verifier_independence_invalid"
                    ),
                    "side": label,
                    "skill_id": skill_id,
                    "case_id": case_id,
                }
            )
        executed_at = parsed_iso_datetime(run_artifact.get("executed_at"))
        reviewed_at = parsed_iso_datetime(verifier.get("reviewed_at"))
        if executed_at is None or reviewed_at is None or reviewed_at < executed_at:
            issues.append({"code": "evidence_review_time_invalid", "side": label, "skill_id": skill_id, "case_id": case_id})
        required_contracts = coverage["case_required_evidence_contracts"].get(case_id, [])
        results = verifier.get("required_evidence_results")
        observed_contracts: list[dict[str, str]] = []
        allowed_basis = {
            run_ref.get("sha256") if isinstance(run_ref, dict) else None,
            output_ref.get("sha256") if isinstance(output_ref, dict) else None,
        }
        allowed_basis.discard(None)
        if not isinstance(results, list):
            issues.append({"code": "evidence_required_results_invalid", "side": label, "skill_id": skill_id, "case_id": case_id})
        else:
            for result in results:
                if not isinstance(result, dict):
                    issues.append({"code": "evidence_required_result_invalid", "side": label, "skill_id": skill_id, "case_id": case_id})
                    continue
                observed_contracts.append({"type": result.get("type"), "requirement_sha256": result.get("requirement_sha256")})
                basis = result.get("basis_sha256")
                if (
                    result.get("result") != "pass"
                    or not isinstance(result.get("type"), str)
                    or not isinstance(result.get("requirement_sha256"), str)
                    or re.fullmatch(r"[0-9a-f]{64}", result["requirement_sha256"]) is None
                    or not isinstance(basis, list)
                    or not basis
                    or any(not isinstance(item, str) or item not in allowed_basis for item in basis)
                ):
                    issues.append({"code": "evidence_required_result_failed", "side": label, "skill_id": skill_id, "case_id": case_id})
            if sorted(observed_contracts, key=lambda item: (str(item.get("type")), str(item.get("requirement_sha256")))) != required_contracts:
                issues.append({"code": "evidence_required_contract_mismatch", "side": label, "skill_id": skill_id, "case_id": case_id})

        if len(issues) == run_issue_count:
            indexed_run = {
                "run_id": run_id,
                "case_id": case_id,
                "skill_id": skill_id,
                "skill_invoked": invoked,
                "observed_primary_skill": observed_primary,
                "observed_supporting_skills": list(observed_supporting),
                "admitted_context": admitted,
                "execution_contract": execution_contract,
                "execution_contract_sha256": execution_contract_sha256,
            }
            if local_pilot:
                indexed_run.update(
                    {
                        "prompt_sha256": prompt_ref.get("sha256") if isinstance(prompt_ref, dict) else None,
                        "review_sha256": review_ref.get("sha256") if isinstance(review_ref, dict) else None,
                        "reviewer_id": reviewer_id,
                    }
                )
            indexed[key] = indexed_run
    return issues, indexed


def paired_evidence_result(
    baseline: dict[str, Any],
    candidate: dict[str, Any],
    baseline_evidence: dict[str, Any],
    candidate_evidence: dict[str, Any],
    baseline_evidence_root: Path | None = None,
    candidate_evidence_root: Path | None = None,
    oracle_snapshot: dict[str, Any] | None = None,
    trusted_reviewers: dict[str, dict[str, Any]] | None = None,
    verification_tier: str = INDEPENDENT_SIGNED_TIER,
) -> dict[str, Any]:
    oracle = oracle_snapshot or baseline
    baseline_issues, baseline_runs = validate_evidence(
        baseline,
        oracle,
        baseline_evidence,
        "baseline",
        baseline_evidence_root,
        trusted_reviewers,
        verification_tier,
    )
    candidate_issues, candidate_runs = validate_evidence(
        candidate,
        oracle,
        candidate_evidence,
        "candidate",
        candidate_evidence_root,
        trusted_reviewers,
        verification_tier,
    )
    issues = baseline_issues + candidate_issues
    if baseline_evidence.get("model") != candidate_evidence.get("model"):
        issues.append({"code": "paired_model_mismatch"})
    if baseline_evidence.get("eval_contract_digest") != candidate_evidence.get("eval_contract_digest"):
        issues.append({"code": "paired_eval_contract_mismatch"})
    if verification_tier == AGENT_REVIEWED_LOCAL_PILOT_TIER and (
        baseline_evidence.get("verification_tier") != candidate_evidence.get("verification_tier")
    ):
        issues.append({"code": "paired_verification_tier_mismatch"})
    if set(baseline_runs) != set(candidate_runs):
        issues.append(
            {
                "code": "paired_case_set_mismatch",
                "baseline": sorted(f"{skill}#{case}" for skill, case in baseline_runs),
                "candidate": sorted(f"{skill}#{case}" for skill, case in candidate_runs),
            }
        )
    for skill_id, case_id in sorted(set(baseline_runs) & set(candidate_runs)):
        baseline_contract = baseline_runs[(skill_id, case_id)].get("execution_contract") or {}
        candidate_contract = candidate_runs[(skill_id, case_id)].get("execution_contract") or {}
        for field in EXECUTION_CONTRACT_FIELDS:
            if baseline_contract.get(field) != candidate_contract.get(field):
                issues.append(
                    {
                        "code": "paired_execution_contract_mismatch",
                        "skill_id": skill_id,
                        "case_id": case_id,
                        "field": field,
                    }
                )
    if verification_tier == AGENT_REVIEWED_LOCAL_PILOT_TIER:
        for skill_id, case_id in sorted(set(baseline_runs) & set(candidate_runs)):
            baseline_run = baseline_runs[(skill_id, case_id)]
            candidate_run = candidate_runs[(skill_id, case_id)]
            if baseline_run.get("prompt_sha256") != candidate_run.get("prompt_sha256"):
                issues.append({"code": "paired_prompt_mismatch", "skill_id": skill_id, "case_id": case_id})
            if baseline_run.get("review_sha256") != candidate_run.get("review_sha256"):
                issues.append({"code": "paired_review_artifact_mismatch", "skill_id": skill_id, "case_id": case_id})
            if baseline_run.get("reviewer_id") != candidate_run.get("reviewer_id"):
                issues.append({"code": "paired_reviewer_mismatch", "skill_id": skill_id, "case_id": case_id})

    def admitted_by_case(runs: dict[tuple[str, str], dict[str, Any]]) -> dict[str, dict[str, int]]:
        totals: dict[str, dict[str, int]] = {}
        for (skill_id, case_id), run in sorted(runs.items()):
            words = 0
            utf8_bytes = 0
            for item in run.get("admitted_context") or []:
                value = item.get("words")
                if isinstance(value, int):
                    words += value
                utf8_bytes += int(item.get("utf8_bytes") or 0)
            totals[f"{skill_id}#{case_id}"] = {"words": words, "utf8_bytes": utf8_bytes}
        return totals

    def admitted_units_by_case(runs: dict[tuple[str, str], dict[str, Any]]) -> dict[str, list[dict[str, str]]]:
        return {
            f"{skill_id}#{case_id}": sorted(
                (
                    {"path": str(item["path"]), "content_unit": str(item["content_unit"])}
                    for item in run.get("admitted_context") or []
                ),
                key=lambda item: (item["path"], item["content_unit"]),
            )
            for (skill_id, case_id), run in sorted(runs.items())
        }

    def admitted_total(per_case: dict[str, dict[str, int]]) -> dict[str, int]:
        words = 0
        utf8_bytes = 0
        for item in per_case.values():
            words += item["words"]
            utf8_bytes += item["utf8_bytes"]
        return {"words": words, "utf8_bytes": utf8_bytes}

    baseline_by_case = admitted_by_case(baseline_runs)
    candidate_by_case = admitted_by_case(candidate_runs)
    baseline_total = admitted_total(baseline_by_case)
    candidate_total = admitted_total(candidate_by_case)
    case_deltas = {
        key: candidate_by_case[key]["utf8_bytes"] - baseline_by_case[key]["utf8_bytes"]
        for key in set(baseline_by_case) & set(candidate_by_case)
    }
    admission = (
        "improved"
        if case_deltas and all(delta <= 0 for delta in case_deltas.values()) and any(delta < 0 for delta in case_deltas.values())
        else "not_improved"
    )
    coverage: dict[str, dict[str, list[str]]] = {}
    for skill_id, case_id in sorted(baseline_runs):
        skill_coverage = coverage_for(oracle, skill_id)
        routes = skill_coverage["declared_route_cases"]
        lanes = coverage.setdefault(
            skill_id,
            {
                "primary": [],
                "supporting": [],
                "negative": [],
                "structured": [],
                "structured_negative": [],
                "edge": [],
            },
        )
        for lane in ("primary", "supporting", "negative"):
            if case_id in routes[lane]:
                lanes[lane].append(case_id)
        if case_id in skill_coverage["structured_observed_candidates"]:
            lanes["structured"].append(case_id)
        if case_id in skill_coverage["structured_negative_candidates"]:
            lanes["structured_negative"].append(case_id)
        if case_id in skill_coverage["explicit_edge_cases"]:
            lanes["edge"].append(case_id)
    local_pilot = verification_tier == AGENT_REVIEWED_LOCAL_PILOT_TIER
    return {
        "issues": issues,
        "verification_tier": verification_tier,
        "behavior": (
            "agent-reviewed"
            if local_pilot and not issues
            else "preserved"
            if not issues
            else "unverified"
        ),
        "admission": "unverified" if local_pilot or issues else admission,
        "release_eligible": bool(not issues and not local_pilot),
        "model": baseline_evidence.get("model") if not issues else None,
        "case_count": len(baseline_runs) if not issues else 0,
        "coverage": coverage if not issues else {},
        "baseline_admitted": baseline_total if not issues else None,
        "candidate_admitted": candidate_total if not issues else None,
        "baseline_admitted_by_case": baseline_by_case if not issues else None,
        "candidate_admitted_by_case": candidate_by_case if not issues else None,
        "baseline_admitted_units_by_case": admitted_units_by_case(baseline_runs) if not issues else None,
        "candidate_admitted_units_by_case": admitted_units_by_case(candidate_runs) if not issues else None,
    }


def metric_delta(candidate: dict[str, Any], baseline: dict[str, Any]) -> dict[str, int]:
    return {
        key: int(candidate.get(key) or 0) - int(baseline.get(key) or 0)
        for key in ("words", "characters", "utf8_bytes")
    }


def resource_bytes(skill: dict[str, Any], kind: str | None = None) -> int:
    return sum(
        int(item["size"]["utf8_bytes"])
        for item in skill["resources"]
        if kind is None or item["kind"] == kind
    )


def exact_admission_bytes(skill: dict[str, Any], admission_class: str) -> int:
    return sum(
        int(item["size"]["utf8_bytes"])
        for item in skill["resources"]
        if item["kind"] == "instruction_reference" and item.get("admission_class") == admission_class
    )


def paired_scope_issues(
    oracle_snapshot: dict[str, Any],
    paired_evidence: dict[str, Any],
    skills_needing_evidence: set[str],
    shared_change: dict[str, Any] | None = None,
    explicit_affected_skills: set[str] | None = None,
) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    covered = paired_evidence.get("coverage") if isinstance(paired_evidence.get("coverage"), dict) else {}
    for skill_id in sorted(skills_needing_evidence):
        coverage = coverage_for(oracle_snapshot, skill_id)
        routes = coverage["declared_route_cases"]
        received = covered.get(skill_id) if isinstance(covered.get(skill_id), dict) else {}

        primary = set(routes["primary"])
        supporting = set(routes["supporting"])
        positive_lane = "primary" if primary else "supporting"
        positive_contracts = primary if primary else supporting
        positive_received = set(received.get(positive_lane) or [])
        if not positive_contracts:
            issues.append({"code": "paired_positive_contract_missing", "skill_id": skill_id})
        elif not positive_contracts & positive_received:
            issues.append({"code": "paired_positive_coverage_missing", "skill_id": skill_id, "lane": positive_lane})

        pure_negative = set(routes["negative"]) - primary - supporting
        negative_received = set(received.get("negative") or [])
        if not pure_negative:
            issues.append({"code": "paired_negative_contract_missing", "skill_id": skill_id})
        elif not pure_negative & negative_received:
            issues.append({"code": "paired_negative_coverage_missing", "skill_id": skill_id})
        structured_negative = set(coverage["structured_negative_candidates"])
        if not structured_negative:
            issues.append({"code": "paired_structured_negative_contract_missing", "skill_id": skill_id})
        elif not structured_negative & set(received.get("structured_negative") or []):
            issues.append({"code": "paired_structured_negative_coverage_missing", "skill_id": skill_id})

        if primary and supporting and not supporting & set(received.get("supporting") or []):
            issues.append({"code": "paired_composition_coverage_missing", "skill_id": skill_id})

        routing = index_skills(oracle_snapshot)[skill_id]["routing"]
        if routing.get("allow_implicit_invocation") is True:
            expected_primary = coverage["case_expected_primary_skills"]
            competing = {case_id for case_id in pure_negative if expected_primary.get(case_id) is not None}
            if not competing:
                issues.append({"code": "paired_competing_contract_missing", "skill_id": skill_id})
            elif not competing & negative_received:
                issues.append({"code": "paired_competing_coverage_missing", "skill_id": skill_id})

        structured = set(coverage["structured_observed_candidates"])
        if not structured:
            issues.append({"code": "paired_structured_contract_missing", "skill_id": skill_id})
        elif not structured & set(received.get("structured") or []):
            issues.append({"code": "paired_structured_coverage_missing", "skill_id": skill_id})

        edge = set(coverage["explicit_edge_cases"])
        if not edge:
            issues.append({"code": "paired_edge_contract_missing", "skill_id": skill_id})
        elif not edge & set(received.get("edge") or []):
            issues.append({"code": "paired_edge_coverage_missing", "skill_id": skill_id})
    if shared_change and shared_change.get("changed"):
        baseline_units = paired_evidence.get("baseline_admitted_units_by_case") or {}
        candidate_units = paired_evidence.get("candidate_admitted_units_by_case") or {}

        def observed(side_units: dict[str, Any], skill_id: str, path: str) -> bool:
            return any(
                key.startswith(f"{skill_id}#")
                and any(isinstance(item, dict) and item.get("path") == path for item in entries)
                for key, entries in side_units.items()
                if isinstance(entries, list)
            )

        side_paths = {
            "baseline": set(shared_change.get("removed") or []) | set(shared_change.get("content_changed") or []),
            "candidate": set(shared_change.get("added") or []) | set(shared_change.get("content_changed") or []),
        }
        affected_by_path = shared_change.get("affected_by_path") or {}
        for side, paths in side_paths.items():
            units = baseline_units if side == "baseline" else candidate_units
            for path in sorted(paths):
                path_affected = set(affected_by_path.get(path) or []) | set(explicit_affected_skills or set())
                for skill_id in sorted(path_affected):
                    if not observed(units, skill_id, path):
                        issues.append(
                            {
                                "code": "paired_shared_context_not_observed",
                                "skill_id": skill_id,
                                "side": side,
                                "path": path,
                            }
                        )
    return issues


def shared_context_change(baseline: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    before = {item["path"]: item for item in baseline.get("shared_context_inventory") or []}
    after = {item["path"]: item for item in candidate.get("shared_context_inventory") or []}
    added = sorted(set(after) - set(before))
    removed = sorted(set(before) - set(after))
    changed = sorted(
        path
        for path in set(before) & set(after)
        if before[path]["sha256"] != after[path]["sha256"]
        or before[path]["kind"] != after[path]["kind"]
        or before[path].get("consumers") != after[path].get("consumers")
    )
    affected_by_path: dict[str, list[str]] = {}
    for path in added:
        affected_by_path[path] = sorted(set(after[path].get("consumers") or []))
    for path in removed:
        affected_by_path[path] = sorted(set(before[path].get("consumers") or []))
    for path in changed:
        affected_by_path[path] = sorted(
            set(before[path].get("consumers") or []) | set(after[path].get("consumers") or [])
        )
    before_bytes = sum(int(item["size"]["utf8_bytes"]) for item in before.values())
    after_bytes = sum(int(item["size"]["utf8_bytes"]) for item in after.values())
    return {
        "changed": bool(added or removed or changed),
        "added": added,
        "removed": removed,
        "content_changed": changed,
        "affected_by_path": dict(sorted(affected_by_path.items())),
        "derived_affected_skills": sorted(
            {skill_id for consumers in affected_by_path.values() for skill_id in consumers}
        ),
        "utf8_bytes_delta": after_bytes - before_bytes,
    }


def oracle_overlay_change_kind(before: dict[str, Any], after: dict[str, Any], case_id: str) -> str:
    if before["case_overlay_stable_digests"].get(case_id) != after["case_overlay_stable_digests"].get(case_id):
        return "nonmonotonic"
    for mapping_key in (
        "case_expected_supporting_skills",
        "case_should_not_trigger",
        "case_expected_behaviors",
        "case_forbidden_behaviors",
        "case_behavior_contract_owners",
        "case_scenario_tags",
    ):
        if not set(before[mapping_key].get(case_id, [])) <= set(after[mapping_key].get(case_id, [])):
            return "weakened"
    before_required = Counter(
        (item["type"], item["requirement_sha256"])
        for item in before["case_required_evidence_contracts"].get(case_id, [])
    )
    after_required = Counter(
        (item["type"], item["requirement_sha256"])
        for item in after["case_required_evidence_contracts"].get(case_id, [])
    )
    if any(after_required[key] < count for key, count in before_required.items()):
        return "weakened"
    before_schema = before["case_schema_versions"].get(case_id)
    after_schema = after["case_schema_versions"].get(case_id)
    if int(after_schema or 0) < int(before_schema or 0):
        return "weakened"
    mode_rank = {"declared_only": 0, "replay": 1, "host-assisted": 2}
    before_mode = str(before["case_required_eval_modes"].get(case_id) or "declared_only")
    after_mode = str(after["case_required_eval_modes"].get(case_id) or "declared_only")
    if mode_rank.get(after_mode, -1) < mode_rank.get(before_mode, -1):
        return "weakened"
    return "strengthened" if before["case_oracle_digests"][case_id] != after["case_oracle_digests"][case_id] else "unchanged"


def compare_manifests(
    baseline: dict[str, Any],
    candidate: dict[str, Any],
    require_paired: bool = False,
    allow_oracle_contract_change: bool = False,
    allow_routing_card_change: bool = False,
    allow_agent_reviewed_local_pilot: bool = False,
    paired_evidence: dict[str, Any] | None = None,
    affected_skills: set[str] | None = None,
    accepted_local_locks: dict[str, dict[str, str]] | None = None,
) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    baseline_skills = index_skills(baseline)
    candidate_skills = index_skills(candidate)
    missing = sorted(set(baseline_skills) - set(candidate_skills))
    added = sorted(set(candidate_skills) - set(baseline_skills))
    for skill_id in missing:
        issues.append({"code": "skill_missing", "skill_id": skill_id})
    for skill_id in added:
        issues.append({"code": "skill_added", "skill_id": skill_id})
    explicit_affected = set(affected_skills or set())
    accepted_locks = accepted_local_locks or {}
    accepted_local = set(accepted_locks)
    for skill_id in sorted(explicit_affected - set(baseline_skills) - set(candidate_skills)):
        issues.append({"code": "affected_skill_unknown", "skill_id": skill_id})
    shared_change = shared_context_change(baseline, candidate)
    derived_affected = set(shared_change["derived_affected_skills"])
    affected = explicit_affected | derived_affected

    changes: list[dict[str, Any]] = []
    skills_needing_evidence: set[str] = set()
    instruction_changed_skills: set[str] = set()
    oracle_owner_skills: set[str] = set()
    oracle_owner_cases_checked: set[str] = set()
    instruction_change_requires_evidence = False
    oracle_expanded = False
    oracle_changed = False
    evaluation_contract_changed = baseline["evaluation_contract"]["digest"] != candidate["evaluation_contract"]["digest"]
    if evaluation_contract_changed and not allow_oracle_contract_change:
        issues.append({"code": "evaluation_contract_drift"})

    def record_oracle_owners(coverage: dict[str, Any], case_id: str) -> None:
        if case_id in oracle_owner_cases_checked:
            return
        oracle_owner_cases_checked.add(case_id)
        owners = set(coverage["case_behavior_contract_owners"].get(case_id, []))
        if not owners:
            issues.append({"code": "oracle_overlay_owner_missing", "case": case_id})
            return
        oracle_owner_skills.update(owners)

    for skill_id in sorted(set(baseline_skills) & set(candidate_skills)):
        before = baseline_skills[skill_id]
        after = candidate_skills[skill_id]
        skill_needs_evidence = False
        if before["routing"] != after["routing"]:
            issues.append({"code": "routing_contract_drift", "skill_id": skill_id})
            skill_needs_evidence = True
        before_digests = before["content_digests"]
        after_digests = after["content_digests"]
        changed_trigger_fields = [
            key
            for key in (
                "frontmatter_description",
                "agent_short_description",
                "agent_default_prompt",
            )
            if before_digests[key] != after_digests[key]
        ]
        if changed_trigger_fields:
            issues.append(
                {
                    "code": "trigger_metadata_drift",
                    "skill_id": skill_id,
                    "fields": changed_trigger_fields,
                }
            )
            skill_needs_evidence = True
        routing_card_changed = before_digests["routing_card"] != after_digests["routing_card"]
        context_targets_changed = before_digests["context_targets"] != after_digests["context_targets"]
        if (routing_card_changed or context_targets_changed) and not allow_routing_card_change:
            issues.append(
                {
                    "code": "routing_card_content_drift",
                    "skill_id": skill_id,
                    "context_targets_changed": context_targets_changed,
                }
            )
        if routing_card_changed or context_targets_changed:
            skill_needs_evidence = True
        before_cov = before["eval_coverage"]
        after_cov = after["eval_coverage"]
        for lane in ("primary", "supporting", "negative"):
            lost = sorted(
                set(before_cov["declared_route_cases"][lane])
                - set(after_cov["declared_route_cases"][lane])
            )
            if lost:
                issues.append({"code": "declared_case_lost", "skill_id": skill_id, "lane": lane, "cases": lost})
                skill_needs_evidence = True
            if set(after_cov["declared_route_cases"][lane]) - set(before_cov["declared_route_cases"][lane]):
                oracle_expanded = True
                if not allow_oracle_contract_change:
                    skill_needs_evidence = True
        before_contracts = before_cov["case_oracle_digests"]
        after_contracts = after_cov["case_oracle_digests"]
        structured_lost = sorted(
            set(before_cov["structured_behavior_candidates"])
            - set(after_cov["structured_behavior_candidates"])
        )
        if structured_lost:
            issues.append(
                {
                    "code": "structured_contract_downgraded",
                    "skill_id": skill_id,
                    "cases": structured_lost,
                }
            )
            skill_needs_evidence = True
        for case_ref in sorted(set(before_contracts) & set(after_contracts)):
            if before_contracts[case_ref] != after_contracts[case_ref]:
                oracle_changed = True
                overlay_kind = oracle_overlay_change_kind(before_cov, after_cov, case_ref)
                if overlay_kind == "weakened":
                    issues.append({"code": "oracle_contract_weakened", "skill_id": skill_id, "case": case_ref})
                    skill_needs_evidence = True
                elif overlay_kind == "nonmonotonic":
                    issues.append(
                        {"code": "oracle_contract_nonmonotonic_change", "skill_id": skill_id, "case": case_ref}
                    )
                    skill_needs_evidence = True
                elif not allow_oracle_contract_change:
                    issues.append({"code": "oracle_contract_changed", "skill_id": skill_id, "case": case_ref})
                    skill_needs_evidence = True
                else:
                    record_oracle_owners(after_cov, case_ref)
        added_contracts = set(after_contracts) - set(before_contracts)
        if added_contracts:
            oracle_expanded = True
            if allow_oracle_contract_change:
                for case_ref in sorted(added_contracts):
                    record_oracle_owners(after_cov, case_ref)
            else:
                skill_needs_evidence = True

        body_delta = metric_delta(after["measurements"]["body"], before["measurements"]["body"])
        skill_file_delta = metric_delta(
            after["measurements"]["skill_file"],
            before["measurements"]["skill_file"],
        )
        resource_delta = resource_bytes(after) - resource_bytes(before)
        owned_delta = skill_file_delta["utf8_bytes"] + resource_delta
        must_read_delta = exact_admission_bytes(after, "must_read_exact") - exact_admission_bytes(before, "must_read_exact")
        body_content_changed = before_digests["body"] != after_digests["body"]
        resources_changed = before_digests["resource_inventory"] != after_digests["resource_inventory"]
        if body_content_changed or resources_changed:
            skill_needs_evidence = True
            instruction_change_requires_evidence = True
            instruction_changed_skills.add(skill_id)
        if body_delta["utf8_bytes"] < 0 and resource_delta > 0:
            classification = "possible_relocation"
        elif body_delta["utf8_bytes"] < 0:
            classification = "possible_compression_or_deletion_candidate"
        elif body_delta["utf8_bytes"] > 0:
            classification = "expanded"
        elif body_content_changed or resources_changed:
            classification = "same_size_content_change"
        else:
            classification = "unchanged"
        if (
            body_content_changed
            or resources_changed
            or changed_trigger_fields
            or routing_card_changed
            or body_delta["utf8_bytes"]
            or resource_delta
            or must_read_delta
        ):
            changes.append(
                {
                    "skill_id": skill_id,
                    "skill_file_delta": skill_file_delta,
                    "body_delta": body_delta,
                    "resource_utf8_bytes_delta": resource_delta,
                    "owned_inventory_utf8_bytes_delta": owned_delta,
                    "must_read_exact_utf8_bytes_delta": must_read_delta,
                    "body_content_changed": body_content_changed,
                    "resources_changed": resources_changed,
                    "trigger_metadata_changed": bool(changed_trigger_fields),
                    "routing_card_changed": routing_card_changed,
                    "classification": classification,
                }
            )
        if skill_needs_evidence:
            skills_needing_evidence.add(skill_id)

    skills_needing_evidence.update(oracle_owner_skills)

    structural_regression = any(
        issue["code"]
        in {
            "skill_missing",
            "skill_added",
            "routing_contract_drift",
            "routing_card_content_drift",
            "trigger_metadata_drift",
        }
        for issue in issues
    )
    oracle_regression = any(
        issue["code"]
        in {
            "declared_case_lost",
            "oracle_contract_changed",
            "oracle_contract_weakened",
            "oracle_contract_nonmonotonic_change",
            "structured_contract_downgraded",
        }
        for issue in issues
    )
    scope_issues: list[dict[str, Any]] = []
    if shared_change["changed"]:
        skills_needing_evidence.update(affected & set(baseline_skills) & set(candidate_skills))
    release_skills_needing_evidence = set(skills_needing_evidence)
    evidence_scope_skills = set(skills_needing_evidence)
    if allow_agent_reviewed_local_pilot:
        for skill_id in sorted(accepted_local):
            expected_digests = accepted_locks.get(skill_id)
            candidate_skill = candidate_skills.get(skill_id)
            if expected_digests is None or candidate_skill is None:
                issues.append({"code": "local_pilot_accepted_skill_unknown", "skill_id": skill_id})
                continue
            if skill_id not in instruction_changed_skills:
                issues.append({"code": "local_pilot_accepted_skill_not_changed", "skill_id": skill_id})
            for digest_name, expected_digest in expected_digests.items():
                actual_digest = candidate_skill["content_digests"].get(digest_name)
                if actual_digest != expected_digest:
                    issues.append(
                        {
                            "code": "local_pilot_accepted_skill_digest_mismatch",
                            "skill_id": skill_id,
                            "digest": digest_name,
                            "expected": expected_digest,
                            "actual": actual_digest,
                        }
                    )
        current_instruction_changed_skills = instruction_changed_skills - accepted_local
        if require_paired:
            issues.append({"code": "local_pilot_release_gate_conflict"})
        if allow_routing_card_change:
            issues.append({"code": "local_pilot_routing_card_change_forbidden"})
        if shared_change["changed"] and (derived_affected or explicit_affected):
            issues.append(
                {
                    "code": "local_pilot_shared_execution_context_change_forbidden",
                    "skills": sorted(affected),
                }
            )
        if candidate["evaluation_contract"]["digest"] != LOCAL_PILOT_EVAL_CONTRACT_DIGEST:
            issues.append(
                {
                    "code": "local_pilot_oracle_not_pinned",
                    "expected": LOCAL_PILOT_EVAL_CONTRACT_DIGEST,
                    "actual": candidate["evaluation_contract"]["digest"],
                }
            )
        if len(current_instruction_changed_skills) != 1:
            issues.append(
                {
                    "code": "local_pilot_single_skill_change_required",
                    "skills": sorted(current_instruction_changed_skills),
                    "accepted_skills": sorted(accepted_local),
                }
            )
        disallowed = current_instruction_changed_skills - LOCAL_PILOT_SKILLS
        if disallowed:
            issues.append({"code": "local_pilot_skill_not_allowed", "skills": sorted(disallowed)})
        if paired_evidence is None or paired_evidence.get("verification_tier") != AGENT_REVIEWED_LOCAL_PILOT_TIER:
            issues.append({"code": "local_pilot_evidence_tier_required"})
        evidence_scope_skills = set(current_instruction_changed_skills)
    else:
        if accepted_local:
            issues.append({"code": "local_pilot_accepted_skills_without_local_mode"})
        if paired_evidence is not None and paired_evidence.get("verification_tier") == AGENT_REVIEWED_LOCAL_PILOT_TIER:
            issues.append({"code": "local_pilot_not_enabled"})
    if paired_evidence is not None:
        issues.extend(paired_evidence["issues"])
        if not paired_evidence["issues"]:
            oracle_snapshot = candidate if allow_oracle_contract_change and evaluation_contract_changed else baseline
            scope_issues.extend(
                paired_scope_issues(
                    oracle_snapshot,
                    paired_evidence,
                    evidence_scope_skills,
                    shared_change,
                    explicit_affected,
                )
            )
    issues.extend(scope_issues)
    behavior = "regressed" if structural_regression or oracle_regression else (
        paired_evidence["behavior"]
        if paired_evidence is not None and not scope_issues
        else "unverified"
    )
    admission = (
        paired_evidence["admission"]
        if paired_evidence is not None and not paired_evidence["issues"] and not scope_issues
        else "unverified"
    )
    release_behavior_ok = behavior == "preserved"
    local_behavior_ok = allow_agent_reviewed_local_pilot and behavior == "agent-reviewed"
    if (require_paired and not release_behavior_ok) or (
        instruction_change_requires_evidence and not (release_behavior_ok or local_behavior_ok)
    ):
        if not any(issue.get("code") == "paired_behavior_evidence_missing" for issue in issues):
            issues.append({"code": "paired_behavior_evidence_missing"})
    aggregate_before = baseline["aggregates"]["measurements"]
    aggregate_after = candidate["aggregates"]["measurements"]
    return {
        "status": "FAIL" if issues else "PASS",
        "baseline": baseline["source"],
        "candidate": candidate["source"],
        "release_eligible": bool(
            not issues
            and paired_evidence is not None
            and paired_evidence.get("release_eligible") is True
            and behavior == "preserved"
        ),
        "axes": {
            "structure": "changed" if changes or missing or added or shared_change["changed"] else "unchanged",
            "routing_contract": "drifted" if structural_regression else "unchanged",
            "oracle_contract": (
                "regressed"
                if oracle_regression
                else "changed_allowed"
                if oracle_changed
                else "expanded"
                if oracle_expanded
                else "unchanged"
            ),
            "behavior": behavior,
            "admission": admission,
            "verification_tier": (
                paired_evidence.get("verification_tier")
                if paired_evidence is not None and not paired_evidence["issues"] and not scope_issues
                else "unverified"
            ),
        },
        "aggregate_deltas": {
            key: metric_delta(aggregate_after[key], aggregate_before[key])
            for key in ("skill_file", "body", "routing_card", "frontmatter_description", "owned_inventory")
        },
        "missing_skills": missing,
        "added_skills": added,
        "skill_changes": changes,
        "shared_context_change": shared_change,
        "skills_needing_evidence": sorted(evidence_scope_skills),
        "release_skills_needing_evidence": sorted(release_skills_needing_evidence),
        "accepted_local_skills": sorted(accepted_local),
        "paired_evidence": paired_evidence,
        "issues": issues,
    }


def render_text(result: dict[str, Any]) -> str:
    axes = result["axes"]
    body = result["aggregate_deltas"]["body"]
    owned = result["aggregate_deltas"]["owned_inventory"]
    shared = result["shared_context_change"]
    lines = [
        result["status"],
        f"structure={axes['structure']}",
        f"routing_contract={axes['routing_contract']}",
        f"oracle_contract={axes['oracle_contract']}",
        f"behavior={axes['behavior']}",
        f"admission={axes['admission']}",
        f"verification_tier={axes['verification_tier']}",
        f"release_eligible={str(result['release_eligible']).lower()}",
        f"accepted_local_skills={','.join(result['accepted_local_skills']) or 'none'}",
        f"body_delta_words={body['words']} body_delta_utf8_bytes={body['utf8_bytes']}",
        f"owned_inventory_delta_utf8_bytes={owned['utf8_bytes']}",
        "shared_context_delta_utf8_bytes={delta} added={added} removed={removed} content_changed={changed}".format(
            delta=shared["utf8_bytes_delta"],
            added=len(shared["added"]),
            removed=len(shared["removed"]),
            changed=len(shared["content_changed"]),
        ),
    ]
    for change in result["skill_changes"]:
        lines.append(
            "- {skill_id}: {classification}; body_bytes={body}; resources_bytes={resources}; "
            "must_read_exact_bytes={must_read}".format(
                skill_id=change["skill_id"],
                classification=change["classification"],
                body=change["body_delta"]["utf8_bytes"],
                resources=change["resource_utf8_bytes_delta"],
                must_read=change["must_read_exact_utf8_bytes_delta"],
            )
        )
    for issue in result["issues"]:
        lines.append(f"- issue: {json.dumps(issue, ensure_ascii=False, sort_keys=True)}")
    return "\n".join(lines) + "\n"


def write_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")


def command_snapshot(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    with archived_ref(root, args.source_ref, label=args.source_ref) as (archived, info):
        snapshot = collect_snapshot(archived, info)
    write_yaml(args.output, snapshot)
    print(f"PASS: wrote {args.output} ({snapshot['aggregates']['skill_count']} skills)")
    return 0


def command_reviewer_entry(args: argparse.Namespace) -> int:
    entry = reviewer_public_entry(args.reviewer_id, args.modulus_hex, args.exponent)
    print(json.dumps(entry, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def command_check(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    load_pinned_trusted_reviewers(root)
    manifest = load_manifest(args.manifest)
    schema = canonical_schema_path(root, args.schema, "skill-diet-baseline.schema.json")
    errors = schema_errors(manifest, schema) + semantic_errors(manifest)
    if (args.require_git_provenance or (root / ".git").exists()) and not errors:
        errors.extend(verify_git_provenance(root, manifest))
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"PASS: skill diet baseline {manifest['baseline_id']} ({manifest['aggregates']['skill_count']} skills)")
    return 0


def command_compare(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    local_pilot = args.allow_agent_reviewed_local_pilot
    if args.use_accepted_local_pilot_state and not local_pilot:
        print("FAIL: --use-accepted-local-pilot-state requires --allow-agent-reviewed-local-pilot")
        return 1
    if local_pilot:
        conflicts: list[str] = []
        if not args.candidate_worktree or args.candidate_ref:
            conflicts.append("local pilot requires --candidate-worktree")
        if args.require_paired_evidence:
            conflicts.append("local pilot cannot use --require-paired-evidence")
        if args.allow_routing_card_change:
            conflicts.append("local pilot cannot use --allow-routing-card-change")
        if args.evidence_schema is not None:
            conflicts.append("local pilot uses the canonical local evidence schema")
        if not args.baseline_evidence or not args.candidate_evidence:
            conflicts.append("local pilot requires both evidence files")
        if conflicts:
            print("FAIL")
            for conflict in conflicts:
                print(f"- {conflict}")
            return 1
        trusted_reviewers = None
    else:
        trusted_reviewers = load_pinned_trusted_reviewers(root)
    baseline = load_manifest(args.manifest)
    schema = canonical_schema_path(root, args.schema, "skill-diet-baseline.schema.json")
    errors = schema_errors(baseline, schema) + semantic_errors(baseline)
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    if (root / ".git").exists():
        errors.extend(verify_git_provenance(root, baseline))
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    if args.candidate_worktree:
        candidate = collect_snapshot(root, worktree_source_info(root))
    else:
        with archived_ref(root, args.candidate_ref, label=args.candidate_ref) as (archived, info):
            candidate = collect_snapshot(archived, info)
    lineage_issues = candidate_lineage_issues(root, baseline, candidate)
    if lineage_issues:
        print("FAIL")
        for issue in lineage_issues:
            print(f"- issue: {json.dumps(issue, ensure_ascii=False, sort_keys=True)}")
        return 1
    accepted_local_locks = (
        load_pinned_local_pilot_state(root, baseline, candidate)
        if args.use_accepted_local_pilot_state
        else {}
    )
    if bool(args.baseline_evidence) != bool(args.candidate_evidence):
        print("FAIL: baseline and candidate evidence must be supplied together")
        return 1
    paired: dict[str, Any] | None = None
    if args.baseline_evidence and args.candidate_evidence:
        baseline_evidence = load_manifest(args.baseline_evidence)
        candidate_evidence = load_manifest(args.candidate_evidence)
        evidence_schema_path = args.evidence_schema
        if local_pilot:
            evidence_schema_path = next(
                (
                    path
                    for path in (
                        root / "source" / "shared" / "eval" / "skill-diet-local-pilot-evidence.schema.json",
                        root / ".codex" / "eval" / "skill-diet-local-pilot-evidence.schema.json",
                    )
                    if path.is_file()
                ),
                None,
            )
        elif evidence_schema_path is None:
            evidence_schema_path = next(
                (
                    path
                    for path in (
                        root / "source" / "shared" / "eval" / "skill-diet-evidence.schema.json",
                        root / ".codex" / "eval" / "skill-diet-evidence.schema.json",
                    )
                    if path.is_file()
                ),
                None,
            )
        if evidence_schema_path is None:
            print("FAIL: canonical skill-diet evidence schema is unavailable")
            return 1
        evidence_schema = json.loads(evidence_schema_path.read_text(encoding="utf-8"))
        evidence_schema_errors = [
            *validate_schema(baseline_evidence, evidence_schema),
            *validate_schema(candidate_evidence, evidence_schema),
        ]
        if evidence_schema_errors:
            print("FAIL")
            for error in evidence_schema_errors:
                print(f"- {error}")
            return 1
        evaluation_contract_changed = baseline["evaluation_contract"]["digest"] != candidate["evaluation_contract"]["digest"]
        oracle_snapshot = candidate if args.allow_oracle_contract_change and evaluation_contract_changed else baseline
        paired = paired_evidence_result(
            baseline,
            candidate,
            baseline_evidence,
            candidate_evidence,
            args.baseline_evidence.parent,
            args.candidate_evidence.parent,
            oracle_snapshot,
            trusted_reviewers,
            AGENT_REVIEWED_LOCAL_PILOT_TIER if local_pilot else INDEPENDENT_SIGNED_TIER,
        )
    result = compare_manifests(
        baseline,
        candidate,
        require_paired=args.require_paired_evidence,
        allow_oracle_contract_change=args.allow_oracle_contract_change,
        allow_routing_card_change=args.allow_routing_card_change,
        allow_agent_reviewed_local_pilot=local_pilot,
        paired_evidence=paired,
        affected_skills=set(args.affected_skill or []),
        accepted_local_locks=accepted_local_locks,
    )
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(render_text(result), end="")
    return 0 if result["status"] == "PASS" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    snapshot = subparsers.add_parser("snapshot")
    snapshot.add_argument("--root", type=Path, default=Path("."))
    snapshot.add_argument("--source-ref", required=True)
    snapshot.add_argument("--output", type=Path, required=True)
    snapshot.set_defaults(func=command_snapshot)

    reviewer_entry = subparsers.add_parser("reviewer-entry")
    reviewer_entry.add_argument("--reviewer-id", required=True)
    reviewer_entry.add_argument("--modulus-hex", required=True)
    reviewer_entry.add_argument("--exponent", type=int, default=65537)
    reviewer_entry.set_defaults(func=command_reviewer_entry)

    check = subparsers.add_parser("check")
    check.add_argument("--root", type=Path, default=Path("."))
    check.add_argument("--manifest", type=Path, required=True)
    check.add_argument("--schema", type=Path)
    check.add_argument("--require-git-provenance", action="store_true")
    check.set_defaults(func=command_check)

    compare = subparsers.add_parser("compare")
    compare.add_argument("--root", type=Path, default=Path("."))
    compare.add_argument("--manifest", type=Path, required=True)
    compare.add_argument("--schema", type=Path)
    candidates = compare.add_mutually_exclusive_group(required=True)
    candidates.add_argument("--candidate-worktree", action="store_true")
    candidates.add_argument("--candidate-ref")
    compare.add_argument("--require-paired-evidence", action="store_true")
    compare.add_argument("--allow-agent-reviewed-local-pilot", action="store_true")
    compare.add_argument("--use-accepted-local-pilot-state", action="store_true")
    compare.add_argument("--baseline-evidence", type=Path)
    compare.add_argument("--candidate-evidence", type=Path)
    compare.add_argument("--evidence-schema", type=Path)
    compare.add_argument("--allow-oracle-contract-change", action="store_true")
    compare.add_argument("--allow-routing-card-change", action="store_true")
    compare.add_argument("--affected-skill", action="append", default=[])
    compare.add_argument("--format", choices=("text", "json"), default="text")
    compare.set_defaults(func=command_compare)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return int(args.func(args))
    except (DietError, OSError, ValueError, yaml.YAMLError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
