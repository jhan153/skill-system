---
doc_type: orchestration_handoff
plan_id: __PLAN_ID__
authority: subordinate_execution_ledger
status: __STATUS__
updated_at: __DATE__
execution_profile: plan-handoff-v6
method_profile: risk-adaptive-development-v1
graph_archetype: __GRAPH_ARCHETYPE__
test_authority: __TEST_AUTHORITY__
test_transition: __TEST_TRANSITION__
timing_policy: worker-done-observation-v2
coordination_mode: event_driven
coordinator_observation: notification_only
---

# __TITLE__ Handoff

## Record Contract

- `plan.md` owns normative scope and completion.
- This file records current state, decisions, observed evidence, and next ownership.
- The Coordinator — or the single session owner when no Coordinator role is instantiated —
  is the only writer of this file; workers report results to that writer.
- This pair is the only execution state. A parallel state artifact or runner is never required to
  advance its existing edges.
- Corrections append a new row; do not erase material prior decisions or failures.
- Method profile and graph archetype mirror `plan.md`. A bounded rewrite updates the canonical
  plan DAG and Typed Edges before this handoff's Task State; this file cannot rewrite topology.
- When superseded rows obscure current state, compact them into one summary row per topic
  that preserves material decisions, failures, and open risks; do not create archive files.
- Do not copy heartbeats, worker transcripts, repeated terminal/source/diff output, or polling
  history into this file. Record only actionable lifecycle outcomes and decisive evidence.
- The Coordinator wakes only from an external notification for `question`, `escalation`, or
  `worker_done`, performs one non-waiting inbox check, acknowledges, and stops.
- This handoff does not authorize or prove implementation.
- A Known Bug is unresolved but locally terminal for the current run. It never means fixed or
  passed and never creates a Coordinator wait or global block by itself.
- Cross-owner results use `core-execution-items-v1`. Workers produce compact cards; only this
  ledger writer records deferred items, final Known Bugs, and the exact next Plan node.

## Current Snapshot

| Field | Value |
|---|---|
| Plan | `plan.md` · __PLAN_STATUS__ |
| Workspace | __WORKSPACE__ |
| Branch / HEAD | __BASELINE__ |
| Dirty ownership | __DIRTY_STATE__ |
| Current phase | __CURRENT_PHASE__ |
| Implementation | __IMPLEMENTATION_STATE__ |
| Method / graph | `risk-adaptive-development-v1` / `__GRAPH_ARCHETYPE__` |
| Test authority | `__TEST_AUTHORITY__` |
| Test transition | `__TEST_TRANSITION__` |
| Timing policy | `worker-done-observation-v2`; plan expectation: __PLAN_TIMING_EXPECTATION__ |
| Coordinator mode | event consumer; automatic polling and `check --wait` forbidden |
| Pending human event | none; when present, one question is delivered and the worker stays passively resumable without an active wait loop |
| Last actionable lifecycle event | none yet |
| Next Coordinator wake | external notification only |

## Execution Routing

| Task / scope | Actual agent | Model / effort | selected_skills | Write or decision boundary |
|---|---|---|---|---|
| `__TASK_ID__` | __AGENT__ | __MODEL_EFFORT__ | __SKILLS__ | __BOUNDARY__ |

## Decisions

| Seq | Decision or deviation | Authority / evidence | Downstream effect |
|---:|---|---|---|
| 1 | __DECISION__ | __AUTHORITY__ | __EFFECT__ |

## Task State

| Task | Depends on | Status | Expected output | Validation owner |
|---|---|---|---|---|
| `__TASK_ID__` | __DEPENDS__ | pending | __OUTPUT__ | __VALIDATION_OWNER__ |

## Execution Items

Insert one row using the matching `references/core-execution-items-v1/cards/<card_type>.md`
template. Full diagrams, source analysis, logs, and diffs stay in their owning artifact or worker
context.

| Item ID | Kind | Producer / node | Compact outcome | Artifact / evidence refs |
|---|---|---|---|---|
| none | none | none | none | none |

## Timing Observations

Update a row only when that task's `worker_done` body arrives. Timing is advisory.

| Task | Expected | Started at | Completed at | Elapsed | Assessment | Planning note |
|---|---|---|---|---|---|---|
| `__TASK_ID__` | __EXPECTED_TIMING__ | pending | pending | pending | pending | none |

## Human Test Transition

Use this section when Test transition is `next_waterfall`; otherwise fill each Contract with
`none`. The current Waterfall terminates before the user begins Test.

| Field | Contract |
|---|---|
| Current plan termination | `human_test_ready` immediately before Human Test |
| Current pair lifecycle | complete and read-only; human Test never resumes or mutates this handoff |
| Test owner | user |
| Start condition | all required agent nodes complete and static review is handoff-ready |
| Test target | __HUMAN_TEST_TARGET__ |
| Test procedure | __HUMAN_TEST_PROCEDURE__ |
| Expected observation | __HUMAN_TEST_EXPECTED__ |
| Result disposition | create a new `plan_id` and new Plan/Handoff pair; do not append to this pair |
| New worklist seed | __NEW_WORKLIST_SEED__ |
| New design seed | __NEW_DESIGN_SEED__ |
| Next Waterfall rule | combine the human Test result with the new worklist/design, rerun Scope Admission, and create a fresh pair |
| Agent wait policy | hand off as `user-verification-needed` and stop; no polling, sleep, or live worker |

## Validation Evidence

| Seq | Condition | Observation | Label |
|---:|---|---|---|
| 1 | Planning artifacts | Plan/Handoff pair created; production behavior not observed | unverified |

## Task Outcomes

| Seq | Task | Outcome | Evidence | Remaining |
|---:|---|---|---|---|
| 1 | Planning | __OUTCOME__ | __EVIDENCE__ | __REMAINING__ |

## Deferred Items

Insert each carry row using `references/core-execution-items-v1/cards/deferred_item.md`.

| ID | Kind | Description / impact | Carry to | Source item |
|---|---|---|---|---|
| none | none | none | none | none |

## Known Bugs

Current review, test, and validation consumers report `SKIP — excluded Known Bug <id>` and do
not reopen or expand verification around these rows during this run. A repair task may remain
`complete` in Task State while its unresolved condition remains visible here.
Insert each final row using `references/core-execution-items-v1/cards/known_bug_record.md`.

| ID | Scope / fingerprint | Attempts and result statuses | Current-run disposition | Reopen condition |
|---|---|---|---|---|
| none | none | none | none | none |

## Next Handoff

- Current owner: __CURRENT_OWNER__.
- Next action: `__NEXT_PLAN_NODE_ID__` — __NEXT_ACTION__; the node must already exist in Plan.
- Open decision or blocker: __OPEN_ITEM__.
- Preserved risk: __RISK__.
- Known Bug transition: record the final Core item and follow the existing Plan edge; when no
  implementation node remains, use the existing terminal node such as `human_test_ready`.
- Coordinator wake: external notification only; do not poll or resume for heartbeat.
- Lifecycle delivery recovery: unused; at most one bounded attempt after confirmed failure.
