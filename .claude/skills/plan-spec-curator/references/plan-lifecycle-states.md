# Plan Lifecycle States

Use these states when deciding whether a plan may enter active context.

| state | meaning | default context policy |
| --- | --- | --- |
| `draft` | Proposed but not adopted. | Load only when the user is deciding whether to adopt it. |
| `active` | Current execution plan for the current goal. | Load when relevant to the current task. |
| `paused` | Temporarily stopped. | Do not load by default; load only if resuming or comparing. |
| `completed` | Work is done and should be closed out. | Load only the summary or memory proposals by default. |
| `abandoned` | Intentionally dropped. | Do not load by default. |
| `superseded` | Replaced by a newer plan. | Load the newer plan; load this only by explicit request. |
| `archived` | Preserved as raw history. | Do not load by default; use explicit request only. |

## State Rules
- Only `active` plans may be loaded by default.
- `completed`, `abandoned`, `superseded`, and `archived` plans are not active instructions.
- A `paused` plan must be explicitly resumed before it becomes default context.
- A `superseded` plan should name the replacing plan when known.
- Missing state is `Unverified`; do not silently treat it as active.

## Minimal Metadata
Use these fields when proposing plan lifecycle metadata:

```yaml
plan_id:
parent_goal:
status:
created_at:
updated_at:
scope:
supersedes: []
superseded_by:
archive_target:
context_load_policy:
```
