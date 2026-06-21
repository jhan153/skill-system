"""Live runtime wiring: build a Kanboard client from workspace configuration.

The token is resolved without reading secrets from config/state/plan: env
override first, then the local Kanboard SQLite DB for the ``jsonrpc`` app
account. When no token is available the builder returns ``None`` so callers
return ``needs_live_kanboard`` instead of attempting an unauthenticated call.
"""

from __future__ import annotations

from typing import Optional

from .config import WorkspaceConfig, resolve_token
from .kanboard_client import KanboardClient


def build_client(
    config: WorkspaceConfig, environ: Optional[dict] = None
) -> Optional[KanboardClient]:
    token = resolve_token(config.kanboard, environ)
    if not token:
        return None
    return KanboardClient(
        url=config.kanboard.url,
        username=config.kanboard.username,
        token=token,
    )
