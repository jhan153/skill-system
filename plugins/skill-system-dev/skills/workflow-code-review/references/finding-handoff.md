# Code Review Presentation And Handoff

Load only after `references/static_code_review_contract.md` has closed the change contract, risk
coverage, result classification, and static disposition. This reference owns presentation; it does
not redefine classification or Core execution-item semantics.

## Blocking Findings

Use stable IDs. Each blocking finding contains:

- `id`, falsifiable `claim`, and `priority` (`P0`, `P1`, or `P2`);
- one or more tight `code_refs` and optional `baseline_refs`;
- current `impact` and the mandatory `required_condition`; and
- an optional non-normative `suggested_solution`.

Use `P0` for immediate systemic, safety/security, or irreversible-data risk; `P1` for material
contract/state/correctness failure; and `P2` for bounded behavior/integration or current-scope
maintainability risk that still requires repair. P3 is not a blocking priority. After Plan semantic
admission, Bug Fix may consume `required_condition` as a bounded same-contract repair contract; it
never treats `suggested_solution` as authority.

## Advisories

Each advisory contains a stable `id`, evidenced `observation`, one or more tight `code_refs`,
optional `baseline_refs`, bounded `impact`, and an optional `suggestion`. Advisories do not change
disposition, create a repair obligation, or become deferred work. Omit generic style preferences,
nits, and unevidenced future possibilities.

## Deferred Items

Classify a deferred item only after the shared static-review contract's four admission conditions
are all satisfied. Use `deferred_kind`, `description`, `code_refs`, `baseline_refs`, `impact`, and
`carry_to` in both modes. In standalone review, render those typed facts as ordinary prose without
inventing an item ID. Only graph/cross-owner mode emits a separate Core `deferred_item` and places
its item ID in `code_review_result.deferred_item_refs`.

| `kind` | Material use | Default `carry_to` |
| --- | --- | --- |
| `design_decision` | accepted behavior/design authority is ambiguous, stale, or conflicting and a named design owner must decide | `next_waterfall_design` |
| `runtime_observation` | static proof is impossible, the unresolved condition is material, and a named observation point exists | `human_test` |
| `out_of_scope_work` | a material later-owned risk lies outside the current Plan/review slice and would be lost if omitted | `next_waterfall_worklist` |
| `static_evidence_gap` | a precise material static gap remains and the later evidence owner is known | `human_test` when observable, otherwise `next_waterfall_worklist` |
| `ambiguous_requirement` | expected behavior materially changes the verdict and needs named product/design authority | `next_waterfall_design` |

Deferred means the review node is complete for the current run, not that merge or product
readiness has been established. Do not acquire evidence automatically, rewrite Plan, create a
design/evidence/re-review node, or wait/poll. Ordinary questions, cleanup ideas, speculative reuse,
and non-blocking improvements are omitted or advisory, never durable deferred work.

## Standalone Presentation

Return ordinary review prose in this order:

1. snapshot and review slice;
2. source-linked representative/disconfirming path evidence, including Mermaid only when needed;
3. material-effect/risk coverage and static proof ceiling;
4. blocking findings ordered by priority;
5. advisories;
6. deferred items; and
7. static disposition and explicit limits.

Do not invent Core item IDs, graph node/round values, Known Bug records, or Plan transitions.

## Cross-Owner Core Presentation

Only when the result crosses a Workflow, Coordinator, Plan/Handoff, or plugin boundary, validate it
as `execution_item.kind: code_review_result` under `references/execution_item_contract.md` and its
schema. Include the compact review coverage, proof ceiling, blocking findings, advisories,
deferred-item refs, exclusions, and artifact/evidence anchors. The execution owner treats
`review_disposition` as one input, compares the required positive work with the Plan's accepted
implementation/method contract, and applies only an existing edge; this review emits no transition
intent or successor.

Keep full source-path analysis and any needed Mermaid diagrams or comparison matrices in one anchored artifact.
The Coordinator/`worker_done` body contains only node/round when applicable, disposition, compact
finding/advisory/deferred summaries, Known Bug exclusions, artifact anchor, and required timing.

If the implementation identity cannot be established or repository access disappears, produce no
review result. Return only a lifecycle question/escalation containing
`review_status: not_produced`, the missing identity/access, and the owner needed to restore it.
