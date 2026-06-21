"""Status mapping between Markdown plan state and Kanboard columns.

Canonical statuses are the internal vocabulary. Markdown tokens / checkboxes
normalize *into* a canonical status; canonical statuses map *out to* Kanboard
column names. The mapping mirrors section 5.3 of the plan.
"""

from __future__ import annotations

from typing import Optional

CANONICAL_STATUSES = ("todo", "doing", "review", "blocked", "done")

# Markdown token or checkbox -> canonical status.
# Keys are matched case-insensitively after stripping surrounding whitespace.
_STATUS_ALIASES = {
    "todo": "todo",
    "[ ]": "todo",
    "[todo]": "todo",
    "doing": "doing",
    "[doing]": "doing",
    "review": "review",
    "[review]": "review",
    "blocked": "blocked",
    "[blocked]": "blocked",
    "done": "done",
    "[x]": "done",
    "[done]": "done",
}

# canonical status -> Kanboard column (Korean board labels per plan 5.3).
CANONICAL_TO_COLUMN = {
    "todo": "TODO",
    "doing": "진행중",
    "review": "검토 필요",
    "blocked": "보류",
    "done": "완료",
}

COLUMN_TO_CANONICAL = {column: status for status, column in CANONICAL_TO_COLUMN.items()}


def normalize_status(token: Optional[str]) -> Optional[str]:
    """Return the canonical status for a Markdown token, or None if unknown."""
    if token is None:
        return None
    key = token.strip().lower()
    return _STATUS_ALIASES.get(key)


def column_for_status(status: str) -> str:
    """Return the Kanboard column for a canonical status."""
    try:
        return CANONICAL_TO_COLUMN[status]
    except KeyError as exc:
        raise ValueError(f"unknown canonical status: {status!r}") from exc


def status_for_column(column: Optional[str]) -> Optional[str]:
    """Return the canonical status for a Kanboard column, or None if unknown."""
    if column is None:
        return None
    return COLUMN_TO_CANONICAL.get(column.strip())
