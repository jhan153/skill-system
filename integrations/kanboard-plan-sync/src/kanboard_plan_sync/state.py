"""Per-workspace sync state cache at ``.kanboard-plan/state.json``.

State maps a canonical ``task_reference`` to its Kanboard projection ids and
the last synced status. It is a cache, not a source of truth: if lost, the
mapping can be rebuilt via ``getTaskByReference(project_id, reference)``.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


class StateError(RuntimeError):
    """Raised when the state file is present but unreadable and recovery is off."""


STATE_DIRNAME = ".kanboard-plan"
STATE_FILENAME = "state.json"
STATE_VERSION = 1


@dataclass
class TaskState:
    kanboard_task_id: Optional[int] = None
    kanboard_project_id: Optional[int] = None
    last_markdown_status: Optional[str] = None
    last_synced_column: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "kanboard_task_id": self.kanboard_task_id,
            "kanboard_project_id": self.kanboard_project_id,
            "last_markdown_status": self.last_markdown_status,
            "last_synced_column": self.last_synced_column,
        }

    @classmethod
    def from_dict(cls, raw: dict) -> "TaskState":
        return cls(
            kanboard_task_id=raw.get("kanboard_task_id"),
            kanboard_project_id=raw.get("kanboard_project_id"),
            last_markdown_status=raw.get("last_markdown_status"),
            last_synced_column=raw.get("last_synced_column"),
        )


@dataclass
class SyncState:
    version: int = STATE_VERSION
    references: dict[str, TaskState] = field(default_factory=dict)

    def get(self, task_reference: str) -> Optional[TaskState]:
        return self.references.get(task_reference)

    def upsert(self, task_reference: str, task_state: TaskState) -> None:
        self.references[task_reference] = task_state

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "references": {ref: st.to_dict() for ref, st in self.references.items()},
        }

    @classmethod
    def from_dict(cls, raw: dict) -> "SyncState":
        refs = {
            ref: TaskState.from_dict(val)
            for ref, val in (raw.get("references") or {}).items()
        }
        return cls(version=raw.get("version", STATE_VERSION), references=refs)


def state_path(workspace_root: str) -> Path:
    return Path(workspace_root) / STATE_DIRNAME / STATE_FILENAME


def load_state(workspace_root: str, recover: bool = True) -> SyncState:
    """Load state.json, returning an empty SyncState when the file is absent.

    On a corrupt file: if ``recover`` (default), the bad file is moved aside to
    ``state.json.corrupt`` and an empty state is returned; otherwise a
    :class:`StateError` is raised so the caller can decide.
    """
    path = state_path(workspace_root)
    if not path.is_file():
        return SyncState()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return SyncState.from_dict(raw)
    except (json.JSONDecodeError, ValueError, TypeError) as exc:
        if not recover:
            raise StateError(f"corrupt state file: {path}") from exc
        backup = path.with_suffix(path.suffix + ".corrupt")
        os.replace(path, backup)
        return SyncState()


def save_state(workspace_root: str, state: SyncState) -> Path:
    """Atomically persist state: write a temp file in the same dir, then rename.

    The rename is atomic on the same filesystem, so a crash mid-write never
    leaves a half-written state.json.
    """
    path = state_path(workspace_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(state.to_dict(), ensure_ascii=False, indent=2) + "\n"
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(payload)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)
    return path
