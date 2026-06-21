"""Dry-run diff engine.

Compares the desired projection (manifest) against the per-workspace sync
state cache and emits the ordered list of write operations needed. The engine
itself performs no I/O — it is pure and therefore safe to run as a dry-run and
easy to unit test. Applying the ops is a separate concern.
"""

from __future__ import annotations

from .models import (
    OP_CREATE_PROJECT,
    OP_CREATE_TASK,
    OP_MOVE_TASK,
    OP_NOOP,
    PlanManifest,
    SyncOp,
)
from .state import SyncState


def build_diff(manifest: PlanManifest, state: SyncState) -> list[SyncOp]:
    ops: list[SyncOp] = []

    project_known = any(
        ts.kanboard_project_id for ts in state.references.values()
    )
    if not project_known:
        ops.append(
            SyncOp(
                op=OP_CREATE_PROJECT,
                task_reference="",
                detail={
                    "project_name": manifest.plan_title or manifest.plan_id,
                    "plan_id": manifest.plan_id,
                    "strategy": manifest.kanboard_project_strategy,
                },
            )
        )

    for task in manifest.tasks:
        ts = state.get(task.task_reference)
        if ts is None or ts.kanboard_task_id is None:
            ops.append(
                SyncOp(
                    op=OP_CREATE_TASK,
                    task_reference=task.task_reference,
                    detail={
                        "title": task.title,
                        "column": task.kanboard_column,
                        "markdown_status": task.markdown_status,
                        "is_candidate": task.is_candidate,
                    },
                )
            )
        elif ts.last_synced_column != task.kanboard_column:
            ops.append(
                SyncOp(
                    op=OP_MOVE_TASK,
                    task_reference=task.task_reference,
                    detail={
                        "from": ts.last_synced_column,
                        "to": task.kanboard_column,
                    },
                )
            )
        else:
            ops.append(
                SyncOp(
                    op=OP_NOOP,
                    task_reference=task.task_reference,
                    detail={"column": task.kanboard_column},
                )
            )
    return ops


def summarize_diff(ops: list[SyncOp]) -> dict:
    counts: dict[str, int] = {}
    for op in ops:
        counts[op.op] = counts.get(op.op, 0) + 1
    return counts
