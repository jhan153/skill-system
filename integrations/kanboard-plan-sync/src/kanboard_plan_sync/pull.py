"""Pull feedback classifier (plan section 7).

Reads a Kanboard board snapshot and the Markdown-derived manifest, then
classifies each divergence as a review *candidate*. Pull never edits Markdown;
it only reports. Promotion to Markdown ``done`` requires separate evidence.

Board snapshot item shape::

    {"reference": "<plan_id>:<task_key>", "column": "완료", "task_id": 12}

A board item with no ``reference`` is treated as a manually created card.
"""

from __future__ import annotations

from typing import Optional

from .models import (
    PULL_COMPLETION_CANDIDATE,
    PULL_DELETION_CANDIDATE,
    PULL_DEMOTION_CANDIDATE,
    PULL_IN_SYNC,
    PULL_NEW_ISSUE_CANDIDATE,
    PULL_SAFE_DEMOTION,
    PlanManifest,
    PullCandidate,
)
from .state import SyncState
from .status import status_for_column

# Progress rank used only to split demotion vs safe-demotion and to orient
# non-done drift. blocked is treated as stalled (same rank as todo).
_RANK = {"todo": 0, "blocked": 0, "doing": 1, "review": 2, "done": 3}


def _rank(status: Optional[str]) -> int:
    return _RANK.get(status or "", 0)


def classify_pull(
    manifest: PlanManifest,
    board_snapshot: list[dict],
    state: Optional[SyncState] = None,
    plan_scope: Optional[str] = None,
) -> list[PullCandidate]:
    """Classify board-vs-markdown differences into review candidates.

    ``plan_scope`` (a plan_id) restricts classification to references in that
    plan's namespace (``<plan_id>:...``). Use it when the snapshot comes from a
    Project shared by several plans (workspace-project mapping) so cards from
    other plans/swimlanes are not mis-flagged as new issues here.
    """
    state = state or SyncState()
    prefix = f"{plan_scope}:" if plan_scope else None

    def _in_scope(ref: str) -> bool:
        return prefix is None or (ref or "").startswith(prefix)

    board_by_ref = {
        item["reference"]: item
        for item in board_snapshot
        if item.get("reference") and _in_scope(item["reference"])
    }
    manifest_refs = {t.task_reference for t in manifest.tasks}
    candidates: list[PullCandidate] = []

    for task in manifest.tasks:
        ref = task.task_reference
        board = board_by_ref.get(ref)
        md_status = task.markdown_status

        if board is None:
            ts = state.get(ref)
            if ts and ts.kanboard_task_id:
                candidates.append(
                    PullCandidate(
                        kind=PULL_DELETION_CANDIDATE,
                        task_reference=ref,
                        markdown_status=md_status,
                        kanboard_column=None,
                        note="card previously synced is missing on the board",
                    )
                )
            # else: never pushed yet — a push concern, not a pull signal.
            continue

        board_status = status_for_column(board.get("column"))
        candidates.append(
            _classify_one(ref, md_status, board_status, board.get("column"))
        )

    # Cards on the board that the plan does not know about.
    for ref, item in board_by_ref.items():
        if ref not in manifest_refs:
            candidates.append(
                PullCandidate(
                    kind=PULL_NEW_ISSUE_CANDIDATE,
                    task_reference=ref,
                    markdown_status=None,
                    kanboard_column=item.get("column"),
                    note="referenced card not present in the plan",
                )
            )
    for item in board_snapshot:
        # When scoped to a plan, project-wide unreferenced cards aren't this
        # plan's concern (curate handles them at project level).
        if not item.get("reference") and prefix is None:
            candidates.append(
                PullCandidate(
                    kind=PULL_NEW_ISSUE_CANDIDATE,
                    task_reference=None,
                    markdown_status=None,
                    kanboard_column=item.get("column"),
                    note="manually created card with no plan reference",
                )
            )
    return candidates


def _classify_one(
    ref: str,
    md_status: str,
    board_status: Optional[str],
    column: Optional[str],
) -> PullCandidate:
    def make(kind: str, note: str = "") -> PullCandidate:
        return PullCandidate(
            kind=kind,
            task_reference=ref,
            markdown_status=md_status,
            kanboard_column=column,
            note=note,
        )

    if board_status == md_status:
        return make(PULL_IN_SYNC)

    if board_status == "done" and md_status != "done":
        return make(
            PULL_COMPLETION_CANDIDATE,
            "moved to 완료; confirm implementation/doc/test evidence before promoting",
        )

    if md_status == "done" and board_status != "done":
        if board_status in ("doing", "review"):
            return make(
                PULL_SAFE_DEMOTION,
                "moved out of 완료 into active work; prior evidence preserved",
            )
        return make(
            PULL_DEMOTION_CANDIDATE,
            "moved out of 완료 to a non-active column; prior evidence preserved",
        )

    # Neither side done, statuses differ.
    if _rank(board_status) > _rank(md_status):
        return make(
            PULL_COMPLETION_CANDIDATE,
            "forward progress on the board (not 완료); review before updating plan",
        )
    return make(
        PULL_DEMOTION_CANDIDATE,
        "board moved the item backward; review before updating plan",
    )


def summarize_pull(candidates: list[PullCandidate]) -> dict:
    counts: dict[str, int] = {}
    for c in candidates:
        counts[c.kind] = counts.get(c.kind, 0) + 1
    return counts
