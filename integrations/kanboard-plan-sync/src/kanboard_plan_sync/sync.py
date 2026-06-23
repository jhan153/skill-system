"""Apply a dry-run diff against a live Kanboard projection.

This is the only write path. It consumes the ops produced by
:mod:`kanboard_plan_sync.diff`, drives them through a :class:`KanboardClient`,
and updates the per-workspace state cache. The client is injectable, so the
apply path is exercised by mock-based unit tests without a running Kanboard.

Cards are projected onto built-in Kanboard objects only (title, reference,
column, color, tags, description) so plan sync is visible on the default UI
without any custom plugin (plan Q9).
"""

from __future__ import annotations

from .kanboard_client import KanboardClient
from .models import (
    OP_CREATE_PROJECT,
    OP_CREATE_TASK,
    OP_MOVE_TASK,
    OP_NOOP,
    PlanManifest,
    SyncOp,
)
from .projection import task_projection
from .state import SyncState, TaskState
from .status import CANONICAL_TO_COLUMN

BOARD_COLUMNS = list(CANONICAL_TO_COLUMN.values())


def board_target(config, manifest: PlanManifest) -> tuple[str, str | None]:
    """Return ``(project_name, swimlane_name)`` for a plan (plan section 5.2).

    - ``dedicated-project``: the plan is its own Kanboard Project (default swimlane).
    - ``workspace-project`` (default): the workspace is the Project and the plan
      is a Swimlane inside it — so a repo with many plans stays one Project.
    """
    entry = config.plan_entry_for(manifest.plan_path) if config else None
    strategy = entry.kanboard_project_strategy if entry else "workspace-project"
    if strategy == "dedicated-project":
        return (manifest.plan_title or manifest.plan_id, None)
    project = (getattr(config, "name", None) if config else None) or manifest.plan_id
    swimlane = manifest.plan_title or manifest.plan_id
    return (project, swimlane)


def default_assignee(config) -> str | None:
    """Single-user kanban: the username every card is assigned to.

    Explicit ``board_assignee`` wins; otherwise the first ``board_members`` entry
    (default ``admin``). ``None`` means leave cards unassigned.
    """
    if config is None:
        return None
    kb = getattr(config, "kanboard", None)
    if kb is None:
        return None
    if getattr(kb, "board_assignee", None):
        return kb.board_assignee
    members = getattr(kb, "board_members", None) or []
    return members[0] if members else None


def resolve_project(client: KanboardClient, project_name: str) -> int:
    """Get-or-create a Kanboard Project by name; return its id."""
    existing = client.get_project_by_name(project_name)
    if existing and isinstance(existing, dict) and existing.get("id"):
        return int(existing["id"])
    created = client.create_project(name=project_name, description="kanboard-plan-sync")
    return int(created)


def ensure_swimlane(
    client: KanboardClient, project_id: int, name: str | None
) -> int | None:
    """Get-or-create a Swimlane by name; ``None`` name means the default swimlane."""
    if not name:
        return None
    for s in (client.get_swimlanes(project_id) or []):
        if s.get("name") == name and s.get("id") is not None:
            return int(s["id"])
    new_id = client.create_swimlane(project_id, name)
    return int(new_id) if new_id else None


def ensure_columns(
    client: KanboardClient, project_id: int, wanted: list[str] | None = None
) -> dict[str, int]:
    """Make sure the status columns exist; return a title -> column_id map.

    Missing columns are added (non-destructive). Pre-existing default columns
    are left in place.
    """
    wanted = wanted or BOARD_COLUMNS
    existing = {
        c["title"]: int(c["id"])
        for c in (client.get_columns(project_id) or [])
        if "title" in c and "id" in c
    }
    for title in wanted:
        if title not in existing:
            new_id = client.add_column(project_id, title)
            if new_id:
                existing[title] = int(new_id)
    return existing


def ensure_members(
    client: KanboardClient, project_id: int, usernames: list[str] | None
) -> list[str]:
    """Auto-add the given users as project members so the board is visible in
    their Kanboard dashboard. Idempotent: existing members are skipped. Tolerant
    of unknown usernames (skipped). Returns the usernames newly added.
    """
    if not usernames:
        return []
    try:
        existing = client.get_project_users(project_id) or {}
    except Exception:
        existing = {}
    existing_names = set(existing.values()) if isinstance(existing, dict) else set()

    added: list[str] = []
    for name in usernames:
        if name in existing_names:
            continue
        user = client.get_user_by_name(name)
        if isinstance(user, dict) and user.get("id"):
            client.add_project_user(project_id, int(user["id"]), "project-manager")
            added.append(name)
    return added


def apply_board_skeleton(
    client: KanboardClient,
    manifest: PlanManifest,
    members: list[str] | None = None,
    project_name: str | None = None,
    swimlane_name: str | None = None,
) -> dict:
    """Create/verify the Project, status columns, the plan's swimlane, and members."""
    project_name = project_name or manifest.plan_title or manifest.plan_id
    project_id = resolve_project(client, project_name)
    columns = ensure_columns(client, project_id)
    swimlane_id = ensure_swimlane(client, project_id, swimlane_name)
    added_members = ensure_members(client, project_id, members)
    return {
        "project_id": project_id,
        "project_name": project_name,
        "swimlane_name": swimlane_name,
        "swimlane_id": swimlane_id,
        "columns": columns,
        "missing_columns": [c for c in BOARD_COLUMNS if c not in columns],
        "added_members": added_members,
    }


def apply_diff(
    client: KanboardClient,
    manifest: PlanManifest,
    state: SyncState,
    ops: list[SyncOp],
    members: list[str] | None = None,
    project_name: str | None = None,
    swimlane_name: str | None = None,
    assignee: str | None = None,
) -> dict:
    """Execute ops against Kanboard, mutating ``state``. Returns an applied report.

    With ``swimlane_name`` set, the plan's cards live in that swimlane of a
    shared (workspace) Project; otherwise the default swimlane is used. With
    ``assignee`` set, every created/moved card is owned by that user so the
    single-user ``assignee:me`` board filter never hides it.
    """
    applied: list[dict] = []
    refreshed: list[dict] = []
    project_name = project_name or manifest.plan_title or manifest.plan_id
    project_id = resolve_project(client, project_name)
    columns = ensure_columns(client, project_id)
    swimlane_id = ensure_swimlane(client, project_id, swimlane_name)
    added_members = ensure_members(client, project_id, members)

    assignee_id = None
    if assignee:
        user = client.get_user_by_name(assignee)
        if isinstance(user, dict) and user.get("id"):
            assignee_id = int(user["id"])

    task_by_ref = {t.task_reference: t for t in manifest.tasks}

    for op in ops:
        if op.op == OP_CREATE_PROJECT:
            continue

        ref = op.task_reference
        task = task_by_ref.get(ref)
        if task is None:
            continue
        proj = task_projection(manifest, task)
        column_id = columns.get(task.kanboard_column)
        projection_fields = {
            "title": proj["title"],
            "description": proj["description"],
            "color_id": proj["color_id"],
        }

        if op.op == OP_CREATE_TASK:
            task_id = client.create_task(
                project_id=project_id,
                title=proj["title"],
                reference=ref,
                column_id=column_id,
                swimlane_id=swimlane_id,
                owner_id=assignee_id,
                description=proj["description"],
                color_id=proj["color_id"],
                tags=proj["tags"],
            )
            state.upsert(
                ref,
                TaskState(
                    kanboard_task_id=int(task_id) if task_id else None,
                    kanboard_project_id=project_id,
                    last_markdown_status=task.markdown_status,
                    last_synced_column=task.kanboard_column,
                ),
            )
            applied.append({"op": op.op, "task_reference": ref, "task_id": task_id})

        elif op.op == OP_MOVE_TASK:
            ts = state.get(ref)
            if ts is None or ts.kanboard_task_id is None or column_id is None:
                applied.append({"op": "skip_move", "task_reference": ref})
                continue
            client.move_task_position(
                project_id=project_id,
                task_id=ts.kanboard_task_id,
                column_id=column_id,
                swimlane_id=swimlane_id or 0,
            )
            # Keep board-facing card text aligned with the Markdown projection.
            update_fields = dict(projection_fields)
            if assignee_id is not None:
                update_fields["owner_id"] = assignee_id
            client.update_task(task_id=ts.kanboard_task_id, **update_fields)
            ts.last_synced_column = task.kanboard_column
            ts.last_markdown_status = task.markdown_status
            applied.append(
                {"op": op.op, "task_reference": ref, "to": task.kanboard_column}
            )

        elif op.op == OP_NOOP:
            ts = state.get(ref)
            if ts is None or ts.kanboard_task_id is None:
                continue
            update_fields = dict(projection_fields)
            if assignee_id is not None:
                update_fields["owner_id"] = assignee_id
            client.update_task(task_id=ts.kanboard_task_id, **update_fields)
            refreshed.append({"op": "refresh_task", "task_reference": ref})

    return {
        "project_id": project_id,
        "project_name": project_name,
        "swimlane_id": swimlane_id,
        "applied": applied,
        "applied_count": len(applied),
        "refreshed": refreshed,
        "refreshed_count": len(refreshed),
        "added_members": added_members,
    }
