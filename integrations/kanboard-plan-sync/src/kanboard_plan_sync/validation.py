"""Record validation/session evidence onto a Kanboard task.

Evidence is projected onto built-in objects: a comment (the evidence text) and
a closed subtask (a checklist marker). This keeps validation visible on the
default board UI without a custom plugin.
"""

from __future__ import annotations

from typing import Optional

from .kanboard_client import KanboardClient

# Kanboard subtask status: 0=todo, 1=in progress, 2=done.
_SUBTASK_DONE = 2
_MAX_COMMENT_FIELD = 1600
_MAX_LIST_ITEMS = 8


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


def _clip(text: str, limit: int = _MAX_COMMENT_FIELD) -> str:
    text = str(text or "").strip()
    if len(text) <= limit:
        return text
    return f"{text[: limit - 3].rstrip()}..."


def _append_optional_block(lines: list[str], title: str, value: object) -> None:
    if value is None:
        return
    if isinstance(value, (list, tuple)):
        values = [_clip(str(v), 240) for v in value if str(v).strip()]
        if not values:
            return
        lines.append(f"**{title}**:")
        for item in values[:_MAX_LIST_ITEMS]:
            lines.append(f"- `{item}`" if "/" in item or "." in item else f"- {item}")
        if len(values) > _MAX_LIST_ITEMS:
            lines.append(f"- ... {len(values) - _MAX_LIST_ITEMS} more")
        return
    text = _clip(str(value))
    if text:
        lines.append(f"**{title}**: {text}")


def session_update_projection(
    task_reference: str,
    session_summary: str,
    result_label: Optional[str] = None,
    validation_evidence: Optional[str] = None,
    changed_files: Optional[list[str]] = None,
    blocked_reason: Optional[str] = None,
) -> dict:
    """Build the comment/subtask projection for a post-session update."""
    label = result_label or "unverified"
    lines = [
        f"post-session update: `{task_reference}`",
        f"**result**: `{label}`",
        f"**summary**: {_clip(session_summary)}",
    ]
    _append_optional_block(lines, "validation evidence", validation_evidence)
    _append_optional_block(lines, "blocked reason", blocked_reason)
    _append_optional_block(lines, "changed files", changed_files)
    lines.extend(
        [
            "",
            "_Session projection only. Markdown remains the source of truth; board comments do not promote completion by themselves._",
        ]
    )
    comment = "\n".join(lines)
    return {
        "task_reference": task_reference,
        "comment": comment,
        "subtask_title": (
            f"session evidence: {result_label or task_reference}"[:128]
            if validation_evidence
            else None
        ),
    }


def apply_session_update(
    client: KanboardClient,
    task_id: int,
    task_reference: str,
    session_summary: str,
    result_label: Optional[str] = None,
    validation_evidence: Optional[str] = None,
    changed_files: Optional[list[str]] = None,
    blocked_reason: Optional[str] = None,
) -> dict:
    """Record a post-session summary on a Kanboard task.

    A plain session update creates a comment only. When validation evidence is
    present, it also creates a done subtask so validated sessions are visible in
    the checklist area without treating every session note as evidence.
    """
    projection = session_update_projection(
        task_reference=task_reference,
        session_summary=session_summary,
        result_label=result_label,
        validation_evidence=validation_evidence,
        changed_files=changed_files,
        blocked_reason=blocked_reason,
    )
    comment_id = client.create_comment(task_id, projection["comment"])
    subtask_id = None
    if validation_evidence and projection["subtask_title"]:
        subtask_id = client.create_subtask(
            task_id, title=projection["subtask_title"], status=_SUBTASK_DONE
        )
    return {
        "task_id": task_id,
        "comment_id": comment_id,
        "subtask_id": subtask_id,
    }
