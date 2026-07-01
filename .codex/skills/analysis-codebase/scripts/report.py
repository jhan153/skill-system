#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import datetime as dt
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

SEVERITY_TO_IMPACT = {
    "info": 1,
    "low": 2,
    "medium": 3,
    "high": 4,
    "critical": 5,
}

QUADRANT_CANONICAL_PREFIX = [
    "```mermaid",
    "quadrantChart",
    '    title "LOC-Complexity 분포"',
    '    x-axis "LOC 낮음" --> "LOC 높음"',
    '    y-axis "Complexity 낮음" --> "Complexity 높음"',
    '    quadrant-1 "고LOC-고복잡도"',
    '    quadrant-2 "저LOC-고복잡도"',
    '    quadrant-3 "저LOC-저복잡도"',
    '    quadrant-4 "고LOC-저복잡도"',
]

QUADRANT_DATA_LINE_RE = re.compile(
    r"^[A-Za-z_][A-Za-z0-9_]*:\s*\[\s*-?\d+(?:\.\d+)?\s*,\s*-?\d+(?:\.\d+)?\s*\]$"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render codebase analysis report from collector artifacts"
    )
    parser.add_argument(
        "--input-dir",
        required=True,
        help="Collector output directory or artifacts directory",
    )
    parser.add_argument("--output", default="", help="Output markdown file path")
    parser.add_argument(
        "--risk-model",
        choices=["default", "strict"],
        default="default",
        help="Gate profile name to use from policy.quality_gates",
    )
    parser.add_argument(
        "--policy",
        default="",
        help="Policy JSON path override (default: artifacts/policy-effective.json)",
    )
    return parser.parse_args()


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def read_tsv(path: Path, has_header: bool = False) -> list[list[str]]:
    if not path.exists():
        return []
    rows: list[list[str]] = []
    for idx, raw in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines()):
        if not raw.strip():
            continue
        if has_header and idx == 0:
            continue
        rows.append(raw.split("\t"))
    return rows


def summarize_lizard(path: Path) -> dict[str, str]:
    if not path.exists() or not path.is_file():
        return {"status": "missing", "artifact": ""}
    text = path.read_text(encoding="utf-8", errors="replace")
    result = {
        "status": "ok" if text.strip() else "empty",
        "artifact": "artifacts/static/lizard-complexity.txt",
    }
    file_match = re.search(r"(\d+)\s+file(?:s)?\s+analyzed", text, re.I)
    if file_match:
        result["files"] = file_match.group(1)
    return result


def sanitize_id(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_]", "_", value)
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned or "X"


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def format_quadrant_number(value: float) -> str:
    if math.isclose(value, round(value), abs_tol=1e-9):
        return str(int(round(value)))
    text = f"{value:.3f}".rstrip("0").rstrip(".")
    return text or "0"


def module_from_path(file_path: str) -> str:
    parts = Path(file_path).parts
    if not parts:
        return "root"
    return parts[0]


def normalize(value: float, max_value: float) -> float:
    if max_value <= 0:
        return 0.0
    return clamp(value / max_value, 0.0, 1.0)


def resolve_artifacts_dir(input_dir: str) -> Path:
    base = Path(input_dir).expanduser().resolve()
    if (base / "artifacts").exists():
        artifacts_dir = base / "artifacts"
    else:
        artifacts_dir = base
    if not artifacts_dir.exists():
        raise SystemExit(f"input-dir does not exist: {input_dir}")
    if not (artifacts_dir / "index.json").exists():
        raise SystemExit(f"index.json not found under: {artifacts_dir}")
    return artifacts_dir


def resolve_policy_path(artifacts_dir: Path, arg_policy: str) -> Path:
    candidates: list[Path] = []
    if arg_policy:
        candidates.append(Path(arg_policy).expanduser().resolve())
    candidates.append((artifacts_dir / "policy-effective.json").resolve())
    candidates.append((Path(__file__).resolve().parent.parent / "references" / "policy-default.json").resolve())

    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate
    raise SystemExit(
        "policy file not found. expected one of: --policy, artifacts/policy-effective.json, references/policy-default.json"
    )


def validate_policy(policy: dict[str, Any], risk_model: str) -> None:
    required_top = [
        "collection",
        "priority_model",
        "action_profiles",
        "owners",
        "quality_gates",
        "diagram",
    ]
    missing = [k for k in required_top if k not in policy]
    if missing:
        raise SystemExit(f"invalid policy: missing top-level keys: {', '.join(missing)}")

    collection_required = [
        "top_n_default",
        "analysis_categories",
        "category_rules",
        "include_prefixes",
        "exclude_prefixes",
        "code_extensions",
    ]
    collection = policy.get("collection", {})
    missing_collection = [k for k in collection_required if k not in collection]
    if missing_collection:
        raise SystemExit(f"invalid policy.collection: missing keys: {', '.join(missing_collection)}")

    priority_model = policy.get("priority_model", {})
    for key in ["weights", "category_bias", "severity_thresholds", "profile_thresholds", "due_days_by_severity"]:
        if key not in priority_model:
            raise SystemExit(f"invalid policy.priority_model: missing key: {key}")

    if risk_model not in policy.get("quality_gates", {}):
        raise SystemExit(f"invalid policy.quality_gates: profile '{risk_model}' not found")


def parse_classification_map(path: Path) -> dict[str, dict[str, Any]]:
    mapping: dict[str, dict[str, Any]] = {}
    for cols in read_tsv(path, has_header=True):
        if len(cols) < 5:
            continue
        file_path, category, included, reason, ext = cols[:5]
        mapping[file_path] = {
            "category": category,
            "included": included.lower() == "true",
            "reason": reason,
            "ext": ext,
        }
    return mapping


def parse_complexity_payload(complexity: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], float]:
    rows: dict[str, dict[str, Any]] = {}
    max_complexity = 0.0
    for row in complexity.get("top_files", []):
        file_path = str(row.get("file", ""))
        if not file_path:
            continue
        score = safe_float(row.get("complexity_score", 0.0))
        max_complexity = max(max_complexity, score)
        rows[file_path] = {
            "complexity": score,
            "loc": safe_int(row.get("loc", 0)),
            "branches": safe_int(row.get("branches", 0)),
            "functions": safe_int(row.get("functions", 0)),
            "density": safe_float(row.get("density", 0.0)),
            "classes": row.get("classes", []),
            "category": row.get("category", "unknown"),
        }
    return rows, max_complexity


def parse_architecture_payload(architecture: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], float]:
    rows: dict[str, dict[str, Any]] = {}
    max_coupling = 0.0
    for row in architecture.get("all_files", []):
        file_path = str(row.get("file", ""))
        if not file_path:
            continue
        coupling = safe_float(row.get("coupling_score", 0.0))
        max_coupling = max(max_coupling, coupling)
        rows[file_path] = {
            "coupling": coupling,
            "fan_in": safe_int(row.get("fan_in", 0)),
            "fan_out": safe_int(row.get("fan_out", 0)),
            "category": row.get("category", "unknown"),
        }
    return rows, max_coupling


def parse_churn_map(artifacts_dir: Path) -> tuple[dict[str, int], Path | None]:
    churn_path_candidates = [artifacts_dir / "git" / "churn_all.tsv", artifacts_dir / "git" / "churn_top.tsv"]
    for source in churn_path_candidates:
        if not source.exists():
            continue
        result: dict[str, int] = {}
        for cols in read_tsv(source):
            if len(cols) < 2:
                continue
            churn = safe_int(cols[0], -1)
            if churn < 0:
                continue
            result[cols[1]] = churn
        if result:
            return result, source
    return {}, None


def build_seed_from_artifacts(
    *,
    artifacts_dir: Path,
    policy: dict[str, Any],
    classification: dict[str, dict[str, Any]],
    complexity_map: dict[str, dict[str, Any]],
    architecture_map: dict[str, dict[str, Any]],
    churn_map: dict[str, int],
    churn_source: Path | None,
) -> list[dict[str, Any]]:
    top_n = safe_int(policy.get("collection", {}).get("top_n_default"), 20)

    seed_path = artifacts_dir / "finding-seed.json"
    existing_seed = load_json(seed_path, [])
    if isinstance(existing_seed, list) and existing_seed:
        normalized_seed: list[dict[str, Any]] = []
        for idx, raw in enumerate(existing_seed, start=1):
            if not isinstance(raw, dict):
                continue
            file_path = str(raw.get("file", "")).strip()
            if not file_path:
                continue
            class_meta = classification.get(file_path, {})
            category = str(raw.get("category") or class_meta.get("category") or "unknown")
            evidence_refs = raw.get("evidence_refs", [])
            if not isinstance(evidence_refs, list):
                evidence_refs = []

            normalized_seed.append(
                {
                    "rank": safe_int(raw.get("rank"), idx),
                    "file": file_path,
                    "category": category,
                    "churn": safe_float(raw.get("churn", churn_map.get(file_path, 0))),
                    "complexity": safe_float(raw.get("complexity", complexity_map.get(file_path, {}).get("complexity", 0.0))),
                    "architecture": safe_float(raw.get("architecture", architecture_map.get(file_path, {}).get("coupling", 0.0))),
                    "evidence_refs": evidence_refs,
                }
            )
        return sorted(normalized_seed, key=lambda x: x.get("rank", 10**9))

    # Reconstruct seed when finding-seed is missing.
    sorted_churn = sorted(churn_map.items(), key=lambda kv: kv[1], reverse=True)
    reconstructed: list[dict[str, Any]] = []
    for idx, (file_path, churn) in enumerate(sorted_churn, start=1):
        class_meta = classification.get(file_path, {})
        if class_meta and not class_meta.get("included", True):
            continue

        category = str(class_meta.get("category", "unknown"))
        evidence_refs = []
        if churn_source is not None:
            try:
                evidence_refs.append(str(churn_source.relative_to(artifacts_dir.parent)))
            except Exception:
                evidence_refs.append(str(churn_source))
        evidence_refs.extend(["artifacts/static/complexity.json", "artifacts/static/architecture.json"])

        reconstructed.append(
            {
                "rank": idx,
                "file": file_path,
                "category": category,
                "churn": float(churn),
                "complexity": safe_float(complexity_map.get(file_path, {}).get("complexity", 0.0)),
                "architecture": safe_float(architecture_map.get(file_path, {}).get("coupling", 0.0)),
                "evidence_refs": evidence_refs,
            }
        )
        if len(reconstructed) >= top_n:
            break

    return reconstructed


def owner_for_scope(file_path: str, policy: dict[str, Any], profile: str) -> str:
    owners = policy.get("owners", {})
    if profile == "security":
        return str(owners.get("security") or owners.get("default") or "Unverified")

    prefix_map = owners.get("prefix_map", {})
    if isinstance(prefix_map, dict):
        longest_match = ""
        owner = None
        for prefix, mapped_owner in prefix_map.items():
            if file_path.startswith(prefix) and len(prefix) > len(longest_match):
                longest_match = prefix
                owner = mapped_owner
        if owner:
            return str(owner)

    return str(owners.get("default") or "Unverified")


def severity_from_priority(priority_score: float, thresholds: dict[str, Any]) -> str:
    if priority_score >= safe_float(thresholds.get("critical", math.inf), math.inf):
        return "critical"
    if priority_score >= safe_float(thresholds.get("high", math.inf), math.inf):
        return "high"
    if priority_score >= safe_float(thresholds.get("medium", math.inf), math.inf):
        return "medium"
    if priority_score >= safe_float(thresholds.get("low", math.inf), math.inf):
        return "low"
    return "info"


def choose_action_profile(
    category: str,
    profile_scores: dict[str, float],
    thresholds: dict[str, Any],
) -> str:
    ranked = sorted(profile_scores.items(), key=lambda kv: kv[1], reverse=True)

    if category == "test":
        for profile, score in ranked:
            if profile == "test_guard":
                continue
            threshold = safe_float(thresholds.get(profile), -math.inf)
            # Test files can still bubble up for architecture/performance only with clear margin.
            if score >= threshold + 0.7:
                return profile
        return "test_guard"

    ranked_non_test = [(profile, score) for profile, score in ranked if profile != "test_guard"]
    for profile, score in ranked_non_test:
        threshold = safe_float(thresholds.get(profile), -math.inf)
        if score >= threshold:
            return profile

    return ranked_non_test[0][0] if ranked_non_test else "refactor"


def due_date_for_severity(severity: str, policy: dict[str, Any]) -> str:
    due_days = policy.get("priority_model", {}).get("due_days_by_severity", {})
    default_days = safe_int(due_days.get("info"), 120)
    days = safe_int(due_days.get(severity), default_days)
    return (dt.date.today() + dt.timedelta(days=days)).isoformat()


def quality_attribute_for_profile(profile: str, policy: dict[str, Any]) -> str:
    action_profile = policy.get("action_profiles", {}).get(profile, {})
    quality_attribute = action_profile.get("quality_attribute")
    if quality_attribute:
        return str(quality_attribute)
    return "maintainability"


def evidence_grade_for_finding(churn: float, complexity: float, architecture: float, refs: list[str]) -> str:
    if not refs:
        return "U"
    if churn > 0 and complexity > 0 and architecture > 0:
        return "A"
    if churn > 0 and complexity > 0:
        return "B"
    return "C"


def summarize_numeric_signals(*, churn: float, complexity: float, coupling: float) -> str:
    return f"churn={int(churn)}, complexity={int(complexity)}, coupling={int(coupling)}"


def build_improvement_plan(
    *,
    profile: str,
    file_path: str,
    churn: float,
    complexity: float,
    coupling: float,
) -> dict[str, Any]:
    file_name = Path(file_path).name or file_path
    signal_summary = summarize_numeric_signals(churn=churn, complexity=complexity, coupling=coupling)

    if profile == "algorithm":
        title = f"{file_name} 분기/반복 로직 단순화"
        detail = (
            f"{file_path}에서 고복잡도 분기 경로를 단계별 함수로 분리하고 중복 조건을 통합합니다. "
            f"핫패스 기준 신호: {signal_summary}."
        )
    elif profile == "architecture":
        title = f"{file_name} 의존 경계 분리"
        detail = (
            f"{file_path}의 호출 책임을 경계 모듈로 분리해 fan-in/fan-out 결합을 낮춥니다. "
            f"구조 기준 신호: {signal_summary}."
        )
    elif profile == "performance":
        title = f"{file_name} 핫패스 성능 최적화"
        detail = (
            f"{file_path}의 반복 호출 구간을 캐시/배치 처리 중심으로 정리해 호출 비용을 줄입니다. "
            f"성능 기준 신호: {signal_summary}."
        )
    elif profile == "security":
        title = f"{file_name} 보안 취약 구간 보완"
        detail = (
            f"{file_path}의 입력/의존성 취약 지점을 재검증하고 방어 로직을 추가합니다. "
            f"보안 기준 신호: {signal_summary}."
        )
    else:
        title = f"{file_name} 유지보수 리팩토링"
        detail = (
            f"{file_path}의 책임 경계를 재배치하고 긴 함수 단위를 분해합니다. "
            f"리팩토링 기준 신호: {signal_summary}."
        )

    return {
        "title": title,
        "detail": detail,
        "related_files": [file_path],
    }


def build_hotspot_findings(
    *,
    seed: list[dict[str, Any]],
    policy: dict[str, Any],
    risk_model: str,
    commit_range: str,
) -> list[dict[str, Any]]:
    if not seed:
        return []

    max_churn = max((safe_float(item.get("churn", 0.0)) for item in seed), default=0.0)
    max_complexity = max((safe_float(item.get("complexity", 0.0)) for item in seed), default=0.0)
    max_architecture = max((safe_float(item.get("architecture", 0.0)) for item in seed), default=0.0)

    weights = policy.get("priority_model", {}).get("weights", {})
    category_bias = policy.get("priority_model", {}).get("category_bias", {})
    severity_thresholds = policy.get("priority_model", {}).get("severity_thresholds", {})
    profile_thresholds = policy.get("priority_model", {}).get("profile_thresholds", {})

    findings: list[dict[str, Any]] = []
    today = dt.date.today()

    for index, row in enumerate(seed, start=1):
        file_path = str(row.get("file", "Unverified"))
        category = str(row.get("category", "unknown") or "unknown")

        churn = safe_float(row.get("churn", 0.0))
        complexity = safe_float(row.get("complexity", 0.0))
        architecture = safe_float(row.get("architecture", 0.0))

        churn_norm = normalize(churn, max_churn)
        complexity_norm = normalize(complexity, max_complexity)
        architecture_norm = normalize(architecture, max_architecture)

        profile_scores = {
            "architecture": round(architecture_norm * 5.0, 3),
            "algorithm": round(complexity_norm * 5.0, 3),
            "performance": round((0.6 * churn_norm + 0.4 * complexity_norm) * 5.0, 3),
            "refactor": round((0.5 * churn_norm + 0.3 * complexity_norm + 0.2 * architecture_norm) * 5.0, 3),
            "test_guard": round(churn_norm * 5.0 if category == "test" else 0.0, 3),
        }

        weighted_score = 0.0
        for profile, signal in profile_scores.items():
            weighted_score += safe_float(weights.get(profile, 0.0)) * signal

        rank = safe_int(row.get("rank"), index)
        rank_boost = max(0.0, (11 - min(rank, 10)) * 0.05)
        cat_bias = safe_float(category_bias.get(category, category_bias.get("unknown", 0.0)), 0.0)

        priority_score = weighted_score + cat_bias + rank_boost
        if risk_model == "strict":
            priority_score *= 1.08
        priority_score = round(priority_score, 3)

        severity = severity_from_priority(priority_score, severity_thresholds)

        impact = SEVERITY_TO_IMPACT.get(severity, 3)
        likelihood = max(1, int(math.ceil(max(churn_norm, complexity_norm) * 5)))
        blast_radius = max(1, int(math.ceil((architecture_norm if architecture > 0 else 0.2) * 3)))
        risk_score = int(impact * likelihood * blast_radius)

        profile = choose_action_profile(category, profile_scores, profile_thresholds)
        action_profile = policy.get("action_profiles", {}).get(profile, {})
        verification = action_profile.get("verification", [])
        if not isinstance(verification, list):
            verification = [str(verification)]
        improvement_plan = build_improvement_plan(
            profile=profile,
            file_path=file_path,
            churn=churn,
            complexity=complexity,
            coupling=architecture,
        )

        evidence_refs = row.get("evidence_refs", [])
        if not isinstance(evidence_refs, list):
            evidence_refs = []

        findings.append(
            {
                "finding_id": f"F-{today.year}-{index:03d}",
                "quality_attribute": quality_attribute_for_profile(profile, policy),
                "severity": severity,
                "risk_score": risk_score,
                "priority_score": priority_score,
                "evidence_grade": evidence_grade_for_finding(churn, complexity, architecture, evidence_refs),
                "evidence_refs": evidence_refs,
                "scope": {
                    "module": module_from_path(file_path),
                    "file": file_path,
                    "category": category,
                    "commit_range": commit_range,
                },
                "decision": {
                    "summary": (
                        f"churn={churn:.1f}, complexity={complexity:.1f}, coupling={architecture:.1f}, "
                        f"dominant_profile={profile}"
                    ),
                },
                "score_breakdown": {
                    "weighted": round(weighted_score, 3),
                    "category_bias": round(cat_bias, 3),
                    "rank_boost": round(rank_boost, 3),
                    "signals": profile_scores,
                },
                "action": {
                    "profile": profile,
                    "owner": owner_for_scope(file_path, policy, profile),
                    "due": due_date_for_severity(severity, policy),
                    "title": str(action_profile.get("title", "Unverified")),
                    "summary": str(action_profile.get("summary", "Unverified")),
                },
                "improvement_plan": improvement_plan,
                "verification_plan": verification,
                "exception": {
                    "approved": False,
                    "expires_on": None,
                },
            }
        )

    return findings


def parse_security_findings(artifacts_dir: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []

    semgrep_payload = load_json(artifacts_dir / "static" / "semgrep.json", {})
    if isinstance(semgrep_payload, dict):
        for idx, item in enumerate(semgrep_payload.get("results", []), start=1):
            severity = str(
                item.get("extra", {}).get("severity")
                or item.get("extra", {}).get("metadata", {}).get("severity")
                or "medium"
            ).lower()
            if severity not in SEVERITY_TO_IMPACT:
                severity = "medium"
            findings.append(
                {
                    "rank": idx,
                    "source": "semgrep",
                    "file": str(item.get("path", "Unverified")),
                    "rule": str(item.get("check_id", "semgrep-rule")),
                    "summary": str(item.get("extra", {}).get("message", "Semgrep finding")),
                    "severity": severity,
                    "evidence_ref": "artifacts/static/semgrep.json",
                }
            )

    dep_payload = load_json(artifacts_dir / "static" / "dependency-check-report.json", {})
    if isinstance(dep_payload, dict):
        rank_offset = len(findings)
        vulns: list[dict[str, Any]] = []
        for dep in dep_payload.get("dependencies", []):
            for vuln in dep.get("vulnerabilities", []):
                severity = str(vuln.get("severity", "medium")).lower()
                if severity not in SEVERITY_TO_IMPACT:
                    severity = "medium"
                vulns.append(
                    {
                        "file": str(dep.get("fileName", "dependency")),
                        "rule": str(vuln.get("name", "dependency-vuln")),
                        "summary": str(vuln.get("description", "Dependency vulnerability")),
                        "severity": severity,
                    }
                )
        for idx, vuln in enumerate(vulns, start=1):
            findings.append(
                {
                    "rank": rank_offset + idx,
                    "source": "dependency-check",
                    "file": vuln["file"],
                    "rule": vuln["rule"],
                    "summary": vuln["summary"],
                    "severity": vuln["severity"],
                    "evidence_ref": "artifacts/static/dependency-check-report.json",
                }
            )

    return findings


def build_security_findings(
    *,
    raw_security: list[dict[str, Any]],
    policy: dict[str, Any],
    risk_model: str,
    commit_range: str,
    start_index: int,
) -> list[dict[str, Any]]:
    if not raw_security:
        return []

    due_by_severity = policy.get("priority_model", {}).get("due_days_by_severity", {})
    security_profile = policy.get("action_profiles", {}).get("security", {})
    security_owner = str(policy.get("owners", {}).get("security") or policy.get("owners", {}).get("default") or "Unverified")

    findings: list[dict[str, Any]] = []
    today = dt.date.today()

    for offset, item in enumerate(raw_security, start=0):
        severity = str(item.get("severity", "medium")).lower()
        if severity not in SEVERITY_TO_IMPACT:
            severity = "medium"

        impact = SEVERITY_TO_IMPACT.get(severity, 3)
        likelihood = 4 if severity in {"high", "critical"} else 3
        blast_radius = 3 if severity in {"high", "critical"} else 2
        risk_score = impact * likelihood * blast_radius

        priority_score = float(impact)
        if severity == "critical":
            priority_score += 2.5
        elif severity == "high":
            priority_score += 1.8
        elif severity == "medium":
            priority_score += 1.0
        else:
            priority_score += 0.3

        if risk_model == "strict":
            priority_score *= 1.1

        days = safe_int(due_by_severity.get(severity), safe_int(due_by_severity.get("high"), 30))
        due = (today + dt.timedelta(days=days)).isoformat()

        verification = security_profile.get("verification", [])
        if not isinstance(verification, list):
            verification = [str(verification)]
        file_path = str(item.get("file", "Unverified"))
        improvement_plan = build_improvement_plan(
            profile="security",
            file_path=file_path,
            churn=0.0,
            complexity=0.0,
            coupling=0.0,
        )

        finding_number = start_index + offset
        findings.append(
            {
                "finding_id": f"F-{today.year}-S{finding_number:03d}",
                "quality_attribute": quality_attribute_for_profile("security", policy),
                "severity": severity,
                "risk_score": int(risk_score),
                "priority_score": round(priority_score, 3),
                "evidence_grade": "A",
                "evidence_refs": [str(item.get("evidence_ref", "Unverified"))],
                "scope": {
                    "module": module_from_path(str(item.get("file", "security"))),
                    "file": file_path,
                    "category": "security",
                    "commit_range": commit_range,
                },
                "decision": {
                    "summary": str(item.get("summary", "Security finding detected"))[:220],
                },
                "score_breakdown": {
                    "weighted": round(priority_score, 3),
                    "category_bias": 0.0,
                    "rank_boost": 0.0,
                    "signals": {
                        "architecture": 0.0,
                        "algorithm": 0.0,
                        "performance": 0.0,
                        "refactor": 0.0,
                        "test_guard": 0.0,
                    },
                },
                "action": {
                    "profile": "security",
                    "owner": security_owner,
                    "due": due,
                    "title": str(security_profile.get("title", "Unverified")),
                    "summary": str(security_profile.get("summary", "Unverified")),
                },
                "improvement_plan": improvement_plan,
                "verification_plan": verification,
                "exception": {
                    "approved": False,
                    "expires_on": None,
                },
            }
        )

    return findings


def summarize_branches(rows: list[list[str]]) -> dict[str, Any]:
    if not rows:
        return {
            "total": 0,
            "stale_30d": 0,
            "stale_ratio": 0.0,
            "long_lived": [],
        }

    now = dt.datetime.now(dt.timezone.utc)
    stale = 0
    long_lived = []
    for row in rows:
        if len(row) < 2:
            continue
        name = row[0]
        date_raw = row[1]
        author = row[2] if len(row) > 2 else "Unverified"
        age_days = None
        try:
            stamp = dt.datetime.fromisoformat(date_raw.replace(" ", "T"))
            if stamp.tzinfo is None:
                stamp = stamp.replace(tzinfo=dt.timezone.utc)
            age_days = (now - stamp).days
        except Exception:
            age_days = None

        if age_days is not None and age_days > 30:
            stale += 1
            long_lived.append({"branch": name, "age_days": age_days, "author": author})

    total = len(rows)
    return {
        "total": total,
        "stale_30d": stale,
        "stale_ratio": round(stale / total, 3) if total else 0.0,
        "long_lived": sorted(long_lived, key=lambda x: x["age_days"], reverse=True)[:10],
    }


def evaluate_quality_gate(
    *,
    findings: list[dict[str, Any]],
    unverified_items: list[dict[str, Any]],
    exceptions: list[dict[str, Any]],
    policy: dict[str, Any],
    risk_model: str,
    architecture_views: list[dict[str, Any]],
) -> dict[str, Any]:
    gate = policy.get("quality_gates", {}).get(risk_model, {})

    security_critical_max = safe_int(gate.get("security_critical_max"), 0)
    security_high_max = safe_int(gate.get("security_high_max"), 0)
    expired_exceptions_max = safe_int(gate.get("expired_exceptions_max"), 0)
    unverified_warn_ratio = safe_float(gate.get("unverified_warn_ratio"), 0.2)
    unverified_fail_ratio = safe_float(gate.get("unverified_fail_ratio"), 0.35)
    require_top10_plan_fields = bool(gate.get("require_top10_plan_fields", True))
    max_test_findings_top10 = safe_int(gate.get("max_test_findings_top10"), 2)
    max_missing_architecture_views = safe_int(gate.get("max_missing_architecture_views"), 2)
    max_fallback_diagrams = safe_int(gate.get("max_fallback_diagrams"), 2)
    if "max_diagrams_without_provenance" in gate:
        max_diagrams_without_provenance = safe_int(gate.get("max_diagrams_without_provenance"), 0)
    else:
        max_diagrams_without_provenance = 0 if bool(gate.get("require_diagram_provenance", False)) else 999
    max_runtime_views_without_entrypoint = safe_int(gate.get("max_runtime_views_without_entrypoint"), 1)

    security_critical = 0
    security_high = 0
    for finding in findings:
        if finding.get("quality_attribute") != "security":
            continue
        sev = str(finding.get("severity", "medium"))
        if sev == "critical":
            security_critical += 1
        elif sev == "high":
            security_high += 1

    today = dt.date.today()
    expired_exceptions = 0
    for ex in exceptions:
        if not isinstance(ex, dict):
            continue
        exp = ex.get("expires_on")
        if not exp:
            continue
        try:
            d = dt.date.fromisoformat(str(exp))
            if d < today:
                expired_exceptions += 1
        except Exception:
            continue

    finding_count = len(findings)
    unverified_ratio = round(len(unverified_items) / finding_count, 3) if finding_count else 0.0

    top10 = sorted(findings, key=lambda x: safe_float(x.get("priority_score", 0.0)), reverse=True)[:10]
    missing_top10_plan = 0
    for finding in top10:
        action = finding.get("action", {}) if isinstance(finding.get("action"), dict) else {}
        plan = finding.get("improvement_plan", {}) if isinstance(finding.get("improvement_plan"), dict) else {}
        file_path = str(finding.get("scope", {}).get("file", "")).strip()
        if not action.get("title") or not plan.get("detail") or not file_path:
            missing_top10_plan += 1

    test_findings_top10 = 0
    for finding in top10:
        category = str(finding.get("scope", {}).get("category", "unknown"))
        if category == "test":
            test_findings_top10 += 1

    required_views = {"context", "container", "component", "runtime", "deployment"}
    present_views = {
        str(view.get("view_type", "")).strip()
        for view in architecture_views
        if isinstance(view, dict) and str(view.get("view_type", "")).strip()
    }
    missing_architecture_views = len(required_views - present_views)
    fallback_diagrams = len([view for view in architecture_views if isinstance(view, dict) and bool(view.get("fallback"))])
    diagrams_without_provenance = len(
        [
            view
            for view in architecture_views
            if isinstance(view, dict) and not list(view.get("provenance", []))
        ]
    )
    runtime_views_without_entrypoint = len(
        [
            view
            for view in architecture_views
            if isinstance(view, dict)
            and str(view.get("view_type", "")) == "runtime"
            and not view.get("meta", {}).get("entrypoint_id")
        ]
    )

    reasons: list[str] = []
    warnings: list[str] = []

    if security_critical > security_critical_max:
        reasons.append(f"security_critical={security_critical} > {security_critical_max}")
    if security_high > security_high_max:
        reasons.append(f"security_high={security_high} > {security_high_max}")
    if expired_exceptions > expired_exceptions_max:
        reasons.append(f"expired_exceptions={expired_exceptions} > {expired_exceptions_max}")
    if unverified_ratio > unverified_fail_ratio:
        reasons.append(f"unverified_ratio={unverified_ratio} > fail_threshold={unverified_fail_ratio}")
    elif unverified_ratio > unverified_warn_ratio:
        warnings.append(f"unverified_ratio={unverified_ratio} > warn_threshold={unverified_warn_ratio}")
    if require_top10_plan_fields and missing_top10_plan > 0:
        reasons.append("top10_plan_fields_missing")
    if test_findings_top10 > max_test_findings_top10:
        reasons.append(f"test_findings_top10={test_findings_top10} > {max_test_findings_top10}")
    if missing_architecture_views > max_missing_architecture_views:
        reasons.append(f"missing_architecture_views={missing_architecture_views} > {max_missing_architecture_views}")
    if fallback_diagrams > max_fallback_diagrams:
        reasons.append(f"fallback_diagrams={fallback_diagrams} > {max_fallback_diagrams}")
    if diagrams_without_provenance > max_diagrams_without_provenance:
        reasons.append(
            f"diagrams_without_provenance={diagrams_without_provenance} > {max_diagrams_without_provenance}"
        )
    if runtime_views_without_entrypoint > max_runtime_views_without_entrypoint:
        reasons.append(
            f"runtime_views_without_entrypoint={runtime_views_without_entrypoint} > {max_runtime_views_without_entrypoint}"
        )

    status = "FAIL" if reasons else "PASS"

    return {
        "status": status,
        "reasons": reasons,
        "warnings": warnings,
        "metrics": {
            "security_critical": security_critical,
            "security_high": security_high,
            "expired_exceptions": expired_exceptions,
            "unverified_ratio": unverified_ratio,
            "missing_top10_plan": missing_top10_plan,
            "test_findings_top10": test_findings_top10,
            "missing_architecture_views": missing_architecture_views,
            "fallback_diagrams": fallback_diagrams,
            "diagrams_without_provenance": diagrams_without_provenance,
            "runtime_views_without_entrypoint": runtime_views_without_entrypoint,
        },
        "applied_thresholds": gate,
    }


def pick_top_modules(findings: list[dict[str, Any]], top_n: int = 10) -> list[str]:
    counter = Counter()
    for finding in findings:
        module = str(finding.get("scope", {}).get("module", ""))
        if module:
            counter[module] += 1
    return [m for m, _ in counter.most_common(top_n)]


def parse_call_node(node_id: str) -> tuple[str, str]:
    if "::" in node_id:
        file_path, symbol = node_id.split("::", 1)
        return file_path, symbol
    return node_id, "unknown"


def short_file_label(file_path: str, max_len: int = 28) -> str:
    name = Path(file_path).name or file_path
    if len(name) <= max_len:
        return name
    return name[: max_len - 3] + "..."


def subsystem_from_file(file_path: str, depth: int = 3) -> str:
    parts = Path(file_path).parts
    if not parts:
        return "root"
    if len(parts) <= depth:
        return "/".join(parts)
    return "/".join(parts[:depth])


def _humanize_token(text: str) -> str:
    t = (text or "").strip()
    if t.endswith(".py"):
        t = t[:-3]
    t = t.replace("_", " ").replace("-", " ").strip()
    t = re.sub(r"\s+", " ", t)
    if not t:
        return "Unknown"
    return " ".join(part.capitalize() for part in t.split(" "))


def mermaid_quoted(text: str, fallback: str = "Unknown") -> str:
    value = (text or "").strip()
    if not value:
        value = fallback
    value = value.replace("\\", "\\\\").replace('"', '\\"')
    value = value.replace("\r", " ").replace("\n", " ")
    value = re.sub(r"\s+", " ", value).strip()
    return value or fallback


def mermaid_identifier(text: str, fallback: str = "item") -> str:
    value = (text or "").strip()
    if not value:
        value = fallback
    value = value.replace("\\", "_").replace("/", "_")
    value = re.sub(r"\.py$", "_py", value, flags=re.IGNORECASE)
    value = re.sub(r"[^0-9A-Za-z_]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    if not value:
        value = fallback
    if re.match(r"^[0-9]", value):
        value = f"{fallback}_{value}"
    if not re.match(r"^[A-Za-z_]", value):
        value = f"{fallback}_{value}"
    value = re.sub(r"_+", "_", value).strip("_")
    return value or fallback


def validate_quadrant_chart_contract(lines: list[str]) -> list[str]:
    errors: list[str] = []
    expected_min = len(QUADRANT_CANONICAL_PREFIX) + 1
    if len(lines) < expected_min:
        errors.append("too_few_lines")
        return errors

    for idx, expected in enumerate(QUADRANT_CANONICAL_PREFIX):
        actual = lines[idx] if idx < len(lines) else ""
        if actual != expected:
            errors.append(f"header_mismatch@{idx + 1}")

    if lines[-1] != "```":
        errors.append("missing_closing_fence")

    for idx, raw in enumerate(lines[len(QUADRANT_CANONICAL_PREFIX) : -1], start=len(QUADRANT_CANONICAL_PREFIX) + 1):
        text = (raw or "").strip()
        if not text:
            continue
        if not QUADRANT_DATA_LINE_RE.match(text):
            errors.append(f"invalid_data_line@{idx}")
    return errors


def build_canonical_quadrant_chart(data_rows: list[tuple[str, float, float]]) -> str:
    lines = list(QUADRANT_CANONICAL_PREFIX)
    label_seen: dict[str, int] = defaultdict(int)
    for idx, (raw_label, x_raw, y_raw) in enumerate(data_rows, start=1):
        label = mermaid_identifier(raw_label, f"item_{idx}")
        label_seen[label] += 1
        if label_seen[label] > 1:
            label = f"{label}_{label_seen[label]}"
        x = clamp(safe_float(x_raw), 0.0, 1.0)
        y = clamp(safe_float(y_raw), 0.0, 1.0)
        lines.append(f"    {label}: [{format_quadrant_number(x)}, {format_quadrant_number(y)}]")
    lines.append("```")

    errors = validate_quadrant_chart_contract(lines)
    if errors:
        fallback = list(QUADRANT_CANONICAL_PREFIX)
        fallback.append("    item_1: [0, 0]")
        fallback.append("```")
        return "\n".join(fallback)
    return "\n".join(lines)


def component_display_name(component_path: str) -> str:
    p = component_path.replace("\\", "/")
    mapping = [
        ("scripts/gui/controllers", "GUI 컨트롤러"),
        ("scripts/gui/viewport", "GUI 뷰포트"),
        ("scripts/gui/services", "GUI 서비스"),
        ("scripts/gui/main_window.py", "GUI 메인윈도우"),
        ("scripts/gui", "GUI"),
        ("scripts/render_core", "Render Core"),
        ("scripts/render_preview_service.py", "Render Preview 서비스"),
        ("scripts/render_", "Render 실행"),
        ("tests/", "테스트"),
        ("config/", "설정"),
        ("data/", "데이터"),
    ]
    for prefix, label in mapping:
        if p.startswith(prefix):
            return label
    parts = [x for x in Path(p).parts if x]
    if not parts:
        return "Unknown"
    if len(parts) >= 2:
        return f"{_humanize_token(parts[-2])} · {_humanize_token(parts[-1])}"
    return _humanize_token(parts[-1])


def node_display_name(node_id: str) -> str:
    file_path, symbol = parse_call_node(node_id)
    component = component_display_name(file_path)
    sym = re.sub(r"^_+", "", symbol or "")
    sym = _humanize_token(sym)
    return f"{component} · {sym}"


def edge_action_label(src_node: str, dst_node: str) -> str:
    _src_file, src_symbol = parse_call_node(src_node)
    _dst_file, dst_symbol = parse_call_node(dst_node)
    src = re.sub(r"^_+", "", src_symbol or "")
    dst = re.sub(r"^_+", "", dst_symbol or "")
    if src and dst:
        return f"{_humanize_token(src)} → {_humanize_token(dst)}"
    if dst:
        return _humanize_token(dst)
    return "핵심 처리 흐름"


def parse_edge_list(call_graph: dict[str, Any]) -> list[tuple[str, str, float]]:
    edges: list[tuple[str, str, float]] = []
    raw_edges = call_graph.get("edges", [])
    if not isinstance(raw_edges, list):
        return edges

    for raw in raw_edges:
        if not isinstance(raw, dict):
            continue
        src = str(raw.get("from", "")).strip()
        dst = str(raw.get("to", "")).strip()
        weight = safe_float(raw.get("weight", 0.0), 0.0)
        if not src or not dst:
            continue
        edges.append((src, dst, max(weight, 0.0)))
    return edges


def aggregate_subsystem_transitions(
    call_graph: dict[str, Any],
    *,
    depth: int,
) -> list[tuple[str, str, float]]:
    counter: dict[tuple[str, str], float] = defaultdict(float)
    for src, dst, weight in parse_edge_list(call_graph):
        src_file, _ = parse_call_node(src)
        dst_file, _ = parse_call_node(dst)
        src_ss = subsystem_from_file(src_file, depth=depth)
        dst_ss = subsystem_from_file(dst_file, depth=depth)
        if not src_ss or not dst_ss:
            continue
        counter[(src_ss, dst_ss)] += weight if weight > 0 else 1.0

    rows = [(src, dst, score) for (src, dst), score in counter.items()]
    rows.sort(key=lambda item: item[2], reverse=True)
    return rows


def build_system_sequence_diagram(call_graph: dict[str, Any], policy: dict[str, Any]) -> str:
    diagram_policy = policy.get("diagram", {})
    depth = safe_int(diagram_policy.get("subsystem_depth"), 3)
    max_participants = safe_int(diagram_policy.get("max_system_participants"), 12)
    max_edges = safe_int(diagram_policy.get("max_system_edges"), 24)
    exclude_tests = bool(diagram_policy.get("exclude_test_subsystems", True))

    transitions = aggregate_subsystem_transitions(call_graph, depth=depth)
    filtered = []
    for src, dst, weight in transitions:
        if src == dst:
            continue
        if exclude_tests and (src.startswith("tests/") or dst.startswith("tests/")):
            continue
        filtered.append((src, dst, weight))
    transitions = filtered[: max_edges * 2] if filtered else transitions[: max_edges * 2]

    participant_volume: dict[str, float] = defaultdict(float)
    for src, dst, score in transitions:
        participant_volume[src] += score
        participant_volume[dst] += score
    selected_participants = {k for k, _ in sorted(participant_volume.items(), key=lambda kv: kv[1], reverse=True)[:max_participants]}

    selected_transitions = [(s, d, w) for s, d, w in transitions if s in selected_participants and d in selected_participants][:max_edges]
    if not selected_transitions:
        return unverified_sequence("Unverified Subsystem")

    participants = sorted({s for s, _, _ in selected_transitions} | {d for _, d, _ in selected_transitions})
    pid_map = {name: f"S{idx}" for idx, name in enumerate(participants, start=1)}

    lines = ["```mermaid", "sequenceDiagram"]
    display_names: dict[str, str] = {}
    display_seen: dict[str, int] = defaultdict(int)
    for name in participants:
        display = component_display_name(name)
        display_seen[display] += 1
        if display_seen[display] > 1:
            display = f"{display} ({display_seen[display]})"
        display_names[name] = display
        lines.append(f'participant {pid_map[name]} as "{mermaid_quoted(display)}"')
    for src, dst, weight in selected_transitions:
        observed = max(1, int(round(weight)))
        action = f"{display_names[dst]} 처리 요청 ({observed}건 관측)"
        lines.append(f'{pid_map[src]}->>{pid_map[dst]}: {mermaid_quoted(action, "처리 요청")}')
    lines.append("```")
    return "\n".join(lines)


def build_hld_flowchart(call_graph: dict[str, Any], policy: dict[str, Any]) -> str:
    diagram_policy = policy.get("diagram", {})
    depth = safe_int(diagram_policy.get("subsystem_depth"), 3)
    max_edges = safe_int(diagram_policy.get("max_hld_flow_edges"), 20)
    exclude_tests = bool(diagram_policy.get("exclude_test_subsystems", True))
    transitions = []
    for src, dst, weight in aggregate_subsystem_transitions(call_graph, depth=depth):
        if src == dst:
            continue
        if exclude_tests and (src.startswith("tests/") or dst.startswith("tests/")):
            continue
        transitions.append((src, dst, weight))
        if len(transitions) >= max_edges:
            break

    if not transitions:
        return unverified_flowchart("Unverified Subsystem")

    nodes = sorted({src for src, _, _ in transitions} | {dst for _, dst, _ in transitions})
    node_ids: dict[str, str] = {}
    lines = ["```mermaid", "flowchart LR"]
    node_display: dict[str, str] = {}
    display_seen: dict[str, int] = defaultdict(int)
    for idx, name in enumerate(nodes, start=1):
        nid = f"N{idx}"
        node_ids[name] = nid
        display = component_display_name(name)
        display_seen[display] += 1
        if display_seen[display] > 1:
            display = f"{display} ({display_seen[display]})"
        node_display[name] = display
        lines.append(f'  {nid}["{mermaid_quoted(display)}"]')
    for src, dst, weight in transitions:
        observed = max(1, int(round(weight)))
        link_target = node_display[dst].replace("(", "").replace(")", "")
        link_label = f"{link_target} 의존 {observed}건"
        lines.append(f'  {node_ids[src]} -->|{mermaid_quoted(link_label, "의존 흐름")}| {node_ids[dst]}')
    lines.append("```")
    return "\n".join(lines)


def build_anchor_path(
    call_graph: dict[str, Any],
    *,
    anchors: list[str],
    max_steps: int,
    allowed_prefixes: tuple[str, ...] = (),
) -> list[str]:
    outgoing: dict[str, list[tuple[str, float]]] = defaultdict(list)
    for src, dst, weight in parse_edge_list(call_graph):
        outgoing[src].append((dst, weight))
    for src in list(outgoing.keys()):
        outgoing[src].sort(key=lambda item: item[1], reverse=True)

    start = ""
    for cand in anchors:
        if cand in outgoing:
            start = cand
            break
    if not start and anchors:
        start = anchors[0]

    if not start:
        return []

    best_path: list[str] = [start]
    best_score = -1.0

    def is_allowed(node_id: str) -> bool:
        file_path, _ = parse_call_node(node_id)
        if not allowed_prefixes:
            return True
        return any(file_path.startswith(prefix) for prefix in allowed_prefixes)

    def dfs(current: str, path: list[str], score: float) -> None:
        nonlocal best_path, best_score
        if len(path) > len(best_path) or (len(path) == len(best_path) and score > best_score):
            best_path = list(path)
            best_score = score
        if len(path) >= max_steps:
            return
        for candidate, edge_score in outgoing.get(current, []):
            if candidate in path:
                continue
            if not is_allowed(candidate):
                continue
            path.append(candidate)
            dfs(candidate, path, score + edge_score)
            path.pop()

    dfs(start, [start], 0.0)
    return best_path


def build_path_sequence_diagram(path_nodes: list[str]) -> str:
    if len(path_nodes) < 2:
        return unverified_sequence("Unverified Path")

    lines = ["```mermaid", "sequenceDiagram"]
    pid_by_node: dict[str, str] = {}
    display_seen: dict[str, int] = defaultdict(int)
    for idx, node in enumerate(path_nodes, start=1):
        pid = f"P{idx}"
        pid_by_node[node] = pid
        display = node_display_name(node)
        display_seen[display] += 1
        if display_seen[display] > 1:
            display = f"{display} ({display_seen[display]})"
        lines.append(f'participant {pid} as "{mermaid_quoted(display)}"')
    for i in range(len(path_nodes) - 1):
        src_node = path_nodes[i]
        dst_node = path_nodes[i + 1]
        action = edge_action_label(src_node, dst_node)
        lines.append(f'{pid_by_node[src_node]}->>{pid_by_node[dst_node]}: {mermaid_quoted(action, "핵심 처리 흐름")}')
    lines.append("```")
    return "\n".join(lines)


def build_subsystem_sequence_diagrams(call_graph: dict[str, Any], policy: dict[str, Any]) -> list[dict[str, str]]:
    max_steps = safe_int(policy.get("diagram", {}).get("max_lld_sequence_steps"), 8)
    profiles: list[tuple[str, list[str], tuple[str, ...]]] = [
        (
            "배치 렌더 파이프라인",
            [
                "scripts/render_core/render_executor.py::render_batch",
                "scripts/gui/controllers/batch_controller.py::run_batch",
            ],
            ("scripts/render_core/", "scripts/gui/controllers/batch_controller.py", "scripts/render_preview_service.py"),
        ),
        (
            "뷰포트 메쉬 로드/시각화",
            [
                "scripts/gui/viewport/mesh_visual_scene_mixin.py::load_scene",
                "scripts/gui/viewport/mesh_visual_internal_mixin.py::_yield_ui_during_load",
            ],
            ("scripts/gui/viewport/",),
        ),
        (
            "오브젝트 편집/상태 동기화",
            [
                "scripts/gui/controllers/object_controller.py::_on_object_tree_selection_changed",
                "scripts/gui/controllers/object_controller.py::_on_apply_jaw_mesh",
            ],
            ("scripts/gui/controllers/object_controller.py", "scripts/gui/main_window.py", "scripts/gui/viewport/"),
        ),
    ]

    outputs: list[dict[str, str]] = []
    for title, anchors, prefixes in profiles:
        path = build_anchor_path(
            call_graph,
            anchors=anchors,
            max_steps=max_steps,
            allowed_prefixes=prefixes,
        )
        if len(path) < 2:
            continue
        outputs.append({"title": title, "diagram": build_path_sequence_diagram(path)})

    if outputs:
        return outputs

    transitions = parse_edge_list(call_graph)
    transitions.sort(key=lambda item: item[2], reverse=True)
    if transitions:
        src, dst, _w = transitions[0]
        outputs.append(
            {
                "title": "핫패스 호출 흐름",
                "diagram": build_path_sequence_diagram([src, dst]),
            }
        )
    return outputs


def build_xy_metric_chart(
    *,
    title: str,
    y_label: str,
    rows: list[dict[str, Any]],
    value_key: str,
    max_items: int = 12,
) -> str:
    selected = [row for row in rows if isinstance(row, dict) and str(row.get("file", "")).strip()][:max_items]
    if not selected:
        return f"> _Unverified — {title}: 차트 생성에 필요한 metric evidence가 부족하여 차트를 생략합니다._"

    labels: list[str] = []
    values: list[float] = []
    seen: set[str] = set()
    for idx, row in enumerate(selected, start=1):
        file_path = str(row.get("file", ""))
        label = short_file_label(file_path, max_len=20)
        if label in seen:
            label = f"{label}_{idx}"
        seen.add(label)
        labels.append(label)
        values.append(safe_float(row.get(value_key, 0.0)))

    axis_max = max(values) if values else 1.0
    if axis_max <= 0:
        axis_max = 1.0
    axis_max = round(axis_max * 1.1, 3)

    label_expr = ", ".join(json.dumps(v, ensure_ascii=False) for v in labels)
    value_expr = ", ".join(str(round(v, 3)) for v in values)
    lines = [
        "```mermaid",
        "xychart-beta",
        f'    title "{title}"',
        f"    x-axis [{label_expr}]",
        f'    y-axis "{y_label}" 0 --> {axis_max}',
        f"    bar [{value_expr}]",
        "```",
    ]
    return "\n".join(lines)


def build_loc_complexity_quadrant(rows: list[dict[str, Any]], max_items: int = 12) -> str:
    selected = [row for row in rows if isinstance(row, dict) and str(row.get("file", "")).strip()][:max_items]
    if not selected:
        return build_canonical_quadrant_chart([])

    max_loc = max((safe_float(row.get("loc", 0.0)) for row in selected), default=1.0)
    max_complexity = max((safe_float(row.get("complexity_score", 0.0)) for row in selected), default=1.0)
    if max_loc <= 0:
        max_loc = 1.0
    if max_complexity <= 0:
        max_complexity = 1.0

    points: list[tuple[str, float, float]] = []
    for idx, row in enumerate(selected, start=1):
        raw_label = short_file_label(str(row.get("file", "")), max_len=18)
        x = clamp(safe_float(row.get("loc", 0.0)) / max_loc, 0.0, 1.0)
        y = clamp(safe_float(row.get("complexity_score", 0.0)) / max_complexity, 0.0, 1.0)
        points.append((raw_label or f"item_{idx}", x, y))
    return build_canonical_quadrant_chart(points)


def build_static_metric_charts(complexity: dict[str, Any]) -> list[dict[str, str]]:
    rows = complexity.get("top_files", []) if isinstance(complexity, dict) else []
    if not isinstance(rows, list):
        rows = []

    return [
        {
            "title": "복잡도 상위 파일 분포",
            "diagram": build_xy_metric_chart(
                title="Top Complexity (Branch+1)",
                y_label="Complexity",
                rows=rows,
                value_key="complexity_score",
            ),
        },
        {
            "title": "브랜치 수 상위 파일 분포",
            "diagram": build_xy_metric_chart(
                title="Top Branch Count",
                y_label="Branch Count",
                rows=rows,
                value_key="branches",
            ),
        },
        {
            "title": "LOC 상위 파일 분포",
            "diagram": build_xy_metric_chart(
                title="Top LOC",
                y_label="Lines of Code",
                rows=rows,
                value_key="loc",
            ),
        },
        {
            "title": "LOC 대비 복잡도 사분면",
            "diagram": build_loc_complexity_quadrant(rows),
        },
        {
            "title": "밀도 상위 파일 분포",
            "diagram": build_xy_metric_chart(
                title="Top Complexity Density",
                y_label="Density",
                rows=rows,
                value_key="density",
            ),
        },
    ]


def format_method_signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    args: list[str] = []
    positional = list(node.args.args)
    if positional and positional[0].arg in {"self", "cls"}:
        positional = positional[1:]
    args.extend(arg.arg for arg in positional)
    if node.args.vararg:
        args.append(f"*{node.args.vararg.arg}")
    if node.args.kwarg:
        args.append(f"**{node.args.kwarg.arg}")
    return f"{node.name}(" + ", ".join(args) + ")"


def build_class_method_specs(repo_path: Path, class_rows: list[dict[str, Any]], max_methods: int = 8) -> list[dict[str, str]]:
    target: dict[str, set[str]] = defaultdict(set)
    for row in class_rows:
        if not isinstance(row, dict):
            continue
        class_name = str(row.get("class", "")).strip()
        file_path = str(row.get("file", "")).strip()
        if class_name and file_path and file_path != "Unverified":
            target[file_path].add(class_name)

    specs: dict[tuple[str, str], list[str]] = {}
    for rel_path, class_names in target.items():
        abs_path = (repo_path / rel_path).resolve()
        methods_map: dict[str, list[str]] = {name: [] for name in class_names}
        try:
            source = abs_path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except Exception:
            for class_name in class_names:
                specs[(rel_path, class_name)] = ["Unverified(parse-failed)"]
            continue

        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            if node.name not in class_names:
                continue
            collected: list[str] = []
            for body_item in node.body:
                if not isinstance(body_item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if body_item.name.startswith("__") and body_item.name != "__init__":
                    continue
                collected.append(format_method_signature(body_item))
            methods_map[node.name] = collected[:max_methods] if collected else ["(no-method)"]

        for class_name in class_names:
            specs[(rel_path, class_name)] = methods_map.get(class_name, ["Unverified(class-missing)"])

    rows: list[dict[str, str]] = []
    for row in class_rows:
        class_name = str(row.get("class", "Unverified"))
        rel_path = str(row.get("file", "Unverified"))
        methods = specs.get((rel_path, class_name), ["Unverified"])
        rows.append(
            {
                "class": class_name,
                "file": rel_path,
                "method_specs": ", ".join(methods),
            }
        )
    return rows


def build_class_diagram(class_hierarchy: dict[str, Any], policy: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    diagram_policy = policy.get("diagram", {})
    max_nodes = safe_int(diagram_policy.get("max_class_nodes"), 26)
    max_edges = safe_int(diagram_policy.get("max_class_edges"), 40)
    excluded_names = {str(n) for n in diagram_policy.get("exclude_class_names", [])}

    nodes = class_hierarchy.get("nodes", []) if isinstance(class_hierarchy, dict) else []
    edges = class_hierarchy.get("edges", []) if isinstance(class_hierarchy, dict) else []

    class_files: dict[str, set[str]] = defaultdict(set)
    class_methods: dict[str, int] = defaultdict(int)
    class_bases: dict[str, set[str]] = defaultdict(set)

    for node in nodes:
        if not isinstance(node, dict):
            continue
        name = str(node.get("name", "")).strip()
        file_path = str(node.get("file", "")).strip()
        method_count = safe_int(node.get("method_count"), 0)
        bases = node.get("bases", [])

        if not name or name in excluded_names:
            continue
        if file_path:
            class_files[name].add(file_path)
        class_methods[name] = max(class_methods[name], method_count)
        if isinstance(bases, list):
            for base in bases:
                base_name = str(base)
                if base_name and base_name not in excluded_names:
                    class_bases[name].add(base_name)

    defined_classes = set(class_files.keys())
    degree = Counter()
    normalized_edges: list[tuple[str, str]] = []
    for edge in edges:
        if not isinstance(edge, dict):
            continue
        parent = str(edge.get("parent", "")).strip()
        child = str(edge.get("child", "")).strip()
        if not parent or not child:
            continue
        if parent in excluded_names or child in excluded_names:
            continue
        # Keep hierarchy focused on classes declared in repository files.
        if parent not in defined_classes or child not in defined_classes:
            continue
        degree[parent] += 1
        degree[child] += 1
        normalized_edges.append((parent, child))

    selected: list[str] = []
    for name, _ in degree.most_common(max_nodes):
        selected.append(name)
    if len(selected) < max_nodes:
        for name in sorted(class_files):
            if name in selected:
                continue
            selected.append(name)
            if len(selected) >= max_nodes:
                break

    if not selected:
        return unverified_flowchart("Unverified Class"), []

    selected_set = set(selected)
    selected_edges = [(p, c) for p, c in normalized_edges if p in selected_set and c in selected_set][:max_edges]

    lines = ["```mermaid", "classDiagram"]
    id_map: dict[str, str] = {}
    for name in selected:
        sid = sanitize_id(name)
        base_sid = sid
        suffix = 2
        while sid in id_map.values():
            sid = f"{base_sid}_{suffix}"
            suffix += 1
        id_map[name] = sid
        lines.append(f'class {sid}["{name}"]')

    for parent, child in selected_edges:
        parent_id = id_map.get(parent)
        child_id = id_map.get(child)
        if parent_id and child_id:
            lines.append(f"{parent_id} <|-- {child_id}")

    lines.append("```")

    detail_rows = []
    for name in selected[:20]:
        files = sorted(class_files.get(name, set()))
        parents = sorted(class_bases.get(name, set()))
        children = sorted([c for p, c in selected_edges if p == name])
        detail_rows.append(
            {
                "class": name,
                "file": files[0] if files else "Unverified",
                "parents": ", ".join(parents) if parents else "-",
                "children": ", ".join(children) if children else "-",
                "method_count": class_methods.get(name, 0),
            }
        )

    return "\n".join(lines), detail_rows


def dedupe_refs(refs: list[Any], max_items: int = 12) -> list[str]:
    seen: list[str] = []
    for ref in refs:
        text = str(ref or "").strip()
        if not text or text in seen:
            continue
        seen.append(text)
        if len(seen) >= max_items:
            break
    return seen


def collect_provenance_refs(model: dict[str, Any], max_items: int = 12) -> list[str]:
    refs: list[Any] = []
    if not isinstance(model, dict):
        return []
    provenance = model.get("provenance", [])
    if not isinstance(provenance, list):
        provenance = []
    for item in provenance:
        if not isinstance(item, dict):
            continue
        item_refs = item.get("refs", [])
        if isinstance(item_refs, list):
            refs.extend(item_refs)
    return dedupe_refs(refs, max_items=max_items)


def build_diagram_view(
    *,
    view_type: str,
    title: str,
    diagram: str,
    provenance: list[str] | None = None,
    fallback: bool = False,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "view_type": view_type,
        "title": title,
        "diagram": diagram,
        "provenance": provenance or [],
        "fallback": bool(fallback),
        "meta": meta or {},
    }


def unverified_flowchart(label: str = "Unverified View") -> str:
    # Evidence-less fallback: emit a plain text notice instead of a placeholder diagram.
    return f"> _Unverified — {label}: 다이어그램 생성에 필요한 구조 evidence가 부족하여 다이어그램을 생략합니다._"


def unverified_sequence(label: str = "Unverified Scenario") -> str:
    # Evidence-less fallback: emit a plain text notice instead of a placeholder diagram.
    return f"> _Unverified — {label}: 다이어그램 생성에 필요한 상호작용 evidence가 부족하여 다이어그램을 생략합니다._"


def flowchart_node(node_id: str, label: str, kind: str) -> str:
    quoted = mermaid_quoted(label)
    kind = (kind or "").lower()
    if kind == "actor":
        return f'  {node_id}(["{quoted}"])'
    if kind in {"external-system", "database", "cache", "messaging", "object-storage"}:
        return f'  {node_id}[["{quoted}"]]'
    if kind in {"orchestrator", "ci-pipeline", "iac"}:
        return f'  {node_id}{{"{quoted}"}}'
    return f'  {node_id}["{quoted}"]'


def build_context_view(context_model: dict[str, Any]) -> dict[str, Any]:
    elements = context_model.get("elements", []) if isinstance(context_model, dict) else []
    relations = context_model.get("relationships", []) if isinstance(context_model, dict) else []
    if not isinstance(elements, list):
        elements = []
    if not isinstance(relations, list):
        relations = []

    if not elements or not relations:
        return build_diagram_view(
            view_type="context",
            title="Context View",
            diagram=unverified_flowchart("Context Unverified"),
            provenance=collect_provenance_refs(context_model),
            fallback=True,
            meta={"status": "Unverified"},
        )

    element_map = {
        str(item.get("id", "")): item
        for item in elements
        if isinstance(item, dict) and str(item.get("id", "")).strip()
    }
    selected_relations = relations[:18]
    selected_ids: list[str] = []
    for relation in selected_relations:
        if not isinstance(relation, dict):
            continue
        for key in ["from", "to"]:
            value = str(relation.get(key, "")).strip()
            if value and value not in selected_ids:
                selected_ids.append(value)

    lines = ["```mermaid", "flowchart LR"]
    node_ids: dict[str, str] = {}
    for idx, element_id in enumerate(selected_ids, start=1):
        element = element_map.get(element_id, {})
        node_name = f"C{idx}"
        node_ids[element_id] = node_name
        lines.append(flowchart_node(node_name, str(element.get("label", element_id)), str(element.get("kind", "container"))))
    for relation in selected_relations:
        if not isinstance(relation, dict):
            continue
        src = node_ids.get(str(relation.get("from", "")).strip())
        dst = node_ids.get(str(relation.get("to", "")).strip())
        if not src or not dst:
            continue
        label = mermaid_quoted(str(relation.get("label", "interacts with"))[:60], "interacts with")
        lines.append(f"  {src} -->|{label}| {dst}")
    lines.append("```")

    return build_diagram_view(
        view_type="context",
        title="Context View",
        diagram="\n".join(lines),
        provenance=collect_provenance_refs(context_model),
        fallback=False,
        meta={"status": context_model.get("status", "ok")},
    )


def build_container_view(container_model: dict[str, Any]) -> dict[str, Any]:
    containers = container_model.get("containers", []) if isinstance(container_model, dict) else []
    relationships = container_model.get("relationships", []) if isinstance(container_model, dict) else []
    if not isinstance(containers, list):
        containers = []
    if not isinstance(relationships, list):
        relationships = []

    if not containers:
        return build_diagram_view(
            view_type="container",
            title="Container View",
            diagram=unverified_flowchart("Container Unverified"),
            provenance=collect_provenance_refs(container_model),
            fallback=True,
            meta={"status": "Unverified"},
        )

    selected = containers[:10]
    node_ids: dict[str, str] = {}
    lines = ["```mermaid", "flowchart LR"]
    for idx, container in enumerate(selected, start=1):
        cid = str(container.get("id", f"container_{idx}"))
        node_ids[cid] = f"T{idx}"
        languages = container.get("languages", {})
        if isinstance(languages, dict) and languages:
            lang_text = ", ".join(sorted(key.lstrip(".").upper() for key in languages.keys()))
            label = f"{container.get('label', cid)} / {lang_text}"
        else:
            label = str(container.get("label", cid))
        lines.append(flowchart_node(node_ids[cid], label, str(container.get("kind", "container"))))

    selected_ids = set(node_ids.keys())
    for relation in relationships[:18]:
        if not isinstance(relation, dict):
            continue
        src = node_ids.get(str(relation.get("from", "")))
        dst = node_ids.get(str(relation.get("to", "")))
        if not src or not dst:
            continue
        if str(relation.get("from", "")) not in selected_ids or str(relation.get("to", "")) not in selected_ids:
            continue
        observed = max(1, safe_int(relation.get("weight", 1), 1))
        label = mermaid_quoted(f"{relation.get('label', 'dependency')} {observed}건", "dependency")
        lines.append(f"  {src} -->|{label}| {dst}")
    lines.append("```")

    return build_diagram_view(
        view_type="container",
        title="Container View",
        diagram="\n".join(lines),
        provenance=collect_provenance_refs(container_model),
        fallback=False,
        meta={"status": container_model.get("status", "ok")},
    )


def build_deployment_view(deployment_model: dict[str, Any]) -> dict[str, Any]:
    nodes = deployment_model.get("nodes", []) if isinstance(deployment_model, dict) else []
    relationships = deployment_model.get("relationships", []) if isinstance(deployment_model, dict) else []
    if not isinstance(nodes, list):
        nodes = []
    if not isinstance(relationships, list):
        relationships = []

    if not nodes:
        return build_diagram_view(
            view_type="deployment",
            title="Deployment View",
            diagram=unverified_flowchart("Deployment Unverified"),
            provenance=collect_provenance_refs(deployment_model),
            fallback=True,
            meta={"status": "Unverified"},
        )

    lines = ["```mermaid", "flowchart TB"]
    node_ids: dict[str, str] = {}
    for idx, node in enumerate(nodes[:12], start=1):
        node_id = str(node.get("id", f"deployment_{idx}"))
        node_ids[node_id] = f"D{idx}"
        lines.append(flowchart_node(node_ids[node_id], str(node.get("label", node_id)), str(node.get("kind", "deployment"))))

    for relation in relationships[:16]:
        if not isinstance(relation, dict):
            continue
        src = node_ids.get(str(relation.get("from", "")))
        dst = node_ids.get(str(relation.get("to", "")))
        if not src or not dst:
            continue
        label = mermaid_quoted(str(relation.get("label", "deploys to")), "deploys to")
        lines.append(f"  {src} -->|{label}| {dst}")
    lines.append("```")

    return build_diagram_view(
        view_type="deployment",
        title="Deployment View",
        diagram="\n".join(lines),
        provenance=collect_provenance_refs(deployment_model),
        fallback=False,
        meta={"status": deployment_model.get("status", "ok")},
    )


def build_component_view(component_model: dict[str, Any]) -> dict[str, Any]:
    components = component_model.get("components", []) if isinstance(component_model, dict) else []
    relationships = component_model.get("relationships", []) if isinstance(component_model, dict) else []
    if not isinstance(components, list):
        components = []
    if not isinstance(relationships, list):
        relationships = []

    if not components:
        return build_diagram_view(
            view_type="component",
            title="Component View",
            diagram=unverified_flowchart("Component Unverified"),
            provenance=collect_provenance_refs(component_model),
            fallback=True,
            meta={"status": "Unverified"},
        )

    selected = components[:12]
    node_ids: dict[str, str] = {}
    lines = ["```mermaid", "flowchart LR"]
    selected_ids = {str(item.get("id", "")) for item in selected}
    for idx, component in enumerate(selected, start=1):
        cid = str(component.get("id", f"component_{idx}"))
        node_ids[cid] = f"K{idx}"
        label = str(component.get("label", cid))
        container_id = str(component.get("container_id", ""))
        if container_id:
            label = f"{label} / {_humanize_token(container_id)}"
        lines.append(flowchart_node(node_ids[cid], label, "component"))

    for relation in relationships[:20]:
        if not isinstance(relation, dict):
            continue
        src_id = str(relation.get("from", ""))
        dst_id = str(relation.get("to", ""))
        if src_id not in selected_ids or dst_id not in selected_ids:
            continue
        src = node_ids.get(src_id)
        dst = node_ids.get(dst_id)
        if not src or not dst:
            continue
        observed = max(1, safe_int(relation.get("weight", 1), 1))
        label = mermaid_quoted(f"{relation.get('label', '의존 호출')} {observed}건", "의존 호출")
        lines.append(f"  {src} -->|{label}| {dst}")
    lines.append("```")

    return build_diagram_view(
        view_type="component",
        title="Component View",
        diagram="\n".join(lines),
        provenance=collect_provenance_refs(component_model),
        fallback=False,
        meta={"status": component_model.get("status", "ok")},
    )


def build_runtime_views(scenario_model: dict[str, Any]) -> list[dict[str, Any]]:
    scenarios = scenario_model.get("scenarios", []) if isinstance(scenario_model, dict) else []
    if not isinstance(scenarios, list):
        scenarios = []

    outputs: list[dict[str, Any]] = []
    for scenario in scenarios[:4]:
        if not isinstance(scenario, dict):
            continue
        steps = scenario.get("steps", [])
        if not isinstance(steps, list) or not steps:
            continue

        participant_order: list[str] = []
        for step in steps:
            if not isinstance(step, dict):
                continue
            for key in ["from", "to"]:
                value = str(step.get(key, "")).strip()
                if value and value not in participant_order:
                    participant_order.append(value)

        if not participant_order:
            continue

        pid_map = {name: f"R{idx}" for idx, name in enumerate(participant_order, start=1)}
        lines = ["```mermaid", "sequenceDiagram"]
        for name in participant_order:
            lines.append(f'participant {pid_map[name]} as "{mermaid_quoted(name)}"')
        for step in steps[:10]:
            if not isinstance(step, dict):
                continue
            src = pid_map.get(str(step.get("from", "")).strip())
            dst = pid_map.get(str(step.get("to", "")).strip())
            if not src or not dst:
                continue
            action = mermaid_quoted(str(step.get("action", "호출")), "호출")
            lines.append(f"{src}->>{dst}: {action}")
        lines.append("```")

        outputs.append(
            build_diagram_view(
                view_type="runtime",
                title=str(scenario.get("title", "Representative Scenario")),
                diagram="\n".join(lines),
                provenance=dedupe_refs(list(scenario.get("evidence_refs", []))),
                fallback=bool(scenario.get("fallback")),
                meta={
                    "entrypoint_id": scenario.get("entrypoint_id"),
                    "source": scenario.get("source"),
                },
            )
        )

    return outputs


def build_interface_rows(interface_model: dict[str, Any]) -> list[list[str]]:
    items = interface_model.get("interfaces", []) if isinstance(interface_model, dict) else []
    if not isinstance(items, list) or not items:
        return [["Unverified", "Unverified", "Unverified", "Unverified"]]

    rows: list[list[str]] = []
    for item in items[:15]:
        if not isinstance(item, dict):
            continue
        rows.append(
            [
                str(item.get("source_component_label", "Unverified")),
                str(item.get("kind", "Unverified")),
                str(item.get("target_label", "Unverified")),
                ", ".join(dedupe_refs(list(item.get("evidence_refs", [])), max_items=4)),
            ]
        )
    return rows or [["Unverified", "Unverified", "Unverified", "Unverified"]]


def build_crosscutting_rows(crosscutting_model: dict[str, Any]) -> list[list[str]]:
    concepts = crosscutting_model.get("concepts", []) if isinstance(crosscutting_model, dict) else []
    if not isinstance(concepts, list) or not concepts:
        return [["Unverified", "0", "Unverified"]]

    rows: list[list[str]] = []
    for item in concepts[:10]:
        if not isinstance(item, dict):
            continue
        rows.append(
            [
                str(item.get("name", "Unverified")),
                str(item.get("occurrence_count", 0)),
                ", ".join(dedupe_refs(list(item.get("evidence_refs", [])), max_items=4)),
            ]
        )
    return rows or [["Unverified", "0", "Unverified"]]


def build_decision_rows(decision_model: dict[str, Any]) -> list[list[str]]:
    candidates = decision_model.get("candidates", []) if isinstance(decision_model, dict) else []
    if not isinstance(candidates, list) or not candidates:
        return [["Unverified", "Unverified", "Unverified", "Unverified"]]

    rows: list[list[str]] = []
    for item in candidates[:8]:
        if not isinstance(item, dict):
            continue
        rows.append(
            [
                str(item.get("title", "Unverified")),
                str(item.get("type", "Unverified")),
                str(item.get("summary", "Unverified")),
                ", ".join(dedupe_refs(list(item.get("evidence_refs", [])), max_items=4)),
            ]
        )
    return rows or [["Unverified", "Unverified", "Unverified", "Unverified"]]


def build_architecture_view_rows(diagram_views: list[dict[str, Any]]) -> list[list[str]]:
    rows: list[list[str]] = []
    for view in diagram_views:
        if not isinstance(view, dict):
            continue
        refs = ", ".join(dedupe_refs(list(view.get("provenance", [])), max_items=4)) or "Unverified"
        rows.append(
            [
                str(view.get("title", "Unverified")),
                str(view.get("view_type", "Unverified")),
                "fallback" if bool(view.get("fallback")) else "primary",
                refs,
            ]
        )
    return rows or [["Unverified", "Unverified", "fallback", "Unverified"]]


def to_markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    if not rows:
        return "| " + " | ".join(headers) + " |\n| " + " | ".join(["---"] * len(headers)) + " |\n| Unverified |" + " Unverified |" * (len(headers) - 1)
    line1 = "| " + " | ".join(headers) + " |"
    line2 = "| " + " | ".join(["---"] * len(headers)) + " |"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([line1, line2] + body)


def trend_symbol(current: float | int | None, previous: float | int | None, reverse_good: bool = False) -> str:
    if current is None or previous is None:
        return "Unverified"
    if current == previous:
        return "→"
    if current > previous:
        return "▼" if reverse_good else "▲"
    return "▲" if reverse_good else "▼"


def build_report(
    *,
    index: dict[str, Any],
    policy: dict[str, Any],
    findings: list[dict[str, Any]],
    gate: dict[str, Any],
    complexity: dict[str, Any],
    architecture: dict[str, Any],
    coverage: dict[str, Any],
    lizard_summary: dict[str, str],
    runtime: dict[str, Any],
    trace: dict[str, Any],
    branch_summary: dict[str, Any],
    previous_metrics: dict[str, Any],
    call_graph: dict[str, Any],
    classification: dict[str, dict[str, Any]],
    unverified_items: list[dict[str, Any]],
    architecture_summary: dict[str, Any],
    entrypoints_model: dict[str, Any],
    context_view: dict[str, Any],
    container_view: dict[str, Any],
    deployment_view: dict[str, Any],
    component_view: dict[str, Any],
    runtime_views: list[dict[str, Any]],
    architecture_view_rows: list[list[str]],
    interface_rows: list[list[str]],
    crosscutting_rows: list[list[str]],
    decision_rows: list[list[str]],
    static_metric_charts: list[dict[str, str]],
    class_diagram: str,
    class_detail_rows: list[dict[str, Any]],
    class_method_rows: list[dict[str, str]],
) -> str:
    generated_at = dt.datetime.now(dt.timezone.utc).isoformat()

    top_findings = sorted(findings, key=lambda x: safe_float(x.get("priority_score", 0.0)), reverse=True)
    high_critical = [f for f in findings if str(f.get("severity", "")).lower() in {"high", "critical"}]

    quality_attr_counter = Counter(str(f.get("quality_attribute", "unknown")) for f in top_findings[:10])
    module_counter = Counter(str(f.get("scope", {}).get("module", "unknown")) for f in findings)
    top_modules = [module for module, _ in module_counter.most_common(10)]
    architecture_counts = architecture_summary.get("counts", {}) if isinstance(architecture_summary, dict) else {}
    entrypoint_summary = entrypoints_model.get("summary", {}) if isinstance(entrypoints_model, dict) else {}

    summary_rows = [
        ["총 Finding", str(len(findings))],
        ["High/Critical", str(len(high_critical))],
        ["Quality Gate", str(gate.get("status", "Unverified"))],
        ["Unverified 항목", str(len(unverified_items))],
        ["엔트리포인트 수", str(entrypoint_summary.get("count", architecture_counts.get("entrypoints", "Unverified")))],
        ["컨테이너/컴포넌트", f"{architecture_counts.get('containers', 'Unverified')} / {architecture_counts.get('components', 'Unverified')}"],
        ["대표 시나리오 수", str(architecture_counts.get("scenarios", "Unverified"))],
        ["콜그래프 노드/엣지", f"{call_graph.get('summary', {}).get('nodes', 'Unverified')} / {call_graph.get('summary', {}).get('edges', 'Unverified')}"],
        ["C/C++ lizard 보강", str(lizard_summary.get("status", "missing"))],
    ]

    metric_rows = [
        [
            "Line Coverage(%)",
            str(coverage.get("line_coverage", "Unverified")),
            str(previous_metrics.get("line_coverage", "Unverified")),
            trend_symbol(coverage.get("line_coverage"), previous_metrics.get("line_coverage")),
        ],
        [
            "Unverified Ratio",
            str(gate.get("metrics", {}).get("unverified_ratio", "Unverified")),
            str(previous_metrics.get("unverified_ratio", "Unverified")),
            trend_symbol(
                gate.get("metrics", {}).get("unverified_ratio"),
                previous_metrics.get("unverified_ratio"),
                reverse_good=True,
            ),
        ],
        [
            "Avg Complexity Score",
            str(complexity.get("summary", {}).get("avg_complexity_score", "Unverified")),
            str(previous_metrics.get("avg_complexity_score", "Unverified")),
            trend_symbol(
                complexity.get("summary", {}).get("avg_complexity_score"),
                previous_metrics.get("avg_complexity_score"),
                reverse_good=True,
            ),
        ],
        [
            "Fallback Diagrams",
            str(gate.get("metrics", {}).get("fallback_diagrams", "Unverified")),
            str(previous_metrics.get("fallback_diagrams", "Unverified")),
            trend_symbol(
                gate.get("metrics", {}).get("fallback_diagrams"),
                previous_metrics.get("fallback_diagrams"),
                reverse_good=True,
            ),
        ],
    ]

    included_categories = Counter()
    excluded_count = 0
    for meta in classification.values():
        if not isinstance(meta, dict):
            continue
        category = str(meta.get("category", "unknown"))
        if bool(meta.get("included", False)):
            included_categories[category] += 1
        else:
            excluded_count += 1

    scope_rows = [[k, str(v)] for k, v in included_categories.most_common()]
    if not scope_rows:
        scope_rows = [["Unverified", "Unverified"]]

    module_rows = [[module, str(count)] for module, count in module_counter.most_common(12)]
    if not module_rows:
        module_rows = [["Unverified", "Unverified"]]

    architecture_rows = []
    for row in architecture.get("top_files", [])[:12]:
        if not isinstance(row, dict):
            continue
        architecture_rows.append(
            [
                str(row.get("file", "Unverified")),
                str(row.get("fan_in", "0")),
                str(row.get("fan_out", "0")),
                str(row.get("coupling_score", "0")),
                str(row.get("category", "unknown")),
            ]
        )

    class_rows = []
    for row in class_detail_rows[:15]:
        class_rows.append(
            [
                str(row.get("class", "Unverified")),
                str(row.get("file", "Unverified")),
                str(row.get("parents", "-")),
                str(row.get("children", "-")),
                str(row.get("method_count", 0)),
            ]
        )

    method_rows = []
    for row in class_method_rows[:20]:
        method_rows.append(
            [
                str(row.get("class", "Unverified")),
                str(row.get("file", "Unverified")),
                str(row.get("method_specs", "Unverified")),
            ]
        )

    backlog_rows = []
    for finding in top_findings:
        action = finding.get("action", {}) if isinstance(finding.get("action"), dict) else {}
        plan = finding.get("improvement_plan", {}) if isinstance(finding.get("improvement_plan"), dict) else {}
        related = plan.get("related_files", [])
        if not isinstance(related, list):
            related = []
        if not related:
            related = [str(finding.get("scope", {}).get("file", "Unverified"))]
        backlog_rows.append(
            [
                str(finding.get("finding_id", "Unverified")),
                str(action.get("title", "Unverified")),
                str(finding.get("severity", "Unverified")),
                str(finding.get("priority_score", "Unverified")),
                str(plan.get("detail", "Unverified")),
                ", ".join(str(x) for x in related if str(x).strip()),
            ]
        )

    quality_distribution_rows = [[k, str(v)] for k, v in sorted(quality_attr_counter.items(), key=lambda x: x[1], reverse=True)]

    lines: list[str] = []
    lines.append("# Codebase Analysis Report")
    lines.append("")
    lines.append(f"- generated_at: {generated_at}")
    lines.append(f"- repo_path: {index.get('repo_path', 'Unverified')}")
    lines.append(f"- commit_range: {index.get('commit_range', 'Unverified')}")
    lines.append(f"- mode: {index.get('mode', 'Unverified')}")
    lines.append(f"- policy_path: {index.get('policy_path', 'Unverified')}")
    lines.append("")

    lines.append("## 1. 실행 요약")
    lines.append("")
    lines.append(to_markdown_table(["항목", "값"], summary_rows))
    lines.append("")
    lines.append(to_markdown_table(["Top10 품질속성", "건수"], quality_distribution_rows))
    lines.append("")
    lines.append(f"- Gate 상태: **{gate.get('status', 'Unverified')}**")
    lines.append(f"- Gate 실패 사유: {', '.join(gate.get('reasons', [])) if gate.get('reasons') else '없음'}")
    lines.append(f"- Gate 경고: {', '.join(gate.get('warnings', [])) if gate.get('warnings') else '없음'}")
    lines.append("")

    lines.append("## 2. 범위/가정/비목표")
    lines.append("")
    lines.append("- 범위")
    lines.append("  - tracked files 기반 정적/동적/Git/보안 시그널을 결합해 단일 통합 마크다운 리포트를 생성")
    lines.append("  - 증거를 context/container/component/interface/scenario/deployment 모델로 승격한 뒤 HLD/LLD 뷰를 파생 생성")
    lines.append("  - finding 전수를 단일 개선 백로그 표로 출력")
    lines.append("- 가정")
    lines.append("  - 동적 워크로드/트레이스 입력이 제공되지 않으면 해당 구간은 Unverified로 유지")
    lines.append("  - 정적 도구(coverage/semgrep/sca) 부재 시 실패 원인을 그대로 보고")
    lines.append("  - 정책 가중치(priority_model)는 우선순위 점수 계산의 단일 기준")
    lines.append("- 비목표")
    lines.append("  - 자동 코드 수정/자동 병합")
    lines.append("  - 근거 없는 일반론 다이어그램 생성")
    lines.append("  - finding 축약 요약본 별도 생성")
    lines.append("")
    lines.append(f"- 포함 파일 분류 수: {sum(included_categories.values()) if included_categories else 'Unverified'}")
    lines.append(f"- 제외 파일 수: {excluded_count if classification else 'Unverified'}")
    lines.append(to_markdown_table(["카테고리", "포함 파일 수"], scope_rows))
    lines.append("")

    lines.append("## 3. 코드베이스 개요")
    lines.append("")
    lines.append(f"- 주요 모듈(파인딩 기준): {', '.join(top_modules) if top_modules else 'Unverified'}")
    lines.append(f"- 브랜치 수: {branch_summary.get('total', 0)}")
    lines.append(f"- 30일 초과 장기 브랜치: {branch_summary.get('stale_30d', 0)}")
    lines.append(f"- 엔트리포인트 수: {entrypoint_summary.get('count', architecture_counts.get('entrypoints', 'Unverified'))}")
    lines.append(f"- 외부 인터페이스 수: {architecture_counts.get('interfaces', 'Unverified')}")
    lines.append(f"- 결정 후보 수: {architecture_counts.get('decision_candidates', 'Unverified')}")
    lines.append(f"- call graph 노드 수: {call_graph.get('summary', {}).get('nodes', 'Unverified')}")
    lines.append(f"- call graph 엣지 수: {call_graph.get('summary', {}).get('edges', 'Unverified')}")
    lines.append(f"- 분석 카테고리: {', '.join(policy.get('collection', {}).get('analysis_categories', []))}")
    lines.append("")
    lines.append(to_markdown_table(["메트릭", "현재", "이전", "추세"], metric_rows))
    lines.append("")
    lines.append(to_markdown_table(["모듈", "Finding 수"], module_rows))
    lines.append("")
    lines.append(to_markdown_table(["뷰", "타입", "생성 경로", "근거"], architecture_view_rows))
    lines.append("")

    lines.append("## 4. 상위 설계 (HLD)")
    lines.append("")
    lines.append("### Context View")
    lines.append(context_view.get("diagram", unverified_flowchart("Context Unverified")))
    lines.append("")
    lines.append(f"- provenance: {', '.join(context_view.get('provenance', [])) if context_view.get('provenance') else 'Unverified'}")
    lines.append(f"- generation: {'fallback' if context_view.get('fallback') else 'primary'}")
    lines.append("")
    lines.append("### Container View")
    lines.append(container_view.get("diagram", unverified_flowchart("Container Unverified")))
    lines.append("")
    lines.append(f"- provenance: {', '.join(container_view.get('provenance', [])) if container_view.get('provenance') else 'Unverified'}")
    lines.append(f"- generation: {'fallback' if container_view.get('fallback') else 'primary'}")
    lines.append("")
    lines.append("### Deployment View")
    lines.append(deployment_view.get("diagram", unverified_flowchart("Deployment Unverified")))
    lines.append("")
    lines.append(f"- provenance: {', '.join(deployment_view.get('provenance', [])) if deployment_view.get('provenance') else 'Unverified'}")
    lines.append(f"- generation: {'fallback' if deployment_view.get('fallback') else 'primary'}")
    lines.append("")
    lines.append("### Crosscutting Concepts")
    lines.append(to_markdown_table(["개념", "증거 수", "대표 근거"], crosscutting_rows))
    lines.append("")
    lines.append("### Architecture Decisions")
    lines.append(to_markdown_table(["결정 후보", "유형", "요약", "대표 근거"], decision_rows))
    lines.append("")
    lines.append("### 결합도 상위 파일(보조 근거)")
    lines.append("")
    lines.append(to_markdown_table(["파일", "fan_in", "fan_out", "coupling", "category"], architecture_rows))
    lines.append("")

    lines.append("## 5. 상세 설계 (LLD)")
    lines.append("")
    lines.append("### 대표 런타임 시나리오")
    if runtime_views:
        for item in runtime_views:
            lines.append(f"#### {item.get('title', 'Unverified')}")
            lines.append(item.get("diagram", unverified_sequence("Scenario Unverified")))
            meta = item.get("meta", {}) if isinstance(item.get("meta"), dict) else {}
            lines.append(f"- entrypoint_id: {meta.get('entrypoint_id', 'Unverified')}")
            lines.append(f"- source: {meta.get('source', 'Unverified')}")
            lines.append(f"- provenance: {', '.join(item.get('provenance', [])) if item.get('provenance') else 'Unverified'}")
            lines.append(f"- generation: {'fallback' if item.get('fallback') else 'primary'}")
            lines.append("")
    else:
        lines.append("- Unverified: 대표 런타임 시나리오 생성 실패")
        lines.append("")

    lines.append("### Component View")
    lines.append(component_view.get("diagram", unverified_flowchart("Component Unverified")))
    lines.append("")
    lines.append(f"- provenance: {', '.join(component_view.get('provenance', [])) if component_view.get('provenance') else 'Unverified'}")
    lines.append(f"- generation: {'fallback' if component_view.get('fallback') else 'primary'}")
    lines.append("")
    lines.append("### Interface Contracts")
    lines.append(to_markdown_table(["Source Component", "Kind", "Target", "Evidence"], interface_rows))
    lines.append("")
    lines.append("### Code-Level Detail (Optional)")
    lines.append(class_diagram)
    lines.append("")
    lines.append("### 클래스 근거 테이블")
    lines.append(to_markdown_table(["Class", "File", "Parents", "Children", "Methods"], class_rows))
    lines.append("")
    lines.append("### 클래스 함수 명세")
    lines.append(to_markdown_table(["Class", "File", "Method Signatures"], method_rows))
    lines.append("")

    lines.append("## 6. 정적 분석 결과")
    lines.append("")
    lines.append("- 복잡도 측정식: $Complexity(file)=1+BranchCount$")
    lines.append("- 결합도 측정식: $Coupling(file)=FanIn+FanOut$")
    lines.append("- 우선순위 추정식: $Priority=\\sum(w_i\\cdot signal_i)+category\\_bias+rank\\_boost$")
    lines.append("")
    lines.append(f"- files_analyzed: {complexity.get('summary', {}).get('files_analyzed', 'Unverified')}")
    lines.append(f"- avg_complexity_score: {complexity.get('summary', {}).get('avg_complexity_score', 'Unverified')}")
    lines.append(f"- line_coverage(%): {coverage.get('line_coverage', 'Unverified')}")
    lines.append(f"- branch_coverage(%): {coverage.get('branch_coverage', 'Unverified')}")
    lines.append(f"- c_cpp_lizard_status: {lizard_summary.get('status', 'missing')}")
    if lizard_summary.get("artifact"):
        lines.append(f"- c_cpp_lizard_artifact: {lizard_summary.get('artifact')}")
    lines.append("")
    for chart in static_metric_charts:
        lines.append(f"### {chart.get('title', 'Unverified')}")
        lines.append(chart.get("diagram", "Unverified"))
        lines.append("")

    lines.append("### 정적 분석 핵심 수치")
    top_complexity_file = "Unverified"
    if isinstance(complexity.get("top_files"), list) and complexity.get("top_files"):
        top_complexity_file = str(complexity.get("top_files", [{}])[0].get("file", "Unverified"))
    static_summary_rows = [
        ["최대 복잡도 파일", top_complexity_file],
        ["평균 복잡도 점수", str(complexity.get("summary", {}).get("avg_complexity_score", "Unverified"))],
        ["분석 파일 수", str(complexity.get("summary", {}).get("files_analyzed", "Unverified"))],
        ["Coverage(Line/Branch)", f"{coverage.get('line_coverage', 'Unverified')} / {coverage.get('branch_coverage', 'Unverified')}"],
        ["C/C++ lizard 보강", f"{lizard_summary.get('status', 'missing')} ({lizard_summary.get('artifact', '') or 'no artifact'})"],
    ]
    lines.append(to_markdown_table(["지표", "값"], static_summary_rows))
    lines.append("")

    lines.append("## 7. 동적 분석 결과")
    lines.append("")
    workload = runtime.get("workload", {}) if isinstance(runtime, dict) else {}
    workload_status = str(workload.get("status", "Unverified"))
    lines.append(f"- workload_status: {workload_status}")
    lines.append(f"- workload_message: {workload.get('message', 'Unverified')}")
    lines.append(f"- workload_exit_code: {workload.get('exit_code', 'Unverified')}")
    lines.append(f"- trace_backed_scenarios: {len([item for item in runtime_views if item.get('meta', {}).get('source') == 'trace'])}")
    lines.append(f"- static_fallback_scenarios: {len([item for item in runtime_views if item.get('fallback')])}")

    tools_available = runtime.get("tools_available", {})
    if isinstance(tools_available, dict) and tools_available:
        tool_items = ", ".join(f"{k}={v}" for k, v in sorted(tools_available.items()))
        lines.append(f"- tools_available: {tool_items}")
    else:
        lines.append("- tools_available: Unverified")

    if trace:
        lines.append(f"- latency_count: {trace.get('count', 'Unverified')}")
        lines.append(f"- latency_p50_ms: {trace.get('p50_ms', 'Unverified')}")
        lines.append(f"- latency_p95_ms: {trace.get('p95_ms', 'Unverified')}")
        lines.append(f"- latency_p99_ms: {trace.get('p99_ms', 'Unverified')}")
    else:
        lines.append("- latency_percentiles: Unverified")
    if workload_status.lower() not in {"ok", "success", "passed"}:
        lines.append("- 참고: 동적 워크로드/트레이스 미제공 상태이므로 성능 결론은 Unverified입니다.")
    lines.append("")

    lines.append("## 8. 수동 리뷰 결과")
    lines.append("")
    lines.append("목적: 자동 분석으로 확정하기 어려운 구조/정확성/보안 판단을 사람이 검증하기 위한 근거 섹션입니다.")
    lines.append("")
    manual_rows = [
        [
            "Architecture",
            "컨테이너/컴포넌트 경계와 fallback 뷰 의존 여부",
            "architecture model + provenance 표를 기준으로 경계 타당성 검토",
        ],
        [
            "Algorithm",
            "핫패스 분기/루프 복잡도와 입력 규모 증가시 기울기",
            "complexity + churn 상위 파일 중심으로 개선 우선순위 확정",
        ],
        [
            "Runtime",
            "대표 시나리오가 실제 entrypoint/trace와 연결되는지",
            "trace-backed 여부와 runtime entrypoint linkage 확인",
        ],
    ]
    lines.append(to_markdown_table(["영역", "수동 검토 포인트", "활용 목적"], manual_rows))
    lines.append("")

    lines.append("## 9. 우선순위 개선 백로그")
    lines.append("")
    lines.append(to_markdown_table(["파인딩", "액션", "Severity", "Priority", "구체적인 개선 내용", "관련 파일"], backlog_rows))
    lines.append("")

    lines.append("## 10. 부록")
    lines.append("")
    lines.append("### Artifact Index")
    lines.append("```json")
    lines.append(json.dumps(index.get("artifacts", {}), ensure_ascii=False, indent=2))
    lines.append("```")
    lines.append("")

    lines.append("### Policy Snapshot")
    lines.append("```json")
    lines.append(json.dumps(policy.get("priority_model", {}), ensure_ascii=False, indent=2))
    lines.append("```")
    lines.append("")
    lines.append("### Architecture Summary")
    lines.append("```json")
    lines.append(json.dumps(architecture_summary, ensure_ascii=False, indent=2))
    lines.append("```")
    lines.append("")
    lines.append("### View Provenance")
    lines.append(to_markdown_table(["뷰", "타입", "생성 경로", "근거"], architecture_view_rows))
    lines.append("")

    lines.append("### Unverified")
    if unverified_items:
        for item in unverified_items:
            if not isinstance(item, dict):
                continue
            lines.append(f"- {item.get('section', 'Unverified')}: {item.get('reason', 'Unverified')}")
    else:
        lines.append("- None")

    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    artifacts_dir = resolve_artifacts_dir(args.input_dir)

    index = load_json(artifacts_dir / "index.json", {})
    if not isinstance(index, dict) or not index:
        raise SystemExit(f"index.json is invalid under: {artifacts_dir}")

    policy_path = resolve_policy_path(artifacts_dir, args.policy)
    policy = load_json(policy_path, {})
    if not isinstance(policy, dict) or not policy:
        raise SystemExit(f"failed to load policy: {policy_path}")
    validate_policy(policy, args.risk_model)

    repo_path = Path(index.get("repo_path", ".")).expanduser()
    commit_range = str(index.get("commit_range", "Unverified"))

    complexity = load_json(artifacts_dir / "static" / "complexity.json", {})
    architecture = load_json(artifacts_dir / "static" / "architecture.json", {})
    class_hierarchy = load_json(artifacts_dir / "static" / "class-hierarchy.json", {})
    call_graph = load_json(artifacts_dir / "static" / "call-graph.json", {})
    coverage = load_json(artifacts_dir / "static" / "coverage-summary.json", {})
    lizard_summary = summarize_lizard(artifacts_dir / "static" / "lizard-complexity.txt")
    runtime = load_json(artifacts_dir / "dynamic" / "runtime.json", {})
    trace = load_json(artifacts_dir / "dynamic" / "trace-artifacts.json", {})
    architecture_summary = load_json(artifacts_dir / "architecture" / "architecture-summary.json", {})
    entrypoints_model = load_json(artifacts_dir / "architecture" / "entrypoints.json", {})
    context_model = load_json(artifacts_dir / "architecture" / "context-model.json", {})
    container_model = load_json(artifacts_dir / "architecture" / "container-model.json", {})
    component_model = load_json(artifacts_dir / "architecture" / "component-model.json", {})
    interface_model = load_json(artifacts_dir / "architecture" / "interface-model.json", {})
    scenario_model = load_json(artifacts_dir / "architecture" / "scenario-model.json", {})
    deployment_model = load_json(artifacts_dir / "architecture" / "deployment-model.json", {})
    crosscutting_model = load_json(artifacts_dir / "architecture" / "crosscutting-model.json", {})
    decision_model = load_json(artifacts_dir / "architecture" / "decision-candidates.json", {})
    previous_metrics = load_json(artifacts_dir / "previous_metrics.json", {})

    classification = parse_classification_map(artifacts_dir / "static" / "path-classification.tsv")
    complexity_map, _ = parse_complexity_payload(complexity if isinstance(complexity, dict) else {})
    architecture_map, _ = parse_architecture_payload(architecture if isinstance(architecture, dict) else {})
    churn_map, churn_source = parse_churn_map(artifacts_dir)

    seed = build_seed_from_artifacts(
        artifacts_dir=artifacts_dir,
        policy=policy,
        classification=classification,
        complexity_map=complexity_map,
        architecture_map=architecture_map,
        churn_map=churn_map,
        churn_source=churn_source,
    )

    hotspot_findings = build_hotspot_findings(
        seed=seed,
        policy=policy,
        risk_model=args.risk_model,
        commit_range=commit_range,
    )

    security_raw = parse_security_findings(artifacts_dir)
    security_findings = build_security_findings(
        raw_security=security_raw,
        policy=policy,
        risk_model=args.risk_model,
        commit_range=commit_range,
        start_index=len(hotspot_findings) + 1,
    )

    findings = hotspot_findings + security_findings
    findings.sort(key=lambda f: safe_float(f.get("priority_score", 0.0)), reverse=True)

    exceptions = load_json(artifacts_dir / "exceptions.json", [])
    if not isinstance(exceptions, list):
        exceptions = []

    unverified_items = index.get("unverified", [])
    if not isinstance(unverified_items, list):
        unverified_items = []

    branch_rows = read_tsv(artifacts_dir / "git" / "branches.tsv")
    branch_summary = summarize_branches(branch_rows)

    context_view = build_context_view(context_model if isinstance(context_model, dict) else {})
    container_view = build_container_view(container_model if isinstance(container_model, dict) else {})
    deployment_view = build_deployment_view(deployment_model if isinstance(deployment_model, dict) else {})
    component_view = build_component_view(component_model if isinstance(component_model, dict) else {})
    runtime_views = build_runtime_views(scenario_model if isinstance(scenario_model, dict) else {})
    if container_view.get("fallback") and isinstance(call_graph, dict) and call_graph.get("edges"):
        container_view = build_diagram_view(
            view_type="container",
            title="Container View",
            diagram=build_hld_flowchart(call_graph, policy),
            provenance=["artifacts/static/call-graph.json"],
            fallback=True,
            meta={"status": "fallback"},
        )
    if not runtime_views:
        legacy_runtime = build_subsystem_sequence_diagrams(call_graph if isinstance(call_graph, dict) else {}, policy)
        runtime_views = [
            build_diagram_view(
                view_type="runtime",
                title=str(item.get("title", "Hot Path")),
                diagram=str(item.get("diagram", unverified_sequence("Scenario Unverified"))),
                provenance=["artifacts/static/call-graph.json"],
                fallback=True,
                meta={"entrypoint_id": None, "source": "call-graph-fallback"},
            )
            for item in legacy_runtime
            if isinstance(item, dict)
        ]
    architecture_views = [context_view, container_view, deployment_view, component_view, *runtime_views]
    architecture_view_rows = build_architecture_view_rows(architecture_views)
    interface_rows = build_interface_rows(interface_model if isinstance(interface_model, dict) else {})
    crosscutting_rows = build_crosscutting_rows(crosscutting_model if isinstance(crosscutting_model, dict) else {})
    decision_rows = build_decision_rows(decision_model if isinstance(decision_model, dict) else {})

    gate = evaluate_quality_gate(
        findings=findings,
        unverified_items=unverified_items,
        exceptions=exceptions,
        policy=policy,
        risk_model=args.risk_model,
        architecture_views=architecture_views,
    )

    static_metric_charts = build_static_metric_charts(complexity if isinstance(complexity, dict) else {})
    class_diagram, class_detail_rows = build_class_diagram(class_hierarchy if isinstance(class_hierarchy, dict) else {}, policy)
    class_method_rows = build_class_method_specs(repo_path=repo_path, class_rows=class_detail_rows)

    index["policy_path"] = str(policy_path)

    report_md = build_report(
        index=index,
        policy=policy,
        findings=findings,
        gate=gate,
        complexity=complexity if isinstance(complexity, dict) else {},
        architecture=architecture if isinstance(architecture, dict) else {},
        coverage=coverage if isinstance(coverage, dict) else {},
        lizard_summary=lizard_summary,
        runtime=runtime if isinstance(runtime, dict) else {},
        trace=trace if isinstance(trace, dict) else {},
        branch_summary=branch_summary,
        previous_metrics=previous_metrics if isinstance(previous_metrics, dict) else {},
        call_graph=call_graph if isinstance(call_graph, dict) else {},
        classification=classification,
        unverified_items=unverified_items,
        architecture_summary=architecture_summary if isinstance(architecture_summary, dict) else {},
        entrypoints_model=entrypoints_model if isinstance(entrypoints_model, dict) else {},
        context_view=context_view,
        container_view=container_view,
        deployment_view=deployment_view,
        component_view=component_view,
        runtime_views=runtime_views,
        architecture_view_rows=architecture_view_rows,
        interface_rows=interface_rows,
        crosscutting_rows=crosscutting_rows,
        decision_rows=decision_rows,
        static_metric_charts=static_metric_charts,
        class_diagram=class_diagram,
        class_detail_rows=class_detail_rows,
        class_method_rows=class_method_rows,
    )

    write_json(artifacts_dir / "findings.json", findings)
    write_json(artifacts_dir / "quality-gate-result.json", gate)

    if args.output:
        out_path = Path(args.output).expanduser().resolve()
    else:
        out_path = repo_path / "docs" / "codebase-analysis-report.md"
        out_path = out_path.expanduser().resolve()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report_md, encoding="utf-8")

    print(f"Report written: {out_path}")
    print(f"Policy used: {policy_path}")
    print(f"Quality gate: {gate.get('status')}")
    if gate.get("reasons"):
        print("Gate reasons: " + ", ".join(gate["reasons"]))

    return 2 if gate.get("status") == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
