"""Markdown plan parser (MVP).

Scope per plan section 9: parse the ``TODO`` section and stable task keys
only. Ambiguous items get an auto-generated *candidate* key and are flagged so
downstream tools can treat them conservatively.

Parsing rules
-------------
- ``plan_id``  : plan document basename without the ``.md`` suffix.
- ``title``    : first level-1 (``# ``) heading text.
- TODO section : the first heading whose text contains ``TODO`` (case
  insensitive); its body runs until the next heading of equal or higher level.
- task item    : ``- [ ] `status` text`` / ``- [x] text``. An explicit inline
  status token (backtick-wrapped or bare leading word) overrides the checkbox.
- task_key     : explicit id in the title — ``(D5)`` / ``(M1)`` / ``KPS-001`` —
  otherwise an auto positional key ``T01`` flagged ``is_candidate=True``.
"""

from __future__ import annotations

import re
from pathlib import Path

from .models import PlanTask
from .status import column_for_status, normalize_status

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
_LIST_ITEM_RE = re.compile(r"^\s*[-*]\s*\[(.)\]\s*(.*)$")
_BACKTICK_TOKEN_RE = re.compile(r"^`([^`]+)`\s*(.*)$")
_BARE_TOKEN_RE = re.compile(r"^(\S+)\s+(.*)$")
_KEY_PAREN_RE = re.compile(r"\(([A-Za-z]{1,5}\d{1,4})\)")
_KEY_DASH_RE = re.compile(r"\b([A-Z][A-Z0-9]*-\d+)\b")


def plan_id_from_path(plan_path: str) -> str:
    return Path(plan_path).stem


def extract_title(lines: list[str]) -> str:
    for line in lines:
        m = _HEADING_RE.match(line)
        if m and len(m.group(1)) == 1:
            return m.group(2).strip()
    return ""


def find_todo_section(lines: list[str]) -> tuple[int, int] | None:
    """Return (start, end) line indices of the TODO section body, or None."""
    start = None
    level = 0
    for idx, line in enumerate(lines):
        m = _HEADING_RE.match(line)
        if not m:
            continue
        if start is None:
            if "todo" in m.group(2).lower():
                start = idx + 1
                level = len(m.group(1))
            continue
        # already inside: stop at the next heading of equal-or-higher level
        if len(m.group(1)) <= level:
            return (start, idx)
    if start is None:
        return None
    return (start, len(lines))


def _split_status_token(rest: str) -> tuple[str | None, str]:
    """Peel a leading status token off the item text.

    Returns (canonical_status_or_None, remaining_title).
    """
    rest = rest.strip()
    m = _BACKTICK_TOKEN_RE.match(rest)
    if m:
        status = normalize_status(m.group(1))
        if status:
            return status, m.group(2).strip()
    m = _BARE_TOKEN_RE.match(rest)
    if m:
        status = normalize_status(m.group(1))
        if status:
            return status, m.group(2).strip()
    return None, rest


def _extract_key(title: str) -> tuple[str | None, str]:
    """Extract an explicit task key from the title, returning (key, title)."""
    for pattern in (_KEY_PAREN_RE, _KEY_DASH_RE):
        m = pattern.search(title)
        if m:
            key = m.group(1)
            cleaned = (title[: m.start()] + title[m.end() :]).strip()
            return key, cleaned
    return None, title


def parse_plan_text(text: str, plan_id: str, plan_path: str) -> tuple[str, list[PlanTask]]:
    """Parse plan Markdown text into (title, tasks)."""
    lines = text.splitlines()
    title = extract_title(lines)
    section = find_todo_section(lines)
    tasks: list[PlanTask] = []
    if section is None:
        return title, tasks

    start, end = section
    auto_index = 0
    for offset in range(start, end):
        line = lines[offset]
        m = _LIST_ITEM_RE.match(line)
        if not m:
            continue
        auto_index += 1
        checkbox_char, rest = m.group(1), m.group(2)

        token_status, rest = _split_status_token(rest)
        checkbox_status = normalize_status(f"[{checkbox_char}]")
        status = token_status or checkbox_status or "todo"

        key, clean_title = _extract_key(rest)
        is_candidate = key is None
        if key is None:
            key = f"T{auto_index:02d}"

        tasks.append(
            PlanTask(
                task_key=key,
                task_reference=f"{plan_id}:{key}",
                title=clean_title,
                markdown_status=status,
                kanboard_column=column_for_status(status),
                is_candidate=is_candidate,
                source_line=offset + 1,
                raw_status_token=(token_status or checkbox_char or "").strip(),
            )
        )
    return title, tasks


def parse_plan(plan_path: str) -> tuple[str, str, list[PlanTask]]:
    """Parse a plan file, returning (plan_id, title, tasks)."""
    path = Path(plan_path)
    if not path.is_file():
        raise FileNotFoundError(f"plan file not found: {plan_path}")
    plan_id = plan_id_from_path(plan_path)
    title, tasks = parse_plan_text(
        path.read_text(encoding="utf-8"), plan_id=plan_id, plan_path=str(path)
    )
    return plan_id, title, tasks
