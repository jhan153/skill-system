#!/usr/bin/env python3
"""Release QA checks for the 8.0 Context Compounding plan and README contract."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


DEFAULT_PLAN = Path("docs/plan/2026-06-21-context-assurance-llm-wiki-kanboard.md")
DEFAULT_README = Path("README.md")
DEFAULT_README_KO = Path("README.ko.md")
MAX_UNVERIFIED_LINE_RATIO = 0.03

REQUIRED_PLAN_HEADINGS = [
    "## 1) 작업 개요",
    "## 2) 변경 파일 목록",
    "## 3) 변경 요약 (What / Why)",
    "## 4) 현재 상태 vs 예정 상태",
    "## 5) 리스크",
    "## 6) 검증 절차",
    "## 7) 질의 (Questions)",
    "## 8) 버전 전략",
    "## 9) TODO",
    "## 10) 승인 게이트",
    "## 11) Coordination Brief",
    "## 12) Plan-Spec Curator Notes",
    "## 13) QA Gate and Qualitative Evaluation Criteria",
    "## 14) 진행 로그",
]

REQUIRED_GUARD_GROUPS = {
    "8.0 target": ["8.0.0 — Context Compounding", "Wiki Bank Architecture"],
    "7.4 legacy": ["7.4.x Context Assurance", "legacy/transition trace"],
    "wiki not sot": [
        "Wiki를 원본 SOT로 승격하지 않는다",
        "Wiki를 Source of Truth로 만들지 않음",
        "not a Source of Truth",
    ],
    "hook no direct mutation": [
        "Hook에서 Memory Bank 또는 accepted Knowledge Store를 직접 변경하지 않는다",
        "Hook은 feedback candidate emission까지만 허용",
    ],
    "runtime projection": ["Runtime Projection은 직접 편집하는 제2 SOT가 아니라"],
}

QUALITATIVE_CRITERIA = [
    "Purpose Fit",
    "Structural Clarity",
    "Evidence and Grounding",
    "Practical Usability",
    "Risk and Failure Modes",
    "Improvement Leverage",
]

README_REQUIRED = {
    "README.md": [
        "8.x — Context Compounding / Wiki Bank Architecture",
        "8.1.0 — Bounded Verification Loops",
        "8.3.0 — Bounded Loop Hardening",
        "8.0.2 — Context Compounding Field Hardening",
        "7.4.x Context Assurance",
        "legacy label",
        "field baseline",
        "Wiki Bank",
        "Runtime Projection",
    ],
    "README.ko.md": [
        "8.x — Context Compounding / Wiki Bank Architecture",
        "8.1.0 — Bounded Verification Loops",
        "8.3.0 — Bounded Loop Hardening",
        "8.0.2 — Context Compounding Field Hardening",
        "7.4.x Context Assurance",
        "legacy label",
        "field 기준선",
        "Wiki Bank",
        "Runtime Projection",
    ],
}


def read_text(path: Path, errors: list[str]) -> str:
    if not path.exists():
        errors.append(f"missing file: {path}")
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def check_required_plan_sections(text: str, errors: list[str]) -> None:
    for heading in REQUIRED_PLAN_HEADINGS:
        if heading not in text:
            errors.append(f"plan missing required section: {heading}")


def check_guard_groups(text: str, errors: list[str]) -> None:
    for label, options in REQUIRED_GUARD_GROUPS.items():
        if not any(option in text for option in options):
            errors.append(f"plan missing guard: {label}")


def check_unverified_ratio(text: str, errors: list[str]) -> None:
    non_empty = [line for line in text.splitlines() if line.strip()]
    unverified = [line for line in non_empty if "unverified" in line.lower()]
    if not non_empty:
        errors.append("plan has no non-empty lines")
        return
    ratio = len(unverified) / len(non_empty)
    if ratio > MAX_UNVERIFIED_LINE_RATIO:
        errors.append(
            "plan unverified-line ratio too high: "
            f"{len(unverified)}/{len(non_empty)} ({ratio:.3f}, max {MAX_UNVERIFIED_LINE_RATIO:.3f})"
        )


def mermaid_blocks(text: str) -> list[str]:
    blocks: list[str] = []
    current: list[str] = []
    in_block = False
    for line in text.splitlines():
        if line.strip() == "```mermaid":
            in_block = True
            current = []
            continue
        if in_block and line.strip() == "```":
            blocks.append("\n".join(current))
            in_block = False
            continue
        if in_block:
            current.append(line)
    return blocks


def check_diagram_scope(text: str, errors: list[str]) -> None:
    for index, block in enumerate(mermaid_blocks(text), start=1):
        first_line = next((line.strip() for line in block.splitlines() if line.strip()), "")
        if first_line != "sequenceDiagram":
            continue
        if re.search(r"\b(User|Codex|Agent|Approval)\b", block):
            errors.append(f"plan sequenceDiagram {index} includes meta participant")


def check_qualitative_criteria(text: str, errors: list[str]) -> None:
    for criterion in QUALITATIVE_CRITERIA:
        if criterion not in text:
            errors.append(f"plan missing qualitative criterion: {criterion}")


def check_readme_contract(path: Path, text: str, errors: list[str]) -> None:
    required = README_REQUIRED.get(path.name, [])
    for marker in required:
        if marker not in text:
            errors.append(f"{path}: missing public contract marker: {marker}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--readme", type=Path, default=DEFAULT_README)
    parser.add_argument("--readme-ko", type=Path, default=DEFAULT_README_KO)
    args = parser.parse_args()

    errors: list[str] = []
    plan_text = read_text(args.plan, errors)
    readme_text = read_text(args.readme, errors)
    readme_ko_text = read_text(args.readme_ko, errors)

    if plan_text:
        check_required_plan_sections(plan_text, errors)
        check_guard_groups(plan_text, errors)
        check_unverified_ratio(plan_text, errors)
        check_diagram_scope(plan_text, errors)
        check_qualitative_criteria(plan_text, errors)
    if readme_text:
        check_readme_contract(args.readme, readme_text, errors)
    if readme_ko_text:
        check_readme_contract(args.readme_ko, readme_ko_text, errors)

    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
