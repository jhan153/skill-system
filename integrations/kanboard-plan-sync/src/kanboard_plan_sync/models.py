"""Core data models for plan tasks, the sync manifest, diffs, and pull feedback.

These are plain dataclasses with explicit ``to_dict`` serialization so the CLI
and MCP facade can emit stable JSON without leaking dataclass internals.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PlanTask:
    """A single tracked plan item parsed from a Markdown plan document."""

    task_key: str
    task_reference: str
    title: str
    markdown_status: str  # canonical: todo/doing/review/blocked/done
    kanboard_column: str
    is_candidate: bool = False  # True when task_key was auto-generated (no explicit ID)
    source_line: int = 0
    raw_status_token: str = ""

    def to_dict(self) -> dict:
        return {
            "task_key": self.task_key,
            "task_reference": self.task_reference,
            "title": self.title,
            "markdown_status": self.markdown_status,
            "kanboard_column": self.kanboard_column,
            "is_candidate": self.is_candidate,
            "source_line": self.source_line,
            "raw_status_token": self.raw_status_token,
        }


@dataclass
class PlanManifest:
    """Intermediate artifact: the desired Kanboard projection of one plan.

    The manifest is derived, not canonical. The canonical state is the Markdown
    plan document it was built from.
    """

    plan_id: str
    plan_path: str
    plan_title: str
    plan_type: str = "short-term"
    parent_plan_id: Optional[str] = None
    kanboard_project_strategy: str = "dedicated-project"
    tasks: list[PlanTask] = field(default_factory=list)

    def duplicate_references(self) -> list[str]:
        """Return references that appear on more than one task (a sync hazard:
        the state cache is keyed by reference, so duplicates collide)."""
        seen: dict[str, int] = {}
        for t in self.tasks:
            seen[t.task_reference] = seen.get(t.task_reference, 0) + 1
        return sorted(ref for ref, count in seen.items() if count > 1)

    def to_dict(self) -> dict:
        return {
            "plan_id": self.plan_id,
            "plan_path": self.plan_path,
            "plan_title": self.plan_title,
            "plan_type": self.plan_type,
            "parent_plan_id": self.parent_plan_id,
            "kanboard_project_strategy": self.kanboard_project_strategy,
            "task_count": len(self.tasks),
            "candidate_count": sum(1 for t in self.tasks if t.is_candidate),
            "duplicate_references": self.duplicate_references(),
            "tasks": [t.to_dict() for t in self.tasks],
        }


# Diff operation kinds produced by the dry-run diff engine.
OP_CREATE_PROJECT = "create_project"
OP_CREATE_TASK = "create_task"
OP_MOVE_TASK = "move_task"
OP_NOOP = "noop"


@dataclass
class SyncOp:
    """One planned write operation against the Kanboard projection."""

    op: str
    task_reference: str
    detail: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"op": self.op, "task_reference": self.task_reference, "detail": self.detail}


# Pull feedback candidate kinds (plan section 7).
PULL_IN_SYNC = "in_sync"
PULL_COMPLETION_CANDIDATE = "completion_candidate"
PULL_DEMOTION_CANDIDATE = "demotion_candidate"
PULL_SAFE_DEMOTION = "safe_demotion"
PULL_NEW_ISSUE_CANDIDATE = "new_issue_candidate"
PULL_DELETION_CANDIDATE = "deletion_candidate"


@dataclass
class PullCandidate:
    """A classified difference between Kanboard state and the Markdown plan.

    Pull never edits Markdown; it only reports candidates for human review.
    """

    kind: str
    task_reference: Optional[str]
    markdown_status: Optional[str]
    kanboard_column: Optional[str]
    note: str = ""

    def to_dict(self) -> dict:
        return {
            "kind": self.kind,
            "task_reference": self.task_reference,
            "markdown_status": self.markdown_status,
            "kanboard_column": self.kanboard_column,
            "note": self.note,
        }
