# Code Review Result And Coordinator Handoff

Load only to classify findings/deferred items, choose the review disposition, or prepare the compact Coordinator/`worker_done` result.

## Result Shape Authority

Cross-owner output must validate as `execution_item.kind: code_review_result` under the Core
schema referenced by `references/execution_item_contract.md`. This file does not redefine the
envelope or payload. It owns only how this review writes `findings`, chooses deferred-item content,
and applies disposition precedence. Standalone review may render the same canonical payload
without a graph transition.

## Findings

Use stable IDs. Each finding contains:

- `id`, falsifiable `claim`, and `priority`;
- one or more tight `code_refs` and optional `baseline_refs`;
- current `impact` and bounded `fix_direction`.

Use `P0` for immediate systemic, safety/security, or irreversible-data risk; `P1` for material contract/state/correctness failure; `P2` for bounded behavior/integration risk; and `P3` only for evidenced future drift. Omit generic style findings.

A concrete current-scope defect or required implementation omission is a finding and forces `repair_required`; never hide it as deferred work. Preserve simultaneously observed deferred items in the same result.

## Deferred Items

Emit each deferred item as a separate Core `deferred_item` card and place its item ID in the review
card's `deferred_item_refs`. Its payload uses `deferred_kind`, `description`, `code_refs`,
`baseline_refs`, `impact`, and `carry_to` from the Core schema.

| `kind` | Use when | Default `carry_to` |
| --- | --- | --- |
| `design_decision` | baseline authority is ambiguous, stale, or conflicting | `next_waterfall_design` |
| `runtime_observation` | static proof is impossible and an observable oracle exists | `human_test` |
| `out_of_scope_work` | useful work lies outside the current Plan/review slice | `next_waterfall_worklist` |
| `static_evidence_gap` | a precise static gap remains without authority to acquire more evidence now | `human_test` when observable, otherwise `next_waterfall_worklist` |
| `ambiguous_requirement` | expected behavior needs human/product/design authority | `next_waterfall_design` |

Deferred means the review node is complete for the current run. Do not acquire evidence automatically, rewrite Plan, create a design/evidence/re-review node, or wait/poll. Normal runtime handoffs may accompany `pass`; use `runtime_observation` only when a material unresolved condition must be preserved beyond the ordinary next test stage.

## Disposition Precedence

1. Any repair-required finding → `repair_required`, `transition_intent: repair`.
2. Otherwise, any deferred item → `complete_with_deferred_items`, `transition_intent: continue`.
3. Otherwise → `pass`, `transition_intent: continue`.

`baseline_decision_needed` and `unverified` may describe lane-local evidence but are never top-level dispositions. `partial_handoff` and `blocked` are not code-review outcomes.

If the implementation snapshot is unavailable or repository access disappears, produce no `code_review_result`. Return only a lifecycle question/escalation containing `review_status: not_produced`, the missing input/access, and the owner needed to restore it.

## Coordinator Consumption

When this result crosses an owner boundary, apply the Core-owned
`references/execution_item_contract.md`. This reference defines Code Review fields and
disposition precedence only; the shared contract exclusively defines Plan/Coordinator authority,
repair-card routing, deferred carry, final Known Bug ownership, and successor selection.

## Worker Done Body

Send only node/round, disposition, compact finding/deferred summaries, Known Bug exclusions, `continue|repair` intent, artifact anchor, and start/finish/elapsed timing when required by the host contract. Never copy full diagrams, comparison matrices, report prose, source analysis, or Plan/Handoff content into `worker_done`.
