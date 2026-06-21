"""Workspace configuration loader for ``.kanboard-plan.yml``.

Configuration and state live per-workspace; the tool itself is global. The
Kanboard API token is never read from this file. The config stores only where
to resolve it from: env override first, then the local Kanboard SQLite DB for
``jsonrpc`` app authentication.
"""

from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

CONFIG_FILENAME = ".kanboard-plan.yml"
DEFAULT_LOCAL_DB_PATH = str(Path.home() / ".ai/infra/kanboard-local/data/db.sqlite")


@dataclass
class KanboardConn:
    url: str = "http://127.0.0.1:8080/jsonrpc.php"
    username: str = "jsonrpc"
    token_env: str = "KANBOARD_API_TOKEN"
    local_db_path: Optional[str] = DEFAULT_LOCAL_DB_PATH
    # Kanboard usernames auto-added as project members on board create/sync, so
    # the board is visible in their dashboard with no manual step. Local
    # single-user default: the admin account.
    board_members: list[str] = field(default_factory=lambda: ["admin"])
    # Single-user kanban: every synced card is assigned to this user so the
    # default `assignee:me` board filter never hides them. None -> fall back to
    # the first board_member.
    board_assignee: Optional[str] = None


@dataclass(frozen=True)
class TokenResolution:
    token: Optional[str]
    source: str  # env | local_db | none


@dataclass
class PlanEntry:
    path: str
    plan_type: str = "short-term"  # short-term | long-term
    parent_plan_id: Optional[str] = None
    kanboard_project_strategy: str = "dedicated-project"  # dedicated-project | workspace-project
    sync: bool = True  # include this plan in sync-all; set false to skip stale plans


@dataclass
class WorkspaceConfig:
    workspace_root: str
    config_path: str
    name: str
    kanboard: KanboardConn = field(default_factory=KanboardConn)
    plans: list[PlanEntry] = field(default_factory=list)
    plan_discovery_globs: list[str] = field(default_factory=lambda: ["docs/plan/*.md"])

    def plan_entry_for(self, plan_path: str) -> Optional[PlanEntry]:
        """Return the configured PlanEntry matching ``plan_path`` (by basename)."""
        target = Path(plan_path).name
        for entry in self.plans:
            if Path(entry.path).name == target:
                return entry
        return None

    def to_dict(self) -> dict:
        return {
            "workspace_root": self.workspace_root,
            "config_path": self.config_path,
            "name": self.name,
            "kanboard": {
                "url": self.kanboard.url,
                "username": self.kanboard.username,
                "token_env": self.kanboard.token_env,
                "local_db_path": self.kanboard.local_db_path,
                "board_members": list(self.kanboard.board_members),
                "board_assignee": self.kanboard.board_assignee,
            },
            "plans": [
                {
                    "path": p.path,
                    "plan_type": p.plan_type,
                    "parent_plan_id": p.parent_plan_id,
                    "kanboard_project_strategy": p.kanboard_project_strategy,
                    "sync": p.sync,
                }
                for p in self.plans
            ],
            "plan_discovery_globs": list(self.plan_discovery_globs),
        }


def find_config(workspace_root: str) -> Optional[Path]:
    path = Path(workspace_root) / CONFIG_FILENAME
    return path if path.is_file() else None


def load_config(workspace_root: str) -> WorkspaceConfig:
    """Load ``.kanboard-plan.yml`` from ``workspace_root``.

    Missing keys fall back to defaults so a minimal config still loads.
    Raises FileNotFoundError if the config file does not exist.
    """
    root = Path(workspace_root)
    path = root / CONFIG_FILENAME
    if not path.is_file():
        raise FileNotFoundError(f"no {CONFIG_FILENAME} in {workspace_root}")

    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return parse_config(raw, workspace_root=str(root), config_path=str(path))


def parse_config(raw: dict, workspace_root: str, config_path: str) -> WorkspaceConfig:
    """Build a WorkspaceConfig from an already-parsed mapping (testable)."""
    ws = raw.get("workspace", {}) or {}
    kb = raw.get("kanboard", {}) or {}
    conn = KanboardConn(
        url=kb.get("url", KanboardConn.url),
        username=kb.get("username", KanboardConn.username),
        token_env=kb.get("token_env", KanboardConn.token_env),
        local_db_path=kb.get("local_db_path", KanboardConn.local_db_path),
        board_members=list(kb.get("board_members") or ["admin"]),
        board_assignee=kb.get("board_assignee"),
    )

    plans = []
    for item in raw.get("plans", []) or []:
        plans.append(
            PlanEntry(
                path=item["path"],
                plan_type=item.get("plan_type", "short-term"),
                parent_plan_id=item.get("parent_plan_id"),
                kanboard_project_strategy=item.get(
                    "kanboard_project_strategy", "dedicated-project"
                ),
                sync=bool(item.get("sync", True)),
            )
        )

    discovery = (raw.get("plan_discovery", {}) or {}).get("glob") or ["docs/plan/*.md"]

    return WorkspaceConfig(
        workspace_root=workspace_root,
        config_path=config_path,
        name=ws.get("name", Path(workspace_root).name),
        kanboard=conn,
        plans=plans,
        plan_discovery_globs=list(discovery),
    )


def resolve_token_info(
    conn: KanboardConn, environ: Optional[dict] = None
) -> TokenResolution:
    """Resolve the Kanboard API token without exposing it in config/state/plan.

    Environment wins so callers can override local defaults. For the local
    ``jsonrpc`` app account, the Kanboard app token is read from the SQLite
    settings table in immutable read-only mode.
    """
    env = environ if environ is not None else os.environ
    token = env.get(conn.token_env)
    if token:
        return TokenResolution(token=token, source="env")

    if conn.username == "jsonrpc":
        db_token = _read_app_token_from_local_db(conn.local_db_path)
        if db_token:
            return TokenResolution(token=db_token, source="local_db")

    return TokenResolution(token=None, source="none")


def resolve_token(conn: KanboardConn, environ: Optional[dict] = None) -> Optional[str]:
    """Resolve the Kanboard API token value for runtime client construction."""
    return resolve_token_info(conn, environ).token


def _read_app_token_from_local_db(local_db_path: Optional[str]) -> Optional[str]:
    if not local_db_path:
        return None

    db_path = Path(local_db_path).expanduser()
    if not db_path.is_file():
        return None

    connection = None
    try:
        connection = sqlite3.connect(f"file:{db_path}?mode=ro&immutable=1", uri=True)
        row = connection.execute(
            "select value from settings where option = ?", ("api_token",)
        ).fetchone()
    except sqlite3.Error:
        return None
    finally:
        if connection is not None:
            connection.close()

    if not row or row[0] is None:
        return None

    token = str(row[0]).strip()
    return token or None
