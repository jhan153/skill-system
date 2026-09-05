---
name: workflow-code-review
description: Statically review a bound production change or test implementation snapshot through a design-first change contract, risk-selected evidence-linked Mermaid models, material-effect coverage, and optional design conformance. Return blocking findings, non-blocking advisories, later-owned deferred items, and a scoped static disposition; production review runs before runtime testing. Not for mapping-only, repair, runtime validation, production test-oracle/evidence review, or Plan/Handoff topology changes.
---

# Workflow Code Review

## Routing Card
- role: review_gate
- family: workflow
- intent_signature: static code review, state/flow/reachability review, dynamic diagrams, optional design conformance, 정적 코드 리뷰
- use_when: review bound production or test code before PR/integration through source-derived models, with or without an authoritative design baseline.
- do_not_use_when: mapping-only (`analysis-codebase-map`), lightweight style/naming feedback, repair, runtime validation, production test-oracle/evidence review, or Plan/Handoff editing is primary.
- expected_inputs: exact snapshot/diff identity, change intent and material changed effects, review slice, code contracts/invariants, optional accepted architecture/UI/Test Design baseline, Known Bug exclusions, and optional node/round identity
- expected_outputs: risk-selected Mermaid evidence, review coverage and ceiling, blocking findings, advisories, deferred items, and a standalone or Core static disposition
- context_targets:
  must_read:
    - exact implementation slice, repository instructions, and `references/static_code_review_contract.md`
    - one representative path plus the material edge/failure/cancel/compensation paths selected by the activated risk axes; these are a minimum, not a coverage ceiling
    - supplied node/round and Known Bug exclusions; never full Plan/Handoff
  read_if_needed:
    - only callers, registrations, state owners, configuration, or decisions that can change a material finding; read tests only when the reviewed artifact is test implementation or an existing test is necessary direct contract/caller evidence
    - `references/architecture_design_contract.md` when an accepted architecture design is supplied
      as a conformance baseline or the bound review explicitly includes architecture-delta
      conformance
    - `references/programming_paradigm_contract.md` when an accepted architecture or atomic
      boundary baseline contains a target-relevant programming-paradigm or adjacent-model
      application, or the bound Implementation result supplies a task-local application and
      `paradigm_conformance`; after that base contract, load only its selected files under
      `references/programming-paradigms/`
    - `references/maintainable_code_principles.md` when maintainability is a material review criterion or the diff materially changes ownership, abstraction, invariant/effect boundaries, conventions, or verification
    - `references/database_persistence_transparency_contract.md` when the bound diff changes database schema, mapping, query, migration, transaction, or data-access ownership
    - `references/identifier_readability_principle.md` when related identifiers materially obstruct state, flow, ownership, or effect tracing, or identifier-readability conformance is explicitly in the bound review scope; never activate this Workflow for lightweight naming feedback alone
    - `references/runtime_debugging_contract.md` when the diff changes crash/dump capture, symbol/build manifests, debugger hooks, dynamic-diagnostic integration, trace/replay capture, graphics validation/markers, or device-loss diagnostics
    - `references/execution_item_contract.md` when node/round identity is supplied or the compact result will cross a Workflow, Coordinator, Plan/Handoff, or plugin boundary
    - `references/testing_stage_contract.md` and `references/testing_strategy_contract.md` when reviewing a Core `test_implementation_result` against a `test_design_result`
    - load only applicable baseline and references: `references/model-comparison.md` for Mermaid mechanics; `references/finding-handoff.md` for standalone/Core presentation
  do_not_load_by_default:
    - unrelated source/design artifacts or runtime evidence
- risk_profile:
  reads: targeted code and directly relevant contract, baseline, ownership, or rationale evidence
  writes: none; the Coordinator alone records results in Handoff
  tools: focused static inspection and risk-selected Mermaid construction/rendering
  sensitive_resources: credentials denied; tests/runtime and code/Plan mutation require another owner
- entry_scene: PREPARE

### Resource Closure

```json
[
  {
    "source": "shared/docs/architecture_design_contract.md",
    "target": "references/architecture_design_contract.md",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "selected skill's matching read_if_needed condition applies"
  },
  {
    "source": "shared/contracts/core-execution-items-v1/cards/bug_fix_result.md",
    "target": "references/core-execution-items-v1/cards/bug_fix_result.md",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "matching Core result crosses the declared workflow boundary"
  },
  {
    "source": "shared/contracts/core-execution-items-v1/cards/code_review_result.md",
    "target": "references/core-execution-items-v1/cards/code_review_result.md",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "matching Core result crosses the declared workflow boundary"
  },
  {
    "source": "shared/contracts/core-execution-items-v1/cards/deferred_item.md",
    "target": "references/core-execution-items-v1/cards/deferred_item.md",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "matching Core result crosses the declared workflow boundary"
  },
  {
    "source": "shared/contracts/core-execution-items-v1/cards/design_result.md",
    "target": "references/core-execution-items-v1/cards/design_result.md",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "matching Core result crosses the declared workflow boundary"
  },
  {
    "source": "shared/contracts/core-execution-items-v1/cards/implementation_result.md",
    "target": "references/core-execution-items-v1/cards/implementation_result.md",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "matching Core result crosses the declared workflow boundary"
  },
  {
    "source": "shared/contracts/core-execution-items-v1/cards/known_bug_record.md",
    "target": "references/core-execution-items-v1/cards/known_bug_record.md",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "matching Core result crosses the declared workflow boundary"
  },
  {
    "source": "shared/contracts/core-execution-items-v1/cards/test_design_result.md",
    "target": "references/core-execution-items-v1/cards/test_design_result.md",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "matching Core result crosses the declared workflow boundary"
  },
  {
    "source": "shared/contracts/core-execution-items-v1/cards/test_implementation_result.md",
    "target": "references/core-execution-items-v1/cards/test_implementation_result.md",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "matching Core result crosses the declared workflow boundary"
  },
  {
    "source": "shared/docs/database_persistence_transparency_contract.md",
    "target": "references/database_persistence_transparency_contract.md",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "selected skill's matching read_if_needed condition applies"
  },
  {
    "source": "shared/schemas/execution/execution-item.schema.json",
    "target": "references/execution-item.schema.json",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "matching Core result crosses the declared workflow boundary"
  },
  {
    "source": "shared/docs/execution_item_contract.md",
    "target": "references/execution_item_contract.md",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "selected skill's matching read_if_needed condition applies"
  },
  {
    "source": "shared/docs/identifier_readability_principle.md",
    "target": "references/identifier_readability_principle.md",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "selected skill's matching read_if_needed condition applies"
  },
  {
    "source": "shared/docs/maintainable_code_principles.md",
    "target": "references/maintainable_code_principles.md",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "selected skill's matching read_if_needed condition applies"
  },
  {
    "source": "shared/docs/programming-paradigms",
    "target": "references/programming-paradigms",
    "projection": "tree",
    "load": "read_if_needed",
    "condition": "selected skill's matching read_if_needed condition applies"
  },
  {
    "source": "shared/docs/programming_paradigm_contract.md",
    "target": "references/programming_paradigm_contract.md",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "selected skill's matching read_if_needed condition applies"
  },
  {
    "source": "shared/docs/runtime_debugging_contract.md",
    "target": "references/runtime_debugging_contract.md",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "selected skill's matching read_if_needed condition applies"
  },
  {
    "source": "shared/docs/static_code_review_contract.md",
    "target": "references/static_code_review_contract.md",
    "projection": "verbatim",
    "load": "must_read",
    "condition": "selected skill's mandatory read contract applies"
  },
  {
    "source": "shared/docs/testing_stage_contract.md",
    "target": "references/testing_stage_contract.md",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "selected skill's matching read_if_needed condition applies"
  },
  {
    "source": "shared/docs/testing_strategy_contract.md",
    "target": "references/testing_strategy_contract.md",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "selected skill's matching read_if_needed condition applies"
  }
]
```

## Core Cards

- produces: `references/core-execution-items-v1/cards/code_review_result.md`, `references/core-execution-items-v1/cards/deferred_item.md`
- consumes: `references/core-execution-items-v1/cards/design_result.md`, `references/core-execution-items-v1/cards/implementation_result.md`, `references/core-execution-items-v1/cards/test_design_result.md`, `references/core-execution-items-v1/cards/test_implementation_result.md`, `references/core-execution-items-v1/cards/bug_fix_result.md`, `references/core-execution-items-v1/cards/known_bug_record.md`

## Ownership And Evidence Contract
- `references/static_code_review_contract.md` owns the change contract, design preflight, risk
  activation, material-effect coverage, result classes, and static proof ceiling. Do not recreate
  its checklist or add a production test-oracle lane locally.
- An accepted `architecture_design` artifact is an optional normative conformance baseline. Check
  only the bound implementation slice against its owners, contracts, dependency direction, pattern
  stop boundaries, transition constraints, and assigned fitness handoff. Do not accept a proposed
  design, invent missing architecture, or turn static conformance into semantic/operational proof.
- An accepted paradigm/model application inside that architecture or an atomic boundary is also an
  immutable conformance baseline. Check the selected axis, owner, minimum closure, maximum scope,
  interactions, forbidden drift, and thin-profile proof ceiling without reselecting the model or
  loading Implementation's detailed method catalog.
- A task-local application supplied by the bound Implementation result is a conformance baseline
  only for that `local_implementation` slice. Check its declared application and
  `paradigm_conformance` against the same thin profile without promoting it to accepted architecture
  or treating maker-authored evidence as an independent runtime oracle.
- Make the implementation snapshot the primary review boundary. A supplied Core `design_result` or `test_design_result` is an optional conformance baseline: its absence disables only that comparison, never the code-derived review or disposition. Preserve its authority and unresolved fields instead of treating every mockup, test idea, or current output as a software invariant.
- For a `test_implementation_result`, review test-only write scope, actual SUT path, design or inline authority lane, oracle/tolerance/baseline conformance, falsifier reachability, diagnostic preservation, and proof ceiling. Do not reinterpret condition Pass/Fail as a static code-review disposition or authorize production repair from runtime evidence.
- Treat `static` as source-based inspection without executing the reviewed behavior. It does not mean a fixed template: select diagram types and altitudes from the code's state, flow, interaction, and failure risks.
- Use `analysis-codebase-map` only as an optional read-only mapping aid. Re-open its source refs before relying on it; this workflow retains finding and verdict ownership.
- Separate direct static facts, static inference, evidenced rationale, and runtime-only claims. Compilation or unit tests may corroborate a path but do not erase a static finding or prove runtime behavior.
- Treat Plan as topology authority and Handoff as the Coordinator-owned ledger. Do not edit either, create design/evidence/repair/re-review nodes, close the DAG, select a next node ID, or wait/poll.
- Treat `repair_required` as a static disposition for the reviewed snapshot, not a Bug Fix
  classification. Record whether the required condition contradicts or exceeds the supplied
  accepted implementation/method contract, but never choose Implementation, Bug Fix, a decision
  owner, or a successor edge. The Coordinator performs that semantic admission against the Plan.
- Preserve supplied Known Bug exclusions as `SKIP — excluded Known Bug <id>` without reopening them.
- When `references/maintainable_code_principles.md` is active, apply its five review questions after tracing the representative and material negative paths and before recording findings. This review owns static findings, deferred items, and disposition; repair and runtime-only verification remain explicit handoffs.
- When `references/database_persistence_transparency_contract.md` is active, own only static conformance findings for the visible `source_of_truth`, database boundary/model, declared read/write effects, transaction, and lifecycle. Defer runtime-only query-plan, cardinality, locking, and latency claims to the implementation or validation owner.
- When `references/runtime_debugging_contract.md` is active, statically review diagnostic
  infrastructure for target/build/symbol/capture identity, partial-capture reporting, lifetime and
  reentrancy, crash-context allocation/lock/loader/stack safety, privacy and retention, trusted
  symbol/source/extension loading, and graphics marker/resource correlation. Test-capture
  provenance/completeness/proof ceiling belongs to `test-evidence-review`; causal interpretation to
  `workflow-runtime-debugging` or semantically admitted bounded-repair `workflow-bug-fix`; and condition-matched runtime
  readback of the infrastructure to its Implementation owner. A source-level `pass` does not
  establish crash-context or debugger behavior.
- If no item supplies a snapshot, resolve an unambiguous repository diff/worktree identity when
  available. If the reviewed identity cannot be established or repository access is lost, emit no
  result; return a lifecycle question/escalation with `review_status: not_produced`. Do not call
  this a review `blocked` disposition.

## Workflow
1. Bind the exact implementation identity, review slice, exclusions, node/round when supplied, and
   the change contract from `references/static_code_review_contract.md`, including stable IDs for
   every material changed effect. Bind the assigned positive production output and accepted
   implementation/method contract when supplied. Bind optional conformance sources including accepted
   `architecture_design`, a task-local paradigm application from the bound Implementation result,
   Core `design_result`, or `test_design_result`. One review item has one input snapshot;
   production and test implementation cards remain separate review items.
2. Run the design preflight before line-level inspection. Record a current-scope
   ownership/boundary/responsibility defect before dependent detail, stop reviewing details that
   the rejected structure would replace, and continue only independent high-consequence risks.
3. Activate only the risk axes signaled by the change, assign every material effect to them, and
   select enough representative and disconfirming paths to expose each distinct material risk.
4. Use `references/model-comparison.md` to build the risk-selected source-derived Mermaid model set
   before disposition and review intrinsic state/flow/propagation/order/failure/reachability
   properties.
5. When an authoritative baseline exists, add only the relevant conformance comparisons. Record an
   accepted architecture artifact in `artifact_refs`/`evidence_refs`, and record its Core
   `design_result` or `test_design_result` reference when supplied. Preserve any accepted or
   task-local paradigm/model application, its owner scope, and its proof ceiling. Preserve baseline
   ambiguity, unresolved fields, or staleness as evidence; do not invent intended behavior, oracle
   authority, or suppress intrinsic findings.
6. Close material-effect coverage, then classify current defects as blocking findings, evidenced
   non-blocking improvements as advisories, and only later-owned material gaps as deferred items.
   When `references/identifier_readability_principle.md` is active, anchor the exact related
   identifier set and affected trace without prescribing an example prefix or abbreviation.
7. Use `references/finding-handoff.md` to render the same review facts as a standalone human report
   or, only in graph/cross-owner mode, the canonical `code_review_result`. The Coordinator treats
   `review_disposition` as one input, runs Plan semantic admission against the positive output and
   accepted implementation/method contract, and applies only an already-existing Plan edge.

## Disposition Gate
- `repair_required`: one or more concrete in-scope implementation defects or required implementation omissions need resolution now. This disposition does not select Bug Fix; preserve simultaneously observed advisories and eligible deferred items.
- `complete_with_deferred_items`: no blocking finding remains, but one or more eligible typed deferred items must be carried by a named later owner or observation point.
- `pass`: every material changed effect is accounted for with no blocking finding, deferred item, or material-unassessed entry. Advisories may accompany `pass`.

Apply precedence `repair_required` > `complete_with_deferred_items` > `pass`. `pass` is limited to
the bound static slice and declared proof ceiling; it does not establish runtime behavior, test
sufficiency, merge readiness, full requirement completion, or product acceptance. Never emit
`baseline_decision_needed`, `unverified`, `partial_handoff`, or `blocked` as a top-level review
disposition.

## Output Contract
For standalone review, return a human-readable report ordered as snapshot/scope, Mermaid evidence,
coverage and ceiling, blocking findings, advisories, deferred items, and disposition. Do not invent
Core item IDs, node/round, or Plan fields.

For graph or cross-owner review, return the canonical Core `code_review_result`, including review
coverage, proof ceiling, advisories, `design_baseline_ref` when a Core `design_result` was consumed,
and `test_design_baseline_ref` when a Core `test_design_result` was consumed. Keep full diagrams and
comparison matrices in one anchored artifact and keep the Coordinator/`worker_done` body compact.
Never return a transition intent, next node ID, or Plan edit; the execution owner combines the
disposition with Plan semantic admission and existing edges.
