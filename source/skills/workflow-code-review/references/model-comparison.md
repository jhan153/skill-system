# Static Review Model Reference

Load only for code-derived model construction, dynamic view selection, intrinsic static checks, or optional baseline comparison.

## Build The Code-Derived Model

- Give each material actor, component, message, state, transition, guard, data/effect, invariant, and failure behavior a stable local ID plus code refs.
- Preserve whether each element or edge is a direct static fact, static inference, or runtime unknown.
- Trace a representative path and one material edge/failure/cancel/compensation path before declaring the view sufficient.
- Do not require or invent an expected design model. Code contracts, explicit invariants, language/framework rules, public interfaces, and accepted requirements may support intrinsic findings when directly evidenced.

## Select Views Dynamically

Choose the minimum complementary set that exposes the material risk; no diagram type or baseline/implementation pair is mandatory by template.

| View | Static review question | Altitude | Mermaid |
| --- | --- | --- | --- |
| use case | Which actor/system responsibility is evidenced? | HLD | bounded `flowchart LR` |
| component | Who owns state/effects and which dependencies bypass that ownership? | HLD/LLD | `flowchart` with `subgraph` |
| sequence | What call/message/effect order, retry, or cancellation is possible? | HLD/LLD | `sequenceDiagram` |
| state | Which guarded transitions, terminal states, and stuck paths exist? | LLD; HLD for durable product state | `stateDiagram-v2` |
| activity | How do branches, joins, rollback, or compensation behave? | LLD | decision-labeled `flowchart` |
| flowchart | How does local control/data propagate and what is reachable? | LLD | `flowchart TD` or `LR` |
| communication | Which peers exchange numbered messages and fan out? | HLD/LLD | numbered-message `flowchart` |

Use one altitude when it answers the review. Add HLD and LLD together only when a material ownership/behavior issue crosses them. Add state for explicit/durable state, sequence or communication for interaction/order, and activity/flowchart for branching, propagation, or compensation.

## Review Intrinsic Static Properties

Inspect only applicable axes:

- state ownership, initial/intermediate/terminal/error/cancel/timeout/retry transitions, guards, writers/readers, and notifications;
- control/data/state propagation, effect order, sync/async semantics, idempotency, partial failure, rollback, and compensation;
- dependency direction, ownership bypasses, interface/contract violations, and contradictory invariants;
- reachability and liveness, including missing exits, terminal escape, stale/lost propagation, and stuck cycles.

Make a finding only when the claim is falsifiable and anchored to code or an authoritative contract. Keep runtime scheduling, external state, production registration, and concurrency outcomes explicitly outside static proof.

## Optional Conformance Lane

When an exact accepted plan/spec/ADR/HLD/LLD is supplied, compare only the elements material to the review. Pair baseline and implementation diagrams only when pairing improves the decision; otherwise attach baseline refs to the code-derived view or finding.

Use these lane-local statuses, never as top-level dispositions:

| Status | Meaning |
| --- | --- |
| `conforms` | Material semantics and ownership match. |
| `missing_in_code` | An evidenced required element/relation is absent. |
| `extra_in_code` | Code adds an undesigned path, state, effect, or dependency. |
| `changed_semantics` | Identity matches but order, guard, data, ownership, effect, or failure behavior differs. |
| `intentional_deviation` | A named constraint and accepted decision authorize the difference. |
| `baseline_gap_or_stale` | The intended model is missing, contradictory, or obsolete. |
| `ambiguous` | Design authority is needed before conformance can be judged. |
| `runtime_unverified` | Static evidence cannot establish dynamic behavior. |

No baseline means no conformance rows; it does not reduce the intrinsic review disposition. Accept `intentional_deviation` only with an evidenced constraint and decision source.

## Reachability Guard

Before calling code unreachable, cover applicable entrypoints, exports, interface implementations, dependency injection, routes/callbacks, framework/plugin registration, configuration/flags, reflection, generated lookup, dynamic dispatch, queues, and subscriptions. If that dispatch surface is incomplete, return an `unreachable_candidate` finding or `static_evidence_gap` deferred item with the missing evidence; text-search or call-graph absence alone is insufficient.

## Render Evidence

- Keep one concern per diagram and use stable IDs across related views.
- Mark `INFERRED`, `RUNTIME UNKNOWN`, or conformance deltas in text; color alone is insufficient.
- Draw only evidenced relations, use domain labels, and keep source refs outside node labels.
- A successful Mermaid render proves syntax only.

`analysis-codebase-map` may provide a source-linked map when explicitly useful, but its map is supporting evidence. It neither supplies this workflow's findings nor decides the disposition.
