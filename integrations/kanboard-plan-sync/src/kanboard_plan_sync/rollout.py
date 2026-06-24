"""Multi-workspace rollout operations: sync-all / status-all.

Iterates the global registry and, per registered workspace, processes each
plan whose ``sync`` flag is on. Default is dry-run (read-only). Apply requires a
live client per workspace; failures are isolated per workspace/plan so one bad
repo never aborts the rest.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional

from .config import load_config
from .diff import build_diff, summarize_diff
from .manifest import build_manifest
from .registry import load_workspaces
from .runtime import build_client
from .state import load_state, save_state
from .sync import apply_diff, board_target, default_assignee


def sync_all(
    apply: bool = False,
    registry_file: Optional[str] = None,
    client_factory: Optional[Callable] = None,
    environ: Optional[dict] = None,
    workspace_root: Optional[str] = None,
) -> dict:
    """Process every registered workspace's sync-enabled plans.

    ``apply=False`` (default) is dry-run: report planned ops only. ``apply=True``
    writes to Kanboard via a live client (built per workspace, or supplied by
    ``client_factory`` for tests). ``workspace_root`` scopes the run to a single
    registered workspace (matched by resolved path); unmatched roots yield an
    empty report. Returns an aggregate report.
    """
    workspaces = load_workspaces(registry_file)
    if workspace_root:
        from pathlib import Path as _Path

        target = str(_Path(workspace_root).expanduser().resolve())
        workspaces = [w for w in workspaces if str(_Path(w).expanduser().resolve()) == target]
    ws_reports: list[dict] = []
    totals = {"workspaces": 0, "plans": 0, "applied": 0, "errors": 0, "skipped": 0}

    for ws in workspaces:
        totals["workspaces"] += 1
        ws_report: dict = {"workspace": ws, "plans": []}
        try:
            config = load_config(ws)
        except FileNotFoundError:
            ws_report["error"] = "no .kanboard-plan.yml"
            totals["errors"] += 1
            ws_reports.append(ws_report)
            continue

        state = load_state(ws)
        ws_report["state_reference_count"] = len(state.references)

        client = None
        if apply:
            client = client_factory(config) if client_factory else build_client(config)
            ws_report["live"] = client is not None

        applied_in_ws = False
        for entry in config.plans:
            if not entry.sync:
                totals["skipped"] += 1
                ws_report["plans"].append({"plan": entry.path, "status": "skipped"})
                continue

            totals["plans"] += 1
            plan_path = str(Path(ws) / entry.path)
            pr: dict = {"plan": entry.path}
            try:
                manifest = build_manifest(plan_path, config=config)
                ops = build_diff(manifest, state)
                pr["plan_id"] = manifest.plan_id
                pr["summary"] = summarize_diff(ops)
                if not apply:
                    pr["status"] = "dry_run"
                elif client is None:
                    pr["status"] = "needs_live_kanboard"
                else:
                    project_name, swimlane_name = board_target(config, manifest)
                    result = apply_diff(
                        client, manifest, state, ops,
                        members=config.kanboard.board_members,
                        project_name=project_name, swimlane_name=swimlane_name,
                        assignee=default_assignee(config),
                    )
                    pr["status"] = "ok"
                    pr["applied_count"] = result["applied_count"]
                    totals["applied"] += result["applied_count"]
                    applied_in_ws = True
            except Exception as exc:  # isolate per-plan failure
                pr["status"] = "error"
                pr["error"] = f"{type(exc).__name__}: {exc}"
                totals["errors"] += 1
            ws_report["plans"].append(pr)

        if apply and applied_in_ws:
            save_state(ws, state)
        ws_reports.append(ws_report)

    return {
        "mode": "apply" if apply else "dry-run",
        "totals": totals,
        "workspaces": ws_reports,
    }
