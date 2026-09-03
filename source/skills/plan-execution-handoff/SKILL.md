---
name: plan-execution-handoff
description: Create or update a canonical plan.md plus mutable handoff.md pair for durable single-node, decision-gated, multi-session, or multi-agent implementation work. Compile one typed risk-adaptive DAG—defaulting clear phase work to design/implementation → static review → human_test_ready and admitting explicit Test Design/Test Implementation nodes when selected—into a self-contained contract for an event-driven Orchestrator. Apply repeated-work principles only to an admitted verifier-steered graph. Do not use for direct one-session implementation, status-only reporting, polling, strict timing enforcement, or unrelated sibling scope.
---

# Plan Execution Handoff

## Routing Card
- role: primary
- intent_signature: durable canonical Plan/Handoff pair with one typed graph archetype, bounded rewrites, and event-driven lifecycle coordination
- use_when: explicit pair, durable single-node execution, accepted repeated verifier-driven work, long-running DAG, phase-gated/risk-adaptive method selection, ownership/lock routing, or cross-session continuation
- do_not_use_when: direct implementation, status-only reporting, a small one-session short-term plan, lightweight one-off handoff, continuous polling, fixed/busy waits, or unrelated sibling scope
- expected_inputs: outcome, repository/plan identity, scope/approval, current baseline, graph-selection constraints, rough node timing, validation, and human boundary
- expected_outputs: validated canonical pair with one typed acyclic DAG, Core execution-item intake, implementation/review/repair gates, compact lifecycle state, and worker-done timing observations
- context_targets: request, repository rules, selected profile/reference, current source/callers, one disconfirming path, lifecycle capability, and resource stops
- risk_profile: writes only the requested planning pair; no production source, Git mutation, automatic coordinator polling, fixed/busy waits, external state, or invented model/skill substitutions
- entry_scene: PREPARE

## Outcome

Create the smallest governed execution package that separates:

- `plan.md`: canonical objective, scope, decisions, behavior, DAG, routing, validation, and
  termination.
- `handoff.md`: current baseline, assignments, decisions, task state, observed evidence, and
  next ownership.

Use this only above the one-session/lightweight tier. `plan-task-handoff` owns lightweight
coordination. This skill authors the pair and stops; after approval, the Orchestrator follows the
copied DAG and its Coordinator contract while recording mutable state in `handoff.md`. No parallel
state runner is required. Planning writes the pair only, never production source.

## Required Resources

Read these files completely before generating or updating a pair:

1. `references/execution-profile.yaml` for the `plan-handoff-v6` method, typed advisory timing, and event-driven
   lifecycle defaults, agents, models, effort, and role boundaries.
2. `references/graph-method-profiles.md` for archetype selection, examples, typed edges, graph
   compilation, and static-validation rules.
3. `references/task-skill-routing.md` for DAG-node skill examples and routing caveats.
4. `references/execution_item_contract.md` for the Core-owned cross-Workflow result cards,
   ownership boundary, deferred-item carry, bounded repair intake, and Coordinator transitions.
5. `references/execution_handoff_input_contract.md` for package-local Planning input paths,
   status/authority rules, Plan consumption, and freeze/revision behavior.

Read `references/repeated-work-principles.md` only for an admitted graph whose verifier feedback is
expected to change a later action more than once. Do not load it for ordinary Waterfall/phase work,
bounded static-review repair, single-node execution, or one-final-check work.

Read `references/research_stage_contract.md` only when the requested DAG includes one or more
Research stages. Include only explicitly requested stages or stages already accepted by the Plan;
bind each `RES-*` node to `workflow-research` plus one exact stage skill. An upstream Research
artifact never creates the next node automatically.

Read `references/design_stage_contract.md` only when the requested DAG includes UI design,
design-to-code implementation, or Design evidence nodes. Include only stages and evidence
conditions explicitly requested or already accepted by the Plan; a Design artifact or gate result
never creates the next node automatically.

Read `references/testing_stage_contract.md` only when the requested DAG includes software Test
Design, Test Implementation, or a conditional Test Discovery decision. Bind `TD*` and `TI*` nodes
to their exact Testing Workflow owners, preserve Test Discovery as Planning support rather than a
DAG node, and keep agent-machine test evidence separate from Human Test authority.

Read `references/runtime_debugging_contract.md` only when an accepted `DBG0` debugging-scope node,
`DBG1` runtime-operation node, or test condition explicitly requires a debugger session, crash
artifact, dynamic diagnostic, concurrency trace, graphics capture, or device-loss artifact. Bind
both node modes to `workflow-runtime-debugging`. Each graph-mode node returns one Core
`debugging_result`, never edits Plan/Handoff, selects a successor, or turns a captured artifact into
repair authorization.

Read `references/execution_assurance_contract.md` only when the Plan or user requires
`assurance: standard | strict` on an owning node whose primary contract declares that local
reference or an accepted equivalent gate. Assurance changes evidence handling, not graph topology,
production ownership, Core Card identity, or successor selection.

Use `assets/plan.md.tpl` and `assets/handoff.md.tpl` as the minimum output shape;
`references/example/` holds one minimal valid pair for shape reference. Replace every
placeholder and delete template commentary the task does not need, but keep every section
heading; fill a non-applicable section or cell with `none` instead of deleting it. Escape a
literal `|` inside a table cell as `\|`.

## Core Cards

- records: `references/core-execution-items-v1/cards/design_result.md`, `references/core-execution-items-v1/cards/research_result.md`, `references/core-execution-items-v1/cards/debugging_result.md`, `references/core-execution-items-v1/cards/implementation_result.md`, `references/core-execution-items-v1/cards/test_design_result.md`, `references/core-execution-items-v1/cards/test_implementation_result.md`, `references/core-execution-items-v1/cards/code_review_result.md`, `references/core-execution-items-v1/cards/deferred_item.md`, `references/core-execution-items-v1/cards/bug_fix_result.md`, `references/core-execution-items-v1/cards/known_bug_candidate.md`, `references/core-execution-items-v1/cards/known_bug_record.md`
- produces after combining an eligible candidate with terminal review evidence: `references/core-execution-items-v1/cards/known_bug_record.md`

## Pair Location and Identity

- Default location: `docs/plans/<plan_id>/plan.md` plus `handoff.md` inside the target
  repository; an explicit user-provided directory overrides the default.
- Related persisted Planning artifacts live only under the same directory's `inputs/` tree from
  `execution-handoff-inputs-v1`. A pre-execution Planning skill may have created that tree before
  the pair exists; preserve it and never create duplicate global copies.
- `plan_id` matches `[A-Za-z0-9][A-Za-z0-9_.-]*`, equals the pair directory basename, names
  the scope rather than a date, and never changes after creation.
- A sibling pair is a sibling directory with its own `plan_id`.
- Resolve the `project` frontmatter field from the nearest `project-context.yaml`
  `project_id`; when none is declared, use the repository name. Do not merge parent
  manifests or guess paths.
- Creating or updating the pair never authorizes Git staging, commits, or history changes.

## Scope Admission Gate

Before adding any follow-up to an existing plan, compare five axes:

1. positive outcome;
2. accepted implementation/method contract, including a selected algorithm, model, backend, or
   canonical production flow;
3. production owner and boundary;
4. execution DAG;
5. completion oracle and human judgment unit.

Append only when all five remain the same. If any axis changes materially, create a sibling
Plan/Handoff pair. Never append a request merely because it concerns the same product, module,
or release number. Record only the split provenance
(`split from <plan_id>`) as one Decision row in the new handoff without importing the
rejected topic's narrative; do not contaminate the old plan with the rejected topic or an
instruction to ignore it.

Before dispatching or appending a BF node, classify the positive production output against the
accepted implementation/method contract. First implementation or explicit production-mechanism
replacement is a `C` Implementation node even when a failure, review finding, or prior attempt
motivated it. BF owns only a bounded repair that preserves an already-implemented accepted contract.

If an unexecuted node was mislabeled BF although the pair's original accepted objective already
requires Implementation, treat the correction as Plan authoring rather than follow-up scope: before
dispatch, revise the current pair's node kind, selected skill, Core output, and edges, record one
Handoff Decision, and consume no repair attempt. This same-pair exception requires no source change
and no execution item from the mislabeled node. After either exists, or when the accepted objective
or method contract actually changes, apply the normal five-axis gate and create a sibling when any
axis differs.

## Graph Method Selection And Compilation

Read `references/graph-method-profiles.md` and select exactly one archetype. Durable work with one
executable owner and no inter-node dependency uses `single_node_execution`. Clear multi-phase work
defaults to `phase_gate_delivery`; uncertainty, paired assurance, real incremental fan-out, or
persistent-state transition selects the corresponding alternative only when its hard condition
is present.

For admitted repeated work, apply `references/repeated-work-principles.md` and choose the
archetype from the actual uncertainty/dependency/assurance/transition condition; `/goal` or
`loop` wording never selects an archetype by itself.

Keep the outer controls fixed and compile a finite acyclic inner DAG. Every Mermaid edge has one
typed row; dynamic continuations and repairs append unique nodes under budget. Role, node, agent,
authority, lock, evidence, and context remain distinct. Return an unresolved selection instead of
inventing a hybrid.

For `phase_gate_delivery`, require `test_authority: human_handoff` and
`test_transition: next_waterfall`. End at `human_test_ready`, close the old pair, and use the
later Test result plus new worklist/design to create a fresh `plan_id`.

## Runner Independence

The generated Plan/Handoff pair is the self-contained execution contract and only execution state.
`plan-execution-handoff` does not run its nodes. After authoring, the Orchestrator applies existing
typed edges, consumes compact node results, updates `handoff.md`, and dispatches the next runnable
node through the available host orchestration capability.

- Do not require or attach an external task/plan runner or ledger skill to operate the pair.
- A legacy pair that already copied a runner skill keeps that historical routing until explicitly
  migrated; new pairs omit it. The runner was procedural guidance, never the host execution engine.
- A host such as Orca supplies dispatch and lifecycle delivery; it does not become a second
  execution-state owner.
- `single_node_execution` contains one executable work node after its baseline. The same
  Plan/Handoff state supports pause/resume without a parallel state projection.
- If the work later requires another independent owner, mandatory review/repair node, fan-out, or
  feedback-driven expansion, it no longer satisfies the single-node archetype. Apply Scope
  Admission and select an appropriate new pair rather than silently adding a runner.
- Execution assurance attaches to an owning node under `references/execution_assurance_contract.md`
  and never becomes a graph node or successor selector.

## Advisory Timing Observation

Use `worker-done-observation-v2` from `execution-profile.yaml`. Give each node one rough
expectation. The worker reports typed start/finish/elapsed once in `worker_done`; the Coordinator
records `on_track`, `overrun_observed`, or `unknown`. Timing is advisory only: never create a
deadline, timeout, retry, monitor, sleep, poll, or completion gate. Carry forward only a material
planning note, and close timing with the pair at `human_test_ready`.

## Workflow

1. Bind outcome, repository, scope/non-goals, approval boundary, plan identity, success authority,
   and the associated package-local input artifacts.
2. Read instructions, branch/HEAD/dirty ownership, canonical path/callers, and one disconfirming
   path once. Do not duplicate worker analysis for liveness.
3. Run Scope Admission and choose create, update, or sibling. Preserve `v1`–`v5` pairs unless an
   explicit migration is accepted.
4. Apply `execution-handoff-inputs-v1`: record every available input's path, status, authority,
   and consumed scope; keep proposed, unanswered, open, assumed, or unshaped material visible but
   non-authoritative. Then select one archetype, its falsifier, test transition, rewrite budget,
   and rough node timing. Resolve only a still-open decision with its narrow specialist.
5. Compile the fixed control graph and selected inner graph into a typed acyclic DAG; apply the
   Implementation-versus-repair semantic gate, then bind node context, executor, lock, output,
   validation owner, timing, and stop condition.
6. Build `plan.md` and `handoff.md` from their templates. Keep normative topology in the plan and
   mutable state/latest evidence in the handoff.
7. Apply `task-skill-routing.md` and the event/timing profile so the copied pair gives the future
   Orchestrator a self-contained compact dispatch and result-consumption contract.
8. Read the completed pair back once. Confirm frontmatter identity, required sections, Plan/Handoff
   agreement, unique node IDs, a finite acyclic DAG, one typed row per edge, Task State coverage,
   Core Card table shape, the selected Human Test boundary, and that every executable node's
   positive output matches its kind, selected skill, and Core result type. In particular, no BF node
   may first establish or replace a production implementation contract. Correct observed structural
   or owner-kind mismatches; semantic quality, evidence sufficiency, and timing realism remain owner
   judgments rather than machine-validator claims.

## Artifact Minimality

This skill creates only `plan.md` and `handoff.md` by default. Preserve package-local inputs that
already exist, but never manufacture empty `inputs/` directories or placeholder Planning files.

- Add `reference.md` only when formulas, algorithm cards, or large non-normative technical
  material would obscure the plan. State that it has no decision authority.
- Add a decision map only when several independent unresolved decisions have separate
  prerequisites or downstream gates. Keep one ordinary open decision in `plan.md`.
- Do not create README, changelog, registry, event log, retrospective, or duplicate summary.

## Plan Contract

Keep the plan stable and source-anchored. Keep every template section heading required by the pair
contract and fill a non-applicable section or cell with `none`. The plan carries:

- positive outcome, non-goals, and do-not-touch;
- current-source baseline and source references;
- consumed Planning input paths, statuses, authority/owners, source refs, and exact consumed scope;
- admitted scope and sibling-plan exclusions;
- accepted implementation/method contract and its authority, including any selected production
  algorithm, model, backend, or canonical flow;
- selected method profile/archetype, selection evidence, checked disqualifiers, rewrite budget,
  fixed outer control, dynamic-inner-graph rule, and test authority;
- selected owner/boundary and observable behavior contracts;
- finite acyclic Task DAG, typed edges, node kinds, context inputs, execution routing, locks,
  outputs, rough expected timing, validation owners, and stop conditions;
- explicit runner independence and, when selected, one executable work node for
  `single_node_execution`;
- worker-done timing observation policy and the current assessment per node;
- event-only Coordinator wake rules, compact result intake, lifecycle recovery, and resource
  stop conditions;
- validation matrix, qualitative judgment boundary, termination, and implementation approval.

Plans store intended verifiers and latest decisive results, not raw logs, retries, or test counts.
A build or plan document never establishes qualitative product completion.

## Handoff Contract

Keep the handoff subordinate to the plan:

- One Coordinator/single-session owner writes it; workers report compact bodies.
- Snapshot baseline without Git mutation; append corrections and compact only superseded rows
  while preserving open risks and latest evidence.
- The plan owns profile, topology, typed edges, and rewrite budget. Update it before synchronizing
  Task State; the handoff never rewrites graph grammar alone.
- Track every task as `pending`, `in progress`, `complete`, or `blocked`, with one matching typed
  Timing Observations row updated only from `worker_done`.
- Consume `design_result`, `research_result`, `debugging_result`, `implementation_result`, `code_review_result`, `deferred_item`,
  `bug_fix_result`, and `known_bug_candidate` according to
  `references/execution_item_contract.md`. Record each item with
  its exact `## Core Cards` row template in the matching existing Handoff ledger table, not a local
  wrapper or reinterpreted worker prose. The Coordinator fills the row from the compact worker
  result; no separate writer, renderer, or card store exists.
- When the terminal bounded review remains `repair_required`, combine its findings with the
  candidate and record the final `known_bug_record`. Mark the repair task `complete` for execution
  bookkeeping and the unresolved condition `excluded_known_bug`; this is not a pass or blocker.
- Preserve review `deferred_item` cards in the Human Test, next-design, or next-worklist destination
  declared by the card while continuing through an existing Plan edge.
- Record actionable questions, escalations, outcomes, evidence, user checks, risk, and one next
  owner—not heartbeats, transcripts, raw terminal output, or repeated source/diff/status dumps.
- At `human_test_ready`, include the complete Human Test Transition, close the pair, and place
  later Test results/worklist/design in a fresh pair. Broader product status remains
  `user-verification-needed`.

Do not restate the full plan. Do not promote planning, interfaces, mocks, or maker-authored checks
into implementation completion.

## Event-Driven Coordination And Resource Safety

`execution-profile.yaml` owns the detailed lifecycle and resource policy. Non-negotiables:

- Worker automation handles dispatch input, its inbox/follow-ups, heartbeat, and `worker_done`;
  unavailable capability stays unresolved and is never emulated by Coordinator polling.
- The Coordinator wakes only for notified `question`, `escalation`, or `worker_done`, checks its
  own mailbox once, acknowledges, and stops. Heartbeat turns, `check --wait`, and post-ack polling
  are forbidden.
- Consume the compact body first; read one relevant artifact slice only if the decision otherwise
  cannot be made. Never use worker transcript replay or repeated terminal/source/diff/plan dumps.
- `worker_done` is the normal completion signal. Confirmed delivery failure permits one bounded
  resend/reconciliation, then unresolved/blocked stop.
- A worker needing approval sends one `question`, continues independent authorized work, and yields
  its active turn while remaining passively resumable. A response hours later is normal; pending
  response is not `worker_done`, timeout, failure, or DAG-level `blocked`.
- Fixed/busy waits are forbidden. On sustained CPU/thermal pressure or `kernel_task` spike,
  capture one observation, stop, and escalate without inferring cause or retrying.
- Add fresh independent review only when the user or a higher-priority accepted contract requires
  it.

## Execution Routing Contract

Use `plan-handoff-v6`; copied routing in older pairs remains canonical. Instantiate only DAG roles,
keep one production writer, preserve plan/user decision authority, and never substitute unavailable
models or skills. The Orchestrator follows the copied Plan/Handoff contract directly; its
Coordinator role needs no planning or runner skill unless a node-specific support question is
separately declared.

Every node records task/kind/dependencies, typed edges, role/agent, model/effort, selected skills,
minimum context, rough timing, lock, output, validation owner, and stop/escalation. Inherit role
defaults unless overridden. Copy the positive objective and this bounded contract to the worker;
do not send unrelated history or make it rediscover selected skills. Use
`references/task-skill-routing.md` for intent-matched examples.

Before dispatch, compare that positive objective and accepted implementation/method contract with
the node kind, selected skill, and expected Core result. Those semantic authorities outrank the node
ID. A mismatched BF node is corrected or escalated under Scope Admission before source work; the
worker does not reinterpret it as an attempt.

## Status and Evidence

Use repository-specific human-grade labels when provided. Otherwise distinguish:

- `agent-verified`: every material machine condition has direct matching evidence;
- `user-verification-needed`: the remaining oracle belongs to the user;
- `unverified`: evidence is unavailable but no required work is blocked;
- `blocked`: no required runnable work remains without external input.

Frontmatter `status` in both files uses exactly: `proposed`, `approved`, `in-progress`,
`blocked`, `complete`, or `superseded`. Handoff Task State status uses exactly: `pending`,
`in progress`, `complete`, or `blocked`. Resolve the plan template's `__HUMAN_GRADE_LABEL__`
from the repository's declared human-grade vocabulary; when the repository declares none,
use `user-verification-needed`.

Never mark a phase or plan complete from one completed batch. An independent review does not
replace condition evidence, and a codebase map does not itself produce a review verdict.
Known Bugs remain visible but are skipped by current-run review/test/validation as
`SKIP — excluded Known Bug <id>`. They do not trigger another repair, verifier expansion,
Coordinator wait, or global `blocked`; follow the next existing Plan edge. When no implementation
node remains, follow the Plan's existing terminal node, such as `human_test_ready`; never invent a
`partial_handoff` or another early-close state.
For `phase_gate_delivery`, current-plan completion is `human_test_ready`, immediately before Human
Test. Close the old handoff, stop without polling, and keep the broader product result
`user-verification-needed`. The user's later Test result, new worklist, and new design brief start
a new Waterfall; they never reopen the old pair.

## Output

Return only what is needed:

- created or updated artifact paths;
- plan status and scope-admission result;
- open decisions and approval state;
- execution-profile ID and material overrides;
- selected method profile/archetype and its falsifier;
- consumed input artifact paths/statuses and any unresolved non-authoritative input;
- selected test authority/transition and human-test-ready status when applicable;
- compact timing assessments and only material carry-forward notes;
- event-driven coordination mode and any unresolved worker-lifecycle capability;
- next owner and next task;
- validation result or exact unresolved check.
