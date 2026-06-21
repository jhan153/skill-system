"""Projection rules that make plan sync visible on the default Kanboard UI.

Per plan Q9, first-class visibility is achieved with built-in Kanboard objects
only — no custom hook/plugin. A plan task projects onto a Kanboard task's
title, reference, description, color, tags, and (for evidence) subtasks. These
are pure functions so the rules are unit-testable without a live board.
"""

from __future__ import annotations

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


def status_color(status: str) -> str:
    return STATUS_COLOR.get(status, "grey")


def task_tags(manifest: PlanManifest, task: PlanTask) -> list[str]:
    tags = [PLAN_SYNC_TAG, manifest.plan_id, f"status:{task.markdown_status}"]
    if task.is_candidate:
        tags.append(CANDIDATE_TAG)
    return tags


def task_description(manifest: PlanManifest, task: PlanTask) -> str:
    """Human-readable card body linking the card back to its plan source."""
    lines = [
        f"**plan**: `{manifest.plan_id}`",
        f"**reference**: `{task.task_reference}`",
        f"**markdown status**: `{task.markdown_status}`",
        f"**source line**: {task.source_line}",
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
        "title": task.title or task.task_reference,
        "reference": task.task_reference,
        "column": task.kanboard_column,
        "color_id": status_color(task.markdown_status),
        "tags": task_tags(manifest, task),
        "description": task_description(manifest, task),
    }
