# Plan Lifecycle States

| state | meaning | default context policy |
| --- | --- | --- |
| `draft` | Proposed but not adopted. | Load only while deciding adoption. |
| `active` | Current plan for the current goal. | Load when task-relevant. |
| `paused` | Temporarily stopped. | Load only for resume or comparison. |
| `completed` | Work is done and needs closeout. | Load summary or proposals only. |
| `abandoned` | Intentionally dropped. | Do not load by default. |
| `superseded` | Replaced by a newer plan. | Prefer the replacement; explicit request only. |
| `closed_out` | Durable decisions/pointers/follow-ups were distilled. | Summary only. |
| `archived` | Raw history retained. | Explicit request only. |

Missing state is `unverified`, never implicitly active. A paused plan must be explicitly resumed; a superseded plan should name its replacement. Closeout and archive transitions require the evidence and fields in `closeout-distillation.md`.
