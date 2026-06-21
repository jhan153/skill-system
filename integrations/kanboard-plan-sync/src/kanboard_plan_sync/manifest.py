"""Internal sync manifest builder.

Combines the parsed Markdown plan with optional workspace configuration to
produce a :class:`PlanManifest` — the intermediate desired-projection model.
The manifest is derived; the Markdown plan stays canonical.
"""

from __future__ import annotations

from typing import Optional

from .config import WorkspaceConfig
from .models import PlanManifest
from .parser import parse_plan


def build_manifest(
    plan_path: str, config: Optional[WorkspaceConfig] = None
) -> PlanManifest:
    plan_id, title, tasks = parse_plan(plan_path)

    plan_type = "short-term"
    parent_plan_id = None
    strategy = "dedicated-project"

    if config is not None:
        entry = config.plan_entry_for(plan_path)
        if entry is not None:
            plan_type = entry.plan_type
            parent_plan_id = entry.parent_plan_id
            strategy = entry.kanboard_project_strategy

    return PlanManifest(
        plan_id=plan_id,
        plan_path=plan_path,
        plan_title=title,
        plan_type=plan_type,
        parent_plan_id=parent_plan_id,
        kanboard_project_strategy=strategy,
        tasks=tasks,
    )
