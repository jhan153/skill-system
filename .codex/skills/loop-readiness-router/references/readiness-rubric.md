# Loop Readiness Rubric

Use this rubric to classify requests before execution.

## Source-Grounded Decision Model

Loop engineering is the control design around repeated agent runs: what state the agent sees, what actions it may take, how observations are collected, how progress is verified, and when the controller continues, retries, recovers, pauses, delegates, or stops. Treat this as a control problem, not as a synonym for a long prompt.

Use these factors before classification:

| Factor | Low loop need | Higher loop need |
| --- | --- | --- |
| Outcome observability | Done state is obvious or one command verifies it. | Done state needs multiple evidence lanes or subjective criteria must become measurable. |
| Verifier feedback value | A check only confirms completion after one edit. | Check results can change the next implementation step. |
| State/checkpoint need | Work fits in one turn and no resume state is needed. | Work needs iteration counters, pending requirements, evidence history, or side-effect journals. |
| Uncertainty shape | Path is known and deterministic. | The path is uncertain, but feedback can narrow it. |
| Side-effect risk | Local reversible edits only. | Credentials, deployment, deletion, paid APIs, external writes, or approvals may be involved. |
| Runtime capability | Manual/direct execution is enough. | Durable resume, event triggers, Stop-hook loop evaluation, Wiki feedback, or parallel agents are expected. |
| Cost/benefit | Loop overhead would not change evidence. | Repeated verifier cycles materially reduce failure risk. |

Default to the smallest reliable workflow. Use loop engineering when repetition plus verification can improve the outcome, not when a direct workflow is enough.

## Classification Rules

### `one_shot`
Use when most of these are true:
- scope is small and local
- done state is obvious
- verifier is deterministic or already known
- no repeated feedback is needed
- no side effects beyond normal local file edits
- no visual fidelity, external system, or long-running state is involved
- the expected validation is a final check, not an iterative steering signal

Examples:
- "버튼 색만 바꿔줘"
- "이 명령 결과 보여줘"
- "이 함수에 null guard 추가해줘"

### `contract_needed`
Use when execution should wait for explicit terms:
- done state is ambiguous or subjective
- success criteria span multiple artifacts
- verifier commands or evidence are unknown
- independent maker/checker separation is needed but not mapped yet
- state, checkpoint, retry, idempotency, or stop terms are missing
- Stop-hook loop evaluation, durable execution, event-driven runtime, Wiki feedback, or improvement-loop expectations are requested but not evidenced
- parallel agents or non-idempotent retries are requested without ownership, merge, idempotency, or approval gates
- side effects, approval gates, credentials, deployment, deletion, paid APIs, or external writes may be involved
- user says "알아서 끝까지" but has not defined stop criteria

Examples:
- "검증 기준 없이 알아서 끝까지 해줘"
- "/goal로 돌리기 전 완료 조건 만들어줘"
- "이 기능이 충분히 좋은지 판단 기준부터 잡아줘"

### `loop_worthy`
Use when repeated verifier feedback is likely to improve or unblock the outcome:
- design or UI fidelity needs render/screenshot/a11y/build feedback
- multiple verifier gates must converge
- implementation may need recovery from failed checks
- progress must be tracked across checkpoints
- task has durable state, resume, or multi-iteration handoff needs
- each iteration can produce a measurable evidence delta, not just more agent activity
- governance contract exists or can be drafted before execution, including no-progress, idempotency, poisoning, reward-hacking, and oscillation controls

Examples:
- "이 Figma 화면을 맞을 때까지 구현해줘"
- "빌드/테스트/스크린샷 검증을 반복해서 통과시켜줘"
- "이 마이그레이션 phase를 검증 실패에 맞춰 반복 실행해줘"

## Contract-Needed vs Loop-Worthy

Choose `contract_needed` when the task may become a loop but the contract is missing. Choose `loop_worthy` only when all of these are true:
- The target outcome can be represented as stable success condition ids.
- At least one verifier can emit fail/pass/unverified/blocked evidence after each batch.
- A failed verifier result can reasonably change the next action.
- A checkpoint can preserve completed, failed, pending, and side-effect state.
- Budget and stop terms can be stated before execution.
- Non-idempotent retry, context poisoning, reward hacking, thrashing, infinite retry, premature completion, and oscillation have explicit stop/recovery rules.

If any of these are absent, request or draft the missing contract first rather than running a loop.

## Anti-Loop Signals
- The user asks for an explanation, summary, or one command output.
- The task has a single obvious edit and one obvious check.
- The requested output is a contract, plan, or review only, not execution.
- A loop would add cost without changing the evidence available.
- The only verifier is the same maker agent saying it is done.
- The task cannot produce independent evidence until a user supplies private/authenticated context.
- The request asks for scheduling, queueing, webhook, cron, or durable runtime but the current host capability is not evidenced.
- Parallel agents would touch overlapping files/artifacts without ownership boundaries.

## Required Rationale
Every classification should name:
- the primary uncertainty
- the verifier situation
- whether side effects exist
- whether runtime/durability/Wiki/parallel/idempotency capabilities are evidenced or missing
- the next skill or direct execution path
- why the chosen path is the minimum sufficient path
