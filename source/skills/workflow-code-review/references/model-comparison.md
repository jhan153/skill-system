# Static Review Model Reference

Load only when interacting state, ownership, or failure paths need a code-derived visual model, or an accepted baseline comparison needs that model.

## Build The Code-Derived Model

- Give each material actor, component, message, state, transition, guard, data/effect, invariant, and failure behavior a stable local ID plus code refs.
- Preserve whether each element or edge is a direct static fact, static inference, or runtime unknown.
- Trace a representative path and the material edge/failure/cancel/compensation paths selected by
  `references/static_code_review_contract.md`. One representative and one disconfirming path are
  the minimum, never the coverage ceiling.
- Do not require or invent an expected design model. Code contracts, explicit invariants, language/framework rules, public interfaces, and accepted requirements may support intrinsic findings when directly evidenced.

## Select Views Dynamically

Apply `references/static_code_review_contract.md` to decide whether a visual model is needed.
Source-linked prose may complete a simple review without loading this reference. When a model is
needed, choose the minimum complementary set that exposes the interacting material relationships;
no particular diagram type or baseline/implementation pair is mandatory by template. Keep every
activated material risk covered by a source-path trace or model element.

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

Make a finding only when the claim is falsifiable and anchored to code or an authoritative
contract. A source-permitted interleaving that violates lifetime, synchronization, ordering,
visibility, or cleanup is a static finding. Keep its occurrence/frequency, external state, actual
production registration, and scheduler-dependent behavior explicitly outside static proof.

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

Apply the reachability guard in `references/static_code_review_contract.md`; a diagram never
substitutes for checking the applicable dispatch and registration surface.

## Render Evidence

- Keep one concern per diagram and use stable IDs across related views.
- Mark `INFERRED`, `RUNTIME UNKNOWN`, or conformance deltas in text; color alone is insufficient.
- Draw only evidenced relations, use domain labels, and keep source refs outside node labels.
- A successful Mermaid render proves syntax only.

`analysis-codebase-map` may provide a source-linked map when explicitly useful, but its map is supporting evidence. It neither supplies this workflow's findings nor decides the disposition.
