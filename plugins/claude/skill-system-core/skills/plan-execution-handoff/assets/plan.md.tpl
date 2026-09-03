---
doc_type: orchestration_execution_plan
status: __STATUS__
canonical: true
plan_id: __PLAN_ID__
created_at: __DATE__
updated_at: __DATE__
project: __PROJECT_ID__
implementation_transition: user_approval_required
runtime_handoff: handoff.md
execution_profile: plan-handoff-v6
method_profile: risk-adaptive-development-v1
graph_archetype: __GRAPH_ARCHETYPE__
test_authority: __TEST_AUTHORITY__
test_transition: __TEST_TRANSITION__
timing_policy: worker-done-observation-v2
coordination_mode: event_driven
coordinator_observation: notification_only
---

# __TITLE__

## Canonical Contract

- This file owns the objective, scope, contracts, DAG, validation, and termination.
- `handoff.md` owns only current execution state, evidence, and the next owner.
- Planning does not authorize production writes.
- Cross-owner node results use `core-execution-items-v1`; no worker result owns Plan topology or
  a successor node ID.

## Positive Outcome

__POSITIVE_OUTCOME__

### Non-goals

- __NON_GOAL__

### Do not touch

- __DO_NOT_TOUCH__

## Scope Admission

Admit a follow-up only when positive outcome, accepted implementation/method contract, production
owner/boundary, execution DAG, and completion oracle all remain the same. Otherwise create a sibling Plan/Handoff pair.
At initial creation, record `initial creation` as the evidence on every axis.

An unexecuted owner-kind mislabel that contradicts this pair's already accepted positive outcome
may be corrected in this pair before dispatch only when the node has produced no source change or
execution item; update its kind, skill, Core output, and edges and consume no repair attempt. Any
actual outcome/method/owner/DAG/oracle change uses the normal table and a sibling pair.

| Axis | Evidence | Result |
|---|---|---|
| Positive outcome | __EVIDENCE__ | same / sibling |
| Accepted implementation/method contract | __EVIDENCE__ | same / sibling |
| Owner and boundary | __EVIDENCE__ | same / sibling |
| DAG | __EVIDENCE__ | same / sibling |
| Completion oracle | __EVIDENCE__ | same / sibling |

## Current-source Evidence

| Field | Observation |
|---|---|
| Workspace | __WORKSPACE__ |
| Branch / HEAD | __BASELINE__ |
| Dirty ownership | __DIRTY_STATE__ |
| Production path | __SOURCE_REFS__ |
| Disconfirming path | __COUNTEREXAMPLE__ |

## Input Artifacts

Record only package-local Planning artifacts that exist. `plan.md` consumes paths and selected
scope/IDs without copying full input content.

| Kind | Path | Status | Authority / owner | Consumed scope or IDs |
|---|---|---|---|---|
| __INPUT_KIND__ | __INPUT_PATH__ | __INPUT_STATUS__ | __INPUT_AUTHORITY__ | __INPUT_SCOPE__ |

## Boundary and Behavior Contracts

| ID | Required behavior or invariant | Authority / source refs |
|---|---|---|
| `B-01` | __CONTRACT__ | __AUTHORITY__ |

## Graph Method Profile

Select exactly one archetype from `risk-adaptive-development-v1`. Use
`single_node_execution` when one durable executable node needs the pair, or
`phase_gate_delivery` by default when multi-node design and sequential phase ownership are clear.

| Field | Decision |
|---|---|
| Method profile | `risk-adaptive-development-v1` |
| Selected archetype | `__GRAPH_ARCHETYPE__` |
| Test authority | `__TEST_AUTHORITY__`; `phase_gate_delivery` defaults to `human_handoff` |
| Test transition | `__TEST_TRANSITION__`; `phase_gate_delivery` requires `next_waterfall` |
| Selection evidence | __GRAPH_SELECTION__ |
| Disqualifiers checked | __GRAPH_DISQUALIFIERS__ |
| Graph rewrite budget | __GRAPH_BUDGET__; every expansion appends unique node IDs and keeps the compiled DAG acyclic |
| Fixed outer control | scope acceptance → method selection → static graph validation → execution approval → integration → verification → bounded repair → Known Bug carry-forward or close eligibility |
| Dynamic inner work graph | selected archetype only; __GRAPH_REWRITE__; no literal back-edge or unbounded hybrid graph |

## Execution Routing

Copy only the roles used by this plan from `plan-handoff-v6`. User overrides win.
Once copied, this table is canonical for this plan and is not changed retroactively by
later skill-profile revisions. DAG node rows inherit Model, Effort, and selected_skills
from their role row here; a node cell overrides only when it differs.

| Role | Agent | Model | Effort | Default selected skills | Boundary |
|---|---|---|---|---|---|
| __ROLE__ | __AGENT__ | __MODEL__ | __EFFORT__ | __SKILLS__ | __BOUNDARY__ |

## Event-Driven Coordination

| Control | Contract |
|---|---|
| Worker lifecycle automation | Required when available: dispatch input, inbox check, follow-up consumption, heartbeat, and `worker_done`; the start receipt confirms capability. Unavailable automation stays unresolved and is not emulated by Coordinator polling. |
| Coordinator wake source | Orca/equivalent host or user notification for `question`, `escalation`, or `worker_done`; heartbeat does not resume a Coordinator turn. Human Test results start a new Waterfall and never wake this pair. |
| Coordinator inbox check | One non-waiting check of its own mailbox per external notification; never read the worker inbox. Process, acknowledge, and stop. |
| Automatic polling | Forbidden: automatic `check --wait`, periodic checks, heartbeat turns, and post-ack polling. |
| Context intake | Read baseline source once before dispatch and consume compact `core-execution-items-v1` cards first. If a Plan decision still lacks evidence, read one relevant artifact/report slice once. No `worker-read`, transcript replay, or repeated terminal/Git/source/plan dumps. |
| Execution state | This Plan/Handoff pair is canonical. The Coordinator applies existing edges directly; no parallel state artifact or runner skill is required. |
| Completion | Normal completion requires `worker_done`; terminal idle or elapsed time is not completion. Clean up the terminal once after the completion event. |
| Lifecycle delivery recovery | After confirmed delivery failure, make one bounded resend/reconciliation attempt, then stop as unresolved or blocked. |
| Human approval wait | Send one `question`, continue independent authorized work, and yield the active turn. A response may arrive hours later; keep the session passively resumable and do not convert pending response into timeout, failure, `worker_done`, or DAG-level `blocked`. |
| Independent re-review | Not a default step; include only on explicit current-user request or a higher-priority repository/accepted-plan contract. |
| Wait/resource guard | Fixed-interval and busy waits are forbidden. On sustained CPU/thermal pressure or a `kernel_task` spike, capture one compact observation, stop the wait/process loop, and escalate without automatic retry; the signal does not prove the cause. |

## Timing Observation

| Control | Contract |
|---|---|
| Timing policy | `worker-done-observation-v2` |
| Plan expectation | __PLAN_TIMING_EXPECTATION__ |
| Enforcement | `advisory_only` |
| Observation point | `worker_done_only` |
| Clock reads | `start_finish_only` |
| Overrun effect | `planning_signal_only` |
| Missing observation | `unknown` |
| Carry forward | `next_waterfall_if_material` |
| Forbidden implementation | `no_deadline_timeout_stall_sleep_polling` |

## Task DAG

```mermaid
flowchart TD
    R0["__R0__"] --> D0["__D0__"]
    D0 --> C0["__C0__"]
    C0 --> CR0["__CR0__"]
    CR0 --> T0["__T0__"]
```

The Mermaid graph is the finite compiled instance. Bounded repair, re-review, re-test, or
Spiral continuation appends new node IDs under the declared rewrite budget; never draw a
back-edge to an executed node. For one semantically admitted same-contract repair, append no more
than `BF1 -> CR1 -> BF2 -> CR2`. A first implementation or explicit production-mechanism
replacement uses an existing or Plan-corrected `C -> CR` path and consumes no BF attempt; without
an authorized edge, escalate for Plan revision.
Only when terminal review remains `repair_required` after semantically admitted same-contract BF
history and a bounded `known_bug_candidate` exists does the Coordinator record the final Known Bug.
It then follows the existing Plan rather than appending a third repair, wait, or early-close node.

## Typed Edges

Include exactly one row for every Mermaid edge. Use only `depends_on`, `unblocks`,
`branches_to`, `verified_by`, `gates`, `repairs`, `reverifies`, or `approves`.

| From | Type | To | Gate / evidence |
|---|---|---|---|
| `__EDGE_FROM__` | __EDGE_TYPE__ | `__EDGE_TO__` | __EDGE_EVIDENCE__ |

## DAG Node Routing

Include exactly one row for every DAG node. Write `inherit` in Model, Effort, or
`selected_skills` to reuse the role default from Execution Routing; write an explicit value
only to override. Fill a non-applicable cell with `none`; escape a literal `|` inside a
cell as `\|`.

| Task | Kind | Depends on | Role / agent | Model | Effort | selected_skills | Context / input | Expected timing | Lock scope | Expected output | Validation owner | Stop / escalation |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `__TASK_ID__` | __NODE_KIND__ | __DEPENDS__ | __ROLE_AGENT__ | __MODEL__ | __EFFORT__ | __SKILLS__ | __CONTEXT_INPUT__ | __EXPECTED_TIMING__ | __LOCK__ | __OUTPUT__ | __VALIDATION_OWNER__ | __STOP__ |

## Validation and Termination

| Condition | Decisive evidence | Owner |
|---|---|---|
| __CONDITION__ | __VERIFIER__ | __OWNER__ |

- Machine checks prove only their stated contracts.
- Broader human-graded product quality remains `__HUMAN_GRADE_LABEL__` outside this plan after
  the `human_test_ready` transition.
- For `phase_gate_delivery`, this plan terminates at `human_test_ready` immediately before Human
  Test. Close the old handoff; the later result and new worklist/design start a new Waterfall.
- Do not infer phase or plan completion from one completed batch.

## Approval Gate

Current state: __APPROVAL_STATE__.

Next authorized action: __NEXT_ACTION__.
