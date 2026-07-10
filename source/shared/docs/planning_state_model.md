# Planning State Model

This reference defines the shared Planning-family state model. It is a routing
and artifact-governance contract, not a queue, scheduler, daemon, automation
runtime, or replacement for implementation workflows.

## Core Rule

Planning skills may propose questions, summaries, candidate scopes, and next
events. State transitions are accepted only when an event satisfies the current
state's invariants.

In practice:

- Nondeterministic language-model output stays at the edge as proposal text.
- The deterministic core is the tuple of `current_state`, `event`, `invariant`,
  `evidence`, and `next_state`.
- A plan document, requirements brief, loop contract, package, or closeout note
  is active only inside the state and horizon where it was admitted.

## States

| state | owner | meaning | required evidence before leaving |
| --- | --- | --- | --- |
| `scratch` | current task | Temporary notes, rough goal, or ambiguous plan intent. | Enough user intent to ask a decision question or start direct work. |
| `discovery` | `plan-requirements-discovery` | Requirements gaps are being converted into explicit decisions. | Decision record or unresolved assumptions marked for handoff. |
| `requirements_contract` | `plan-requirements-brief` | Scope, non-goals, assumptions, and observable acceptance criteria are stable. | Accepted or explicitly referenced contract. |
| `active_plan` | `plan-short-term-docs` | Current-horizon implementation design/status artifact under `docs/plan`. | Changed-file list, risks, validation procedure, TODOs, and transition status. |
| `implementation_ready` | `plan-short-term-docs` plus execution owner | Active plan has clear current-task implementation approval. | Plan scope is explicit and the approval event links to the current task. |
| `executing` | task-specific workflow or `workflow-plan-runner` | Source, test, runtime config/build, or executable scaffold work is in progress. | Changed artifacts and command/manual observations. |
| `validating` | execution owner or `workflow-validation` | Verification is being run against stated success conditions. | Validation output tied to changed artifacts or accepted manual checks. |
| `completed` | execution owner | Required success conditions are satisfied or a scoped result is accepted. | Evidence for each material success condition. |
| `closed_out` | `plan-spec-curator` | Plan is distilled into durable decisions, artifact pointers, and follow-ups. | Closeout summary and future load policy. |
| `archived` | `plan-spec-curator` | Raw plan is historical material. | Archive/load policy: summary-only or explicit-request-only by default. |

Overlay states may attach to the main lifecycle:

- `loop_contract_ready`: `plan-loop-term` has accepted success conditions,
  verifier evidence mapping, retry terms, and stop policy.
- `package_planned`: `plan-long-term-package` has a canonical source-of-truth
  hierarchy and release gates for a multi-document package.
- `summary_only`: a closed or archived plan may inform context through a compact
  summary without admitting raw plan text.

## Events And Preconditions

| event | valid from | next state | preconditions |
| --- | --- | --- | --- |
| `ask_decision_question` | `scratch`, `discovery` | `discovery` | A requirements gap changes scope, acceptance, edge behavior, data ownership, or non-goals. |
| `record_decision` | `discovery` | `discovery` | The answer is decision-bearing and linked to the open question. |
| `distill_requirements` | `discovery` | `requirements_contract` | Decisions are sufficient to state scope, non-goals, assumptions, and observable acceptance criteria. |
| `create_active_plan` | `requirements_contract`, `scratch` | `active_plan` | The user requested a persisted current-horizon `docs/plan` artifact or an active plan already owns the task. |
| `approve_implementation` | `active_plan` | `implementation_ready` | The current active plan scope is explicit and the approval wording applies to this task. |
| `start_execution` | `implementation_ready` | `executing` | Runtime/sandbox policy permits mutation and a task-specific implementation workflow owns the work. |
| `record_validation_evidence` | `executing`, `validating` | `validating` | Evidence is tied to changed artifacts or accepted manual checks. |
| `mark_completed` | `validating` | `completed` | Every material success condition has evidence or an accepted residual-risk note. |
| `closeout_plan` | `completed` | `closed_out` | Durable decisions, artifact pointers, follow-ups, and future load policy are captured. |
| `archive_or_summary_only` | `closed_out`, `archived` | `archived` or `summary_only` | Raw plan text is not needed for the current task. |
| `reject_invalid_transition` | any | unchanged | Preconditions are missing, stale, contradictory, or outside the current scope. |

## Invalid Transition Examples

- A one-word `approved`, `승인`, `go`, `작업해`, or `구현해` without an explicit
  active plan scope does not fire `approve_implementation`.
- A casual mention of `plan`, `goal`, `phase`, or `loop` does not create a plan,
  package, or loop contract by itself.
- A requirements contract with non-observable acceptance criteria does not become
  an executable plan.
- A `/goal` or loop request without success conditions and verifier evidence
  mapping cannot enter loop execution.
- A `completed`, `closed_out`, `superseded`, or `archived` plan does not return
  to active context by historical relevance alone.
- A multi-document package must not duplicate canonical state names, release
  gates, or source-of-truth ownership across derived docs.

## Skill Responsibilities

| skill | state responsibility |
| --- | --- |
| `plan-requirements-discovery` | `scratch -> discovery`; ask one decision-bearing question and record decisions. |
| `plan-requirements-brief` | `discovery -> requirements_contract`; stabilize scope, non-goals, assumptions, and acceptance criteria. |
| `plan-short-term-docs` | `active_plan -> implementation_ready`; keep the current-horizon plan synchronized and gate implementation transition. |
| `plan-loop-term` | `loop_contract_ready` overlay; define verifier-backed success, progress, retry, and stop terms before loop execution. |
| `plan-long-term-package` | `package_planned` overlay; keep canonical contracts and package-derived docs from drifting. |
| `plan-spec-curator` | `completed -> closed_out -> archived`; control raw-plan admission, closeout summaries, and memory/archive proposals. |

## Reporting Requirement

When a planning state affects execution or context admission, report the current
state, attempted event, accepted next state or rejection reason, and the evidence
used for that decision.
