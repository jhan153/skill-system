---
name: workflow-code-review
description: Statically review a bound production or test implementation diff through risk-selected, evidence-linked Mermaid models. Use before PR or integration testing to inspect state, flow, propagation, reachability, ordering, failure behavior, and optional UI or Test Design conformance, then return a compact Coordinator disposition. Not for mapping-only, repair, runtime validation, or Plan/Handoff topology changes.
---

# Workflow Code Review

## Routing Card
- role: review_gate
- intent_signature: static code review, state/flow/reachability review, dynamic diagrams, optional design conformance, 정적 코드 리뷰
- use_when: review bound production or test code before PR/integration through source-derived models, with or without an authoritative design baseline.
- do_not_use_when: mapping-only (`analysis-codebase-map`), lightweight style/naming feedback, repair, runtime validation, or Plan/Handoff editing is primary.
- expected_inputs: snapshot/diff, review slice, code contracts/invariants, optional UI/Test Design baseline, Known Bug exclusions, and optional node/round identity
- expected_outputs: compact `code_review_result`, optional evidence anchor, and `continue|repair` intent
- context_targets:
  must_read:
    - exact implementation slice, repository instructions, one representative path, and one material edge/failure/cancel/compensation path
    - supplied node/round and Known Bug exclusions; never full Plan/Handoff
  read_if_needed:
    - only callers, registrations, state owners, configuration, tests, or decisions that can change a material finding
    - `references/maintainable_code_principles.md` when maintainability is a material review criterion or the diff materially changes ownership, abstraction, invariant/effect boundaries, conventions, or verification
    - `references/database_persistence_transparency_contract.md` when the bound diff changes database schema, mapping, query, migration, transaction, or data-access ownership
    - `references/identifier_readability_principle.md` when related identifiers materially obstruct state, flow, ownership, or effect tracing, or identifier-readability conformance is explicitly in the bound review scope; never activate this Workflow for lightweight naming feedback alone
    - `references/execution_item_contract.md` when node/round identity is supplied or the compact result will cross a Workflow, Coordinator, Plan/Handoff, or plugin boundary
    - `references/testing_stage_contract.md` and `references/testing_strategy_contract.md` when reviewing a Core `test_implementation_result` against a `test_design_result`
    - load only applicable baseline and references: `references/model-comparison.md` for review mechanics; `references/finding-handoff.md` for disposition/handoff
  do_not_load_by_default:
    - unrelated source/design artifacts or runtime evidence
- risk_profile:
  reads: targeted code and directly relevant contract, baseline, ownership, or rationale evidence
  writes: none; the Coordinator alone records results in Handoff
  tools: focused static inspection and optional Mermaid syntax rendering
  sensitive_resources: credentials denied; tests/runtime and code/Plan mutation require another owner
- entry_scene: PREPARE

## Core Cards

- produces: `references/core-execution-items-v1/cards/code_review_result.md`, `references/core-execution-items-v1/cards/deferred_item.md`
- consumes: `references/core-execution-items-v1/cards/design_result.md`, `references/core-execution-items-v1/cards/implementation_result.md`, `references/core-execution-items-v1/cards/test_design_result.md`, `references/core-execution-items-v1/cards/test_implementation_result.md`, `references/core-execution-items-v1/cards/bug_fix_result.md`, `references/core-execution-items-v1/cards/known_bug_record.md`

## Ownership And Evidence Contract
- Make the implementation snapshot the primary review boundary. A supplied Core `design_result` or `test_design_result` is an optional conformance baseline: its absence disables only that comparison, never the code-derived review or disposition. Preserve its authority and unresolved fields instead of treating every mockup, test idea, or current output as a software invariant.
- For a `test_implementation_result`, review test-only write scope, actual SUT path, design or inline authority lane, oracle/tolerance/baseline conformance, falsifier reachability, diagnostic preservation, and proof ceiling. Do not reinterpret condition Pass/Fail as a static code-review disposition or authorize production repair from runtime evidence.
- Treat `static` as source-based inspection without executing the reviewed behavior. It does not mean a fixed template: select diagram types and altitudes from the code's state, flow, interaction, and failure risks.
- Use `analysis-codebase-map` only as an optional read-only mapping aid. Re-open its source refs before relying on it; this workflow retains finding and verdict ownership.
- Separate direct static facts, static inference, evidenced rationale, and runtime-only claims. Compilation or unit tests may corroborate a path but do not erase a static finding or prove runtime behavior.
- Treat Plan as topology authority and Handoff as the Coordinator-owned ledger. Do not edit either, create design/evidence/repair/re-review nodes, close the DAG, select a next node ID, or wait/poll.
- Preserve supplied Known Bug exclusions as `SKIP — excluded Known Bug <id>` without reopening them.
- When `references/maintainable_code_principles.md` is active, apply its five review questions after tracing the representative and material negative paths and before recording findings. This review owns static findings, deferred items, and disposition; repair and runtime-only verification remain explicit handoffs.
- When `references/database_persistence_transparency_contract.md` is active, own only static conformance findings for the visible `source_of_truth`, database boundary/model, declared read/write effects, transaction, and lifecycle. Defer runtime-only query-plan, cardinality, locking, and latency claims to the implementation or validation owner.
- If the implementation snapshot is absent or repository access is lost, emit no `code_review_result`; return a lifecycle question/escalation with `review_status: not_produced`. Do not call this a review `blocked` verdict.

## Workflow
1. Bind node/round identity when supplied, implementation snapshot, review slice, exclusions, material criteria, and optional conformance sources including `design_result` or `test_design_result`. One review item has one input snapshot; use separate review nodes when production and test implementation cards both require review.
2. Trace one representative entrypoint-to-effect path plus one material negative or disconfirming path. Inspect only evidence that can change the review.
3. Use `references/model-comparison.md` to choose dynamic views, build the code-derived model, and review intrinsic state/flow/propagation/order/failure/reachability properties.
4. When an authoritative baseline exists, add only the relevant conformance comparisons. Record its Core `design_result` or `test_design_result` reference when supplied. Preserve baseline ambiguity, unresolved fields, or staleness as evidence; do not invent intended behavior, oracle authority, or suppress intrinsic findings.
5. Record concrete current-scope implementation defects as findings. Record design authority, runtime observation, out-of-scope work, static evidence, or requirement ambiguity that should not be repaired now as typed deferred items. When `references/identifier_readability_principle.md` is active, own only the material finding and disposition: anchor it to the exact related identifier set and affected trace, then hand repair to the applicable implementation owner without prescribing an example prefix or abbreviation.
6. Use `references/finding-handoff.md` for finding/deferred content and disposition precedence. In graph or cross-Workflow mode, build the one canonical `code_review_result` shape from `references/execution_item_contract.md` and its machine schema; do not recreate a local wrapper.
7. Return `transition_intent` only. The Coordinator records the result and applies an already-existing Plan edge.

## Disposition Gate
- `repair_required`: one or more concrete in-scope implementation defects or required implementation omissions need repair now. Preserve any deferred items and return `transition_intent: repair`.
- `complete_with_deferred_items`: no repair-required finding remains, but one or more typed deferred items must be carried. The review node is complete; return `transition_intent: continue`.
- `pass`: the static review is complete with neither repair-required findings nor deferred items. Normal runtime handoffs may still exist; return `transition_intent: continue`.

Apply precedence `repair_required` > `complete_with_deferred_items` > `pass`. Never emit `baseline_decision_needed`, `unverified`, `partial_handoff`, or `blocked` as a top-level review disposition. Runtime-only conditions do not invalidate a completed static review.

## Output Contract
Return `code_review_result` only in the canonical Core envelope/payload, including
`design_baseline_ref` when a Core `design_result` was consumed and `test_design_baseline_ref` when
a Core `test_design_result` was consumed. Keep full diagrams, matrices, and
runtime handoffs in one optional anchored artifact; do not copy them into the Coordinator or
`worker_done` body. The compact body contains item/ref IDs, disposition, finding/deferred
summaries, Known Bug exclusions, evidence/artifact anchors, and `continue|repair` intent—never a
next node ID or Plan edit.
