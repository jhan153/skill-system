"""Fetch a live board snapshot from Kanboard for pull / curate.

Builds the same snapshot shape the pull classifier and curate tool accept::

    {"reference": "<plan_id>:<task_key>", "column": "완료", "task_id": 12}

so those tools can operate against a live board without the caller supplying a
snapshot. Read-only: only ``getColumns`` and ``getAllTasks`` are used.
"""

from __future__ import annotations

from .kanboard_client import KanboardClient


def _as_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def fetch_board_snapshot(client: KanboardClient, project_id: int) -> list[dict]:
    columns = client.get_columns(project_id) or []
    col_title = {_as_int(c.get("id")): c.get("title") for c in columns}

    snapshot: list[dict] = []
    for task in client.get_all_tasks(project_id) or []:
        snapshot.append(
            {
                "reference": task.get("reference") or "",
                "column": col_title.get(_as_int(task.get("column_id"))),
                "task_id": _as_int(task.get("id")),
            }
        )
    return snapshot


def resolve_project_id(state) -> int | None:
    """Best-effort project id from the state cache (first known)."""
    for ts in state.references.values():
        if ts.kanboard_project_id:
            return int(ts.kanboard_project_id)
    return None
