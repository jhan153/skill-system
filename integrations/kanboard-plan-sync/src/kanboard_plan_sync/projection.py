"""Projection rules that make plan sync visible on the default Kanboard UI.

Per plan Q9, first-class visibility is achieved with built-in Kanboard objects
only — no custom hook/plugin. A plan task projects onto a Kanboard task's
title, reference, description, color, tags, and (for evidence) subtasks. These
are pure functions so the rules are unit-testable without a live board.
"""

from __future__ import annotations

import re

from .models import PlanManifest, PlanTask

# canonical status -> Kanboard built-in color id.
STATUS_COLOR = {
    "todo": "grey",
    "doing": "blue",
    "review": "purple",
    "blocked": "red",
    "done": "green",
}

PLAN_SYNC_TAG = "plan-sync"
CANDIDATE_TAG = "candidate"
MAX_CARD_TITLE = 96

_MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
_MARKDOWN_NOISE_RE = re.compile(r"[*_`#>]+")
_CHECKBOX_RE = re.compile(r"^\s*[-*]?\s*\[[ xX]\]\s*")
_STATUS_PREFIX_RE = re.compile(
    r"^\s*(?:todo|doing|in[-_ ]?progress|review|blocked|done|완료|진행중|보류)"
    r"\s*[:/\-]\s*",
    re.IGNORECASE,
)
_STATUS_WORD_RE = re.compile(
    r"^\s*(?:todo|doing|in[-_ ]?progress|review|blocked|done|완료|진행중|보류)\s+",
    re.IGNORECASE,
)
_PHASE_PREFIX_RE = re.compile(
    r"^\s*(?:phase|step|task|todo|item)\s*[\w.-]*\s*[:.)/\-]\s*",
    re.IGNORECASE,
)


def status_color(status: str) -> str:
    return STATUS_COLOR.get(status, "grey")


def task_tags(manifest: PlanManifest, task: PlanTask) -> list[str]:
    tags = [PLAN_SYNC_TAG, manifest.plan_id, f"status:{task.markdown_status}"]
    if task.is_candidate:
        tags.append(CANDIDATE_TAG)
    return tags


def kanban_card_title(task: PlanTask) -> str:
    """Return a concise, end-user-facing title for the board card.

    The Markdown plan remains canonical, but board users should see an action
    item, not a raw checklist line. Keep this deterministic: no LLM calls during
    sync, and preserve the raw source title in the card description.
    """
    title = (task.title or task.task_reference).strip()
    title = _MARKDOWN_LINK_RE.sub(r"\1", title)
    title = _CHECKBOX_RE.sub("", title)
    title = _STATUS_PREFIX_RE.sub("", title)
    title = _STATUS_WORD_RE.sub("", title)
    title = _PHASE_PREFIX_RE.sub("", title)
    title = _MARKDOWN_NOISE_RE.sub("", title)
    title = _STATUS_PREFIX_RE.sub("", title)
    title = _STATUS_WORD_RE.sub("", title)
    title = _PHASE_PREFIX_RE.sub("", title)
    title = re.sub(r"\s+", " ", title).strip(" -:\t")
    if not title:
        title = task.task_reference
    if len(title) > MAX_CARD_TITLE:
        title = f"{title[: MAX_CARD_TITLE - 3].rstrip()}..."
    return title


def task_description(manifest: PlanManifest, task: PlanTask) -> str:
    """Human-readable card body linking the card back to its plan source."""
    lines = [
        "## Task",
        f"**Do**: {kanban_card_title(task)}",
        "",
        "## Completion Gate",
        "- Record implementation, documentation, test, or validation evidence before promoting Markdown to `done`.",
        "- Use `record_validation` or `record_session_update` for evidence visible on this card.",
        "",
        "## Source",
        f"**plan**: `{manifest.plan_id}`",
        f"**reference**: `{task.task_reference}`",
        f"**markdown status**: `{task.markdown_status}`",
        f"**source line**: {task.source_line}",
        f"**source title**: {task.title or task.task_reference}",
    ]
    if task.is_candidate:
        lines.append(
            "**candidate**: task key was auto-generated; add an explicit id "
            "(e.g. `(D5)`/`KPS-001`) in the plan for a stable mapping."
        )
    lines.append("")
    lines.append("_Managed by kanboard-plan-sync. Markdown plan is the source of truth._")
    return "\n".join(lines)


def task_projection(manifest: PlanManifest, task: PlanTask) -> dict:
    """The full set of built-in fields used when creating/updating a card."""
    return {
        "title": kanban_card_title(task),
        "reference": task.task_reference,
        "column": task.kanboard_column,
        "color_id": status_color(task.markdown_status),
        "tags": task_tags(manifest, task),
        "description": task_description(manifest, task),
    }
