# Instruction Budget

Place each admitted item exactly once:

- `runtime_terms`: minimal stable rules needed every turn.
- `active_goal_brief`: current goal and non-goals.
- `active_plan_brief`: current tasks, risks, validation, and next action.
- `reference_material`: detail loaded only when needed.
- `memory_proposals`: durable items awaiting explicit persistence.
- `archived_raw_source`: preserved history excluded from default context.

Prefer compact active briefs and on-demand references. Never solve instruction bloat by loading raw archives or generating another heavyweight package.
