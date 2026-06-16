#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path

from phase_plan_schema import (
    ARCHETYPES,
    DATED_PLAN_HEADINGS,
    GENERIC_CONTRACTS,
    GROUP_HEADINGS,
    MODIFIERS,
    README_HEADINGS,
    REQUIRED_FRONT_MATTER,
    SPEC_HEADINGS,
    SPEC_DOC_TYPES,
    canonical_archetype,
    required_specs_for,
)

PLACEHOLDER_VALUES = {
    "",
    "-",
    "n/a",
    "na",
    "none",
    "tbd",
    "todo",
    "unverified",
    "`unverified`",
    "<path>",
    "<command>",
    "<artifact>",
    "path",
    "command",
    "artifact",
}

CANONICAL_FALSE_DOC_TYPES = {
    "domain_ingest_summary",
    "handoff_index",
    "phase_group",
    "plan_package_readme",
}


def parse_front_matter(text: str) -> tuple[dict[str, object], str]:
    if not text.startswith("---\n"):
        return {}, text
    parts = text.split("\n")
    meta: dict[str, object] = {}
    key: str | None = None
    idx = 1
    while idx < len(parts):
        line = parts[idx]
        if line == "---":
            body = "\n".join(parts[idx + 1 :])
            return meta, body
        if line.startswith("  - ") and key:
            meta.setdefault(key, [])
            assert isinstance(meta[key], list)
            meta[key].append(line[4:].strip())
        elif ":" in line:
            k, v = line.split(":", 1)
            key = k.strip()
            val = v.strip()
            if val == "":
                meta[key] = []
            elif val == "[]":
                meta[key] = []
            else:
                meta[key] = val
        idx += 1
    return {}, text


def update_front_matter_values(path: Path, values: dict[str, str]) -> None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return
    lines = text.splitlines()
    end = next((idx for idx, line in enumerate(lines[1:], start=1) if line == "---"), None)
    if end is None:
        return
    present = {line.split(":", 1)[0].strip(): idx for idx, line in enumerate(lines[:end]) if ":" in line}
    insert_at = present.get("last_validated", end - 1) + 1
    for key, value in values.items():
        if key in present:
            lines[present[key]] = f"{key}: {value}"
        else:
            lines.insert(insert_at, f"{key}: {value}")
            insert_at += 1
            present = {line.split(":", 1)[0].strip(): idx for idx, line in enumerate(lines[:end + 1]) if ":" in line}
            end += 1
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validation_stamp_values(stamp: str, strict: bool, strict_handoff: bool) -> dict[str, str]:
    mode = "strict-handoff" if strict and strict_handoff else "strict" if strict else "default"
    values = {
        "last_validated": stamp,
        "last_validated_mode": mode,
    }
    if strict:
        values["strict_validated_at"] = stamp
    if strict_handoff:
        values["strict_handoff_validated_at"] = stamp
    return values


def meta_value(meta: dict[str, object], key: str) -> str:
    return str(meta.get(key, "")).strip().strip('"').strip("'")


def meta_bool(meta: dict[str, object], key: str) -> str:
    return meta_value(meta, key).lower()


def validate_required_front_matter(path: Path, meta: dict[str, object], errors: list[str]) -> None:
    for key in REQUIRED_FRONT_MATTER:
        if key not in meta:
            errors.append(f"{path.name}: missing front matter `{key}`")

    doc_type = meta_value(meta, "doc_type")
    canonical = str(meta.get("canonical", "")).strip()
    if canonical not in {"true", "false"}:
        errors.append(f"{path.name}: canonical must be exactly true or false")
    if doc_type:
        expected = "false" if doc_type in CANONICAL_FALSE_DOC_TYPES else "true"
        if canonical in {"true", "false"} and canonical != expected:
            errors.append(f"{path.name}: doc_type={doc_type} requires canonical={expected}")

    if "source_of_truth_for" in meta and not isinstance(meta.get("source_of_truth_for"), list):
        errors.append(f"{path.name}: source_of_truth_for must be a YAML list")
    if "derived_from" in meta and not isinstance(meta.get("derived_from"), list):
        errors.append(f"{path.name}: derived_from must be a YAML list")


def require_headings(text: str, headings: list[str], label: str, errors: list[str]) -> None:
    for heading in headings:
        if heading not in text:
            errors.append(f"{label}: missing heading {heading}")


def find_doc_by_type(paths: list[Path], doc_type: str) -> Path | None:
    for path in paths:
        meta, _ = parse_front_matter(path.read_text(encoding="utf-8"))
        if meta.get("doc_type") == doc_type:
            return path
    return None


def parse_markdown_table_rows(text: str, heading: str) -> list[list[str]]:
    rows: list[list[str]] = []
    if heading not in text:
        return rows
    tail = text.split(heading, 1)[1]
    lines = tail.splitlines()
    started = False
    for line in lines:
        if line.startswith("|"):
            started = True
            cols = [c.strip() for c in line.strip().strip("|").split("|")]
            rows.append(cols)
        elif started and line.strip():
            break
    # remove header + separator
    if len(rows) >= 2:
        return rows[2:]
    return []


def is_placeholder(value: str) -> bool:
    normalized = value.strip().strip("`").lower()
    return normalized in PLACEHOLDER_VALUES or normalized.startswith("<") and normalized.endswith(">")


def row_has_real_value(row: list[str]) -> bool:
    return any(not is_placeholder(cell) for cell in row)


def require_nonempty_table(body: str, heading: str, label: str, errors: list[str]) -> list[list[str]]:
    rows = [row for row in parse_markdown_table_rows(body, heading) if row_has_real_value(row)]
    if not rows:
        errors.append(f"{label}: strict mode requires at least one real row under {heading}")
    return rows


def require_numeric_column(
    rows: list[list[str]],
    column_index: int,
    label: str,
    heading: str,
    errors: list[str],
) -> None:
    for row in rows:
        if len(row) <= column_index:
            errors.append(f"{label}: missing numeric column under {heading}")
            continue
        value = row[column_index]
        if is_placeholder(value) or not re.search(r"\d", value):
            errors.append(f"{label}: non-numeric value `{value}` under {heading}")


def require_real_column(
    rows: list[list[str]],
    column_index: int,
    label: str,
    heading: str,
    column_name: str,
    errors: list[str],
) -> None:
    for row in rows:
        if len(row) <= column_index:
            errors.append(f"{label}: missing {column_name} under {heading}")
            continue
        value = row[column_index]
        if is_placeholder(value):
            errors.append(f"{label}: placeholder {column_name} `{value}` under {heading}")


def require_boolean_column(
    rows: list[list[str]],
    column_index: int,
    label: str,
    heading: str,
    column_name: str,
    errors: list[str],
) -> None:
    allowed = {"true", "false", "yes", "no"}
    for row in rows:
        if len(row) <= column_index:
            errors.append(f"{label}: missing boolean {column_name} under {heading}")
            continue
        value = row[column_index].strip().lower()
        if value not in allowed:
            errors.append(f"{label}: invalid boolean value `{row[column_index]}` for {column_name} under {heading}")


def validate_readme_links(
    readme_text: str,
    package: Path,
    spec_dir: Path,
    slug: str,
    required_specs: list[str],
    errors: list[str],
) -> None:
    group_paths = sorted(p.relative_to(package).as_posix() for p in package.rglob("*.md") if p.name != "README.md")
    for rel in group_paths:
        if rel not in readme_text:
            errors.append(f"README: missing link or mention for {rel}")
    for suffix in required_specs:
        path = f"docs/spec/{slug}-{suffix}.md"
        if (spec_dir / f"{slug}-{suffix}.md").exists() and path not in readme_text:
            errors.append(f"README: missing spec link {path}")


def validate_release_gate(path: Path, body: str, errors: list[str], strict: bool = False) -> None:
    require_headings(body, SPEC_HEADINGS["release-gate"], path.name, errors)
    rows = parse_markdown_table_rows(body, "## Numeric Thresholds")
    for row in rows:
        if len(row) < 2:
            continue
        threshold = row[1]
        if threshold and not re.search(r"\d", threshold):
            errors.append(f"{path.name}: non-numeric threshold value `{threshold}`")
    if strict:
        gate_input_rows = require_nonempty_table(body, "## Gate Inputs", path.name, errors)
        require_real_column(gate_input_rows, 1, path.name, "## Gate Inputs", "Source Gate", errors)
        require_boolean_column(gate_input_rows, 2, path.name, "## Gate Inputs", "Required?", errors)
        upstream_rows = require_nonempty_table(body, "## Upstream Gates", path.name, errors)
        require_real_column(upstream_rows, 1, path.name, "## Upstream Gates", "Contract Doc", errors)
        require_boolean_column(upstream_rows, 3, path.name, "## Upstream Gates", "Blocks Release?", errors)
        dataset_rows = require_nonempty_table(body, "## Datasets", path.name, errors)
        require_real_column(dataset_rows, 1, path.name, "## Datasets", "Version", errors)
        require_real_column(dataset_rows, 2, path.name, "## Datasets", "Source", errors)
        require_boolean_column(dataset_rows, 4, path.name, "## Datasets", "Frozen?", errors)
        threshold_rows = require_nonempty_table(body, "## Numeric Thresholds", path.name, errors)
        require_numeric_column(threshold_rows, 1, path.name, "## Numeric Thresholds", errors)
        require_real_column(threshold_rows, 2, path.name, "## Numeric Thresholds", "Unit", errors)
        regression_rows = require_nonempty_table(body, "## Regression Matrix", path.name, errors)
        require_real_column(regression_rows, 3, path.name, "## Regression Matrix", "Owner", errors)
        rollback_rows = require_nonempty_table(body, "## Rollback Triggers", path.name, errors)
        require_real_column(rollback_rows, 2, path.name, "## Rollback Triggers", "Action", errors)
        evidence_rows = require_nonempty_table(body, "## Evidence Artifacts", path.name, errors)
        require_real_column(evidence_rows, 1, path.name, "## Evidence Artifacts", "Path", errors)


def validate_capability_map(path: Path, body: str, errors: list[str], strict: bool = False) -> None:
    require_headings(body, SPEC_HEADINGS["capability-map"], path.name, errors)
    rows = parse_markdown_table_rows(body, "## Capability Matrix")
    for row in rows:
        if len(row) < 11:
            continue
        priority = row[6]
        contract_link = row[7]
        descoping = row[10]
        if priority == "P0" and is_placeholder(contract_link) and is_placeholder(descoping):
            errors.append(f"{path.name}: P0 row missing contract link or descoping decision")
    if strict:
        require_nonempty_table(body, "## Capability Matrix", path.name, errors)


def section_text(body: str, heading: str) -> str:
    if heading not in body:
        return ""
    tail = body.split(heading, 1)[1]
    match = re.search(r"\n## ", tail)
    return tail[: match.start()] if match else tail


def validate_handoff(path: Path, body: str, errors: list[str], strict_handoff: bool = False) -> None:
    require_headings(body, SPEC_HEADINGS["agent-handoff-index"], path.name, errors)
    if strict_handoff and "unverified" in section_text(body, "## Active Blockers").lower():
        errors.append(f"{path.name}: strict handoff mode requires Active Blockers to be verified")


def list_meta(meta: dict[str, object], key: str) -> list[str]:
    value = meta.get(key, [])
    if isinstance(value, list):
        return [str(item).strip().strip('"').strip("'") for item in value if str(item).strip()]
    raw = str(value).strip()
    return [] if raw in {"", "[]"} else [raw]


def validate_group_doc(
    path: Path,
    meta: dict[str, object],
    body: str,
    errors: list[str],
    quality_warnings: list[str],
    strict_handoff: bool = False,
    quality_lint: bool = False,
) -> None:
    hard = meta_value(meta, "hard_predecessor").lower()
    body_hard = re.search(r"hard predecessor:\s*([A-Za-z0-9_-]+)", body, re.IGNORECASE)
    if body_hard and hard in {"true", "false"} and body_hard.group(1).lower() != hard:
        errors.append(f"{path.name}: hard_predecessor front matter and Dependencies body disagree")

    depends = list_meta(meta, "depends_on")
    body_dep = re.search(r"depends_on:\s*([^\n]+)", body)
    if body_dep and body_dep.group(1).strip().lower() not in {"none", "[]"} and not depends:
        errors.append(f"{path.name}: body Dependencies mention depends_on but front matter depends_on is empty")

    relevant_specs = list_meta(meta, "relevant_specs")
    if len(relevant_specs) > 8:
        quality_warnings.append(f"{path.name}: group relevant_specs has {len(relevant_specs)} docs; prefer 8 or fewer")

    vague_tokens = ["through", "all ids", "etc", "관련 ids"]
    ids_section = section_text(body, "## Referenced Canonical IDs").lower()
    for token in vague_tokens:
        if token in ids_section:
            message = f"{path.name}: vague canonical id expression `{token}` under Referenced Canonical IDs"
            if strict_handoff:
                errors.append(message)
            else:
                quality_warnings.append(message)

    if "## Implementation Digest" not in body:
        errors.append(f"{path.name}: missing Implementation Digest")
    if "## Prohibited Shortcuts" not in body:
        errors.append(f"{path.name}: missing Prohibited Shortcuts")

    if strict_handoff or quality_lint:
        for heading in ["## Purpose", "## Current State", "## Target State"]:
            content = section_text(body, heading).strip()
            if not content:
                errors.append(f"{path.name}: {heading} must not be empty")
        generic_phrases = [
            "Existing behavior or module boundary is not yet decomposed",
            "Define the group-specific success condition",
            "Target structure to be defined",
            "Critical gap to be identified",
            "Target component list to be confirmed",
            "Group responsibilities to be confirmed",
        ]
        for phrase in generic_phrases:
            if phrase in body:
                errors.append(f"{path.name}: quality lint forbids generic scaffold phrase `{phrase}`")

    ac = section_text(body, "## Acceptance Criteria")
    if "- [ ]" in ac or "- [x]" in ac:
        required_tokens = ["Contract:", "Evidence:", "Test command:", "Blocking:"]
        for token in required_tokens:
            if token not in ac:
                message = f"{path.name}: Acceptance Criteria missing `{token}`"
                if strict_handoff:
                    errors.append(message)
                elif quality_lint:
                    quality_warnings.append(message)
        if strict_handoff:
            for placeholder in ["<artifact-or-test-path>", "<command>", "Contract: `{{", "Evidence: `<"]:
                if placeholder in ac:
                    errors.append(f"{path.name}: strict handoff requires concrete Acceptance Criteria evidence and test command")

    todo = section_text(body, "## TODO")
    if re.search(r"- \[ \] [A-Za-z가-힣 ]+$", todo):
        quality_warnings.append(f"{path.name}: TODO item may be too generic; include artifact or contract target")


def validate_strict_contract(path: Path, suffix: str, body: str, errors: list[str]) -> None:
    if suffix == "api-contract":
        require_nonempty_table(body, "## Endpoint Matrix", path.name, errors)
        require_nonempty_table(body, "## Request Response Contracts", path.name, errors)
        evidence_rows = require_nonempty_table(body, "## Evidence", path.name, errors)
        require_real_column(evidence_rows, 1, path.name, "## Evidence", "Path / Command", errors)
    elif suffix == "app-runtime-contract":
        require_nonempty_table(body, "## Runtime Scope", path.name, errors)
        require_nonempty_table(body, "## Lifecycle Matrix", path.name, errors)
        require_nonempty_table(body, "## Resource Ownership", path.name, errors)
    elif suffix == "algorithm-inventory":
        if "### <Algorithm Name>" in body:
            errors.append(f"{path.name}: strict mode requires replacing `<Algorithm Name>`")
        rows = require_nonempty_table(body, "## Validation Matrix", path.name, errors)
        require_numeric_column(rows, 3, path.name, "## Validation Matrix", errors)
    elif suffix == "architecture-contract":
        require_nonempty_table(body, "## Architecture Goals", path.name, errors)
        require_nonempty_table(body, "## Layer Model", path.name, errors)
        require_nonempty_table(body, "## State Ownership", path.name, errors)
        require_nonempty_table(body, "## Dependency Direction", path.name, errors)
    elif suffix == "benchmark-contract":
        require_nonempty_table(body, "## Benchmark Cases", path.name, errors)
        benchmark_rows = parse_markdown_table_rows(body, "## Benchmark Cases")
        require_real_column(benchmark_rows, 3, path.name, "## Benchmark Cases", "Command", errors)
        rows = require_nonempty_table(body, "## Metrics", path.name, errors)
        require_numeric_column(rows, 3, path.name, "## Metrics", errors)
        require_real_column(rows, 4, path.name, "## Metrics", "Unit", errors)
        baseline_rows = require_nonempty_table(body, "## Baseline", path.name, errors)
        require_real_column(baseline_rows, 3, path.name, "## Baseline", "Artifact", errors)
        evidence_rows = require_nonempty_table(body, "## Evidence", path.name, errors)
        require_real_column(evidence_rows, 1, path.name, "## Evidence", "Path", errors)
    elif suffix == "behavior-parity-contract":
        rows = require_nonempty_table(body, "## Behavior Matrix", path.name, errors)
        require_real_column(rows, 4, path.name, "## Behavior Matrix", "Comparator", errors)
        tests = require_nonempty_table(body, "## Characterization Tests", path.name, errors)
        require_real_column(tests, 2, path.name, "## Characterization Tests", "Command", errors)
        evidence_rows = require_nonempty_table(body, "## Evidence", path.name, errors)
        require_real_column(evidence_rows, 1, path.name, "## Evidence", "Path / Command", errors)
    elif suffix == "compatibility-matrix":
        rows = require_nonempty_table(body, "## Compatibility Matrix", path.name, errors)
        require_boolean_column(rows, 2, path.name, "## Compatibility Matrix", "Compatible?", errors)
        combos = require_nonempty_table(body, "## Supported Combinations", path.name, errors)
        require_boolean_column(combos, 2, path.name, "## Supported Combinations", "Supported?", errors)
        validation_rows = require_nonempty_table(body, "## Validation", path.name, errors)
        require_real_column(validation_rows, 1, path.name, "## Validation", "Command", errors)
        evidence_rows = require_nonempty_table(body, "## Evidence", path.name, errors)
        require_real_column(evidence_rows, 1, path.name, "## Evidence", "Path / Command", errors)
    elif suffix == "characterization-test-plan":
        require_nonempty_table(body, "## Characterization Inventory", path.name, errors)
        tests = require_nonempty_table(body, "## Test Matrix", path.name, errors)
        require_real_column(tests, 2, path.name, "## Test Matrix", "Command", errors)
        artifacts = require_nonempty_table(body, "## Golden Artifacts", path.name, errors)
        require_real_column(artifacts, 1, path.name, "## Golden Artifacts", "Path", errors)
        require_boolean_column(artifacts, 3, path.name, "## Golden Artifacts", "Frozen?", errors)
    elif suffix == "data-contract":
        require_nonempty_table(body, "## Entity Matrix", path.name, errors)
        require_nonempty_table(body, "## Schema Rules", path.name, errors)
        evidence_rows = require_nonempty_table(body, "## Evidence", path.name, errors)
        require_real_column(evidence_rows, 1, path.name, "## Evidence", "Path / Command", errors)
    elif suffix == "deployment-contract":
        require_nonempty_table(body, "## Deployment Matrix", path.name, errors)
        release_rows = require_nonempty_table(body, "## Release Environments", path.name, errors)
        require_real_column(release_rows, 3, path.name, "## Release Environments", "Validation", errors)
        rollout_rows = require_nonempty_table(body, "## Rollout Rules", path.name, errors)
        require_real_column(rollout_rows, 3, path.name, "## Rollout Rules", "Stop Condition", errors)
        rollback_rows = require_nonempty_table(body, "## Rollback Link", path.name, errors)
        require_real_column(rollback_rows, 1, path.name, "## Rollback Link", "Rollback Contract", errors)
        evidence_rows = require_nonempty_table(body, "## Evidence", path.name, errors)
        require_real_column(evidence_rows, 1, path.name, "## Evidence", "Path / Command", errors)
    elif suffix == "build-contract":
        require_nonempty_table(body, "## Build Targets", path.name, errors)
        command_rows = require_nonempty_table(body, "## Build Commands", path.name, errors)
        require_real_column(command_rows, 2, path.name, "## Build Commands", "Command", errors)
        artifact_rows = require_nonempty_table(body, "## Artifacts", path.name, errors)
        require_real_column(artifact_rows, 1, path.name, "## Artifacts", "Path", errors)
        input_rows = require_nonempty_table(body, "## Environment Inputs", path.name, errors)
        require_boolean_column(input_rows, 2, path.name, "## Environment Inputs", "Required?", errors)
        evidence_rows = require_nonempty_table(body, "## Evidence", path.name, errors)
        require_real_column(evidence_rows, 1, path.name, "## Evidence", "Path / Command", errors)
    elif suffix == "dataset-contract":
        dataset_rows = require_nonempty_table(body, "## Dataset Matrix", path.name, errors)
        require_real_column(dataset_rows, 1, path.name, "## Dataset Matrix", "Version", errors)
        require_real_column(dataset_rows, 2, path.name, "## Dataset Matrix", "Source", errors)
        require_boolean_column(dataset_rows, 4, path.name, "## Dataset Matrix", "Frozen?", errors)
        rows = require_nonempty_table(body, "## Data Quality Rules", path.name, errors)
        require_numeric_column(rows, 3, path.name, "## Data Quality Rules", errors)
        evidence_rows = require_nonempty_table(body, "## Evidence", path.name, errors)
        require_real_column(evidence_rows, 1, path.name, "## Evidence", "Path", errors)
    elif suffix == "dependency-graph":
        require_nonempty_table(body, "## Graph Scope", path.name, errors)
        require_nonempty_table(body, "## Dependency Matrix", path.name, errors)
        evidence_rows = require_nonempty_table(body, "## Evidence", path.name, errors)
        require_real_column(evidence_rows, 1, path.name, "## Evidence", "Path / Command", errors)
    elif suffix == "dependency-rule-contract":
        require_nonempty_table(body, "## Rule Matrix", path.name, errors)
        require_nonempty_table(body, "## Allowed Dependencies", path.name, errors)
        require_nonempty_table(body, "## Forbidden Dependencies", path.name, errors)
        enforcement_rows = require_nonempty_table(body, "## Enforcement", path.name, errors)
        require_real_column(enforcement_rows, 1, path.name, "## Enforcement", "Command / Tool", errors)
    elif suffix == "evaluation-gate":
        require_nonempty_table(body, "## Evaluation Matrix", path.name, errors)
        rows = require_nonempty_table(body, "## Numeric Thresholds", path.name, errors)
        require_numeric_column(rows, 1, path.name, "## Numeric Thresholds", errors)
        require_real_column(rows, 2, path.name, "## Numeric Thresholds", "Unit", errors)
        artifact_rows = require_nonempty_table(body, "## Required Artifacts", path.name, errors)
        require_real_column(artifact_rows, 1, path.name, "## Required Artifacts", "Path", errors)
    elif suffix == "experiment-contract":
        require_nonempty_table(body, "## Experiment Matrix", path.name, errors)
        reproducibility_rows = require_nonempty_table(body, "## Reproducibility Rules", path.name, errors)
        require_real_column(reproducibility_rows, 2, path.name, "## Reproducibility Rules", "Command", errors)
        metric_rows = require_nonempty_table(body, "## Metrics", path.name, errors)
        require_numeric_column(metric_rows, 1, path.name, "## Metrics", errors)
        artifact_rows = require_nonempty_table(body, "## Artifacts", path.name, errors)
        require_real_column(artifact_rows, 1, path.name, "## Artifacts", "Path", errors)
        evidence_rows = require_nonempty_table(body, "## Evidence", path.name, errors)
        require_real_column(evidence_rows, 1, path.name, "## Evidence", "Path / Command", errors)
    elif suffix == "environment-contract":
        require_nonempty_table(body, "## Environment Matrix", path.name, errors)
        tool_rows = require_nonempty_table(body, "## Toolchain Versions", path.name, errors)
        require_real_column(tool_rows, 1, path.name, "## Toolchain Versions", "Version", errors)
        require_real_column(tool_rows, 3, path.name, "## Toolchain Versions", "Verification Command", errors)
        reproducibility_rows = require_nonempty_table(body, "## Reproducibility", path.name, errors)
        require_real_column(reproducibility_rows, 1, path.name, "## Reproducibility", "Command", errors)
        require_real_column(reproducibility_rows, 3, path.name, "## Reproducibility", "Artifact", errors)
        evidence_rows = require_nonempty_table(body, "## Evidence", path.name, errors)
        require_real_column(evidence_rows, 1, path.name, "## Evidence", "Path / Command", errors)
    elif suffix == "failure-mode-contract":
        require_nonempty_table(body, "## Failure Mode Matrix", path.name, errors)
        detection_rows = require_nonempty_table(body, "## Detection Rules", path.name, errors)
        require_numeric_column(detection_rows, 3, path.name, "## Detection Rules", errors)
        recovery_rows = require_nonempty_table(body, "## Recovery Rules", path.name, errors)
        require_boolean_column(recovery_rows, 2, path.name, "## Recovery Rules", "Retry?", errors)
        escalation_rows = require_nonempty_table(body, "## Escalation Rules", path.name, errors)
        require_boolean_column(escalation_rows, 2, path.name, "## Escalation Rules", "Blocking?", errors)
        evidence_rows = require_nonempty_table(body, "## Evidence", path.name, errors)
        require_real_column(evidence_rows, 1, path.name, "## Evidence", "Path / Command", errors)
    elif suffix == "failure-matrix":
        require_nonempty_table(body, "## Failure Matrix", path.name, errors)
        detection_rows = require_nonempty_table(body, "## Detection Matrix", path.name, errors)
        require_numeric_column(detection_rows, 2, path.name, "## Detection Matrix", errors)
        require_nonempty_table(body, "## Fallback Matrix", path.name, errors)
        escalation_rows = require_nonempty_table(body, "## Escalation Rules", path.name, errors)
        require_boolean_column(escalation_rows, 2, path.name, "## Escalation Rules", "Blocking?", errors)
        evidence_rows = require_nonempty_table(body, "## Evidence", path.name, errors)
        require_real_column(evidence_rows, 1, path.name, "## Evidence", "Path / Command", errors)
    elif suffix == "firmware-behavior-contract":
        require_nonempty_table(body, "## Firmware Scope", path.name, errors)
        require_nonempty_table(body, "## Behavior Matrix", path.name, errors)
        rows = require_nonempty_table(body, "## Timing Requirements", path.name, errors)
        require_numeric_column(rows, 1, path.name, "## Timing Requirements", errors)
        require_real_column(rows, 2, path.name, "## Timing Requirements", "Unit", errors)
    elif suffix == "hardware-interface-contract":
        require_nonempty_table(body, "## Hardware Revisions", path.name, errors)
        require_nonempty_table(body, "## Interface Matrix", path.name, errors)
        rows = require_nonempty_table(body, "## Electrical Constraints", path.name, errors)
        require_numeric_column(rows, 2, path.name, "## Electrical Constraints", errors)
        require_real_column(rows, 3, path.name, "## Electrical Constraints", "Unit", errors)
        fixtures = require_nonempty_table(body, "## Validation Fixtures", path.name, errors)
        require_real_column(fixtures, 3, path.name, "## Validation Fixtures", "Command / Procedure", errors)
    elif suffix == "input-output-contract":
        input_rows = require_nonempty_table(body, "## Input Matrix", path.name, errors)
        require_boolean_column(input_rows, 2, path.name, "## Input Matrix", "Required?", errors)
        require_nonempty_table(body, "## Output Matrix", path.name, errors)
        require_nonempty_table(body, "## Transformation Rules", path.name, errors)
        fixture_rows = require_nonempty_table(body, "## Validation Fixtures", path.name, errors)
        require_real_column(fixture_rows, 1, path.name, "## Validation Fixtures", "Input Artifact", errors)
        require_real_column(fixture_rows, 2, path.name, "## Validation Fixtures", "Expected Output", errors)
        require_real_column(fixture_rows, 3, path.name, "## Validation Fixtures", "Command", errors)
        evidence_rows = require_nonempty_table(body, "## Evidence", path.name, errors)
        require_real_column(evidence_rows, 1, path.name, "## Evidence", "Path / Command", errors)
    elif suffix == "mesh-ops-contract":
        ops_rows = require_nonempty_table(body, "## Mesh Operation Matrix", path.name, errors)
        require_boolean_column(ops_rows, 3, path.name, "## Mesh Operation Matrix", "Required?", errors)
        require_real_column(ops_rows, 4, path.name, "## Mesh Operation Matrix", "Fallback", errors)
        require_nonempty_table(body, "## Geometry Risk Matrix", path.name, errors)
        poc_rows = require_nonempty_table(body, "## PoC Plan", path.name, errors)
        require_real_column(poc_rows, 2, path.name, "## PoC Plan", "Success Criteria", errors)
        output_rows = require_nonempty_table(body, "## Output Validity", path.name, errors)
        require_real_column(output_rows, 3, path.name, "## Output Validity", "Evidence", errors)
    elif suffix == "local-storage-contract":
        require_nonempty_table(body, "## Storage Matrix", path.name, errors)
        schema_rows = require_nonempty_table(body, "## Schema And Versioning", path.name, errors)
        require_real_column(schema_rows, 1, path.name, "## Schema And Versioning", "Version", errors)
        require_nonempty_table(body, "## Persistence Rules", path.name, errors)
        safety_rows = require_nonempty_table(body, "## Data Safety", path.name, errors)
        require_real_column(safety_rows, 3, path.name, "## Data Safety", "Validation", errors)
        evidence_rows = require_nonempty_table(body, "## Evidence", path.name, errors)
        require_real_column(evidence_rows, 1, path.name, "## Evidence", "Path / Command", errors)
    elif suffix == "migration-map":
        require_nonempty_table(body, "## Migration Scope", path.name, errors)
        require_nonempty_table(body, "## Old To New Mapping", path.name, errors)
        require_nonempty_table(body, "## Sequence", path.name, errors)
        require_nonempty_table(body, "## Rollback Hook", path.name, errors)
    elif suffix == "module-boundary-map":
        require_nonempty_table(body, "## Module Matrix", path.name, errors)
        require_nonempty_table(body, "## Public Boundaries", path.name, errors)
        require_nonempty_table(body, "## Cross Module Rules", path.name, errors)
    elif suffix == "gap-registry":
        gap_rows = require_nonempty_table(body, "## Gap Matrix", path.name, errors)
        require_real_column(gap_rows, 2, path.name, "## Gap Matrix", "Severity", errors)
        require_real_column(gap_rows, 4, path.name, "## Gap Matrix", "Required Before", errors)
    elif suffix == "old-new-mapping":
        require_nonempty_table(body, "## Mapping Matrix", path.name, errors)
        behavior_rows = require_nonempty_table(body, "## Behavior Equivalence", path.name, errors)
        require_real_column(behavior_rows, 3, path.name, "## Behavior Equivalence", "Comparator", errors)
        validation_rows = require_nonempty_table(body, "## Validation", path.name, errors)
        require_real_column(validation_rows, 1, path.name, "## Validation", "Command", errors)
        evidence_rows = require_nonempty_table(body, "## Evidence", path.name, errors)
        require_real_column(evidence_rows, 1, path.name, "## Evidence", "Path / Command", errors)
    elif suffix == "observability-contract":
        require_nonempty_table(body, "## Signal Matrix", path.name, errors)
        require_nonempty_table(body, "## Logging Rules", path.name, errors)
        rows = require_nonempty_table(body, "## Metrics", path.name, errors)
        require_real_column(rows, 1, path.name, "## Metrics", "Unit", errors)
    elif suffix == "performance-budget":
        rows = require_nonempty_table(body, "## Budget Matrix", path.name, errors)
        require_numeric_column(rows, 3, path.name, "## Budget Matrix", errors)
        require_real_column(rows, 4, path.name, "## Budget Matrix", "Unit", errors)
        require_real_column(rows, 6, path.name, "## Budget Matrix", "Measurement Command", errors)
        methods = require_nonempty_table(body, "## Measurement Method", path.name, errors)
        require_real_column(methods, 5, path.name, "## Measurement Method", "Output Artifact", errors)
        evidence_rows = require_nonempty_table(body, "## Evidence", path.name, errors)
        require_real_column(evidence_rows, 1, path.name, "## Evidence", "Path", errors)
    elif suffix == "parity-contract":
        rows = require_nonempty_table(body, "## Parity Matrix", path.name, errors)
        require_real_column(rows, 3, path.name, "## Parity Matrix", "Comparator", errors)
        method_rows = require_nonempty_table(body, "## Comparison Method", path.name, errors)
        require_real_column(method_rows, 1, path.name, "## Comparison Method", "Command", errors)
        require_nonempty_table(body, "## Validation Fixtures", path.name, errors)
        evidence_rows = require_nonempty_table(body, "## Evidence", path.name, errors)
        require_real_column(evidence_rows, 1, path.name, "## Evidence", "Path / Command", errors)
    elif suffix == "pin-map":
        require_nonempty_table(body, "## Pin Matrix", path.name, errors)
        require_nonempty_table(body, "## Revision Mapping", path.name, errors)
        rows = require_nonempty_table(body, "## Electrical Notes", path.name, errors)
        require_numeric_column(rows, 2, path.name, "## Electrical Notes", errors)
    elif suffix == "platform-lifecycle-contract":
        require_nonempty_table(body, "## Platform Matrix", path.name, errors)
        require_nonempty_table(body, "## Lifecycle Events", path.name, errors)
        require_nonempty_table(body, "## Validation", path.name, errors)
    elif suffix == "protocol-contract":
        require_nonempty_table(body, "## Protocol Scope", path.name, errors)
        require_nonempty_table(body, "## Message Matrix", path.name, errors)
        rows = require_nonempty_table(body, "## Timing Rules", path.name, errors)
        require_numeric_column(rows, 2, path.name, "## Timing Rules", errors)
        require_real_column(rows, 3, path.name, "## Timing Rules", "Unit", errors)
    elif suffix == "public-api-contract":
        require_nonempty_table(body, "## Public Surface", path.name, errors)
        require_nonempty_table(body, "## Compatibility Policy", path.name, errors)
        require_nonempty_table(body, "## Versioning Rules", path.name, errors)
    elif suffix == "refactor-target-inventory":
        require_nonempty_table(body, "## Target Inventory", path.name, errors)
        require_nonempty_table(body, "## Refactor Drivers", path.name, errors)
        require_nonempty_table(body, "## Blast Radius", path.name, errors)
        evidence_rows = require_nonempty_table(body, "## Evidence", path.name, errors)
        require_real_column(evidence_rows, 1, path.name, "## Evidence", "Path / Command", errors)
    elif suffix == "resource-lifecycle-contract":
        require_nonempty_table(body, "## Resource Matrix", path.name, errors)
        require_nonempty_table(body, "## Ownership Transfer", path.name, errors)
        require_nonempty_table(body, "## Lifecycle Rules", path.name, errors)
        leak_rows = require_nonempty_table(body, "## Leak Prevention", path.name, errors)
        require_numeric_column(leak_rows, 2, path.name, "## Leak Prevention", errors)
        require_real_column(leak_rows, 3, path.name, "## Leak Prevention", "Action", errors)
        evidence_rows = require_nonempty_table(body, "## Evidence", path.name, errors)
        require_real_column(evidence_rows, 1, path.name, "## Evidence", "Path / Command", errors)
    elif suffix == "regression-matrix":
        require_nonempty_table(body, "## Regression Matrix", path.name, errors)
        baseline_rows = require_nonempty_table(body, "## Baseline", path.name, errors)
        require_real_column(baseline_rows, 2, path.name, "## Baseline", "Artifact", errors)
        require_boolean_column(baseline_rows, 3, path.name, "## Baseline", "Frozen?", errors)
        execution_rows = require_nonempty_table(body, "## Execution", path.name, errors)
        require_real_column(execution_rows, 1, path.name, "## Execution", "Command", errors)
        require_real_column(execution_rows, 3, path.name, "## Execution", "Output Artifact", errors)
        evidence_rows = require_nonempty_table(body, "## Evidence", path.name, errors)
        require_real_column(evidence_rows, 1, path.name, "## Evidence", "Path / Command", errors)
    elif suffix == "rendering-pipeline-contract":
        require_nonempty_table(body, "## Pipeline Stages", path.name, errors)
        require_nonempty_table(body, "## Resource Flow", path.name, errors)
        rows = require_nonempty_table(body, "## Frame Budget", path.name, errors)
        require_numeric_column(rows, 2, path.name, "## Frame Budget", errors)
        require_real_column(rows, 3, path.name, "## Frame Budget", "Unit", errors)
        require_real_column(rows, 4, path.name, "## Frame Budget", "Measurement Method", errors)
        evidence_rows = require_nonempty_table(body, "## Evidence", path.name, errors)
        require_real_column(evidence_rows, 1, path.name, "## Evidence", "Path", errors)
    elif suffix == "security-contract":
        require_nonempty_table(body, "## Security Scope", path.name, errors)
        require_nonempty_table(body, "## Threat Matrix", path.name, errors)
        require_nonempty_table(body, "## Control Matrix", path.name, errors)
        require_nonempty_table(body, "## Verification", path.name, errors)
    elif suffix == "rollback-plan":
        require_nonempty_table(body, "## Rollback Scope", path.name, errors)
        require_nonempty_table(body, "## Triggers", path.name, errors)
        procedure_rows = require_nonempty_table(body, "## Procedure", path.name, errors)
        require_real_column(procedure_rows, 2, path.name, "## Procedure", "Command / Path", errors)
        require_nonempty_table(body, "## Verification", path.name, errors)
    elif suffix == "rollback-trigger":
        rows = require_nonempty_table(body, "## Trigger Matrix", path.name, errors)
        require_numeric_column(rows, 2, path.name, "## Trigger Matrix", errors)
        require_nonempty_table(body, "## Severity Rules", path.name, errors)
        actions = require_nonempty_table(body, "## Actions", path.name, errors)
        require_real_column(actions, 2, path.name, "## Actions", "Command / Procedure", errors)
        evidence_rows = require_nonempty_table(body, "## Evidence", path.name, errors)
        require_real_column(evidence_rows, 1, path.name, "## Evidence", "Path / Command", errors)
    elif suffix == "route-contract":
        require_nonempty_table(body, "## Route Matrix", path.name, errors)
        state_rows = require_nonempty_table(body, "## State Binding", path.name, errors)
        require_boolean_column(state_rows, 2, path.name, "## State Binding", "Persisted?", errors)
        require_nonempty_table(body, "## Guard Rules", path.name, errors)
        evidence_rows = require_nonempty_table(body, "## Evidence", path.name, errors)
        require_real_column(evidence_rows, 1, path.name, "## Evidence", "Path / Command", errors)
    elif suffix == "runtime-loop-contract":
        require_nonempty_table(body, "## Loop Matrix", path.name, errors)
        rows = require_nonempty_table(body, "## Timing Budget", path.name, errors)
        require_numeric_column(rows, 2, path.name, "## Timing Budget", errors)
        require_real_column(rows, 3, path.name, "## Timing Budget", "Unit", errors)
        evidence_rows = require_nonempty_table(body, "## Evidence", path.name, errors)
        require_real_column(evidence_rows, 1, path.name, "## Evidence", "Path / Command", errors)
    elif suffix == "scene-graph-contract":
        require_nonempty_table(body, "## Node Matrix", path.name, errors)
        require_nonempty_table(body, "## Transform Rules", path.name, errors)
        require_nonempty_table(body, "## Resource Binding", path.name, errors)
        mutation_rows = require_nonempty_table(body, "## Mutation Rules", path.name, errors)
        require_real_column(mutation_rows, 2, path.name, "## Mutation Rules", "Thread / Queue", errors)
        evidence_rows = require_nonempty_table(body, "## Evidence", path.name, errors)
        require_real_column(evidence_rows, 1, path.name, "## Evidence", "Path / Command", errors)
    elif suffix == "source-of-truth-policy":
        require_nonempty_table(body, "## Authority Map", path.name, errors)
        require_nonempty_table(body, "## Derived Documents", path.name, errors)
        require_nonempty_table(body, "## Drift Smells", path.name, errors)
    elif suffix == "theme-token-contract":
        require_nonempty_table(body, "## Semantic Components", path.name, errors)
        hard_rules = section_text(body, "## Hard Rules").lower()
        if "literal" not in hard_rules or not any(token in hard_rules for token in ["no ", "prohibit", "forbid"]):
            errors.append(f"{path.name}: strict mode requires literal-style prohibition rules under ## Hard Rules")
    elif suffix == "tolerance-contract":
        rows = require_nonempty_table(body, "## Tolerance Matrix", path.name, errors)
        require_numeric_column(rows, 3, path.name, "## Tolerance Matrix", errors)
        require_real_column(rows, 4, path.name, "## Tolerance Matrix", "Unit", errors)
        methods = require_nonempty_table(body, "## Measurement Method", path.name, errors)
        require_real_column(methods, 2, path.name, "## Measurement Method", "Command", errors)
        datasets = require_nonempty_table(body, "## Dataset Binding", path.name, errors)
        require_real_column(datasets, 1, path.name, "## Dataset Binding", "Version", errors)
        require_boolean_column(datasets, 2, path.name, "## Dataset Binding", "Frozen?", errors)
    elif suffix == "threading-contract":
        require_nonempty_table(body, "## Thread Matrix", path.name, errors)
        require_nonempty_table(body, "## Ownership Rules", path.name, errors)
        evidence_rows = require_nonempty_table(body, "## Evidence", path.name, errors)
        require_real_column(evidence_rows, 1, path.name, "## Evidence", "Path / Command", errors)
    elif suffix == "training-pipeline-contract":
        require_nonempty_table(body, "## Pipeline Matrix", path.name, errors)
        dataset_rows = require_nonempty_table(body, "## Data Inputs", path.name, errors)
        require_boolean_column(dataset_rows, 2, path.name, "## Data Inputs", "Frozen?", errors)
        command_rows = require_nonempty_table(body, "## Training Commands", path.name, errors)
        require_real_column(command_rows, 1, path.name, "## Training Commands", "Command", errors)
        artifact_rows = require_nonempty_table(body, "## Output Artifacts", path.name, errors)
        require_real_column(artifact_rows, 1, path.name, "## Output Artifacts", "Path", errors)
        evidence_rows = require_nonempty_table(body, "## Evidence", path.name, errors)
        require_real_column(evidence_rows, 1, path.name, "## Evidence", "Path / Command", errors)
    elif suffix == "test-inventory":
        require_nonempty_table(body, "## Test Inventory", path.name, errors)
        coverage_rows = require_nonempty_table(body, "## Coverage Matrix", path.name, errors)
        require_boolean_column(coverage_rows, 2, path.name, "## Coverage Matrix", "Required?", errors)
        command_rows = require_nonempty_table(body, "## Execution Commands", path.name, errors)
        require_real_column(command_rows, 1, path.name, "## Execution Commands", "Command", errors)
        evidence_rows = require_nonempty_table(body, "## Evidence", path.name, errors)
        require_real_column(evidence_rows, 1, path.name, "## Evidence", "Path / Command", errors)
    elif suffix == "ui-state-contract":
        require_nonempty_table(body, "## Canonical State IDs", path.name, errors)
        require_nonempty_table(body, "## Error States", path.name, errors)
        require_nonempty_table(body, "## CTA Visibility / Enabled Rules", path.name, errors)
        transitions = section_text(body, "## Transitions")
        normalized = re.sub(r"[`\s]", "", transitions).lower()
        if normalized in {"mermaidflowchartlr", "flowchartlr"} or "-->" not in transitions:
            errors.append(f"{path.name}: strict mode requires a non-empty transition graph under ## Transitions")
    elif suffix == "validation-dataset":
        dataset_rows = require_nonempty_table(body, "## Dataset Matrix", path.name, errors)
        require_real_column(dataset_rows, 1, path.name, "## Dataset Matrix", "Version", errors)
        require_real_column(dataset_rows, 2, path.name, "## Dataset Matrix", "Source", errors)
        require_boolean_column(dataset_rows, 4, path.name, "## Dataset Matrix", "Frozen?", errors)
        require_nonempty_table(body, "## Coverage", path.name, errors)
        access_rows = require_nonempty_table(body, "## Access Rules", path.name, errors)
        require_real_column(access_rows, 1, path.name, "## Access Rules", "Access Path", errors)
        evidence_rows = require_nonempty_table(body, "## Evidence", path.name, errors)
        require_real_column(evidence_rows, 1, path.name, "## Evidence", "Path / Command", errors)
    elif suffix == "versioning-policy":
        require_nonempty_table(body, "## Versioning Rules", path.name, errors)
        require_nonempty_table(body, "## Compatibility Promises", path.name, errors)
        breaking_rows = require_nonempty_table(body, "## Breaking Change Policy", path.name, errors)
        require_boolean_column(breaking_rows, 1, path.name, "## Breaking Change Policy", "Allowed?", errors)
        require_nonempty_table(body, "## Release Tags", path.name, errors)
        evidence_rows = require_nonempty_table(body, "## Evidence", path.name, errors)
        require_real_column(evidence_rows, 1, path.name, "## Evidence", "Path / Command", errors)
    elif suffix == "visual-regression-gate":
        require_nonempty_table(body, "## Baseline Artifacts", path.name, errors)
        baseline_rows = parse_markdown_table_rows(body, "## Baseline Artifacts")
        require_real_column(baseline_rows, 2, path.name, "## Baseline Artifacts", "Path", errors)
        require_boolean_column(baseline_rows, 4, path.name, "## Baseline Artifacts", "Frozen?", errors)
        require_nonempty_table(body, "## Scenario Matrix", path.name, errors)
        rows = require_nonempty_table(body, "## Thresholds", path.name, errors)
        require_numeric_column(rows, 1, path.name, "## Thresholds", errors)
        require_real_column(rows, 2, path.name, "## Thresholds", "Unit", errors)
        evidence_rows = require_nonempty_table(body, "## Evidence", path.name, errors)
        require_real_column(evidence_rows, 1, path.name, "## Evidence", "Path", errors)
    elif suffix in GENERIC_CONTRACTS:
        require_nonempty_table(body, "## Contract Matrix", path.name, errors)
        require_nonempty_table(body, "## Evidence", path.name, errors)


def validate_ui_state_singularity(package_paths: list[Path], spec_paths: list[Path], errors: list[str]) -> None:
    for path in package_paths + spec_paths:
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        if meta.get("doc_type") == "ui_state_contract":
            continue
        if "## Canonical State IDs" in body:
            errors.append(f"{path.name}: redefines canonical state ids outside UI state contract")


def parse_plan_implementation_status(plan_meta: dict[str, object], plan_body: str) -> str:
    status = meta_value(plan_meta, "implementation_status")
    if status:
        return status
    match = re.search(r"current_status:\s*`([^`|]+)`", plan_body)
    if match:
        return match.group(1).strip()
    match = re.search(r"current_status:\s*([A-Za-z0-9_-]+)", plan_body)
    if match:
        return match.group(1).strip()
    return ""


def validate_integration_vs_plan(
    integration_path: Path,
    integration_body: str,
    implementation_status: str,
    errors: list[str],
) -> None:
    impl_open = implementation_status == "implementation-open"
    rows = parse_markdown_table_rows(integration_body, "## Unresolved Interfaces")
    if impl_open:
        for row in rows:
            if len(row) < 3:
                continue
            blocking = row[2].lower()
            if blocking in {"hard", "critical", "blocking"}:
                errors.append(f"{integration_path.name}: blocking unresolved interface while implementation is open")


def validate_hard_predecessors(group_paths: list[Path], errors: list[str]) -> None:
    groups = []
    for path in group_paths:
        meta, _ = parse_front_matter(path.read_text(encoding="utf-8"))
        if meta.get("doc_type") != "phase_group":
            continue
        groups.append((path, meta))

    def phase_num(meta: dict[str, object], path: Path) -> int:
        raw = str(meta.get("phase_order", "")).strip()
        if raw.isdigit():
            return int(raw)
        errors.append(f"{path.name}: missing numeric phase_order front matter")
        return 0

    progressed = [
        (path, meta)
        for path, meta in groups
        if meta_value(meta, "status").lower() in {"in-progress", "doing", "done", "validated"}
    ]
    blockers = [
        (path, meta)
        for path, meta in groups
        if meta_value(meta, "hard_predecessor").lower() == "true"
        and meta_value(meta, "status").lower() not in {"done", "validated", "waived"}
    ]

    for block_path, block_meta in blockers:
        bp = phase_num(block_meta, block_path)
        for prog_path, prog_meta in progressed:
            pp = phase_num(prog_meta, prog_path)
            if pp > bp:
                errors.append(
                    f"{prog_path.name}: later phase progressed while hard predecessor {block_path.name} is incomplete"
                )


def validate_selection_metadata(readme_body: str, plan_body: str, archetype: str, modifiers: list[str], errors: list[str]) -> None:
    expected_archetype = f"archetype: `{archetype}`"
    if expected_archetype not in readme_body:
        errors.append(f"README: missing selected {expected_archetype}")
    if f"archetype: `{archetype}`" not in plan_body:
        errors.append(f"canonical dated plan: missing selected {expected_archetype}")

    modifier_text = ", ".join(modifiers) if modifiers else "none"
    expected_modifiers = f"modifiers: `{modifier_text}`"
    if expected_modifiers not in readme_body:
        errors.append(f"README: missing selected {expected_modifiers}")
    if expected_modifiers not in plan_body:
        errors.append(f"canonical dated plan: missing selected {expected_modifiers}")


def command_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if "validate_phase_plan_package.py" in line]


def validate_validation_command_consistency(readme_body: str, plan_body: str, errors: list[str]) -> None:
    readme_commands = command_lines(section_text(readme_body, "## Validation Commands"))
    plan_commands = command_lines(section_text(plan_body, "### Agent Validation"))
    if readme_commands and plan_commands and readme_commands != plan_commands:
        errors.append("validation commands differ between README and canonical dated plan")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a phase plan package")
    parser.add_argument("--root", required=True, help="Repo root")
    parser.add_argument("--package", required=True, help="Package path under docs/plan")
    parser.add_argument("--slug", required=True, help="Spec doc slug")
    parser.add_argument("--dated-plan", required=True, help="Canonical dated plan basename or relative path")
    parser.add_argument("--archetype", default="application-product", choices=sorted(set(ARCHETYPES.keys()) | {"ui-product", "algorithm-rewrite", "migration-only"}))
    parser.add_argument("--modifiers", default="", help="Optional comma-separated modifiers")
    parser.add_argument("--strict", action="store_true", help="Fail on placeholder or empty release-critical contract content")
    parser.add_argument("--strict-handoff", action="store_true", help="Fail if handoff blockers remain unverified")
    parser.add_argument("--quality-lint", action="store_true", help="Emit quality warnings for handoff readability and implementation density")
    parser.add_argument("--write-validation-stamp", action="store_true", help="Update last_validated after successful validation")
    args = parser.parse_args()

    canonical = canonical_archetype(args.archetype)
    modifiers = [x.strip() for x in args.modifiers.split(",") if x.strip()]
    unknown_modifiers = [m for m in modifiers if m not in MODIFIERS]
    if unknown_modifiers:
        print("VALIDATION_FAILED")
        for modifier in unknown_modifiers:
            print(f"unknown modifier {modifier}")
        raise SystemExit(1)
    required_specs = required_specs_for(canonical, modifiers)

    root = Path(args.root).resolve()
    package = root / "docs" / "plan" / args.package
    spec_dir = root / "docs" / "spec"
    dated_plan = root / args.dated_plan if "/" in args.dated_plan else root / "docs" / "plan" / args.dated_plan
    errors: list[str] = []
    quality_warnings: list[str] = []

    if not package.exists():
        errors.append(f"missing package directory {package}")

    # README
    readme = package / "README.md"
    if not readme.exists():
        errors.append("missing package README")
        readme_text = ""
    else:
        readme_text = readme.read_text(encoding="utf-8")
        meta, readme_body = parse_front_matter(readme_text)
        validate_required_front_matter(readme, meta, errors)
        if meta.get("doc_type") != "plan_package_readme":
            errors.append("README: missing doc_type=plan_package_readme")
        require_headings(readme_body, README_HEADINGS, "README", errors)
        if "- [ ]" in readme_body or "- [x]" in readme_body:
            errors.append("README: contains checklist items; README must be derived navigation only")
        if "derived" not in str(meta.get("status", "")):
            errors.append("README: status should be derived")

    # Canonical dated plan
    if not dated_plan.exists():
        errors.append(f"missing canonical dated plan {dated_plan}")
        plan_body = ""
        plan_meta: dict[str, object] = {}
        implementation_status = ""
    else:
        plan_text = dated_plan.read_text(encoding="utf-8")
        plan_meta, plan_body = parse_front_matter(plan_text)
        validate_required_front_matter(dated_plan, plan_meta, errors)
        implementation_status = parse_plan_implementation_status(plan_meta, plan_body)
        if plan_meta.get("doc_type") != "canonical_dated_plan":
            errors.append("canonical dated plan: missing doc_type=canonical_dated_plan")
        require_headings(plan_body, DATED_PLAN_HEADINGS, dated_plan.name, errors)

    # Phase/group docs
    package_paths = sorted([p for p in package.rglob("*.md") if p.name != "README.md"])
    group_paths = []
    for path in package_paths:
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        validate_required_front_matter(path, meta, errors)
        if meta.get("doc_type") == "phase_group":
            group_paths.append(path)
            require_headings(body, GROUP_HEADINGS, path.name, errors)
            validate_group_doc(
                path,
                meta,
                body,
                errors,
                quality_warnings,
                strict_handoff=args.strict_handoff,
                quality_lint=args.quality_lint,
            )
            if "Placeholder Scope" in body or "Placeholder Scope" in meta_value(meta, "title"):
                errors.append(f"{path.name}: placeholder group scope is not allowed")
            if "canonical" in body.lower() and "Derived Document Notice" not in body:
                errors.append(f"{path.name}: missing derived document notice")

    if not group_paths:
        errors.append("no phase/group docs found")

    # README links
    if readme.exists():
        validate_readme_links(readme_text, package, spec_dir, args.slug, required_specs, errors)

    # Spec docs by archetype
    spec_paths = []
    for suffix in required_specs:
        path = spec_dir / f"{args.slug}-{suffix}.md"
        if not path.exists():
            errors.append(f"missing spec doc {path.name}")
            continue
        spec_paths.append(path)
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        validate_required_front_matter(path, meta, errors)
        expected_doc_type = SPEC_DOC_TYPES[suffix]
        if meta.get("doc_type") != expected_doc_type:
            errors.append(f"{path.name}: missing doc_type={expected_doc_type}")
        require_headings(body, SPEC_HEADINGS[suffix], path.name, errors)
        if suffix == "release-gate":
            validate_release_gate(path, body, errors, strict=args.strict)
        elif suffix == "capability-map":
            validate_capability_map(path, body, errors, strict=args.strict)
        elif suffix == "agent-handoff-index":
            validate_handoff(path, body, errors, strict_handoff=args.strict_handoff)
        if args.strict:
            validate_strict_contract(path, suffix, body, errors)

    # UI state singularity
    validate_ui_state_singularity(group_paths, spec_paths, errors)

    # Integration vs implementation open
    integration_path = spec_dir / f"{args.slug}-integration-contract.md"
    if integration_path.exists() and dated_plan.exists():
        _, integration_body = parse_front_matter(integration_path.read_text(encoding="utf-8"))
        validate_integration_vs_plan(integration_path, integration_body, implementation_status, errors)

    # Hard predecessor gating
    validate_hard_predecessors(group_paths, errors)

    if readme.exists() and dated_plan.exists():
        validate_selection_metadata(readme_body, plan_body, canonical, modifiers, errors)
        validate_validation_command_consistency(readme_body, plan_body, errors)

    if args.strict_handoff and dated_plan.exists():
        active_group_match = re.search(r"active_group:\s*`?([^`\n]+)`?", plan_body)
        active_group = active_group_match.group(1).strip() if active_group_match else ""
        if not active_group or active_group in {"", "none"}:
            errors.append("canonical dated plan: strict handoff requires active_group")

    if args.quality_lint and readme.exists():
        if "## Human Quickstart" not in readme_body:
            errors.append("README: quality lint requires Human Quickstart")
        read_order_lines = [line for line in section_text(readme_body, "## Canonical Read Order").splitlines() if re.match(r"\d+\. ", line)]
        if len(read_order_lines) > 20:
            quality_warnings.append("README: Canonical Read Order exceeds 20 items; keep Human Quickstart compact")

    if errors:
        print("VALIDATION_FAILED")
        for err in errors:
            print(err)
        raise SystemExit(1)

    if args.quality_lint and quality_warnings:
        print("QUALITY_WARNINGS")
        for warning in quality_warnings:
            print(warning)

    if args.write_validation_stamp:
        stamp = datetime.now().astimezone().isoformat(timespec="seconds")
        stamp_values = validation_stamp_values(stamp, args.strict, args.strict_handoff)
        stamped_paths = []
        for path in [readme, dated_plan, *package_paths, *spec_paths]:
            if path.exists() and path not in stamped_paths:
                update_front_matter_values(path, stamp_values)
                stamped_paths.append(path)

    print("VALIDATION_OK")


if __name__ == "__main__":
    main()
