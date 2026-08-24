---
name: workflow-bug-fix
description: Repair one concrete failure with proportional diagnosis, one bounded intervention, original-signal observation, actual-path readback, and a visible attempt status. In Plan DAG mode, BF1 or BF2 owns exactly one assigned round and returns a changed snapshot or no-change result for Coordinator consumption; it never reviews the full implementation, edits Plan/Handoff, selects another node, or finalizes a Coordinator-owned Known Bug. Direct standalone repair may own at most two locally reviewed rounds.
---

# Workflow Bug Fix

## Routing Card
- role: primary
- intent_signature:
  - bug/failing-test/build/runtime/regression fix; broken behavior repair
- use_when:
  - the user requests repair of an observed or reproducible failure and expects verification afterward, whether the cause is known or still needs proportional diagnosis.
  - a Plan/Coordinator dispatches an explicit `BF1` or `BF2` node with `node_id`, `round`, `source_review_item_ref`, and concrete source findings.
  - a direct standalone repair resumes after one locally reviewed attempt and still has one bounded round available.
- do_not_use_when:
  - diagnosis-only with no repair request, full static code review/disposition, Plan or Handoff mutation, successor selection, a Known Bug already excluded for the current run, ordinary feature work, or validation-only work.
- expected_inputs:
  - observed symptom/original signal, material expected condition, available oracle or canonical source, reproduction context, attempt history, and, in DAG mode, assigned node/round/source-review identity plus concrete findings
- expected_outputs:
  - one `bug_fix_result` containing attempt history, changed snapshot/review anchor or an explicit no-change result, original-signal observation, actual-path readback, visible attempt status, and an optional non-final Known Bug candidate
- context_targets:
  must_read:
    - original failure, material expected condition, implicated production owner/path, and repository instructions
  read_if_needed:
    - canonical input/source, caller/state flow, boundary readback, existing tests, config/manifests, and validation contract
    - `references/database_persistence_transparency_contract.md` when the bounded repair changes database schema, ORM/ODM mapping, query, migration, transaction, or data-access-boundary behavior
    - `references/identifier_readability_principle.md` when the assigned failure or review finding is an identifier-readability defect, or the bounded intervention must rename a related identifier set
    - `workflow-implementation` paradigm references as non-owning shape context when the user/expected contract names a paradigm, data layout, execution model, construction rule, or other implementation shape; `workflow-bug-fix` remains the repair owner
    - `references/execution_item_contract.md` in DAG mode or whenever a repair result/candidate crosses a Workflow, Coordinator, Plan/Handoff, or plugin boundary
    - `references/causal-diagnosis.md` when the cause is unclear, recurring, intermittent, high-risk, or needs a discriminator before repair
    - `references/attempt-and-known-bug.md` whenever a prior repair attempt exists or the bug sits inside a graph/handoff
  do_not_load_by_default:
    - full repo/memory, broad reports, unrelated history, raw production data, or credentials
- risk_profile:
  reads: failure output, production source/callers/state, tests/config, and validation/readback evidence
  writes: DAG mode exactly one assigned repair intervention; standalone mode at most two locally reviewed interventions for the same problem
  tools: reproduction, focused diagnostics, diff inspection, one original-signal observation after an intervention, and actual-path readback
  sensitive_resources: deny credentials; external or destructive reproduction needs explicit boundary review
- entry_scene:
  - PREPARE

## Core Cards

- produces: `references/core-execution-items-v1/cards/bug_fix_result.md`, `references/core-execution-items-v1/cards/known_bug_candidate.md`
- produces in standalone mode after bounded final review: `references/core-execution-items-v1/cards/known_bug_record.md`
- consumes: `references/core-execution-items-v1/cards/code_review_result.md`

## Completion And Evidence
- Bind each material condition to its authority and evidence. A user/canonical contract or production observation can define expected behavior; an agent-authored test can preserve that expectation but is not an independent oracle.
- Fix and read back the actual production path. Structural checks, command exit, mocks, interfaces, and test passes prove only what they directly cover; they cannot establish a broader semantic result.
- A required `fail`, `needs_review`, blocked, or unverified condition stays unresolved until evidence from that same condition resolves it. Do not report complete or agent-verified from a narrower pass.
- Source selection, migration, media/data transformation, and external boundaries require canonical-input identification plus actual selected/output readback. Missing or mismatched canonical input fails closed; never substitute legacy data silently.
- A review or test is an observation surface, not an unquestionable oracle. When evidence shows the test or harness contract is wrong, repair that owner directly; never expand validation merely to keep the bug-fix loop alive.

## Mode And Attempt Boundary

Use `references/attempt-and-known-bug.md` for repair-specific identity, attempt rows, result
classification, and candidate fields. In DAG mode, use the Core-owned
`references/execution_item_contract.md` for cross-owner envelopes and Coordinator consumption.

- **DAG mode:** when Plan fields `node_id`, `round`, and `source_review_item_ref` are supplied, own exactly that `A1` or `A2` intervention and return. Never begin another round inside the same invocation. `A2` is admitted only when the dispatch already names `A2`, cites a `CR1` result with concrete `repair_required` findings, and the Coordinator confirms the assigned Plan node.
- **Standalone mode:** without those Plan fields, the workflow may perform and locally review at most two rounds for one problem. The second round is optional and requires evidence from the first local review; there is no third round.

A repair intervention is one code, configuration, test, or harness change intended to alter the assigned failure. Diagnostic observations and unchanged reruns do not consume another round. `resolved`, `narrowed`, `moved`, `unchanged`, and `unreproducible` describe the attempt observation only; they authorize no DAG action.

In DAG mode, full source-derived Mermaid/model/baseline review and `pass | repair_required | complete_with_deferred_items` disposition belong to `workflow-code-review`. This workflow checks only diff churn, the original signal once after an intervention, actual-path readback, and attempt classification. A changed result returns a `changed_snapshot` and `review_anchor`. A no-change or unreproducible result returns `postcondition: no_change_unresolved` without manufacturing an empty review cycle.

## Implementation Shape Invariants
- Fix the complete evidenced cause with the least conceptual machinery, not the smallest diff. A direct change may update every in-scope producer/consumer required to remove the cause.
- Give each internal concept one canonical contract, representation, state machine, and policy owner. On mismatch, migrate all in-scope participants; do not add an adapter, bridge, proxy, shim, dual model, or fallback to preserve the disagreement.
- Prefer plain functions, values, concrete types, direct calls, existing primitives, and composition. Reject Clean Code-style class/interface/function fragmentation, mock-created seams, forwarding layers, and speculative factories/registries/frameworks.
- Interface/inheritance/proxy is a rare present runtime exception. An unmodifiable external edge may use only thin stateless validation/translation to one canonical value or typed failure, with no domain policy or hidden state.
- Preserve every explicit user/canonical paradigm and shape condition. A paradigm label without observable state/data/effect/dispatch/construction rules remains an unresolved requirement rather than permission to improvise.
- When `references/database_persistence_transparency_contract.md` is active, preserve accepted `source_of_truth`, database boundary/model, read/write effects, consistency/transaction, and lifecycle. This workflow owns only the bounded repair and matching original-signal/actual-path readback; a new source, database policy, or ownership decision remains unresolved outside the repair.

## Workflow
1. Select DAG or standalone mode before editing. Bind the problem identity, original signal, expected result/authority, attempt history, and any supplied node/round/source-review fields. Do not reset history after retrigger or compaction.
2. In DAG mode, refuse an unassigned round or an `A2` dispatch lacking both concrete `CR1 repair_required` findings and the explicit `BF2` node assignment. Return the missing authorization without editing.
3. Trace the actual entry, production owner, state/data flow, canonical source when relevant, and one representative boundary/readback. Read `references/causal-diagnosis.md` only when a bounded discriminator is needed.
4. Select one evidenced cause and one direct canonical intervention. Keep source/policy/fallback decisions at their domain owner and update every in-scope participant required by that cause. Never weaken assertions, skip checks, widen mocks, add bypasses, or substitute a plausible fallback. When `references/identifier_readability_principle.md` is active, change only the assigned identifier set and required callers, preserve higher-priority naming authorities, and return static disposition to `workflow-code-review` without inventing a spelling rule.
5. Inspect the resulting diff. If a repair was applied, capture `changed_artifacts`, `changed_snapshot`, and a `review_anchor`; observe the original signal once and read back the actual affected path. If no meaningful change remains or the signal is unavailable, record the exact no-change or unreproducible evidence instead.
6. Append the assigned attempt row and classify `attempt_status` as `resolved`, `narrowed`, `moved`, `unchanged`, or `unreproducible`.
7. In DAG mode, return immediately with the structured result. After `A2`, include only a non-final Known Bug candidate when the attempt ledger can support later Coordinator consumption. In standalone mode, perform its bounded local review and only then decide whether an optional second round or a final standalone Known Bug result is warranted.

## Output Contract
In DAG mode return exactly one canonical Core `bug_fix_result` item and, when applicable, a separate `known_bug_candidate` item referenced by ID. `references/attempt-and-known-bug.md` owns repair-specific writing rules, not payload shape. When the database contract is consumed, carry its material conformance in the changed snapshot and actual-path readback instead of adding a new envelope. Do not add Plan/Handoff edits, a review disposition, or any successor/terminal field. Standalone mode may additionally return a Core `known_bug_record` after its own bounded review, but it uses the same attempt evidence and never hides unresolved conditions behind a task label.

## Cross-Skill Boundaries
- A diagnosis-only request stays with the current task owner under the global read-only boundary. It does not start this workflow, create a repair round, or require a separate Bug Analysis skill.
- `workflow-code-review` owns full read-only static review and the `pass | repair_required | complete_with_deferred_items` disposition. This workflow supplies its changed snapshot/review anchor but never substitutes local checks for that review.
- Cross-owner repair, review, deferred, final Known Bug, and successor semantics come only from `references/execution_item_contract.md`; this skill does not restate or override them.
- `workflow-implementation` owns ordinary feature work and refactoring without a current failure.
- `analysis-boundary-design` supplies deep module, seam, and boundary decisions when needed; it does not replace `workflow-bug-fix` as owner of the concrete repair.
- `workflow-implementation` paradigm references may constrain repair shape without transferring primary ownership.
- Review, test, and validation consumers preserve a Coordinator-registered Known Bug as `SKIP — excluded Known Bug <id>` for the current run without reopening it or expanding validation.
