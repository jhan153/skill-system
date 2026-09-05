# Planning State Model

This reference governs only the requirements-admission sequence shared by Planning skills. It is
not an execution state machine, scheduler, archive manager, or substitute for a Plan/Handoff pair.

Direct work with sufficient requirements stays outside this model. Durable execution state belongs
only to `plan-execution-handoff`; lightweight handoff packets and decision maps keep their own
artifact contracts without entering this state machine.

For materially fuzzy or dependent work, `docs/task_working_state_contract.md` defines task-local
facts, constraint meaning, freshness, and selective correction. That envelope adds no planning
state or transition and grants no persistence or execution authority. Clear one-shot work bypasses it.

## States

| State | Owner | Meaning | Exit evidence |
|---|---|---|---|
| `scratch` | current task | A rough goal or ambiguous planning premise. | Enough intent to ask a bounded decision question, begin discovery, or return to direct work. |
| `discovery` | `plan-requirements-discovery` | Material requirement gaps are being converted into explicit decisions. | Decisions plus unresolved assumptions and their owners. |
| `requirements_contract` | `plan-requirements-brief` | Scope, non-goals, assumptions, and observable acceptance criteria are stable. | Accepted or explicitly referenced contract ready for direct work or Execution Handoff authoring. |

`plan-behavior-discovery`, `plan-test-discovery`, `plan-decision-map`, and `plan-question-document` stay outside
this state model. They provide bounded decision input but do not imply requirements acceptance,
implementation approval, or execution completion.

## Events

| Event | Valid from | Next state | Preconditions |
|---|---|---|---|
| `ask_decision_question` | `scratch`, `discovery` | `discovery` | The question changes scope, acceptance, edge behavior, data ownership, constraints, or non-goals. |
| `record_decision` | `discovery` | `discovery` | The answer is linked to one open question and its decision owner. |
| `distill_requirements` | `discovery` | `requirements_contract` | Decisions are sufficient to state observable scope and acceptance. |
| `route_direct_work` | `scratch`, `requirements_contract` | outside this model | Requirements are sufficient, no durable execution artifact is needed, and the current request authorizes the work. |
| `author_execution_handoff` | `requirements_contract`, `scratch` | outside this model | Durable single-node or multi-node execution state is explicitly needed; `plan-execution-handoff` creates its own canonical pair and approval boundary. |
| `reject_invalid_transition` | any | unchanged | Required intent, authority, or evidence is missing, stale, contradictory, or outside scope. |

## Invariants

- A casual mention of `plan`, `goal`, `phase`, or `loop` creates no planning state.
- A requirements contract with non-observable acceptance criteria is not ready for execution.
- Planning text, approval prose, or a plan-only diff is never implementation evidence.
- A task-specific Workflow owns direct execution; an Orchestrator follows only an accepted
  Plan/Handoff pair.
- Execution Handoff status, DAG transitions, Human Test handoff, closeout, and supersession remain
  inside that pair's own contract and are not projected back into this state model.

## Responsibilities

| Skill | Responsibility |
|---|---|
| `plan-requirements-discovery` | Move `scratch` into bounded `discovery` and record decision-bearing answers. |
| `plan-requirements-brief` | Distill accepted discovery into `requirements_contract`. |
| `plan-behavior-discovery` | Resolve one existing-capability behavior decision outside this state model. |
| `plan-test-discovery` | Resolve one human-owned test judgment surfaced by Test Design outside this state model; decided scope becomes Execution Handoff input only through its own admission/revision contract. |
| `plan-decision-map` | Hold durable unresolved decision dependencies without implying execution readiness. |
| `plan-question-document` | Request one answer owner's input; returned answers enter discovery only through a later explicit action. |
| `plan-execution-handoff` | Consume accepted requirements or explicit current scope and create its own durable execution pair. |

When reporting an admitted transition, name the current state, attempted event, accepted next state
or rejection reason, and the evidence that decided it.
