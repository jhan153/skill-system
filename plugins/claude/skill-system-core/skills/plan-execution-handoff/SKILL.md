---
name: plan-execution-handoff
description: Create or update a canonical plan.md plus mutable handoff.md pair for durable single-node, decision-gated, multi-session, or multi-agent implementation work. Compile one typed risk-adaptive DAG—defaulting clear phase work to design/implementation → static review → human_test_ready and admitting explicit Test Design/Test Implementation nodes when selected—into a self-contained contract for an event-driven Orchestrator. Apply repeated-work principles only to an admitted verifier-steered graph. Do not use for direct one-session implementation, status-only reporting, polling, strict timing enforcement, or unrelated sibling scope.
disable-model-invocation: true
---

# Plan Execution Handoff

## Routing Card
- role: primary
- family: planning
- intent_signature: durable canonical Plan/Handoff pair with one typed graph archetype, bounded rewrites, and event-driven lifecycle coordination
- use_when: explicit pair, durable single-node execution, accepted repeated verifier-driven work, long-running DAG, phase-gated/risk-adaptive method selection, ownership/lock routing, or cross-session continuation
- do_not_use_when: direct implementation, status-only reporting, a small one-session short-term plan, lightweight one-off handoff, continuous polling, fixed/busy waits, or unrelated sibling scope
- expected_inputs: outcome, repository/plan identity, scope/approval, current baseline, graph-selection constraints, rough node timing, validation, and human boundary
- expected_outputs: validated canonical pair with one typed acyclic DAG, Core execution-item intake, implementation/review/repair gates, compact lifecycle state, and worker-done timing observations
- context_targets: request, repository rules, selected profile/reference, current source/callers, one disconfirming path, lifecycle capability, and resource stops
- risk_profile: writes only the requested planning pair; no production source, Git mutation, automatic coordinator polling, fixed/busy waits, external state, or invented model/skill substitutions
- entry_scene: PREPARE

## Outcome

Author the smallest self-contained `plan.md` plus `handoff.md` pair for durable work.
The Plan owns objective, scope, decisions, graph, validation, and termination; one
Coordinator/single-session owner writes current state and decisive evidence in Handoff.
After authoring, the Orchestrator executes the copied contract through the host. This skill
does not execute nodes, write production source, or require another runner/state artifact.
Direct one-session work bypasses this skill; lightweight coordination uses `plan-task-handoff`.

## Context Loading

Load by the decision being made, not by package inventory. Reuse already-read unchanged material;
on an update, refresh the affected rules and their dependent paths. New nodes, inputs, or failure
branches require the corresponding context before they become execution authority.

1. **Select the graph.** Read `references/graph-method-profiles.md` completely. Its common
   compilation rules, full Selection Gate, test authority, typed edges, and validation apply to
   every pair. Then read only the selected file under `references/graph-archetypes/`.
2. **Bind execution.** Read the common portion of `references/execution-profile.yaml` before
   `roles:`, then only the roles used by the selected DAG. Preserve all common lifecycle,
   approval-wait, timing, delivery-recovery, and resource safeguards. Skip only
   `human_test_transition` when the selected transition is not `next_waterfall`.
   Copy defaults using current-user override → canonical Plan copy → default profile precedence.
   Do not reinterpret models, efforts, unavailable capabilities, or existing copied profiles.
3. **Bind node semantics.** For every new or changed node, read the introduction and matching
   rows of `references/task-skill-routing.md`, even when its skill choice is obvious; those rows
   also own constraints on support skills and separate review nodes. Read the applicable stage
   contract below. Reuse only unchanged copied assignments; no node needs the full catalog.
   Node kind, positive output, selected skill, and Core result must agree before dispatch.
4. **Bind result handling.** In `references/execution_item_contract.md`, read Authority,
   Common Envelope, Core Markdown Cards, Coordinator Consumption, and Worker-Done Body.
   Then read each Item Kind and exact Core card reachable in the selected DAG, including
   authorized rewrite, failure, deferred, and terminal paths—not only results already received.
   A C → CR graph with bounded BF repair therefore includes implementation, review, deferred,
   repair, candidate, and final Known Bug handling before authoring finishes.
5. **Admit inputs when present.** On discovery, consumption, addition, or revision of persisted
   Planning inputs, read `references/execution_handoff_input_contract.md`: Package Root,
   Common Input Meaning, Plan Consumption, Freeze And Revision, and only the applicable
   Canonical Layout/Type Bindings rows. Read Inline Boundary when an inline result becomes a
   persisted input. With no such inputs, record `none`; do not create placeholders or load an
   unrelated input catalog. An answer arriving during execution still requires the declared
   Plan revision before a pinned decision or authority changes.
6. **Author and read back.** Read `assets/plan.md.tpl` and `assets/handoff.md.tpl`.
   Keep their sections and ledger columns; fill non-applicable sections/cells with `none`,
   replace every placeholder, remove unnecessary template commentary, and escape table-cell
   pipes as `\|`. Read `references/example/` only to resolve a remaining shape question.

Conditional details stay conditional:

| Selected scope | Additional reference and boundary |
|---|---|
| Verifier feedback will change later actions more than once | `references/repeated-work-principles.md`; ordinary phase work, static-review repair, single-node execution, or one final check does not trigger it. |
| Research nodes | `references/research_stage_contract.md`; bind each RES node to `workflow-research` plus exactly one accepted stage skill. |
| UI design, design-to-code, or Design evidence | `references/design_stage_contract.md`; admit only requested/accepted stages and evidence conditions. |
| Software Test Design/Implementation or conditional Test Discovery | `references/testing_stage_contract.md`; preserve TD/TI owners, human decision authority, and the input-revision gate. |
| Debugger, dump, dynamic diagnostic, concurrency trace, graphics/device-loss evidence | `references/runtime_debugging_contract.md`; DBG scope/operate keep identity, permissions, handback, and proof limits. |
| Required standard/strict assurance | `references/execution_assurance_contract.md` only when the owning node declares it or an accepted equivalent gate; no new graph node or owner. |

A stage output never creates its successor. Read only the admitted stage contract and kinds;
do not preload every domain. Copy the selected execution rules into the pair so its future
Coordinator needs no planning-skill reload. Links alone cannot replace dispatch, result intake,
failure, escalation, or termination instructions. Do not copy unused role catalogs or examples
into worker context.

## Core Cards

- records: `references/core-execution-items-v1/cards/design_result.md`, `references/core-execution-items-v1/cards/research_result.md`, `references/core-execution-items-v1/cards/debugging_result.md`, `references/core-execution-items-v1/cards/implementation_result.md`, `references/core-execution-items-v1/cards/test_design_result.md`, `references/core-execution-items-v1/cards/test_implementation_result.md`, `references/core-execution-items-v1/cards/code_review_result.md`, `references/core-execution-items-v1/cards/deferred_item.md`, `references/core-execution-items-v1/cards/bug_fix_result.md`, `references/core-execution-items-v1/cards/known_bug_candidate.md`, `references/core-execution-items-v1/cards/known_bug_record.md`
- produces after combining an eligible candidate with terminal review evidence: `references/core-execution-items-v1/cards/known_bug_record.md`

## Pair Identity And Scope

- Default pair: `docs/plans/<plan_id>/plan.md` and `handoff.md` in the target repository;
  an explicit user directory wins. `plan_id` matches `[A-Za-z0-9][A-Za-z0-9_.-]*`,
  equals the directory basename, names the scope, and never changes after creation.
- Resolve frontmatter `project` from the nearest manifest's `project_id`, otherwise the
  repository name. Never merge manifests or guess context paths.
- Persisted Planning inputs belong to that package's `inputs/` tree under their owning
  contract. Preserve existing inputs; do not create empty directories or duplicate copies.
- Before appending a follow-up, compare positive outcome, accepted implementation/method contract,
  production owner/boundary, execution DAG, and completion oracle/human judgment unit.
  Append only if all five stay the same. Otherwise create a sibling pair and record only
  `split from <plan_id>` in its Decision row; leave the old scope intact.
- An unexecuted BF node mislabeled against the pair's already accepted implementation objective
  may be corrected in the same pair before any source change or execution item exists.
  Revise kind, skill, Core output, and edges, record one Handoff Decision, and consume no attempt.
  Any actual scope/method change uses the five-axis gate.
- Preserve copied `v1`–`v5` contracts unless migration is explicitly accepted. Authoring never
  grants Git staging/commit, production, deployment, or external-state authority.

## Execution Safeguards

These are common to every selected graph, regardless of model or host:

- Compile one finite acyclic DAG from the fixed outer controls and one selected archetype.
  Every edge has one typed row; rewrites append unique nodes under the accepted budget.
  Keep role, node, agent, authority, lock, evidence, and context distinct. Never invent a hybrid
  to evade a disqualifier.
- Derive parallelism from dependencies and disjoint locks. Keep one production writer per
  checkout, fan in all required predecessors, and bind each node's output, validation owner,
  and stop/escalation. A worker cannot create nodes, select successors, or change the budget.
- First implementation or replacement of an accepted production mechanism is Implementation,
  even after a failure/review finding. BF preserves an already-implemented contract and owns
  only the assigned BF1/A1 or BF2/A2 node. A `repair_required` label is insufficient authority.
- Host worker automation owns dispatch input, inbox/follow-ups, heartbeat, and `worker_done`;
  require the start capability receipt. Unavailable lifecycle capability stays unresolved,
  never emulated by Coordinator polling.
- The Coordinator consumes only notified `question`, `escalation`, or `worker_done`, checks
  its own mailbox once, acknowledges, and stops. No worker-inbox reads, `check --wait`,
  heartbeat turns, or post-ack polling. Read compact results first and at most one relevant
  artifact slice when a decision still lacks evidence; no transcript/terminal/source replay.
- Normal completion requires `worker_done`. Confirmed delivery failure permits one bounded
  resend/reconciliation, then unresolved/blocked stop. Terminal idleness or elapsed time proves
  neither completion nor failure.
- A worker needing approval sends one question, finishes independent authorized work, and
  yields while passively resumable. Hours of human-response latency are normal, not timeout,
  failure, `worker_done`, or DAG-level `blocked`.
- Timing is `worker-done-observation-v2`: one rough expectation per node, start/finish clock
  reads, and one `on_track | overrun_observed | unknown` assessment when its result arrives.
  Missing/late timing never creates a deadline, retry, wait, or completion gate.
- Fixed/busy waits are forbidden. Sustained CPU/thermal pressure or a `kernel_task` spike
  permits one compact observation, then stop the wait/process loop and escalate without retry
  or an invented cause.
- Fresh independent review requires explicit user or higher-priority contract authority;
  assurance is attached evidence handling, never another owner/node. Existing mandatory
  static review and condition evidence remain required.

## Authoring Workflow

1. Bind outcome, scope/non-goals, requested approval boundary, success authority, and pair identity.
   Read repository instructions, branch/HEAD/dirty ownership, canonical path/callers, and one
   disconfirming path once. Do not duplicate future worker analysis for liveness.
2. Apply Scope Admission. Select the graph using the full comparison gate, its falsifier,
   disqualifiers, rewrite budget, test authority/transition, and rough timing. A
   `single_node_execution` has exactly one executable owner after baseline; a new mandatory
   owner/review/repair/feedback graph requires a new appropriate pair.
3. Follow Context Loading for every admitted node, input, and possible result path. Proposed,
   unanswered, open, assumed, or unshaped inputs remain visible and non-authoritative.
   Resolve only decisions that still prevent a correct pair.
4. Compile nodes and typed edges. Check positive-output/skill/result agreement, dependency and
   lock safety, failure routes, and validation/termination authority. Copy only used roles and
   the selected execution contract into the templates. Worker handoffs carry the positive
   objective, canonical skill IDs, bounded context, and output/stop terms—not full history.
5. Keep normative topology and pinned input authority in Plan; one owner records Task State,
   latest evidence, questions, timing, deferred carry, and next existing node in Handoff.
   Update Plan before synchronizing a changed topology/input. Preserve unresolved evidence
   when compacting superseded rows.
6. Read the completed pair back once against `Plan Authoring And Validation Boundary` in
   `graph-method-profiles.md` and the templates: identity/sections/placeholders, pair agreement,
   reachability/acyclicity, unique IDs and typed edges, node/Task State/timing coverage, exact
   Core card rows, kind/skill/output agreement, and selected Human Test transition.
   Correct observed mismatches. Structural agreement never proves design, evidence sufficiency,
   lock correctness, timing realism, or product completion.

## Result Intake And Closure

Copy the applicable Core transitions into the pair before execution. The Coordinator records exact
Core rows in existing Handoff tables, not wrappers, a second ledger, or rewritten worker narratives.
A result never grants graph authority.

- Preserve `deferred_item` in its declared Human Test/next-design/next-worklist destination and
  continue through an existing edge. Ordinary advice creates no extra work.
- After the terminal bounded repair review still requires repair, combine the eligible candidate
  and terminal evidence into `known_bug_record`. A repair task can be bookkeeping-complete while
  its condition stays `excluded_known_bug`; this is neither fixed nor a pass. Current-run
  consumers report `SKIP — excluded Known Bug <id>`, retain its reopen condition, and follow
  the existing successor/terminal node without another repair, wait, or global block.
- `phase_gate_delivery` uses `human_handoff` + `next_waterfall` and terminates at
  `human_test_ready`. Include the full Human Test Transition, close the pair, and stop.
  Later Test results plus new worklist/design create a fresh pair; they never reopen this one.
- A batch, plan document, interface, mock, or maker-authored check does not establish broader
  completion. Keep every material condition evidenced, human-owned, or explicitly unresolved;
  an independent review does not replace matching condition evidence.

Keep pair frontmatter status to `proposed | approved | in-progress | blocked | complete |
superseded` and Task State to `pending | in progress | complete | blocked`. Use repository
result labels when declared, otherwise `agent-verified` for evidenced machine conditions,
`user-verification-needed` for human-owned checks, `unverified` for unavailable evidence,
and `blocked` only when no required runnable work remains without external input.

## Artifact And Output Budget

Create only the pair by default. Add a non-authoritative `reference.md` only when large
technical material would obscure it; add a decision map only for independently dependent open
decisions. Do not create placeholder inputs, README, changelog, registry, event log, retrospective,
or duplicate summaries. Store intended verifiers and latest decisive results, not retries/logs.

Return the pair paths, status/scope decision, selected profile/archetype and material overrides,
open authority/input/lifecycle gaps, decisive readback, and next owner/action. Include Human Test
readiness and timing only when material.

## Task Cases

- **Positive:** clear C → CR phase work reads the common graph/profile rules, its phase archetype,
  and every authorized repair/deferred/terminal result kind; it skips unrelated Research,
  Design, and Test payloads while producing a self-contained pair.
- **Positive:** one durable single-owner node needs no role catalog, other archetype examples,
  or absent Planning input inventory. It still keeps capability, ownership, failure, and
  completion safeguards.
- **Negative:** a request described as incremental hides schema/data migration. The full
  Selection Gate exposes the controlled-transition requirement before graph selection.
- **Edge:** an approved TD node receives a new human oracle answer. Re-enter input authority
  and freeze/revision rules before resuming; a newly written answer file is not approval.
