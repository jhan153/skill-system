"""Read-only workspace inspection.

Reports workspace configuration, discovered plan files, state location, and
whether a Kanboard API token is reachable — without performing any network
call and without ever revealing the token value.
"""

from __future__ import annotations

from pathlib import Path

from .config import find_config, load_config, resolve_token_info
from .token_guard import scan_workspace
from .state import load_state, state_path


def inspect_workspace(workspace_path: str) -> dict:
    root = Path(workspace_path)
    report: dict = {
        "workspace_root": str(root),
        "exists": root.is_dir(),
        "config_present": False,
    }

    if not root.is_dir():
        report["error"] = "workspace directory does not exist"
        return report

    cfg_path = find_config(str(root))
    if cfg_path is None:
        report["error"] = "no .kanboard-plan.yml found"
        report["discovered_plans"] = _discover(root, ["docs/plan/*.md"])
        return report

    config = load_config(str(root))
    token = resolve_token_info(config.kanboard)
    report["config_present"] = True
    report["config_path"] = config.config_path
    report["workspace_name"] = config.name
    report["kanboard"] = {
        "url": config.kanboard.url,
        "username": config.kanboard.username,
        "token_env": config.kanboard.token_env,
        "local_db_path": config.kanboard.local_db_path,
        "token_present": token.token is not None,
        "token_source": token.source,
    }
    report["configured_plans"] = [
        {
            "path": p.path,
            "exists": (root / p.path).is_file(),
            "plan_type": p.plan_type,
            "parent_plan_id": p.parent_plan_id,
            "kanboard_project_strategy": p.kanboard_project_strategy,
        }
        for p in config.plans
    ]
    report["discovered_plans"] = _discover(root, config.plan_discovery_globs)

    sp = state_path(str(root))
    state = load_state(str(root))
    report["state"] = {
        "path": str(sp),
        "exists": sp.is_file(),
        "reference_count": len(state.references),
    }

    secrets = scan_workspace(str(root))
    report["secret_hygiene"] = {
        "ok": secrets["ok"],
        "finding_count": len(secrets["findings"]),
        "findings": secrets["findings"],
    }
    return report


def _discover(root: Path, globs: list[str]) -> list[str]:
    found: set[str] = set()
    for pattern in globs:
        for match in root.glob(pattern):
            if match.is_file():
                found.add(str(match.relative_to(root)))
    return sorted(found)
