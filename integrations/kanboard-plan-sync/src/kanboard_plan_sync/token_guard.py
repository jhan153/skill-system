"""Secret-hygiene checks: ensure no API token / credential is stored in the
config, state, or plan files.

The token must live only in an environment variable (``token_env``), the local
Kanboard SQLite DB (``local_db_path``), or another host-local secret. This
module verifies that contract two ways:

1. structural — flag any ``token:``/``password:``/``secret:`` assignment in the
   config file (the correct key is ``token_env``, which holds only a *name*);
2. literal — if the env token is set, flag any file that contains its value.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Optional

from .config import find_config, load_config

# Matches a credential-bearing key assignment, but NOT ``token_env``.
_SECRET_KEY_RE = re.compile(
    r"(?im)^\s*(api[_-]?token|token|password|secret|api[_-]?key)\s*[:=]"
)


def scan_text(text: str, env_token: Optional[str] = None) -> list[str]:
    issues: list[str] = []
    for m in _SECRET_KEY_RE.finditer(text):
        issues.append(f"credential-bearing key '{m.group(1)}' assigned a value")
    if env_token and env_token in text:
        issues.append("the resolved API token value appears verbatim")
    return issues


def scan_workspace(workspace_root: str) -> dict:
    root = Path(workspace_root)
    findings: list[dict] = []

    cfg_path = find_config(str(root))
    token_env = "KANBOARD_API_TOKEN"
    files: list[Path] = []
    if cfg_path is not None:
        files.append(cfg_path)
        config = load_config(str(root))
        token_env = config.kanboard.token_env
        files.append(root / ".kanboard-plan" / "state.json")
        for p in config.plans:
            files.append(root / p.path)

    env_token = os.environ.get(token_env)

    for path in files:
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for issue in scan_text(text, env_token=env_token):
            findings.append({"file": str(path), "issue": issue})

    return {
        "workspace_root": str(root),
        "token_env": token_env,
        "scanned_files": [str(p) for p in files if p.is_file()],
        "ok": not findings,
        "findings": findings,
    }
