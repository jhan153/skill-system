---
name: workflow-bug-fix
description: Repair one concrete defect in an already-implemented accepted production contract with proportional diagnosis, bounded contract-preserving interventions, original-signal observation, actual-path readback, and visible attempt status. Do not use for first implementation or explicit replacement of a production algorithm, model, backend, canonical data/ownership flow, or other production mechanism, even when a current failure motivated it. In Plan DAG mode, BF1 or BF2 owns exactly one semantically admitted assigned round; standalone continuation requires new causal evidence or material progress supporting the next intervention under the same accepted repair contract.
---

# Workflow Bug Fix

## Routing Card
- role: primary
- family: workflow
- intent_signature:
  - bug/failing-test/build/runtime/regression fix; broken behavior repair
- use_when:
  - the user requests a bounded repair of an observed or reproducible defect in an already-implemented accepted production contract and expects verification afterward, whether the cause is known or still needs proportional diagnosis.
  - a Plan/Coordinator dispatches an explicit `BF1` or `BF2` node with `node_id`, `round`, `source_review_item_ref`, concrete source findings, and an accepted repair contract that the intervention preserves.
  - a direct standalone repair under the same accepted repair contract resumes when the local review supplies new causal evidence or material progress supporting a distinct next intervention within any user-supplied budget.
- do_not_use_when:
  - diagnosis-only with no repair request, full static code review/disposition, Plan or Handoff mutation, successor selection, a Known Bug already excluded for the current run, first implementation or explicit production-mechanism replacement, an unresolved algorithm/model/behavior decision, ordinary feature work, or validation-only work.
- expected_inputs:
  - observed symptom/original signal, already-implemented accepted repair contract, material expected condition, available oracle or canonical source, reproduction context, genuine same-contract attempt history, and, in DAG mode, assigned node/round/source-review identity plus concrete findings
- expected_outputs:
  - after semantic admission, DAG mode returns one `bug_fix_result` with attempt history, changed snapshot/review anchor or explicit no-change result, original-signal observation, actual-path readback, visible attempt status, and an optional non-final Known Bug candidate; standalone mode returns compact task-local attempt evidence and unresolved conditions without Core cards; on owner-kind mismatch, no card or attempt
- context_targets:
  must_read:
    - original failure, material expected condition, implicated production owner/path, and repository instructions
  read_if_needed:
    - canonical input/source, caller/state flow, boundary readback, existing tests, config/manifests, and validation contract
    - `references/database_persistence_transparency_contract.md` when the bounded repair changes database schema, ORM/ODM mapping, query, migration, transaction, or data-access-boundary behavior
    - `references/identifier_readability_principle.md` when the assigned failure or review finding is an identifier-readability defect, or the bounded intervention must rename a related identifier set
    - `workflow-implementation` paradigm references as non-owning shape context only after semantic admission confirms that the accepted production contract stays unchanged
    - `references/execution_item_contract.md` in DAG mode or whenever a repair result/candidate crosses a Workflow, Coordinator, Plan/Handoff, or plugin boundary
    - `references/runtime_debugging_contract.md` when a supplied `debugging_result` must be consumed or the repair diagnosis uses a debugger, crash/core/minidump, symbols/unwind, dynamic diagnostics, concurrency trace, graphics capture, or device-loss artifact
    - select only the matching detailed runtime lane: `references/runtime-debugging/debugging-signal-and-causal-loop.md`, `references/runtime-debugging/live-debugger-operation.md`, `references/runtime-debugging/crash-dump-symbols-and-unwind.md`, `references/runtime-debugging/dynamic-temporal-and-concurrency-debugging.md`, or `references/runtime-debugging/graphics-debugging.md`
    - `references/causal-diagnosis.md` when the cause is unclear, recurring, intermittent, high-risk, or needs a discriminator before repair
    - `references/attempt-and-known-bug.md` whenever a prior repair attempt exists or the bug sits inside a graph/handoff
    - `references/execution_assurance_contract.md` when a repair has material maker/checker separation or destructive, auth/security, schema/data, infrastructure, external-write, or broad-refactor risk
  do_not_load_by_default:
    - full repo/memory, broad reports, unrelated history, raw production data, or credentials
- risk_profile:
  reads: failure output, production source/callers/state, tests/config, and validation/readback evidence
  writes: DAG mode exactly one semantically admitted contract-preserving intervention; standalone mode evidence-gated bounded interventions for the same problem and accepted repair contract within any user-supplied budget
  tools: reproduction, focused diagnostics, diff inspection, one original-signal observation after an intervention, and actual-path readback
  sensitive_resources: deny credentials; external or destructive reproduction needs explicit boundary review
- entry_scene:
  - PREPARE

## Core Cards

- produces in DAG mode: `references/core-execution-items-v1/cards/bug_fix_result.md`, `references/core-execution-items-v1/cards/known_bug_candidate.md`
- consumes: `references/core-execution-items-v1/cards/code_review_result.md`, `references/core-execution-items-v1/cards/debugging_result.md`

## Semantic Admission And Misroute Exit

Classify the positive production output before the symptom, failing condition, review disposition,
attempt history, or `BF1`/`BF2` label and before any edit. Structural Plan authorization is not
semantic admission. Admit Bug Fix only when an already-implemented accepted production contract
exists and the requested intervention restores that contract without first establishing or
replacing its accepted algorithm, model, backend, canonical data/ownership flow, or other
production mechanism.

- In DAG mode, a node whose positive output is first implementation or explicit production-mechanism
  replacement emits one lifecycle escalation with `result: not_produced` and the owner-kind
  mismatch. Make no source change, emit no Core card, and consume no A1/A2 attempt. The worker never
  selects a `C` successor or edits Plan/Handoff.
- In direct mode, return the mismatch to the current task owner for unambiguous Implementation or
  decision routing without consuming an attempt.
- A current failure, `repair_required` disposition, prior attempt count, or BF node label alone is
  insufficient. An optional reviewer solution is non-normative and never authorizes a broader
  replacement.

## Completion And Evidence
- Bind each material condition to its authority and evidence. A user/canonical contract or production observation can define expected behavior; an agent-authored test can preserve that expectation but is not an independent oracle.
- Fix and read back the actual production path. Structural checks, command exit, mocks, interfaces, and test passes prove only what they directly cover; they cannot establish a broader semantic result.
- A required `fail`, `needs_review`, blocked, or unverified condition stays unresolved until evidence from that same condition resolves it. Do not report complete or agent-verified from a narrower pass.
- Source selection, migration, media/data transformation, and external boundaries require canonical-input identification plus actual selected/output readback. Missing or mismatched canonical input fails closed; never substitute legacy data silently.
- A review or test is an observation surface, not an unquestionable oracle. When evidence shows the test or harness contract is wrong, repair that owner directly; never expand validation merely to keep the bug-fix loop alive.
- Apply `references/execution_assurance_contract.md` only for its additional independent pass or rollback/readback evidence. It never adds a repair round, resets attempt history, or becomes another repair owner.

## Mode And Attempt Boundary

Use `references/attempt-and-known-bug.md` for repair-specific identity, attempt rows, result
classification, and candidate fields. In DAG mode, use the Core-owned
`references/execution_item_contract.md` for cross-owner envelopes and Coordinator consumption.

- **DAG mode:** after semantic admission, when Plan fields `node_id`, `round`, and `source_review_item_ref` are supplied, own exactly that `A1` or `A2` intervention and return. `A1` requires concrete `CR0 repair_required` findings and an assigned `BF1`; `A2` requires concrete `CR1 repair_required` findings and an assigned `BF2`. Preserve the accepted copied graph's finite budget. Never begin another round inside the same invocation, extend the graph, or switch to standalone mode to evade that budget.
- **Standalone mode:** without those Plan fields, locally review each bounded intervention before another. Apply the evidence-gated continuation and stop rules in `references/attempt-and-known-bug.md` under the same problem, scope, accepted repair contract, and any user-supplied budget. Attempt count alone neither authorizes another intervention nor ends a progressing repair. Keep ordinal task-local attempt rows; do not map them to DAG `A1`/`A2` cards.

A repair intervention is one code, configuration, test, or harness change intended to alter the assigned failure while preserving the accepted repair contract. Diagnostic observations, unchanged reruns, and owner-kind corrections do not consume a round. `resolved`, `narrowed`, `moved`, `unchanged`, and `unreproducible` describe the attempt observation only; they authorize no DAG action.

In DAG mode, full source-derived path/model/baseline review and `pass | repair_required | complete_with_deferred_items` disposition belong to `workflow-code-review`. This workflow checks only diff churn, the original signal once after an intervention, actual-path readback, and attempt classification. A changed result returns a `changed_snapshot` and `review_anchor`. A no-change or unreproducible result returns `postcondition: no_change_unresolved` without manufacturing an empty review cycle.

## Implementation Shape Invariants
- Fix the complete evidenced cause with the least conceptual machinery, not the smallest diff. A direct change may update every in-scope producer/consumer required to remove the cause.
- Give each internal concept one canonical contract, representation, state machine, and policy owner. On mismatch, migrate all in-scope participants; do not add an adapter, bridge, proxy, shim, dual model, or fallback to preserve the disagreement.
- Prefer plain functions, values, concrete types, direct calls, existing primitives, and composition. Reject Clean Code-style class/interface/function fragmentation, mock-created seams, forwarding layers, and speculative factories/registries/frameworks.
- Interface/inheritance/proxy is a rare present runtime exception. An unmodifiable external edge may use only thin stateless validation/translation to one canonical value or typed failure, with no domain policy or hidden state.
- Preserve every explicit user/canonical paradigm and shape condition. A paradigm label without observable state/data/effect/dispatch/construction rules remains an unresolved requirement rather than permission to improvise.
- When `references/database_persistence_transparency_contract.md` is active, preserve accepted `source_of_truth`, database boundary/model, read/write effects, consistency/transaction, and lifecycle. This workflow owns only the bounded repair and matching original-signal/actual-path readback; a new source, database policy, or ownership decision remains unresolved outside the repair.

## Workflow
1. Run Semantic Admission before selecting DAG or standalone mode. Bind the problem identity, original signal, accepted repair contract, expected result/authority, genuine same-contract attempt history, and any supplied node/round/source-review fields. Do not reset genuine history after retrigger or compaction, and do not carry it into a newly accepted production-mechanism replacement.
2. In DAG mode, refuse an unassigned round, a `BF1/A1` dispatch lacking concrete `CR0 repair_required` findings, or a `BF2/A2` dispatch lacking concrete `CR1 repair_required` findings. Return the missing authorization without editing.
3. Trace the actual entry, production owner, state/data flow, canonical source when relevant, and one representative boundary/readback. Read `references/causal-diagnosis.md` only when a bounded discriminator is needed. When runtime artifacts or a supplied `debugging_result` are material, apply `references/runtime_debugging_contract.md` plus only the matching detailed runtime lane, validate target/build/symbol/capture identity before causal use, and preserve its scope, session handoff, perturbation, causal status, and proof ceiling. This remains diagnosis inside the same repair owner and consumes no repair round until an intervention is made.
4. Select one evidenced cause and one direct canonical intervention. Keep source/policy/fallback decisions at their domain owner and update every in-scope participant required by that cause. Never weaken assertions, skip checks, widen mocks, add bypasses, or substitute a plausible fallback. When `references/identifier_readability_principle.md` is active, change only the assigned identifier set and required callers, preserve higher-priority naming authorities, and return static disposition to `workflow-code-review` without inventing a spelling rule.
5. Inspect the resulting diff. If a repair was applied, capture `changed_artifacts`, `changed_snapshot`, and a `review_anchor`; observe the original signal once and read back the actual affected path. If no meaningful change remains or the signal is unavailable, record the exact no-change or unreproducible evidence instead.
6. Append the assigned DAG or ordinal standalone attempt row and classify `attempt_status` as `resolved`, `narrowed`, `moved`, `unchanged`, or `unreproducible`. Preserve each intervention identity and decisive evidence in compact rows; create no new history artifact by default.
7. In DAG mode, return immediately with the structured result. After `A2`, include only a non-final Known Bug candidate when the attempt ledger can support later Coordinator consumption. In standalone mode, perform the bounded local review and apply the continuation gate before another intervention. Stop on resolution, exhausted user budget, unavailable required observation, or no new evidence supporting a distinct next intervention; return any remaining condition as task-local unresolved work without automatic Known Bug registration.

## Output Contract
After semantic admission, DAG mode returns exactly one canonical Core `bug_fix_result` item and, when applicable, a separate `known_bug_candidate` item referenced by ID. A semantic mismatch returns lifecycle `not_produced` with no Core item or attempt. `references/attempt-and-known-bug.md` owns repair-specific writing rules, not DAG payload shape. When the database contract is consumed, carry its material conformance in the changed snapshot and actual-path readback instead of adding a new envelope. Do not add Plan/Handoff edits, a review disposition, or any successor/terminal field. Standalone mode returns task-local scope, compact ordinal attempt evidence, changed snapshot/source refs, original-signal observation, actual-path readback, continuation or stop reason, and remaining conditions. It emits no Core repair/Known Bug cards, creates no history artifact by default, and never turns an unresolved condition into an automatic exclusion or hidden completion.

## Cross-Skill Boundaries
- A diagnosis-only request for an execution-ready debugging scope or using an existing/approved debugger, crash artifact, dynamic diagnostic, or graphics capture routes to `workflow-runtime-debugging`; simple source/log-only explanation stays with the current task owner. Neither starts this repair workflow or creates a repair round.
- A supplied task-local or Core `debugging_result` is evidence input, not another repair owner or permission to skip identity/scope checks. In DAG mode it never substitutes for the assigned node/round, `source_review_item_ref`, or concrete review findings required by this Workflow. A scope-only result authorizes no debugger operation beyond its recorded permission boundary. This Workflow may apply the shared runtime-debugging contract and one selected detailed lane internally when repair is primary, but it never auto-invokes Runtime Debugging.
- `workflow-code-review` owns full read-only static review and the `pass | repair_required | complete_with_deferred_items` disposition. This workflow supplies its changed snapshot/review anchor but never substitutes local checks for that review.
- Cross-owner repair, review, deferred, final Known Bug, and successor semantics come only from `references/execution_item_contract.md`; this skill does not restate or override them.
- `workflow-implementation` owns first implementation and explicit replacement of production algorithms, models, backends, canonical data/ownership flows, and implementation contracts, including when a current failure motivated that work.
- `analysis-boundary-design` supplies deep module, seam, and boundary decisions when needed; it does not replace `workflow-bug-fix` as owner of the concrete repair.
- `workflow-implementation` paradigm references may constrain an admitted repair shape without transferring primary ownership; a changed accepted production mechanism fails semantic admission instead.
- Review, test, and validation consumers preserve a Coordinator-registered Known Bug as `SKIP — excluded Known Bug <id>` for the current run without reopening it or expanding validation.
