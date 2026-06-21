"""Global multi-workspace registry.

Lists registered workspace roots so ``sync-all`` / ``status-all`` can operate
across repos. Stores only filesystem paths — never tokens or secrets. The
location defaults to a host-local file and can be overridden via the
``KANBOARD_PLAN_REGISTRY`` env var (used by tests for isolation).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import yaml

DEFAULT_REGISTRY_PATH = str(Path.home() / ".ai/infra/kanboard-plan-sync/workspaces.yml")
REGISTRY_ENV = "KANBOARD_PLAN_REGISTRY"


def registry_path(path: Optional[str] = None) -> Path:
    return Path(path or os.environ.get(REGISTRY_ENV) or DEFAULT_REGISTRY_PATH)


def _normalize(workspace: str) -> str:
    return str(Path(workspace).expanduser().resolve())


def load_workspaces(path: Optional[str] = None) -> list[str]:
    p = registry_path(path)
    if not p.is_file():
        return []
    raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    return [str(w) for w in (raw.get("workspaces") or [])]


def save_workspaces(workspaces: list[str], path: Optional[str] = None) -> Path:
    p = registry_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        yaml.safe_dump({"workspaces": list(workspaces)}, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return p


def register(workspace: str, path: Optional[str] = None) -> list[str]:
    ws = _normalize(workspace)
    items = load_workspaces(path)
    if ws not in items:
        items.append(ws)
        save_workspaces(items, path)
    return items


def unregister(workspace: str, path: Optional[str] = None) -> list[str]:
    ws = _normalize(workspace)
    items = [w for w in load_workspaces(path) if w != ws]
    save_workspaces(items, path)
    return items


def list_workspaces(path: Optional[str] = None) -> list[dict]:
    """Report each registered workspace with config/dir presence (read-only)."""
    from .config import find_config

    out: list[dict] = []
    for w in load_workspaces(path):
        out.append(
            {
                "path": w,
                "exists": Path(w).is_dir(),
                "config_present": find_config(w) is not None,
            }
        )
    return out
