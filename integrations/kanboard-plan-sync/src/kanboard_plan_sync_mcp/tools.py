"""Plan-centric MCP tool registry and handlers.

Each tool is a pure-ish function over the core package. Write-capable tools
default to ``dry_run=True``. When a live Kanboard is required but unavailable
(no running server / no token), tools return a structured
``status="needs_live_kanboard"`` result rather than failing — the offline
projection of the work is still reported.

The registry is plain data so the tool list can be inspected without importing
the MCP SDK (see ``--list-tools``).
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional

from kanboard_plan_sync import registry as _registry
from kanboard_plan_sync.bootstrap import init_workspace as _init_workspace
from kanboard_plan_sync.config import WorkspaceConfig, load_config
from kanboard_plan_sync.diff import build_diff, summarize_diff
from kanboard_plan_sync.manifest import build_manifest
from kanboard_plan_sync.rollout import sync_all as _sync_all
from kanboard_plan_sync.pull import classify_pull, summarize_pull
from kanboard_plan_sync.runtime import build_client
from kanboard_plan_sync.snapshot import fetch_board_snapshot, resolve_project_id
from kanboard_plan_sync.state import load_state, save_state
from kanboard_plan_sync.status import CANONICAL_TO_COLUMN
from kanboard_plan_sync.sync import apply_board_skeleton, apply_diff, board_target, default_assignee
from kanboard_plan_sync.validation import (
    apply_session_update,
    apply_validation,
    session_update_projection,
)
from kanboard_plan_sync.workspace import inspect_workspace as _inspect_workspace

# Kanboard column order for a freshly created board projection.
_BOARD_COLUMNS = list(CANONICAL_TO_COLUMN.values())


def _config_opt(workspace: Optional[str]) -> Optional[WorkspaceConfig]:
    if not workspace:
        return None
    try:
        return load_config(workspace)
    except FileNotFoundError:
        return None


def _live_client(args: dict, config: Optional[WorkspaceConfig]):
    """Return a Kanboard client: an injected ``_client`` (tests) or one built
    from workspace config + env token. ``None`` means no live connection."""
    if args.get("_client") is not None:
        return args["_client"]
    if config is None:
        return None
    return build_client(config)


def _resolve_live_project_id(client, state, project_name):
    """Find the Kanboard project id: from state cache, else by project name."""
    pid = resolve_project_id(state)
    if pid is not None:
        return pid
    if client is None:
        return None
    proj = client.get_project_by_name(project_name)
    if isinstance(proj, dict) and proj.get("id"):
        return int(proj["id"])
    return None


def _resolve_plan_path(plan_id: str, config: Optional[WorkspaceConfig]) -> Optional[str]:
    if config is None:
        return None
    for entry in config.plans:
        if Path(entry.path).stem == plan_id:
            return str(Path(config.workspace_root) / entry.path)
    return None


def _task_reference_from_args(args: dict) -> Optional[str]:
    if args.get("task_reference"):
        return str(args["task_reference"])
    if args.get("plan_id") and args.get("task_key"):
        return f"{args['plan_id']}:{args['task_key']}"
    return None


def _plan_id_from_reference(reference: str) -> Optional[str]:
    if ":" not in reference:
        return None
    return reference.split(":", 1)[0] or None


def _resolve_task_id(reference: str, client, state, config) -> Optional[int]:
    ts = state.get(reference)
    if ts and ts.kanboard_task_id:
        return ts.kanboard_task_id

    project_id = resolve_project_id(state)
    plan_id = _plan_id_from_reference(reference)
    if project_id is None and plan_id:
        plan_path = _resolve_plan_path(plan_id, config)
        manifest = build_manifest(plan_path, config=config) if plan_path else None
        if manifest is not None:
            project_name, _ = board_target(config, manifest)
            project_id = _resolve_live_project_id(client, state, project_name)

    if project_id is None:
        return None
    task = client.get_task_by_reference(project_id, reference)
    if isinstance(task, dict) and task.get("id"):
        return int(task["id"])
    return None


# --- handlers --------------------------------------------------------------
def h_create_board_from_plan(args: dict) -> dict:
    config = _config_opt(args.get("workspace"))
    manifest = build_manifest(args["plan_path"], config=config)
    dry_run = args.get("dry_run", True)
    project_name, swimlane_name = board_target(config, manifest)
    skeleton = {
        "project_name": project_name,
        "plan_id": manifest.plan_id,
        "plan_type": manifest.plan_type,
        "strategy": manifest.kanboard_project_strategy,
        "columns": _BOARD_COLUMNS,
        "swimlane": swimlane_name or "Default",
        "task_count": len(manifest.tasks),
    }
    if dry_run:
        return {
            "tool": "create_board_from_plan",
            "dry_run": True,
            "applied": False,
            "skeleton": skeleton,
            "status": "dry_run",
            "note": "dry-run skeleton only; creating the board requires a live Kanboard",
        }

    client = _live_client(args, config)
    if client is None:
        return {
            "tool": "create_board_from_plan",
            "dry_run": False,
            "applied": False,
            "skeleton": skeleton,
            "status": "needs_live_kanboard",
            "note": "needs workspace config + a running Kanboard + API token (env) to apply",
        }
    members = config.kanboard.board_members if config else None
    report = apply_board_skeleton(
        client, manifest, members=members,
        project_name=project_name, swimlane_name=swimlane_name,
    )
    return {
        "tool": "create_board_from_plan",
        "dry_run": False,
        "applied": True,
        "skeleton": skeleton,
        "status": "ok",
        "result": report,
    }


def h_sync_plan_to_board(args: dict) -> dict:
    config = _config_opt(args.get("workspace"))
    manifest = build_manifest(args["plan_path"], config=config)
    workspace = args.get("workspace") or "."
    state = load_state(workspace)
    ops = build_diff(manifest, state)
    dry_run = args.get("dry_run", True)
    duplicates = manifest.duplicate_references()
    result = {
        "tool": "sync_plan_to_board",
        "push_policy": "markdown-primary",
        "dry_run": dry_run,
        "plan_id": manifest.plan_id,
        "summary": summarize_diff(ops),
        "duplicate_references": duplicates,
        "operations": [op.to_dict() for op in ops],
    }
    if dry_run:
        result["status"] = "dry_run"
        return result

    if duplicates:
        result["applied"] = False
        result["status"] = "blocked"
        result["note"] = (
            f"duplicate task references {duplicates} would collide in the state "
            "cache; give those plan items distinct explicit ids before applying"
        )
        return result

    client = _live_client(args, config)
    if client is None:
        result["applied"] = False
        result["status"] = "needs_live_kanboard"
        result["note"] = (
            "apply requires workspace config + a running Kanboard + API token (env); "
            "start serve.sh, set the token env var, then re-run with dry_run=false"
        )
        return result

    members = config.kanboard.board_members if config else None
    project_name, swimlane_name = board_target(config, manifest)
    applied = apply_diff(
        client, manifest, state, ops, members=members,
        project_name=project_name, swimlane_name=swimlane_name,
        assignee=default_assignee(config),
    )
    if args.get("workspace"):
        save_state(args["workspace"], state)
    result["applied"] = True
    result["status"] = "ok"
    result["result"] = applied
    return result


def h_pull_board_status(args: dict) -> dict:
    config = _config_opt(args.get("workspace"))
    manifest = build_manifest(args["plan_path"], config=config)
    workspace = args.get("workspace") or "."
    state = load_state(workspace)
    board_snapshot = args.get("board_snapshot")
    source = "provided"
    plan_scope = None
    if board_snapshot is None:
        client = _live_client(args, config)
        project_name, _ = board_target(config, manifest)
        project_id = _resolve_live_project_id(client, state, project_name)
        if client is None or project_id is None:
            return {
                "tool": "pull_board_status",
                "plan_id": manifest.plan_id,
                "status": "needs_live_kanboard",
                "note": "no board_snapshot provided and no live Kanboard project to fetch",
                "candidates": [],
            }
        board_snapshot = fetch_board_snapshot(client, project_id)
        source = "fetched"
        # The project may be shared across plans (workspace-project); scope the
        # classification to this plan's own references.
        plan_scope = manifest.plan_id

    candidates = classify_pull(manifest, board_snapshot, state, plan_scope=plan_scope)
    return {
        "tool": "pull_board_status",
        "plan_id": manifest.plan_id,
        "status": "ok",
        "snapshot_source": source,
        "markdown_unchanged": True,
        "summary": summarize_pull(candidates),
        "candidates": [c.to_dict() for c in candidates],
    }


def h_record_validation(args: dict) -> dict:
    plan_id = args["plan_id"]
    task_key = args["task_key"]
    evidence = args["evidence"]
    dry_run = args.get("dry_run", True)
    reference = f"{plan_id}:{task_key}"
    projection = {
        "task_reference": reference,
        "comment": f"validation evidence: {evidence}",
        "subtask_title": f"evidence: {evidence[:60]}",
    }
    if dry_run:
        return {
            "tool": "record_validation",
            "dry_run": True,
            "applied": False,
            "projection": projection,
            "status": "dry_run",
            "note": "dry-run projection only",
        }

    config = _config_opt(args.get("workspace"))
    client = _live_client(args, config)
    if client is None:
        return {
            "tool": "record_validation",
            "dry_run": False,
            "applied": False,
            "projection": projection,
            "status": "needs_live_kanboard",
            "note": "recording to Kanboard requires workspace config + API token (env)",
        }

    state = load_state(args["workspace"]) if args.get("workspace") else load_state(".")
    task_id = _resolve_task_id(reference, client, state, config)

    if task_id is None:
        return {
            "tool": "record_validation",
            "dry_run": False,
            "applied": False,
            "projection": projection,
            "status": "needs_sync",
            "note": f"no Kanboard task for {reference}; run sync_plan_to_board first",
        }

    result = apply_validation(client, task_id, evidence, label=task_key)
    return {
        "tool": "record_validation",
        "dry_run": False,
        "applied": True,
        "projection": projection,
        "status": "ok",
        "result": result,
    }


def h_record_session_update(args: dict) -> dict:
    reference = _task_reference_from_args(args)
    dry_run = args.get("dry_run", True)
    if reference is None:
        return {
            "tool": "record_session_update",
            "dry_run": dry_run,
            "applied": False,
            "status": "needs_task_reference",
            "note": "pass task_reference or plan_id + task_key; post-session sync will not guess the Kanboard card",
        }

    projection = session_update_projection(
        task_reference=reference,
        session_summary=args["session_summary"],
        result_label=args.get("result_label"),
        validation_evidence=args.get("validation_evidence"),
        changed_files=args.get("changed_files"),
        blocked_reason=args.get("blocked_reason"),
    )
    if dry_run:
        return {
            "tool": "record_session_update",
            "dry_run": True,
            "applied": False,
            "projection": projection,
            "status": "dry_run",
            "note": "dry-run projection only",
        }

    config = _config_opt(args.get("workspace"))
    client = _live_client(args, config)
    if client is None:
        return {
            "tool": "record_session_update",
            "dry_run": False,
            "applied": False,
            "projection": projection,
            "status": "needs_live_kanboard",
            "note": "recording to Kanboard requires workspace config + API token (env)",
        }

    state = load_state(args["workspace"]) if args.get("workspace") else load_state(".")
    task_id = _resolve_task_id(reference, client, state, config)
    if task_id is None:
        return {
            "tool": "record_session_update",
            "dry_run": False,
            "applied": False,
            "projection": projection,
            "status": "needs_sync",
            "note": f"no Kanboard task for {reference}; run sync_plan_to_board first",
        }

    result = apply_session_update(
        client,
        task_id,
        task_reference=reference,
        session_summary=args["session_summary"],
        result_label=args.get("result_label"),
        validation_evidence=args.get("validation_evidence"),
        changed_files=args.get("changed_files"),
        blocked_reason=args.get("blocked_reason"),
    )
    return {
        "tool": "record_session_update",
        "dry_run": False,
        "applied": True,
        "projection": projection,
        "status": "ok",
        "result": result,
    }


def h_curate_plan_board(args: dict) -> dict:
    plan_id = args["plan_id"]
    config = _config_opt(args.get("workspace"))
    plan_path = _resolve_plan_path(plan_id, config)

    manifest = build_manifest(plan_path, config=config) if plan_path else None
    known_refs: set[str] = (
        {t.task_reference for t in manifest.tasks} if manifest else set()
    )

    board_snapshot = args.get("board_snapshot")
    if board_snapshot is None:
        client = _live_client(args, config)
        state = load_state(args["workspace"]) if args.get("workspace") else load_state(".")
        project_name = board_target(config, manifest)[0] if manifest else None
        project_id = (
            _resolve_live_project_id(client, state, project_name) if project_name else None
        )
        if client is None or project_id is None:
            return {
                "tool": "curate_plan_board",
                "plan_id": plan_id,
                "status": "needs_live_kanboard",
                "note": "no board_snapshot provided and no live Kanboard project to fetch",
                "categories": {},
            }
        board_snapshot = fetch_board_snapshot(client, project_id)

    orphaned, foreign, completed, matched = [], [], [], []
    for item in board_snapshot:
        ref = item.get("reference")
        column = item.get("column")
        if not ref:
            orphaned.append(item)
            continue
        if not ref.startswith(f"{plan_id}:"):
            foreign.append(ref)
            continue
        if ref not in known_refs:
            orphaned.append(ref)
        elif column == CANONICAL_TO_COLUMN["done"]:
            completed.append(ref)
        else:
            matched.append(ref)

    return {
        "tool": "curate_plan_board",
        "plan_id": plan_id,
        "status": "ok" if plan_path else "partial",
        "categories": {
            "orphaned_candidates": orphaned,
            "foreign_cards": foreign,
            "completed_projection": completed,
            "matched": matched,
        },
        "note": None
        if plan_path
        else "plan not found in workspace config; orphan detection limited",
    }


def h_inspect_workspace(args: dict) -> dict:
    return _inspect_workspace(args["workspace_path"])


def h_register_workspace(args: dict) -> dict:
    ws = args["workspace_path"]
    init_report = _init_workspace(ws) if args.get("init", True) else None
    registered = _registry.register(ws)
    return {
        "tool": "register_workspace",
        "workspace": ws,
        "init": init_report,
        "registered": registered,
    }


def h_list_workspaces(args: dict) -> dict:
    return {
        "tool": "list_workspaces",
        "registry": str(_registry.registry_path()),
        "workspaces": _registry.list_workspaces(),
    }


def h_sync_all(args: dict) -> dict:
    report = _sync_all(apply=args.get("apply", False), workspace_root=args.get("workspace"))
    report["tool"] = "sync_all"
    return report


# --- registry --------------------------------------------------------------
class ToolSpec:
    def __init__(self, name: str, description: str, input_schema: dict, handler: Callable):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.handler = handler


PLAN_TOOLS: list[ToolSpec] = [
    ToolSpec(
        "create_board_from_plan",
        "Read a plan and produce the Project/Swimlane/Column skeleton it needs. Dry-run by default.",
        {
            "type": "object",
            "properties": {
                "plan_path": {"type": "string"},
                "workspace": {"type": "string"},
                "dry_run": {"type": "boolean", "default": True},
            },
            "required": ["plan_path"],
        },
        h_create_board_from_plan,
    ),
    ToolSpec(
        "sync_plan_to_board",
        "Markdown-primary push: project the plan's task statuses onto the board. Dry-run by default.",
        {
            "type": "object",
            "properties": {
                "plan_path": {"type": "string"},
                "workspace": {"type": "string"},
                "dry_run": {"type": "boolean", "default": True},
            },
            "required": ["plan_path"],
        },
        h_sync_plan_to_board,
    ),
    ToolSpec(
        "pull_board_status",
        "Read manual Kanboard changes and report plan-update candidates. Never edits Markdown.",
        {
            "type": "object",
            "properties": {
                "plan_path": {"type": "string"},
                "workspace": {"type": "string"},
                "board_snapshot": {"type": "array", "items": {"type": "object"}},
            },
            "required": ["plan_path"],
        },
        h_pull_board_status,
    ),
    ToolSpec(
        "record_validation",
        "Record validation evidence for a task as a comment/subtask projection. Dry-run by default.",
        {
            "type": "object",
            "properties": {
                "plan_id": {"type": "string"},
                "task_key": {"type": "string"},
                "evidence": {"type": "string"},
                "workspace": {"type": "string"},
                "dry_run": {"type": "boolean", "default": True},
            },
            "required": ["plan_id", "task_key", "evidence"],
        },
        h_record_validation,
    ),
    ToolSpec(
        "record_session_update",
        "Record a post-session task summary on the mapped Kanboard card; creates an evidence subtask only when validation_evidence is supplied. Dry-run by default.",
        {
            "type": "object",
            "properties": {
                "task_reference": {"type": "string"},
                "plan_id": {"type": "string"},
                "task_key": {"type": "string"},
                "session_summary": {"type": "string"},
                "result_label": {"type": "string"},
                "validation_evidence": {"type": "string"},
                "changed_files": {"type": "array", "items": {"type": "string"}},
                "blocked_reason": {"type": "string"},
                "workspace": {"type": "string"},
                "dry_run": {"type": "boolean", "default": True},
            },
            "required": ["session_summary"],
        },
        h_record_session_update,
    ),
    ToolSpec(
        "curate_plan_board",
        "Classify orphaned, completed, and foreign projection cards for cleanup review.",
        {
            "type": "object",
            "properties": {
                "plan_id": {"type": "string"},
                "workspace": {"type": "string"},
                "board_snapshot": {"type": "array", "items": {"type": "object"}},
            },
            "required": ["plan_id"],
        },
        h_curate_plan_board,
    ),
    ToolSpec(
        "inspect_workspace",
        "Read-only report of workspace config, plan discovery, and sync state.",
        {
            "type": "object",
            "properties": {"workspace_path": {"type": "string"}},
            "required": ["workspace_path"],
        },
        h_inspect_workspace,
    ),
    ToolSpec(
        "register_workspace",
        "Onboard a repo: scaffold .kanboard-plan.yml from its docs/plan (unless init=false) and add it to the global registry.",
        {
            "type": "object",
            "properties": {
                "workspace_path": {"type": "string"},
                "init": {"type": "boolean", "default": True},
            },
            "required": ["workspace_path"],
        },
        h_register_workspace,
    ),
    ToolSpec(
        "list_workspaces",
        "List registered workspaces with config/dir presence (read-only).",
        {"type": "object", "properties": {}},
        h_list_workspaces,
    ),
    ToolSpec(
        "sync_all",
        "Sync every registered workspace's sync-enabled plans. Dry-run by default; apply=true writes live.",
        {
            "type": "object",
            "properties": {"apply": {"type": "boolean", "default": False}},
        },
        h_sync_all,
    ),
]


def tool_names() -> list[str]:
    return [t.name for t in PLAN_TOOLS]


def get_tool(name: str) -> Optional[ToolSpec]:
    for t in PLAN_TOOLS:
        if t.name == name:
            return t
    return None


def run_tool(name: str, args: dict) -> dict:
    spec = get_tool(name)
    if spec is None:
        raise KeyError(f"unknown tool: {name}")
    return spec.handler(args)
