# Analysis Loop Readiness Rubric

Classify before execution. A loop is a feedback-control choice, not a synonym for long, autonomous, risky, or expensive work.

## Two Independent Axes

Score both axes; never use governance risk as a proxy for iteration value.

### `feedback_loop_value`

| value | test |
| --- | --- |
| `none` | validation only confirms a known one-step outcome; it would not change the action |
| `low` | findings may adjust later dependent steps, but work does not need repeated convergence on the same conditions |
| `high` | each verifier batch can materially change the next implementation action until stable conditions pass |

### `governance_risk`

| value | test |
| --- | --- |
| `local` | reversible local work with ordinary validation |
| `governed` | approval, idempotency, rollback, ownership, budget, or checkpoint gates exist and are explicit |
| `high` | required gates are missing, verifier/state integrity is uncertain, or non-idempotent/live effects are uncontrolled |

A deterministic deployment or migration can be governed one-shot/checkpointed work. It becomes `contract_needed` when its gates are missing, not `loop_worthy` merely because it is risky.

## Supporting Factors

- **Outcome observability:** one obvious check versus multiple/subjective evidence lanes.
- **Checkpoint need:** fits one turn versus dependent, resumable steps and accepted findings.
- **Uncertainty shape:** known path versus feedback that can narrow the path.
- **Runtime capability:** direct execution versus evidenced durable/event runtime.
- **Cost/benefit:** whether another verifier cycle can reduce failure risk.

Cron, webhook, queue, automation, durable scheduling, or event-trigger claims require `.codex/docs/orchestration_capability_contract.md` or equivalent current evidence.

## Classification

### `one_shot`

Use when the action and done state are direct, checkpoint state is unnecessary, and `feedback_loop_value` is `none`. Governance may be `local` or already `governed`.

Examples:
- change one button color and render once;
- show one command result;
- run one approved, idempotent external action and verify its result.

### `checkpointed_task`

Use when work has dependent steps, spans turns, or must resume safely, but checks do not repeatedly steer convergence on the same conditions. Attach `workflow-task-ledger`; keep the task-specific primary skill as execution owner.

Signals:
- several ordered implementation/validation steps;
- accepted findings or partial artifacts must survive handoff;
- a bounded migration/release has explicit approval, rollback, and idempotency gates;
- `feedback_loop_value` is `none` or `low`, even if governance is `governed`.

### `contract_needed`

Use when execution should wait because at least one required invariant is missing:

- outcome or pass/fail signals are ambiguous;
- verifier owner/evidence path is unknown;
- checkpoint, retry, budget, stop, approval, idempotency, rollback, or ownership terms are required but absent;
- durable/event/Stop-hook/Wiki capability is claimed but not evidenced;
- user asks for repeated execution without stable `SC-NNN` conditions.

This classification says "define terms first"; it does not assert that the eventual execution should be a loop.

### `loop_worthy`

Use only when `feedback_loop_value` is `high` and these terms are already known or can be stated in the next contract:

- stable success conditions can be stated;
- a verifier emits pass/fail/unverified/blocked after each batch;
- failed evidence can change the next action;
- checkpoints preserve condition, evidence, pending, and side-effect state;
- budgets and stop/recovery terms can be bounded;
- approval/idempotency and anti-gaming/stability controls are explicit where applicable.

Typical examples are UI fidelity driven by screenshot/a11y findings, multi-gate implementation whose failed checks require different fixes, or recovery-driven work where each narrowed failure changes the strategy.

## Decision Order

1. Can a separate verifier observe the user-visible outcome?
2. Would verifier feedback change the next action more than once?
3. Does work need durable step/finding state without feedback convergence?
4. Which governance gates are required, and are they already explicit?
5. Choose the smallest class that preserves evidence and safety:
   - no repeated steering, no checkpoint -> `one_shot`;
   - dependent/resumable but non-convergent -> `checkpointed_task`;
   - required terms missing -> `contract_needed`;
   - repeated steering plus complete/authorable contract -> `loop_worthy`.

Choose `loop_worthy` when repeated steering is clear and stable conditions plus governance terms can be authored; the next step is still to draft and accept the contract. Choose `contract_needed` when missing information or capability prevents those terms or even the control shape from being safely defined.

## Anti-Loop Signals

- explanation, summary, review, or one command output;
- one obvious edit and final check;
- plan/contract creation rather than execution;
- no independent evidence until the user supplies private context;
- iterations would repeat the same evidence;
- parallel writers lack distinct ownership;
- scheduling/runtime is requested but host capability is not evidenced.

## Required Rationale

Return one classification and name:

- primary uncertainty and outcome observability;
- `feedback_loop_value` with the steering evidence;
- `governance_risk` and missing gates;
- checkpoint/runtime needs;
- next skill or direct path;
- why this is the minimum sufficient class.
