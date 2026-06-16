#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass, field
from pathlib import Path


REPORT_DIR_NAMES = {
    "codebase-intel",
    "report",
    "reports",
    "plan",
    "docs",
}

BUCKET_KEYWORDS: dict[str, list[str]] = {
    "domain": [
        "domain",
        "product",
        "scenario",
        "workflow",
        "user",
        "도메인",
        "제품",
        "시나리오",
        "사용자",
        "흐름",
        "목표",
    ],
    "capabilities": [
        "capability",
        "p0",
        "p1",
        "feature",
        "library",
        "export",
        "convert",
        "scanbody",
        "기능",
        "동등성",
        "선택",
        "변환",
        "내보내기",
    ],
    "algorithms": [
        "algorithm",
        "icp",
        "kabsch",
        "threepoint",
        "three point",
        "kd-tree",
        "kdtree",
        "remesh",
        "registration",
        "align",
        "알고리즘",
        "정렬",
        "정합",
    ],
    "mesh_ops": [
        "mesh",
        "cylinder",
        "hole",
        "patch",
        "replace",
        "replacement",
        "cross-section",
        "topology",
        "메시",
        "절삭",
        "패치",
        "홀",
        "치환",
        "단면",
    ],
    "ui_state": [
        "state",
        "cta",
        "empty",
        "loaded",
        "align_ready",
        "convert_ready",
        "output_ready",
        "error",
        "상태",
        "전이",
        "버튼",
    ],
    "integration": [
        "trucore",
        "ioconnect",
        "module",
        "adapter",
        "reuse",
        "boundary",
        "migration",
        "재사용",
        "경계",
        "모듈",
    ],
    "evidence": [
        ".cpp",
        ".h",
        ".hpp",
        ".swift",
        ".xaml",
        ".cs",
        ".md",
        "source",
        "file",
        "path",
        "근거",
        "증거",
    ],
}


@dataclass
class ReportHit:
    source: Path
    line_no: int
    text: str


@dataclass
class IngestResult:
    sources: list[Path] = field(default_factory=list)
    buckets: dict[str, list[ReportHit]] = field(default_factory=lambda: {key: [] for key in BUCKET_KEYWORDS})
    limits: list[str] = field(default_factory=list)


def is_markdown_report(path: Path) -> bool:
    if not path.is_file() or path.suffix.lower() not in {".md", ".markdown", ".txt"}:
        return False
    parts = {part.lower() for part in path.parts}
    return bool(parts & REPORT_DIR_NAMES)


def discover_reports(root: Path, max_files: int) -> list[Path]:
    candidates: list[Path] = []
    for base in [root / "docs", root]:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if is_markdown_report(path):
                candidates.append(path)
    unique = sorted(set(candidates), key=lambda p: (len(p.parts), str(p)))
    return unique[:max_files]


def expand_inputs(inputs: list[str], root: Path, max_files: int) -> list[Path]:
    paths: list[Path] = []
    for raw in inputs:
        candidate = Path(raw).expanduser()
        if not candidate.is_absolute():
            candidate = root / candidate
        if candidate.is_dir():
            paths.extend(path for path in candidate.rglob("*") if is_markdown_report(path))
        elif candidate.exists() and candidate.is_file():
            paths.append(candidate)
    return sorted(set(paths), key=lambda p: str(p))[:max_files]


def normalize_line(line: str) -> str:
    text = re.sub(r"\s+", " ", line.strip())
    return text[:300]


def score_line(line: str, keywords: list[str]) -> bool:
    lower = line.lower()
    return any(keyword.lower() in lower for keyword in keywords)


def ingest(paths: list[Path], max_hits_per_bucket: int = 24, max_lines_per_file: int = 1200) -> IngestResult:
    result = IngestResult(sources=paths)
    seen: set[tuple[str, str]] = set()
    for path in paths:
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            result.limits.append(f"failed to read `{path}`")
            continue
        if len(lines) > max_lines_per_file:
            result.limits.append(f"`{path}` truncated to {max_lines_per_file} lines")
        for line_no, line in enumerate(lines[:max_lines_per_file], start=1):
            text = normalize_line(line)
            if not text or text in {"---", "| --- | --- |"}:
                continue
            for bucket, keywords in BUCKET_KEYWORDS.items():
                if len(result.buckets[bucket]) >= max_hits_per_bucket:
                    continue
                if score_line(text, keywords):
                    key = (bucket, text.lower())
                    if key in seen:
                        continue
                    seen.add(key)
                    result.buckets[bucket].append(ReportHit(path, line_no, text))
    return result


def relative_to_root(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def render_markdown(result: IngestResult, root: Path, title: str = "Domain Ingest Summary") -> str:
    lines = [
        "---",
        "doc_type: domain_ingest_summary",
        "canonical: false",
        "status: derived",
        "last_validated: Unverified",
        "last_validated_mode: none",
        "strict_validated_at: Unverified",
        "strict_handoff_validated_at: Unverified",
        "release_ready: false",
        "source_of_truth_for: []",
        "derived_from:",
    ]
    if result.sources:
        lines.extend(f'  - "{relative_to_root(path, root)}"' for path in result.sources)
    else:
        lines.append("  []")
    lines.extend(
        [
            "---",
            "",
            f"# {title}",
            "",
            "## Purpose",
            "Derived evidence index created from existing analysis reports and planning docs before generating or filling a phase subplan package.",
            "",
            "## Source Files",
        ]
    )
    if result.sources:
        lines.extend(f"- `{relative_to_root(path, root)}`" for path in result.sources)
    else:
        lines.append("- No source reports discovered.")

    lines.extend(["", "## Extracted Domain Signals"])
    for bucket, hits in result.buckets.items():
        lines.extend(["", f"### {bucket.replace('_', ' ').title()}"])
        if not hits:
            lines.append("- No matching signal extracted.")
            continue
        for hit in hits:
            source = relative_to_root(hit.source, root)
            lines.append(f"- `{source}:{hit.line_no}` {hit.text}")

    lines.extend(["", "## Ingestion Limits"])
    if result.limits:
        lines.extend(f"- {item}" for item in result.limits)
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Usage Rule",
            "- Use this file as derived evidence only.",
            "- Copy domain facts into canonical docs only after checking the cited source lines.",
            "- If generated docs still contain empty Purpose/Current State/Target State/Acceptance Criteria, the plan is scaffold-only.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest existing analysis reports into a derived domain summary")
    parser.add_argument("--root", required=True, help="Project root")
    parser.add_argument("--out", required=True, help="Output markdown path")
    parser.add_argument("--report", action="append", default=[], help="Report file or directory to ingest; may be repeated")
    parser.add_argument("--auto", action="store_true", help="Auto-discover reports under docs/report, docs/codebase-intel, docs/plan")
    parser.add_argument("--max-files", type=int, default=40)
    parser.add_argument("--max-hits-per-bucket", type=int, default=24)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    paths = expand_inputs(args.report, root, args.max_files)
    if args.auto or not paths:
        paths.extend(discover_reports(root, args.max_files))
    paths = sorted(set(paths), key=lambda p: str(p))[: args.max_files]
    result = ingest(paths, max_hits_per_bucket=args.max_hits_per_bucket)
    out = Path(args.out).expanduser()
    if not out.is_absolute():
        out = root / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_markdown(result, root), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
