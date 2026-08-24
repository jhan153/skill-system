# Orca Worker Runtime Contract

This contract applies only when Orca dispatches a Skill System task or a node from an accepted
Plan/Handoff. Orca owns lifecycle delivery; the selected Workflow still owns the task work, and
the Plan/Handoff Coordinator alone applies existing DAG edges.

## Worker Lifecycle

- The start receipt states whether automatic dispatch intake, worker-inbox intake, follow-up
  consumption, heartbeat, and `worker_done` delivery are available for this worker.
- An available worker-side lifecycle stays enabled. An unavailable capability remains unresolved;
  the Coordinator never emulates it with polling.
- Heartbeats contain liveness only. They never carry source, diffs, transcripts, plans, analysis,
  or a repeated result body.
- `worker_done` is the normal completion signal. Its body contains the compact result/card
  reference, changed artifact references, decisive evidence, unresolved conditions, and one
  start/finish/elapsed observation when the Plan declared advisory timing.
- When work needs human approval or an answer, send one `question`, continue any independent
  authorized work, then yield the active agent turn. Keep the worker session passively resumable;
  do not keep a model turn, shell loop, or reader running.
- A human response may arrive hours later. Pending response is `awaiting_human_event`, not
  `worker_done`, timeout, failure, or DAG-level `blocked`. Resume only when Orca delivers the
  follow-up. Explicit denial or unavailable interaction is handled by the User Work Contract.
- A worker does not select `next_node`, edit Plan/Handoff topology, or finalize a Coordinator-owned
  Known Bug.

## Coordinator Lifecycle

- The Coordinator is an event consumer, not a continuous observer.
- It wakes only after an external notification for `question`, `escalation`, or `worker_done`,
  performs one non-waiting check of its own mailbox, handles the event, acknowledges it, and stops.
- Automatic `check --wait`, periodic inbox checks, heartbeat-driven turns, post-ack checks,
  worker transcript replay, `worker-read`, and repeated terminal/source/diff/status/Plan dumps are
  forbidden.
- Consume the compact event body first. Read one relevant artifact slice once only when the DAG
  decision cannot be made from the body and references.
- Normal completion uses `worker_done`, not terminal idle, elapsed time, or absence of output.
- A confirmed lifecycle-delivery failure permits one bounded resend or reconciliation attempt.
  After that attempt, expose the unresolved delivery condition and stop without polling.
- Surface a pending human question once. Do not send periodic reminders or restart Coordinator
  turns while the user is unavailable.

## Time And Resource Boundary

- Node timing is advisory. Compare expected and actual time once when `worker_done` arrives; never
  implement it as a deadline, timeout, retry schedule, sleep, or liveness interval.
- Human-response latency is excluded from node timing and overrun judgments.
- Do not create fixed waits such as a recurring 15-second check, busy waits, or background terminal
  readers. Waiting must not keep a provider process or coordinator turn active merely to observe
  liveness.
- If sustained CPU/thermal pressure or a `kernel_task` spike is observed, capture one compact
  process/resource observation, stop the wait or process loop, and escalate without automatic
  retry. The signal is operational evidence, not proof of a specific cause.

## Provider Boundary

- Codex, Claude, Grok, and Antigravity may all execute Orca-dispatched work when the current worker
  receipt proves the required lifecycle capability.
- Installing a Skill System plugin or global rule does not prove Orca lifecycle support.
- Provider-native subagents, background tasks, workflows, or polling facilities do not replace
  this lifecycle contract unless the accepted Plan explicitly assigns them and preserves the same
  bounded event semantics.
- Orca messages and receipts do not grant new file, command, network, approval, or external-write
  authority.
