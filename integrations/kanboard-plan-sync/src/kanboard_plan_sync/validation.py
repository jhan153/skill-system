"""Record validation evidence onto a Kanboard task.

Evidence is projected onto built-in objects: a comment (the evidence text) and
a closed subtask (a checklist marker). This keeps validation visible on the
default board UI without a custom plugin.
"""

from __future__ import annotations

from typing import Optional

from .kanboard_client import KanboardClient

# Kanboard subtask status: 0=todo, 1=in progress, 2=done.
_SUBTASK_DONE = 2


def apply_validation(
    client: KanboardClient,
    task_id: int,
    evidence: str,
    label: Optional[str] = None,
) -> dict:
    title = f"validated: {label or evidence}"[:128]
    comment_id = client.create_comment(task_id, f"validation evidence: {evidence}")
    subtask_id = client.create_subtask(task_id, title=title, status=_SUBTASK_DONE)
    return {
        "task_id": task_id,
        "comment_id": comment_id,
        "subtask_id": subtask_id,
    }
